import os
import subprocess
import platform
import time

def install_dependencies():
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

def activate_virtualenv():
    system = platform.system()
    if system == "Windows":
        subprocess.run([".venv\\Scripts\\activate"], shell=True)
    else:
        subprocess.run(["source", ".venv/bin/activate"], shell=True)

def run_backend():
    print("Running Backend...")
    subprocess.Popen(["uvicorn", "main:app", "--port", "8000", "--reload", "--log-level", "debug"])

def run_frontend():
    print("Running Frontend...")
    subprocess.Popen(["streamlit", "run", "frontend.py"])

def start_mongodb():
    print("Starting MongoDB...")
    system = platform.system()
    if system == "Windows":
        # For Windows, assuming MongoDB is installed as a service and it's already running
        subprocess.Popen(["net", "start", "MongoDB"])
    elif system == "Darwin":  # macOS
        # For macOS, assuming MongoDB was installed using Homebrew
        subprocess.Popen(["brew", "services", "start", "mongodb-community"])
    else:  # Linux
        # For Linux, MongoDB is typically started using systemd
        subprocess.Popen(["sudo", "systemctl", "start", "mongodb"])

def main():
    install_dependencies()
    activate_virtualenv()

    # Start MongoDB
    start_mongodb()

    # Run Backend
    os.chdir("server")
    run_backend()

    # Wait for 3 seconds
    time.sleep(3)

    # Run Frontend
    os.chdir("../frontend")
    run_frontend()

    # Wait for user input to keep the terminal open
    input("Press any key to exit...")

if __name__ == "__main__":
    main()
