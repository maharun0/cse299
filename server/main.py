from langchain_ollama import ChatOllama

model = 'gemma:2b'

llm = ChatOllama(
    model = model,
    temperature = 0.8,
    num_predict = 256,
)

messages = [
    ("system", "You're Sherlock Holmes the detective. Act like him all the time."),
    ("human", "hi"),
]
print(llm.invoke(messages))
