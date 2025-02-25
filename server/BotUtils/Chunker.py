""" Text Splitters """
""" Document -> Splits or Chunks """
# https://python.langchain.com/docs/concepts/text_splitters/

""" Semantic Chunking """
# https://python.langchain.com/docs/how_to/semantic-chunker/

# What semantic chunking threshold to choose?
# https://youtu.be/7_YNeJvcAtM

from langchain_ollama import OllamaEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

def semanticChunker(docs, embed_model):
    try:
        embed = OllamaEmbeddings(model=embed_model)
        text_splitter = SemanticChunker(embed, breakpoint_threshold_type="standard_deviation")
        chunkedDocuments = text_splitter.transform_documents(docs)
        print("Documents chunked semantically.")
        return chunkedDocuments
    except Exception as e:
        print(f"Error semantically chunking documents: {e}")

