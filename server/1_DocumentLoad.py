""" Document Loaders """
""" PDF, PPTX, CSV, etc. -> Documents""" 
# https://python.langchain.com/docs/concepts/document_loaders/

import pprint
from langchain_community.document_loaders import PyPDFLoader

file_path = "../input/aida.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()
pprint.pp(docs[0])
pprint.pp(docs[0].metadata)
pprint.pp(docs[0].page_content)

## This is how a document looks like
# Document(
#     metadata = {
        
#     },
#     page_content = 'contents'
# )