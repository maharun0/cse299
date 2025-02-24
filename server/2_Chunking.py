""" Text Splitters """
""" Document -> Splits or Chunks """
# https://python.langchain.com/docs/concepts/text_splitters/

""" Semantic Chunking """
# https://python.langchain.com/docs/how_to/semantic-chunker/

# What semantic chunking threshold to choose?
# https://youtu.be/7_YNeJvcAtM

## Document loading
from langchain_community.document_loaders import PyPDFLoader

file_path = "../input/aida.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()

## Chunking

## Embedding
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings

embed = OllamaEmbeddings(model="nomic-embed-text")
text_splitter = SemanticChunker(embed, breakpoint_threshold_type="standard_deviation")

documents = text_splitter.transform_documents(docs)

print(len(docs))
print(len(documents))

print(documents)