import io
import os
import pickle
import faiss
import datetime
import pymongo
import gridfs
from bson import ObjectId
from typing import Dict, Any, List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import BotUtils
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Start Ollama
BotUtils.start_ollama()

# Global Constants
EMBED_MODEL = "nomic-embed-text"
DEFAULT_LLM_MODEL = "gemma:2b"

# Session-specific state dictionary
session_states: Dict[str, Dict[str, Any]] = {}

# Helper function to convert MongoDB ObjectId to string recursively
def serialize_mongo_doc(doc):
    if isinstance(doc, dict):
        return {key: serialize_mongo_doc(value) for key, value in doc.items()}
    elif isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

# Helper to get or initialize session-specific state
def get_session_state(session_id: str) -> Dict[str, Any]:
    if session_id not in session_states:
        session_states[session_id] = {
            "llm_model": DEFAULT_LLM_MODEL,
            "LLM": ChatOllama(model=DEFAULT_LLM_MODEL),
            "VECTOR_STORE": None,
            "RETRIEVER": None,
            "RAG_MODE": False
        }
    return session_states[session_id]

# ✅ Pydantic Model for API Requests
class QuestionRequest(BaseModel):
    session_id: str
    question: str
    llm_model: str = DEFAULT_LLM_MODEL

# Connect to MongoDB
db, fs = BotUtils.connect_to_MongoDB(db_name="rag_app_db")

# Initialize FastAPI App
app = FastAPI()

# Executor for running blocking calls asynchronously
executor = ThreadPoolExecutor()

# Root API Endpoint
@app.get("/")
async def root():
    return {"message": "Chatbot backend is running."}

# Get - All Sessions
@app.get("/sessions")
async def get_all_sessions():
    try:
        sessions_collection = db["sessions"]
        sessions = list(sessions_collection.find({}))
        
        if not sessions:
            return {"message": "No sessions found"}
        
        # Serialize all sessions to convert ObjectId instances
        sessions = [serialize_mongo_doc(session) for session in sessions]
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {e}")

# Get - A Specific Session
@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    try:
        sessions_collection = db["sessions"]
        session = sessions_collection.find_one({"session_id": session_id})
        
        if not session:
            raise HTTPException(status_code=404, detail="Specified Session not found")
        
        session = serialize_mongo_doc(session)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving specific session: {e}")

# Fn - Create a New Session
def get_or_create_session(session_id: str) -> Dict[str, Any]:
    sessions_collection = db["sessions"]
    session = sessions_collection.find_one({"session_id": session_id})
    if not session:
        session_data = {
            "session_id": session_id,
            "created_at": datetime.datetime.utcnow(),
            "last_modified_at": datetime.datetime.utcnow(),
            "conversation": [],
            "files": {
                "faiss": None,
                "pkl": None
            }
        }
        result = sessions_collection.insert_one(session_data)
        session_data["_id"] = str(result.inserted_id)
        return session_data
    session["_id"] = str(session["_id"])
    return session

# Fn - Update Vector Store and Retriever for a given session state
def update_vector_store_and_retriever(session_id: str):
    state = get_session_state(session_id)
    session = get_or_create_session(session_id)
    if session["files"]["faiss"] is None:
        state["RAG_MODE"] = False
        state["VECTOR_STORE"] = None
        state["RETRIEVER"] = None
    else:
        state["RAG_MODE"] = True
        state["VECTOR_STORE"] = BotUtils.loadVectorStore(f"vector_db/{session_id}", EMBED_MODEL)
        state["RETRIEVER"] = BotUtils.getRetriverFromVectorStore(state["VECTOR_STORE"])

# Fn - Update LLM Model for a given session state
def update_llm(session_id: str, selected_llm_model: str):
    state = get_session_state(session_id)
    if state["llm_model"] != selected_llm_model:
        state["llm_model"] = selected_llm_model
        state["LLM"] = ChatOllama(model=selected_llm_model)

# Post - Ask a Question
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    # Get session-specific state
    state = get_session_state(request.session_id)
    
    # Update LLM and vector store state if needed
    update_llm(request.session_id, request.llm_model)
    update_vector_store_and_retriever(request.session_id)
    
    session = get_or_create_session(request.session_id)
    response = None

    if session["files"]["faiss"] is None:
        # Run blocking LLM call in executor if needed
        response = await asyncio.get_event_loop().run_in_executor(
            executor, lambda: state["LLM"].invoke(input=request.question).content
        )
    else:
        # Define RAG Chain using the per-session retriever and LLM
        RAG_CHAIN = (
            {
                "context": state["RETRIEVER"] | BotUtils.combine_docs,
                "question": RunnablePassthrough()
            }
            | BotUtils.getPrompt()
            | state["LLM"]
            | StrOutputParser()
        )
        response = await asyncio.get_event_loop().run_in_executor(
            executor, lambda: RAG_CHAIN.invoke(input=request.question)
        )

    # Store response in MongoDB
    try:
        db["sessions"].update_one(
            {"session_id": request.session_id},
            {
                "$push": {"conversation": {"user_input": request.question, "response": response}},
                "$set": {"last_modified_at": datetime.datetime.utcnow()}
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB update failed: {e}")

    return {
        "session_id": request.session_id,
        "response": response,
        "created_at": session["created_at"],
        "last_modified_at": datetime.datetime.utcnow()
    }

# Post - Upload File
@app.post("/upload/{session_id}")
async def upload_file(session_id: str, file: UploadFile = File(...)):
    # Ensure upload directory exists
    upload_dir = "files"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")
        
    session = get_or_create_session(session_id)
    state = get_session_state(session_id)
    
    if session["files"]["faiss"] is None:
        state["VECTOR_STORE"] = BotUtils.createVectorStore(EMBED_MODEL)
    
    docs = BotUtils.loadDocument(file_path)
    chunked_docs = BotUtils.semanticChunker(docs, EMBED_MODEL)
    BotUtils.embedChunksInVectorStore(chunked_docs, state["VECTOR_STORE"])
    
    # Save vector store (ensure the function name is correct in BotUtils)
    BotUtils.saveVectoreStore(f"vector_db/{session_id}", state["VECTOR_STORE"])
    
    state["RETRIEVER"] = BotUtils.getRetriverFromVectorStore(state["VECTOR_STORE"])
    
    # GridFS Storage
    vector_store_path = f"vector_db/{session_id}"
    faiss_path = os.path.join(vector_store_path, "index.faiss")
    pkl_path = os.path.join(vector_store_path, "index.pkl")
    
    if not os.path.exists(faiss_path) or not os.path.exists(pkl_path):
        raise HTTPException(status_code=404, detail="Vector store files not found")
    
    try:
        with open(faiss_path, "rb") as f:
            faiss_id = fs.put(f, filename="index.faiss")
        with open(pkl_path, "rb") as f:
            pkl_id = fs.put(f, filename="index.pkl")
    
        db["sessions"].update_one(
            {"session_id": session_id},
            {
                "$set": {"files": {"faiss": faiss_id, "pkl": pkl_id}}
            },
            upsert=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB update failed: {e}")
    
    return {"message": "File uploaded and vector store updated successfully"}
