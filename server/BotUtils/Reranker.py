from flashrank.Ranker import Ranker, RerankRequest
from langchain.schema import Document

# Function to convert documents to passages
def convert_docs_to_passages(docs):
    """
    Converts a list of Document objects into a list of passages with 'id', 'text', and 'meta'.
    """
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
    """
    Converts a list of passages (dictionaries) back into Document objects.
    """
    documents = []
    for passage in passages:
        doc = Document(
            page_content=passage['text'],
            metadata=passage['meta']
        )
        documents.append(doc)
    return documents

# Updated reranker_fn to convert docs to passages, rerank them, and then convert them back to documents
def reranker(query, docs, choice):
    # Convert docs to passages
    passages = convert_docs_to_passages(docs)
    
    # Select the ranker model based on the choice
    if choice == "Nano":
        ranker = Ranker()
    elif choice == "Small":
        ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="/opt")
    elif choice == "Medium":
        ranker = Ranker(model_name="rank-T5-flan", cache_dir="/opt")
    elif choice == "Large":
        ranker = Ranker(model_name="ms-marco-MultiBERT-L-12", cache_dir="/opt")

    # Create a rerank request
    rerankrequest = RerankRequest(query=query, passages=passages)
    
    # Perform the reranking
    results = ranker.rerank(rerankrequest)
    
    # # Print results to inspect the structure
    # print("Results:", results)
    
    # If results are a list, directly return them (assuming passages are the list items)
    if isinstance(results, list):
        return convert_passages_to_docs(results)  # Convert passages back to documents
    else:
        # If results are in a dictionary format with a 'passages' key, convert them to documents
        return convert_passages_to_docs(results.get("passages", []))