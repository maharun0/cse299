import BotUtils
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def getRAGChain(vector_db, llm_model, embed_model):
    BotUtils.start_ollama()

    vector_store = BotUtils.loadVectorStore(vector_db, embed_model)
    retriever = BotUtils.getRetriverFromVectorStore(vector_store)
    
    llm = ChatOllama(model=llm_model)
    
    rag_chain = (
        { "context": retriever | BotUtils.combine_docs,"question": RunnablePassthrough() }
        | BotUtils.getPrompt()
        | llm
        | StrOutputParser()
    )
    
    return rag_chain