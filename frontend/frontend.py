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