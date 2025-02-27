from langchain_ollama import OllamaEmbeddings
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

def createVectorStore(embed_model):
    try:
        embeddings = OllamaEmbeddings(model=embed_model)
        vector = embeddings.embed_query("hello world")
        # print(len(vector))
        index = faiss.IndexFlatL2(len(vector))
        
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index, 
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        
        print("Vectore store created")
        return vector_store
    except Exception as e:
        print(f"Error creating vector store: {e}")

def loadVectorStore(db_name, embed_model):
    try:
        embeddings = OllamaEmbeddings(model=embed_model)
        vector_store = FAISS.load_local(
            db_name, embeddings, allow_dangerous_deserialization=True)
        print("Vector store loaded")
        return vector_store
    except Exception as e:
        print(f"Error loading vector store: {e}")

def saveVectoreStore(db_name, vector_store):
    vector_store.save_local(db_name)

def embedChunksInVectorStore(chunkedDocs, vector_store):
    ids = vector_store.add_documents(documents=chunkedDocs)
    return vector_store

def getRetriverFromVectorStore(vector_store):
     ## Converting vector store as a retriver
    
    retriver = vector_store.as_retriever(search_type="similarity",
                                        search_kwargs = {'k': 3})
    
    # retriver = vector_store.as_retriever(search_type="similarity_score_threshold",
    #                                     search_kwargs = {'k': 3, 'score_threshold': 0.1})
    
    # retriver = vector_store.as_retriever(search_type="mmr",
    #                                     search_kwargs = {'k': 3, 'fetch_k': 20, 'lamda_mult': 1})
    
    return retriver
     
    
