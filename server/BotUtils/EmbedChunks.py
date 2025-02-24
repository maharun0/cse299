from langchain_ollama import OllamaEmbeddings

import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

def embedChunks(chunkedDocs):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vector = embeddings.embed_query("hello world")
    index = faiss.IndexFlatL2(len(vector))
    
    print(index.ntotal)
    print(index.d)

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index, 
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    
    print(vector_store.index.ntotal)
    print(vector_store.index.d)
    
    ids = vector_store.add_documents(documents=chunkedDocs)
    
    print(vector_store.index.ntotal)
    print(vector_store.index.d)
    print(ids)
    
    ### Retrivals
    question = "how to gain muscle mass?"
    docs = vector_store.search(query=question, k = 5, search_type="similarity")
    print(docs)
    
    ## store the vector_store or it will be lost
    db_name = "health_supplements"
    vector_store.save_local(db_name)
    
    ## load previously saved vector store
    db_path = "path/to/vector_store"
    vector_store = FAISS.load_local(db_name, embeddings, allow_dengerous_deserialization=True)
    

    
    retriver.invoke(question)
    
    ### 
