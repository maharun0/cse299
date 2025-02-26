import streamlit as st
import PyPDF2
from datetime import datetime, timedelta

# Set page configuration FIRST
st.set_page_config(page_title="OmniBot", layout="wide")

# Initialize session state for theme selection
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Sidebar - Theme Toggle
st.sidebar.header("☾☀︎ Theme")
theme_choice = st.sidebar.radio("Select Theme:", ["Dark", "Light"], index=0 if st.session_state.theme == "dark" else 1)

# Update theme in session state
if theme_choice.lower() != st.session_state.theme:
    st.session_state.theme = theme_choice.lower()

# Apply CSS for themes
if st.session_state.theme == "dark":
    theme_css = """
    <style>
        body {
            background-color: #0d1117;
            color: white;
        }
        .sidebar .sidebar-content {
            background-color: #161b22 !important;
        }
        .sidebar-option {
            padding: 10px;
            font-size: 18px;
            border-radius: 5px;
            color: white;
            text-align: left;
            margin-bottom: 10px;
            cursor: pointer;
        }
        .sidebar-option:hover {
            background-color: #238636;
        }
        .search-history {
            font-size: 16px;
            color: #b1bac4;
            margin-top: 10px;
            padding-left: 10px;
        }
        .search-query {
            color: white;
            margin-left: 15px;
        }
    </style>
    """
else:
    theme_css = """
    <style>
        body {
            background-color: #ffffff;
            color: black;
        }
        .sidebar .sidebar-content {
            background-color: #f0f0f0 !important;
        }
        .sidebar-option {
            padding: 10px;
            font-size: 18px;
            border-radius: 5px;
            color: black;
            text-align: left;
            margin-bottom: 10px;
            cursor: pointer;
        }
        .sidebar-option:hover {
            background-color: #d0d0d0;
        }
        .search-history {
            font-size: 16px;
            color: #555;
            margin-top: 10px;
            padding-left: 10px;
        }
        .search-query {
            color: black;
            margin-left: 15px;
        }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

# Initialize session state for search history
if "search_history" not in st.session_state:
    st.session_state.search_history = {
        "Today": [],
        "Yesterday": [],
        "Previously": []
    }

# Sidebar - Navigation Menu
st.sidebar.title("➤ Navigation")
if st.sidebar.button("🏷 Bookmarks"):
    st.sidebar.info("Your saved bookmarks will appear here.")
if st.sidebar.button("☆ Favourites"):
    st.sidebar.info("Your favorite documents will appear here.")
if st.sidebar.button("⚙ Settings"):
    st.sidebar.info("Settings will be available here.")

# Sidebar - Search History
st.sidebar.header("𓂃🖊 Search History")

# Display categorized history
for category, queries in st.session_state.search_history.items():
    if queries:
        st.sidebar.markdown(f"**{category}**")
        for query in queries[-5:]:  # Show last 5 searches per category
            st.sidebar.markdown(f'<div class="search-query">🔹 {query}</div>', unsafe_allow_html=True)

# Sidebar - PDF Upload
st.sidebar.header("🗁 Upload PDFs")
uploaded_files = st.sidebar.file_uploader("Upload one or multiple PDFs", type=["pdf"], accept_multiple_files=True)

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text + "\n"
    return text

# Store extracted documents
documents = {}
if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            documents[uploaded_file.name] = extract_text_from_pdf(uploaded_file)
    st.sidebar.success("🗁 PDFs uploaded successfully!")

# Main Chat Interface
st.title("OmniBot")
st.subheader("💬 AI Chat Search")
search_query = st.text_input("Ask anything from the uploaded PDFs:")

# Handle search queries and update history
if search_query:
    # Add query to the history with category
    now = datetime.now()
    if now.date() == datetime.today().date():
        category = "Today"
    elif now.date() == (datetime.today() - timedelta(days=1)).date():
        category = "Yesterday"
    else:
        category = "Previously"

    st.session_state.search_history[category].append(search_query)

    # Display search results
    st.write("### ⌕ Search Results")
    found = False
    for filename, text in documents.items():
        if search_query.lower() in text.lower():
            found = True
            st.markdown(f"**🗒 Found in:** `{filename}`")
            st.text_area("Excerpt:", text[:500] + "...", height=150)
    if not found:
        st.warning("✖ No matching results found.")
else:
    st.info("⎙ Upload PDFs and enter a search query to find information.")