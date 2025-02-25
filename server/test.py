from langchain_ollama import ChatOllama
import BotUtils
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def run(doc_path):
    vector_db = "physics_db"
    llm_model = "llama3.1:8b"
    embed_model = "nomic-embed-text"
    
    BotUtils.start_ollama()
    
    # docs = BotUtils.loadDocument(pdf_path)
    # chunked_docs = BotUtils.semanticChunker(docs, embed_model)
    
    # vector_store = BotUtils.createVectorStore(embed_model)
    # BotUtils.embedChunksInVectorStore(chunked_docs, vector_store)
    # BotUtils.saveVectoreStore(vector_db, vector_store)
    
    vector_store = BotUtils.loadVectorStore(vector_db, embed_model)
    
    retriever = BotUtils.getRetriverFromVectorStore(vector_store)
    
    llm = ChatOllama(model=llm_model)
    
    while True:
        question=input("User: ")
        retrieved_docs = retriever.invoke(question)
        
        rag_chain = (
            { "context": retriever | BotUtils.combine_docs,"question": RunnablePassthrough() }
            | BotUtils.getPrompt()
            | llm
            | StrOutputParser()
        )
        
        response = rag_chain.invoke(input=question)
        
        print(f"AI: {response}")

# pdf_path = "./input/aida.pdf"
pdf_path = "./input/physics_book.pdf"
run(pdf_path)