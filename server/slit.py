import streamlit as st
import requests
import json
import datetime
import time

# API Endpoint
API_BASE_URL = "http://127.0.0.1:8000"  # Ensure this matches your FastAPI backend URL

# Updated Available LLM Models
LLM_MODELS = [
    "qwen2.5:0.5b",
    "qwen2.5:7b",
    "gemma3:4b",
    "llama3.1:8b",
    "llama2-uncensored:latest",
    "deepseek-r1:1.5b",
    "deepseek-r1:8b",
]

# Streamlit App Configurations
st.set_page_config(
    page_title="Wingbot",
    page_icon="🧠",
    layout="wide",
)

# Sidebar for Session Management
def create_new_session():
    """Creates a new session using the current timestamp."""
    timestamp = datetime.datetime.now()
    return f"session_{timestamp.strftime('%d%m%Y%H%M%S')}{timestamp.microsecond // 1000}"

def fetch_all_sessions():
    """Fetches all available sessions from the backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/sessions")
        if response.status_code == 200:
            return response.json()
        else:
            st.sidebar.warning("Failed to fetch sessions from backend")
            return []
    except Exception as e:
        st.sidebar.error(f"Error connecting to backend: {str(e)}")
        return []

# Initialize session states if not already present
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = LLM_MODELS[0]
if "local_sessions" not in st.session_state:
    st.session_state.local_sessions = []

# "New Chat" button to create a new session on demand
if st.sidebar.button("New Chat"):
    new_session_id = create_new_session()
    st.session_state.current_session_id = new_session_id
    st.session_state.conversations = []
    # Add to local sessions list if not already present
    if new_session_id not in [session.get("session_id") for session in st.session_state.local_sessions]:
        st.session_state.local_sessions.append({"session_id": new_session_id, "conversation": []})
    st.sidebar.success(f"Created new session: {new_session_id}")

# Automatically create a new session if none exists
if st.session_state.current_session_id is None:
    new_session_id = create_new_session()
    st.session_state.current_session_id = new_session_id
    st.session_state.conversations = []
    if new_session_id not in [session.get("session_id") for session in st.session_state.local_sessions]:
        st.session_state.local_sessions.append({"session_id": new_session_id, "conversation": []})
    st.sidebar.success(f"Created new session: {new_session_id}")

# Option to refresh sessions from the backend
if st.sidebar.button("Refresh Sessions"):
    with st.sidebar.spinner("Fetching sessions..."):
        all_sessions = fetch_all_sessions()
        if all_sessions:
            st.sidebar.success(f"Found {len(all_sessions)} sessions in the backend")
        else:
            st.sidebar.info("No sessions found in the backend")

# Get all sessions (combination of backend + local)
all_sessions = fetch_all_sessions()
backend_session_ids = [session["session_id"] for session in all_sessions]

# Include any local sessions not yet in the backend
all_session_ids = backend_session_ids.copy()
for local_session in st.session_state.local_sessions:
    if local_session["session_id"] not in all_session_ids:
        all_session_ids.append(local_session["session_id"])

# Display session list if any exist
if all_session_ids:
    selected_session = st.sidebar.selectbox("Select a session", options=all_session_ids, index=all_session_ids.index(st.session_state.current_session_id) if st.session_state.current_session_id in all_session_ids else 0)
    
    if selected_session and st.sidebar.button("Load Session"):
        with st.sidebar.spinner("Loading session..."):
            # Try loading from local sessions first
            local_session_data = next((s for s in st.session_state.local_sessions if s["session_id"] == selected_session), None)
            if local_session_data:
                st.session_state.current_session_id = selected_session
                st.session_state.conversations = local_session_data.get("conversation", [])
                st.sidebar.success(f"Loaded session: {selected_session}")
            else:
                # Fallback: try loading from backend
                try:
                    response = requests.get(f"{API_BASE_URL}/sessions/{selected_session}")
                    if response.status_code == 200:
                        session_data = response.json()
                        st.session_state.current_session_id = selected_session
                        st.session_state.conversations = session_data.get("conversation", [])
                        st.sidebar.success(f"Loaded session: {selected_session}")
                    else:
                        st.sidebar.error(f"Failed to load session (Status code: {response.status_code})")
                except Exception as e:
                    st.sidebar.error(f"Error loading session: {str(e)}")
else:
    st.sidebar.info("No sessions available. Use 'New Chat' to create one.")

# Sidebar Model Selection
st.sidebar.subheader("Model Selection")
st.session_state.selected_model = st.sidebar.selectbox("Choose an LLM model", options=LLM_MODELS)

# File Upload Feature
st.sidebar.subheader("Upload Documents")
uploaded_file = st.sidebar.file_uploader("Upload a file", type=["pdf", "txt", "docx", "csv"])
if uploaded_file and st.session_state.current_session_id:
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{API_BASE_URL}/upload/{st.session_state.current_session_id}", files=files)
        if response.status_code == 200:
            st.sidebar.success(f"File uploaded: {uploaded_file.name}")
        else:
            st.sidebar.error(f"Failed to upload file (Status code: {response.status_code})")
    except Exception as e:
        st.sidebar.error(f"Error uploading file: {str(e)}")

st.title("Wingbot 🧠")
st.caption(f"Current Session: {st.session_state.current_session_id} | Model: {st.session_state.selected_model}")

# Function to fetch conversation history
def fetch_conversation_history(session_id):
    # Check local sessions first
    local_session = next((s for s in st.session_state.local_sessions if s["session_id"] == session_id), None)
    if local_session:
        return local_session.get("conversation", [])
    # Fallback: fetch from backend
    try:
        response = requests.get(f"{API_BASE_URL}/sessions/{session_id}")
        if response.status_code == 200:
            return response.json().get("conversation", [])
        return []
    except Exception:
        return []

# Load conversation history only once
if st.session_state.current_session_id and not st.session_state.conversations:
    st.session_state.conversations = fetch_conversation_history(st.session_state.current_session_id)

# Display chat history
chat_container = st.container()
with chat_container:
    for conv in st.session_state.conversations:
        with st.chat_message("user"):
            st.write(conv["user_input"])
        with st.chat_message("assistant"):
            st.write(conv["response"])

# Chat input field and handling
if st.session_state.current_session_id:
    user_question = st.chat_input("Ask a question...")
    if user_question:
        with st.chat_message("user"):
            st.write(user_question)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                payload = {
                    "session_id": st.session_state.current_session_id,
                    "question": user_question,
                    "llm_model": st.session_state.selected_model
                }
                with st.spinner("Getting response..."):
                    response = requests.post(f"{API_BASE_URL}/ask", json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        responses = result["response"]
                        # Append the new conversation
                        new_message = {"user_input": user_question, "response": responses}
                        st.session_state.conversations.append(new_message)
                        # Update local session history
                        for i, session in enumerate(st.session_state.local_sessions):
                            if session["session_id"] == st.session_state.current_session_id:
                                st.session_state.local_sessions[i]["conversation"] = st.session_state.conversations
                                break
                        # Simulate streaming response for better UX
                        for chunk in responses:
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
                            time.sleep(0.01)
                        message_placeholder.markdown(full_response)
                    else:
                        message_placeholder.error(f"Error from backend (Status code: {response.status_code})")
            except Exception as e:
                message_placeholder.error(f"Error: {str(e)}")

# Add UI styling
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        max-width: 100%;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #f7f7f7;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #f0f7fb;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Wingbot | Powered by FastAPI & MongoDB")
