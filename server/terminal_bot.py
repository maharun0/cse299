from langchain_ollama import ChatOllama
from ..BotUtils import BotUtils
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# Main function to run the process
def run(file_path):
    vector_db = "vector_db/physics_db"
    llm_model = "qwen2.5:0.5b"
    embed_model = "nomic-embed-text"
    rerank_model_size = "Small"
    
    BotUtils.start_ollama()
    
    docs = BotUtils.loadDocument(file_path)
    chunked_docs = BotUtils.semanticChunker(docs, embed_model)
    vector_store = BotUtils.createVectorStore(embed_model)
    BotUtils.embedChunksInVectorStore(chunked_docs, vector_store)
    # BotUtils.saveVectoreStore(vector_db, vector_store)
    
    # Load the vector store (assumed to be pre-built)
    # vector_store = BotUtils.loadVectorStore(vector_db, embed_model)
    retriever = BotUtils.getRetriverFromVectorStore(vector_store)
    
    llm = ChatOllama(model=llm_model)
    
    while True:
        question = input("User: ")
        
        Reranker = RunnableLambda(lambda docs, c=rerank_model_size, q=question: 
                                  BotUtils.reranker(query=q, docs=docs, choice=c))
        rag_chain = (
            { 
                "context":  retriever | Reranker | BotUtils.combine_docs,  
                "question": RunnablePassthrough() 
            }
            | BotUtils.getPrompt()
            | llm
            | StrOutputParser()
        )
        
        response = rag_chain.invoke(input=question)
        
        print(f"AI: {response}")

# pdf_path = "./input/aida.pdf"
pdf_path = "./files/physics_book.pdf"
run(pdf_path)