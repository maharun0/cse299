import sys
import os
import time
import pandas as pd
import csv
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# Add project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
import BotUtils

def load_csv(file_path):
    """Load the CSV file into a Pandas DataFrame with error handling."""
    try:
        # Read the CSV file with comma separator and quotes
        df = pd.read_csv(file_path, sep=",", quotechar='"', encoding='utf-8')

        # Ensure the DataFrame has the required columns
        required_columns = ['resource_name', 'question', 'bot_answer', 'response_time']
        for col in required_columns:
            if col not in df.columns:
                # Add the column if it doesn't exist
                df[col] = None

        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        print(f"Attempted to load file from: {os.path.abspath(file_path)}")
        raise

def save_csv(df, output_file_path):
    """Save the updated DataFrame to a new CSV file."""
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # Ensure only specified columns are saved
        columns_to_save = ['resource_name', 'question', 'bot_answer', 'response_time']
        df_to_save = df[columns_to_save]

        # Save with comma separator and fully quoted
        df_to_save.to_csv(output_file_path, index=False, sep=",", encoding='utf-8', quoting=csv.QUOTE_ALL)
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        raise

def run(csv_file_path, output_csv_path):
    # Configuration
    llm_model = "qwen2.5:7b"
    embed_model = "nomic-embed-text"
    rerank_model_size = "Small"

    # Start Ollama service
    BotUtils.start_ollama()

    # Load the CSV file
    df = load_csv(csv_file_path)

    # Initialize LLM
    llm = ChatOllama(model=llm_model)

    vector_store = None
    retriever = None
    previous_resource = None

    # Process each row in the CSV file
    for index, row in df.iterrows():
        try:
            resource_name = row["resource_name"]
            question = row["question"]

            # Skip if already processed
            if pd.notna(row.get('bot_answer')):
                print(f"Skipping already processed question: {question}")
                continue

            # Construct PDF path from resource_name
            pdf_path = os.path.join("resources", f"{resource_name}.pdf")

            # Check if PDF exists
            if not os.path.exists(pdf_path):
                print(f"Warning: PDF file not found for {resource_name}")
                continue

            # Update vector store if resource changes
            if previous_resource != resource_name:
                previous_resource = resource_name
                print(f"Processing new resource: {resource_name}")

                # Load and process the new PDF document
                docs = BotUtils.loadDocument(pdf_path)
                chunked_docs = BotUtils.semanticChunker(docs, embed_model)
                vector_store = BotUtils.createVectorStore(embed_model)
                BotUtils.embedChunksInVectorStore(chunked_docs, vector_store)
                retriever = BotUtils.getRetriverFromVectorStore(vector_store)

            # Build the RAG chain
            Reranker = RunnableLambda(
                lambda docs, c=rerank_model_size, q=question: BotUtils.reranker(query=q, docs=docs, choice=c)
            )
            rag_chain = (
                {
                    "context": retriever | Reranker | BotUtils.combine_docs,
                    "question": RunnablePassthrough(),
                }
                | BotUtils.getTestPrompt()
                | llm
                | StrOutputParser()
            )

            # Measure response time
            start_time = time.time()

            # Generate response
            bot_answer = rag_chain.invoke(input=question)

            # Calculate response time
            response_time = time.time() - start_time

            # Update the DataFrame
            df.at[index, "bot_answer"] = bot_answer
            df.at[index, "response_time"] = response_time

            # Save the CSV after each row is processed
            save_csv(df, output_csv_path)

            print(f"Processed question: {question}")
            print(f"Bot Answer: {bot_answer}")
            print(f"Response Time: {response_time:.2f} seconds\n")

        except Exception as e:
            print(f"Error processing row {index}: {e}")
            continue

    print(f"Final updated CSV saved to {output_csv_path}")

def main():
    # File paths
    csv_file_path = "./dataset/chemistry_cleaned.csv"  # Input CSV file path (quoted, comma-separated)
    output_csv_path = "./output/chemistry_answered.csv"  # Output CSV path (fully quoted)

    # Run the process
    run(csv_file_path, output_csv_path)

if __name__ == "__main__":
    main()
