import streamlit as st
from langchain_ollama import ChatOllama
import BotUtils
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import Document

from flashrank.Ranker import Ranker, RerankRequest
import json

# Function to convert documents to passages
def convert_docs_to_passages(docs):
    passages = []
    for i, doc in enumerate(docs):
        passage = {
            "id": i,
            "text": doc.page_content,
            "meta": doc.metadata
        }
        passages.append(passage)
    return passages

# Function to convert passages back into Document objects
def convert_passages_to_docs(passages):
    documents = []
    for passage in passages:
        doc = Document(
            page_content=passage['text'],
            metadata=passage['meta']
        )
        documents.append(doc)
    return documents

# Updated reranker_fn to convert docs to passages, rerank them, and then convert them back to documents
def reranker_fn(query, docs, choice):
    passages = convert_docs_to_passages(docs)
    
    if choice == "Nano":
        ranker = Ranker()
    elif choice == "Small":
        ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="/opt")
    elif choice == "Medium":
        ranker = Ranker(model_name="rank-T5-flan", cache_dir="/opt")
    elif choice == "Large":
        ranker = Ranker(model_name="ms-marco-MultiBERT-L-12", cache_dir="/opt")

    rerankrequest = RerankRequest(query=query, passages=passages)
    results = ranker.rerank(rerankrequest)
    
    if isinstance(results, list):
        return convert_passages_to_docs(results)
    else:
        return convert_passages_to_docs(results.get("passages", []))

# Main function to run the process
def run():
    vector_db = "vector_db/physics_db"
    llm_model = "llama3.1:8b"
    embed_model = "nomic-embed-text"
    
    # Initialize the bot (in your code, you may need to ensure BotUtils is available)
    BotUtils.start_ollama()
    
    vector_store = BotUtils.loadVectorStore(vector_db, embed_model)
    retriever = BotUtils.getRetriverFromVectorStore(vector_store)
    llm = ChatOllama(model=llm_model)
    
    choice = "Small"  # You can also make this dynamic based on user input

    # Streamlit interface
    st.title('Document Retrieval and Reranking')
    
    # Input for the user query
    query = st.text_input("Enter your query:")
    
    if query:
        # Step 1: Retrieve documents from vector store
        retrieved_docs = retriever.invoke(query)

        # Step 2: Rerank the retrieved documents using reranker_fn
        reranked_docs = reranker_fn(query=query, docs=retrieved_docs, choice=choice)

        # Create a two-column layout in Streamlit
        col1, col2 = st.columns(2)
        
        # Display the original retrieved documents in the left column
        with col1:
            st.header("Retriever Output")
            for i, doc in enumerate(retrieved_docs):
                st.subheader(f"Document {i+1}")
                st.write(doc.page_content)
                st.write("Metadata:", doc.metadata)

        # Display the reranked documents in the right column
        with col2:
            st.header("Reranked Output")
            for i, doc in enumerate(reranked_docs):
                st.subheader(f"Document {i+1}")
                st.write(doc.page_content)
                st.write("Metadata:", doc.metadata)

# Run the Streamlit app
if __name__ == "__main__":
    run()
