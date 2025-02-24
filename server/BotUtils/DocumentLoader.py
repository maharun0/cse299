""" Document Loaders """
""" PDF, PPTX, CSV, etc. -> Documents""" 
# https://python.langchain.com/docs/concepts/document_loaders/

from langchain_community.document_loaders import PyPDFLoader

def loadDocument(file_path) {
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return docs
}

# Test purpose
if __name__ == "__main__":
    loadPDF("")