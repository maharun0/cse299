from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss
import os

def embedDocuments(documents, db_name="document_embeddings"):
    # Initialize the embedding model
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Create an empty FAISS index
    sample_vector = embeddings.embed_query("test")
    index = faiss.IndexFlatL2(len(sample_vector))
    
    # Create FAISS vector store
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )

    # Add full documents to the vector store
    vector_store.add_documents(documents=documents)

    # Save vector store to disk
    save_path = f"./{db_name}"
    vector_store.save_local(save_path)
    
    print(f"Vector database saved at: {save_path}")

    return save_path

def loadVectorStore(db_name="document_embeddings"):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    load_path = f"./{db_name}"
    
    if not os.path.exists(load_path):
        print("No existing vector store found!")
        return None

    vector_store = FAISS.load_local(load_path, embeddings, allow_dangerous_deserialization=True)
    print(f"Loaded vector store from: {load_path}")
    
    return vector_store

def searchDocuments(query, db_name="document_embeddings", k=5):
    vector_store = loadVectorStore(db_name)
    if not vector_store:
        return None

    results = vector_store.search(query=query, k=k, search_type="similarity")
    
    print("Search Results:")
    for doc in results:
        print(doc)
    
    return results
