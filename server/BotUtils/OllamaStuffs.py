import subprocess
import requests

def is_ollama_running():
    try:
        response = requests.get("http://localhost:11434")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_ollama():
    """Start Ollama if it's not running."""
    if not is_ollama_running():
        try:
            print("Starting Ollama...")
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Ollama started successfully.")
        except Exception as e:
            print(f"Error starting Ollama: {e}")
    else:
        print("Ollama is already running.")
        
def getAvailableOllamaLM():
    """Returns available Language Models in Ollama"""
    
    url = "http://localhost:11434/api/tags"
    response = requests.get(url)

    if response.status_code == 200:
        models = response.json().get("models", [])
        filtered_model_names = [
            model.get("model") for model in models 
            if model.get("details", {}).get("quantization_level", "")[0] == "Q"
        ]
        return filtered_model_names
    else:
        return f"Error: {response.status_code}"

if __name__ == "__main__":
    start_ollama()
