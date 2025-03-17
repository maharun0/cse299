import base64
import os
from PIL import Image
import streamlit as st
import requests
import json
import datetime
import time

# API Endpoint
API_BASE_URL = "http://127.0.0.1:8000"

# Function to convert image to base64
def image_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded_image}"

# Streamlit App Configurations
st.set_page_config(
    page_title="Wingbot",
    page_icon=image_to_base64("wingbot_avatar.png"),
    layout="wide",
)

time.sleep(3) # 10 sec

def get_available_llm_models():
    response = requests.get(f"{API_BASE_URL}/language_models")
    
    if response.status_code == 200:
        language_models = response.json().get("language_models", [])
        return language_models
    else:
        print(f"Error: {response.status_code}")
        return []

# Updated Available LLM Models
LLM_MODELS = get_available_llm_models()

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

# Function to get display name (either session_name or session_id)
def get_display_name(session):
    """Returns the session name if it exists, otherwise returns the session_id."""
    return session.get('session_name', session['session_id'])

# Show wingbot logo
text_logo_path = './images/wingbot_logo_text.png'
logo = Image.open(text_logo_path)
# Center the image
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image(logo, width=250)


# "New Chat" button to create a new session on demand
if st.sidebar.button("New Chat"):
    new_session_id = create_new_session()
    st.session_state.current_session_id = new_session_id
    st.session_state.conversations = []
    # Add to local sessions list if not already present
    if new_session_id not in [session.get("session_id") for session in st.session_state.local_sessions]:
        st.session_state.local_sessions.append({"session_id": new_session_id, "conversation": []})
    
    # Display success message and then hide it after 600ms
    success_message = st.sidebar.empty()
    success_message.success(f"Created new session: {new_session_id}")
    time.sleep(0.6)
    success_message.empty()

# Automatically create a new session if none exists
if st.session_state.current_session_id is None:
    new_session_id = create_new_session()
    st.session_state.current_session_id = new_session_id
    st.session_state.conversations = []
    if new_session_id not in [session.get("session_id") for session in st.session_state.local_sessions]:
        st.session_state.local_sessions.append({"session_id": new_session_id, "conversation": []})
    # Display success message and then hide it after 600ms
    success_message = st.sidebar.empty()
    success_message.success(f"Created new session: {new_session_id}")
    time.sleep(0.6)
    success_message.empty()

# Sidebar Model Selection
st.session_state.selected_model = st.sidebar.selectbox("Choose an LLM model", options=LLM_MODELS)

# File Upload Feature
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

# Fetch sessions
all_sessions = fetch_all_sessions()
backend_sessions = [session for session in all_sessions]

# Add local sessions
for local_session in st.session_state.local_sessions:
    backend_sessions.append(local_session)

# Sort sessions so the latest one appears at the top
sorted_sessions = sorted(backend_sessions, key=lambda x: x['session_id'], reverse=True)

# Display session list if any exist
if sorted_sessions:
    st.sidebar.subheader("Sessions")
    for idx, session in enumerate(sorted_sessions):
        session_display_name = get_display_name(session)
        
        with st.sidebar.container():
            col1, col2 = st.sidebar.columns([4, 1])
            with col1:
                if st.session_state.current_session_id == session['session_id']:
                    st.button(f"{session_display_name} (Current)", disabled=True)
                else:
                    if st.button(f"{session_display_name}", key=f"load_{session['session_id']}"):
                        st.session_state.current_session_id = session['session_id']
                        
                        try:
                            response = requests.get(f"{API_BASE_URL}/sessions/{session['session_id']}")
                            if response.status_code == 200:
                                st.session_state.conversations = response.json().get("conversation", [])
                                st.sidebar.success(f"Session Loaded")
                            else:
                                st.sidebar.error(f"Failed to load session data (Status code: {response.status_code})")
                        except Exception as e:
                            st.sidebar.error(f"Error fetching conversation history: {str(e)}")
            
            with col2:
                delete_button_key = f"delete_{session['session_id']}_{idx}"
                if st.button(f"🗑️", key=delete_button_key):
                    try:
                        response = requests.delete(f"{API_BASE_URL}/sessions/{session['session_id']}")
                        if response.status_code == 200:
                            success_message = st.sidebar.empty()
                            success_message.success(f"Deleted session: {session_display_name}")
                            time.sleep(0.6)
                            success_message.empty()

                            st.session_state.local_sessions = [
                                s for s in st.session_state.local_sessions if s["session_id"] != session['session_id']
                            ]
                            
                            new_session_id = create_new_session()
                            st.session_state.current_session_id = new_session_id
                            st.session_state.conversations = []
                            if new_session_id not in [session.get("session_id") for session in st.session_state.local_sessions]:
                                st.session_state.local_sessions.append({"session_id": new_session_id, "conversation": []})
                            
                            success_message = st.sidebar.empty()
                            success_message.success(f"Created new session: {new_session_id}")
                            time.sleep(0.6)
                            success_message.empty()
                        else:
                            st.sidebar.error(f"Failed to delete session (Status code: {response.status_code})")
                    except Exception as e:
                        st.sidebar.error(f"Error deleting session: {str(e)}")

# Display current session in the title and caption
current_session_display_name = get_display_name(
    next(session for session in sorted_sessions if session["session_id"] == st.session_state.current_session_id)
)

# Define paths or URLs for your avatar images
user_avatar = "./images/user_avatar.png"
assistant_avatar = "./images/wingbot_avatar.png"

# Display chat history with avatars
chat_container = st.container()
with chat_container:
    for conv in st.session_state.conversations:
        with st.chat_message("user", avatar=user_avatar):
            
            st.write(conv["user_input"])
        with st.chat_message("assistant", avatar=assistant_avatar):
            st.write(conv["response"])

# Chat input field and handling
if st.session_state.current_session_id:
    user_question = st.chat_input("Ask a question...")
    if user_question:
        with st.chat_message("user", avatar=user_avatar):
            st.write(user_question)
        with st.chat_message("assistant", avatar=assistant_avatar):
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
                        for i, session in enumerate(st.session_state.local_sessions):
                            if session["session_id"] == st.session_state.current_session_id:
                                st.session_state.local_sessions[i]["conversation"] = st.session_state.conversations
                                break
                        for chunk in responses:
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
                            time.sleep(0.01)
                        message_placeholder.markdown(full_response)
                    else:
                        message_placeholder.error(f"Error from backend (Status code: {response.status_code})")
            except Exception as e:
                message_placeholder.error(f"Error: {str(e)}")

# Add UI styling for hover effect (glowing container)
st.markdown("""
<style>
    .stButton:hover {
        background-color: #ff9800 !important;
        color: white !important;
        border: 1px solid #ff9800 !important;
    }
    .stContainer:hover {
        background-color: #f0f7fb;
        box-shadow: 0px 4px 20px rgba(255, 165, 0, 0.5);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)
