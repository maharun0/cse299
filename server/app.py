from fastapi import FastAPI
from pydantic import BaseModel
import BotUtils

app = FastAPI()

# Initialize the RAG Chain
chain = BotUtils.getRAGChain(
    vector_db="physics_db",
    llm_model="llama3.1:8b",
    embed_model="nomic-embed-text"
)

# Request model
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    responses = []
    for response in chain.stream(input=request.question):
        responses.append(response)
    
    return {"response": responses}

@app.get("/")
async def root():
    return {"message": "AI RAG Chain is running!"}

# Run the FastAPI app using: 
# uvicorn app:app --host 0.0.0.0 --port 8000 --reload
# uvicorn app:app --reload
