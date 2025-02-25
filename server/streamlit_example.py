import streamlit as st
from datetime import datetime
import BotUtils  # Importing your LangChain model utilities

# Streamlit UI Config
st.set_page_config(page_title="WingBot Chat", page_icon="🤖", layout="wide")

# Initialize LangChain RAG Chain
rag_chain = BotUtils.getRAGChain(
    vector_db="physics_db",
    llm_model="llama3.1:8b",
    embed_model="nomic-embed-text"
)

# Dark mode styling
st.markdown("""
    <style>
        body {
            background-color: #121212;
            color: white;
        }
        .stTextInput, .stButton {
            border-radius: 10px;
        }
        .chat-message {
            background-color: #262626;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .chat-history {
            background-color: #1a1a1a;
            padding: 10px;
            border-radius: 10px;
        }
        .chat-session {
            padding: 5px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-session:hover {
            background-color: #333;
        }
        .sidebar-container {
            transition: width 0.3s ease-in-out;
        }
    </style>
""", unsafe_allow_html=True)

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "history" not in st.session_state:
    st.session_state["history"] = []
if "sessions" not in st.session_state:
    st.session_state["sessions"] = {}
if "current_session" not in st.session_state:
    st.session_state["current_session"] = str(datetime.now())
if "sidebar_collapsed" not in st.session_state:
    st.session_state["sidebar_collapsed"] = False

# Layout configuration based on sidebar state
if st.session_state["sidebar_collapsed"]:
    layout_config = [0.05, 2, 1]  # Collapsed sidebar
else:
    layout_config = [1, 2, 1]  # Normal sidebar

left_col, chat_col, right_col = st.columns(layout_config)

# Left Panel: Chat History (Collapsible with Smooth Animation)
with left_col:
    st.markdown("<div class='sidebar-container'>", unsafe_allow_html=True)
    if not st.session_state["sidebar_collapsed"]:
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("⬅", key="toggle_sidebar"):
                st.session_state["sidebar_collapsed"] = True
                st.rerun()
        with col2:
            if st.button("➕ New Chat", key="new_chat"):
                st.session_state["current_session"] = str(datetime.now())
                st.session_state["messages"] = []
                st.rerun()
        
        st.divider()
        
        st.subheader("Today")
        for session in st.session_state["sessions"]:
            st.button(session, key=session)
        
        st.subheader("Yesterday")
        for session in st.session_state["sessions"]:
            st.button(session, key=f"y_{session}")
        
        st.subheader("Previously")
        for session in st.session_state["sessions"]:
            st.button(session, key=f"p_{session}")
        
        st.divider()
        st.button("📌 Bookmarks")
        st.button("❤️ Favourites")
    else:
        if st.button("➡", key="toggle_sidebar_open"):
            st.session_state["sidebar_collapsed"] = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Middle Panel: Chat Interface
with chat_col:
    st.title("🦾 WingBot AI Chat")
    st.markdown("<div style='margin-top: -30px;'></div>", unsafe_allow_html=True)  # Reduce spacing
    
    # Display chat messages directly
    for msg in st.session_state["messages"]:
        with st.chat_message("assistant" if msg["role"] == "bot" else "user"):
            st.write(msg["content"])
    
# Input box fixed at the bottom of the screen inside the middle column
user_input = st.chat_input("Ask me anything...")
    
if user_input:
    # Show user input immediately
    with chat_col:
        with st.chat_message("user"):
            st.write(user_input)
    
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.session_state["sessions"][st.session_state["current_session"]] = st.session_state["messages"]
    
    # Call LangChain RAG Chain for AI response
    response = rag_chain.invoke(input=user_input)
    bot_response = response  # Assume response is a string
    
    st.session_state["messages"].append({"role": "bot", "content": bot_response})
    st.session_state["sessions"][st.session_state["current_session"]] = st.session_state["messages"]
    st.rerun()

# Right Panel: Settings, Options, and Notes
with right_col:
    st.subheader("Settings")
    ollama_models = ["deepseek-r1:8b", "deepseek-r1:1.5b", "gemma:2b", "qwen:0.5b", "bakllava:latest", "codellama:7b-code", "gemma:7b", "llama2-uncensored:latest", "llama3.1:8b"]
    llm_model = st.selectbox("Select LLM", ollama_models, index=0)
    embedding_model = st.selectbox("Select Embedding Model", ["kisu akta", "sentence-transformers", "openai"], index=0)
    
    st.subheader("Options")
    st.selectbox("Select Theme", ["Dark Mode", "Light Mode"], index=0)
    st.selectbox("Font Size", ["Small", "Medium", "Large"], index=1)
    st.markdown("---")
    st.write("📌 Notes & Insights")
    st.text_area("Add your notes here...")
