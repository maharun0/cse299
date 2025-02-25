from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

from langchain import hub

def getPrompt():
    # prompt = hub.pull("krunal/more-crafted-rag-prompt")
    prompt = """
    # Your role
    You are a brilliant expert at understanding the intent of the questioner and the crux of the question, and providing the most optimal answer to the questioner's needs from the documents you are given.


    # Instruction
    Your task is to answer the question using the following pieces of retrieved context delimited by XML tags.

    <retrieved context>
    Retrieved Context:
    {context}
    </retrieved context>


    # Constraint
    1. Think deeply and multiple times about the user's question\nUser's question:\n{question}\nYou must understand the intent of their question and provide the most appropriate answer.
    - Ask yourself why to understand the context of the question and why the questioner asked it, reflect on it, and provide an appropriate response based on what you understand.
    2. Choose the most relevant content(the key content that directly relates to the question) from the retrieved context and use it to generate an answer.
    3. Generate a concise, logical answer. When generating the answer, Do Not just list your selections, But rearrange them in context so that they become paragraphs with a natural flow. 
    4. When you don't have retrieved context for the question or If you have a retrieved documents, but their content is irrelevant to the question, you should answer 'I can't find the answer to that question in the material I have'.
    5. Use three sentences maximum. Keep the answer concise but logical/natural/in-depth.
    6. Just give the answer. No prefix.

    # Question:
    {question}
    """

    prompt = ChatPromptTemplate.from_template(prompt)
    # print(prompt)
    return prompt

def getRAGChain():
    pass