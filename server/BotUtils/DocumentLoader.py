""" Document Loaders """
""" PDF, PPTX, CSV, etc. -> Documents""" 
# https://python.langchain.com/docs/concepts/document_loaders/

import os

# Combine content of all docs
def combine_docs(docs):
    return '\n\n'.join([doc.page_content for doc in docs])

def getFileExtension(file_name):
    file_extension = os.path.splitext(file_name)[-1]
    print(file_extension)

def loadDocument(file_path):
    extension = getFileExtension(file_path)
    
    if extension == ".pdf":
        return loadPDFDocument(file_path)
    elif extension == ".csv":
        return loadCSVDocument(file_path)
    elif extension == ".json":
        return loadJSONDocument(file_path)
    elif extension == ".md":
        return loadMarkdownDocument(file_path)
    elif extension == ".docx":
        return loadMSWordDocument(file_path)
    elif extension == ".xlsx":
        return loadMSExcelDocument(file_path)
    elif extension == ".pptx":
        return loadMSPPTDocument(file_path)
    else:
        print("Provided file extraction is not supported yet.")

# PDF
# from langchain_community.document_loaders import PyPDFLoader
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
def loadPDFDocument(file_path):
    try:
        # loader = PyPDFLoader(file_path, extraction_mode="layout")
        loader = PyMuPDF4LLMLoader(file_path, mode = "page")
        docs = loader.load()
        print("Document loaded successfully from file.")
        return docs
    except Exception as e:
        print(f"Error loading document from PDF: {e}")

# CSV
from langchain_community.document_loaders.csv_loader import CSVLoader
def loadCSVDocument(file_path):
    try:
        loader = CSVLoader(file_path=file_path)
        docs = loader.load()
        return docs
    except Exception as e:
      print(f"Error loading document from CSV: {e}")
      
# MS Excel
from langchain_community.document_loaders import UnstructuredExcelLoader
def loadMSExcelDocument(file_path):
    try:
        loader = UnstructuredExcelLoader(file_path, mode="elements")
        docs = loader.load()
        return docs
    except Exception as e:
      print(f"Error loading document from MS Excel file: {e}")
      
# JSON
from langchain_community.document_loaders import JSONLoader
def loadJSONDocument(file_path):
    try:
        loader = JSONLoader(
            file_path=file_path,
            jq_schema='.messages[].content',
            text_content=False
        )

        docs = loader.load()
        return docs
    except Exception as e:
      print(f"Error loading document from JSON: {e}")    
# MS Word
from langchain_community.document_loaders import Docx2txtLoader
def loadMSWordDocument(file_path):
    try:
        loader = Docx2txtLoader(file_path)
        docs = loader.load()
        return docs
    except Exception as e:
      print(f"Error loading document from MS Word file: {e}")
 # MS Powerpoint
from langchain_community.document_loaders import UnstructuredPowerPointLoader
def loadMSPPTDocument(file_path):
    try:
        loader = UnstructuredPowerPointLoader(file_path)
        docs = loader.load()
        return docs
    except Exception as e:
      print(f"Error loading document from MS PowerPoint file: {e}")