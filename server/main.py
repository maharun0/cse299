import os
import datetime
import pymongo
import gridfs
import asyncio
import BotUtils
from bson import ObjectId
from typing import Dict, Any, List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from concurrent.futures import ThreadPoolExecutor

# Start Ollama
BotUtils.start_ollama()

# Global Constants
EMBED_MODEL = "nomic-embed-text"
DEFAULT_LLM_MODEL = "qwen2.5:0.5b"

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
    
#
def get_session_state(session_id: str):
    pass

#

###

# Initialize FastAPI App
app = FastAPI()

###

###

###

## 
    
# Fn - Create a New Session
def get_or_create_session(session_id: str) -> Dict[str, Any]:
    sessions_collection = db["sessions"]
    session = sessions_collection.find_one({"session_id": session_id})
    if not session:
        session_data = {
            "session_id": session_id,
            "session_name": None,
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
        
##

# Post - Ask a Question
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    # Get session-specific state
    state = get_session_state(request.session_id)
    
    # Get or create the session and check if session_name is None
    session = get_or_create_session(request.session_id)
    
    if session["session_name"] is None:
        # Call the function to generate the session name if it's None
        session_name = await generate_session_name(request.question)
        
        # Update the session with the generated name
        db["sessions"].update_one(
            {"session_id": request.session_id},
            {
                "$set": {"session_name": session_name},
                "$setOnInsert": {"created_at": datetime.datetime.utcnow()},
            },
        )
        session["session_name"] = session_name  # Update session state with the new name
    
    # Update LLM and vector store state if needed
    update_llm(request.session_id, request.llm_model)
    update_vector_store_and_retriever(request.session_id)
    
    response = None

    # Record the start time
    start_time = datetime.datetime.utcnow()

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

    # Record the end time
    end_time = datetime.datetime.utcnow()

    # Calculate the time taken to generate the response in milliseconds
    time_taken_ms = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds

    # Store response and time in MongoDB
    try:
        db["sessions"].update_one(
            {"session_id": request.session_id},
            {
                "$push": {
                    "conversation": {
                        "user_input": request.question,
                        "response": response,
                        "time_ms": time_taken_ms,  # Store time taken inside the conversation
                    }
                },
                "$set": {"last_modified_at": datetime.datetime.utcnow()},
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB update failed: {e}")

    return {
        "session_id": request.session_id,
        "response": response,
        "session_name": session["session_name"],  # Return the session name
        "created_at": session["created_at"],
        "last_modified_at": datetime.datetime.utcnow(),
        "time_taken_ms": time_taken_ms,  # Include time in the API response as well
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

###


