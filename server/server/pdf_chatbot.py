Added pdf_chatbot.py
 import os
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import Ollama
from langchain.chains import RetrievalQA

def load_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def load_documents():
    pdf_folder = "pdfs"  # Folder where PDFs are stored
    documents = []
    
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            text = load_pdf(pdf_path)
            documents.append(text)

    return documents

docs = load_documents()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_texts = text_splitter.create_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(split_texts, embeddings)

llm = Ollama(model="qwen2.5:0.5b")  # Use your installed Ollama model
retriever = vector_store.as_retriever()
qa_chain = RetrievalQA(llm=llm, retriever=retriever)

def ask_question(query):
    return qa_chain.run(query)

if __name__ == "__main__":
    while True:
        query = input("Ask a question: ")
        if query.lower() == "exit":
            break
        print("Answer:", ask_question(query))
