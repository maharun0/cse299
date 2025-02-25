""" Document Loaders """
""" PDF, PPTX, CSV, etc. -> Documents""" 
# https://python.langchain.com/docs/concepts/document_loaders/

from langchain_community.document_loaders import PyPDFLoader

def loadDocument(file_path):
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        print("Document loaded successfully from file.")
        return docs
    except Exception as e:
        print(f"Error loading document from file: {e}")

# Combine content of all docs
def combine_docs(docs):
    return '\n\n'.join([doc.page_content for doc in docs])