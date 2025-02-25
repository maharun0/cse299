import BotUtils

def run():
    chain = BotUtils.getRAGChain(
        vector_db="physics_db",
        llm_model="llama3.1:8b",
        embed_model="nomic-embed-text"
    )

    try:
        while True:
            question = input("User: ")
            for response in chain.stream(input=question):
                print(response)
            # responses = chain.invoke(input=question)
            print(f"AI: {response}")
    except KeyboardInterrupt:
        print("\nAI: Session terminated by user. Goodbye!")
    
run()
