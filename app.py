import streamlit as st
import os
import sys
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load API keys from Streamlit secrets or environment variables
if "GROQ_API_KEY" not in os.environ and "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
if "OPENAI_API_KEY" not in os.environ and "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
if "GOOGLE_API_KEY" not in os.environ and "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
if "TAVILY_API_KEY" not in os.environ and "TAVILY_API_KEY" in st.secrets:
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

from models.llm import get_chatgroq_model, get_best_available_model
from models.embeddings import get_embedding_model
from config.config import SYSTEM_PROMPT_BASE, CONCISE_INSTRUCTION, DETAILED_INSTRUCTION, TAVILY_API_KEY
from utils.rag_utils import load_documents, split_documents, build_vector_store, retrieve_context
from utils.search_utils import web_search, should_search


def apply_futuristic_theme():
    """Apply custom futuristic CSS theme"""
    futuristic_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Mono:wght@400;700&display=swap');
    
    * {
        font-family: 'Space Mono', monospace;
        color: #ffffff !important;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 50%, #0d0820 100%) !important;
        color: #ffffff !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1729 0%, #1a0d2e 100%);
        border-right: 2px solid #00d9ff;
        box-shadow: -10px 0px 40px rgba(0, 217, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Main content area */
    [data-testid="stMain"] {
        background: transparent;
        color: #ffffff !important;
    }
    
    [data-testid="stMain"] * {
        color: #ffffff !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00d9ff !important;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
        font-weight: 700;
    }
    
    h1 {
        font-size: 2.5em;
        margin-bottom: 0.5em;
        letter-spacing: 2px;
    }
    
    h2 {
        font-size: 1.8em;
        margin-top: 1.5em;
        letter-spacing: 1px;
    }
    
    h3 {
        color: #ff006e !important;
        font-size: 1.3em;
    }
    
    /* Paragraph and general text */
    p, span, div, label, li, a {
        color: #ffffff !important;
    }
    
    /* Input fields */
    input, textarea, [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
        background-color: rgba(15, 23, 41, 0.8) !important;
        border: 2px solid #00d9ff !important;
        color: #e0e6ff !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-family: 'Space Mono', monospace !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    input:focus, textarea:focus, [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
        border-color: #ff006e !important;
        box-shadow: 0 0 25px rgba(255, 0, 110, 0.4) !important;
    }
    
    /* Buttons */
    button, [data-testid="stButton"] button {
        background: linear-gradient(135deg, #00d9ff 0%, #0099cc 100%) !important;
        color: #0a0e27 !important;
        border: 2px solid #00d9ff !important;
        font-weight: 700 !important;
        font-family: 'Orbitron', sans-serif !important;
        padding: 10px 20px !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.3) !important;
        letter-spacing: 1px !important;
    }
    
    button:hover, [data-testid="stButton"] button:hover {
        background: linear-gradient(135deg, #00ff88 0%, #00d9ff 100%) !important;
        box-shadow: 0 0 25px rgba(0, 255, 136, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: rgba(26, 26, 62, 0.6) !important;
        border-left: 4px solid #00d9ff !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin: 12px 0 !important;
        backdrop-filter: blur(10px);
        box-shadow: inset 0 0 20px rgba(0, 217, 255, 0.05);
    }
    
    [data-testid="stChatMessage"][data-testid*="user"] {
        border-left-color: #ff006e !important;
        background: rgba(51, 10, 30, 0.5) !important;
    }
    
    [data-testid="stChatMessage"][data-testid*="assistant"] {
        border-left-color: #00d9ff !important;
    }
    
    /* Radio buttons and checkboxes */
    [role="radio"], [type="checkbox"] {
        accent-color: #00d9ff !important;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(0, 217, 255, 0.3) !important;
        border-width: 2px !important;
    }
    
    /* Success/Error messages */
    [data-testid="stAlert"] {
        border-radius: 8px !important;
        font-family: 'Space Mono', monospace !important;
    }
    
    .stAlert[kind="success"] {
        background-color: rgba(0, 255, 136, 0.15) !important;
        border: 2px solid #00ff88 !important;
    }
    
    .stAlert[kind="error"] {
        background-color: rgba(255, 0, 110, 0.15) !important;
        border: 2px solid #ff006e !important;
    }
    
    .stAlert[kind="info"] {
        background-color: rgba(0, 217, 255, 0.15) !important;
        border: 2px solid #00d9ff !important;
    }
    
    /* Spinner */
    [data-testid="stSpinner"] > div > div {
        border-top-color: #00d9ff !important;
        border-right-color: #ff006e !important;
    }
    
    /* Container styling */
    [data-testid="stVerticalBlock"] > [style*="flex-direction"] {
        gap: 1rem;
    }
    
    /* Code blocks */
    pre {
        background: rgba(10, 14, 39, 0.8) !important;
        border: 2px solid #00d9ff !important;
        border-radius: 8px !important;
        padding: 16px !important;
        color: #00ff88 !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.2) !important;
    }
    
    code {
        color: #00ff88 !important;
        background: rgba(0, 255, 136, 0.1) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    
    /* Markdown links */
    a {
        color: #00d9ff !important;
        text-decoration: none;
        transition: all 0.3s ease;
        border-bottom: 2px solid transparent;
    }
    
    a:hover {
        color: #ff006e !important;
        text-shadow: 0 0 10px rgba(255, 0, 110, 0.5);
        border-bottom: 2px solid #ff006e !important;
    }
    
    /* Tabs */
    [data-testid="stTabs"] {
        background: transparent !important;
    }
    
    button[data-baseweb="tab"] {
        color: #00d9ff !important;
        font-family: 'Space Mono', monospace !important;
    }
    
    /* Select boxes */
    [data-testid="stSelectbox"] {
        color: #e0e6ff !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #00d9ff !important;
    }
    
    /* Progress bar */
    [role="progressbar"] {
        background-color: #00d9ff !important;
    }
    </style>
    """
    st.markdown(futuristic_css, unsafe_allow_html=True)


def get_chat_response(chat_model, messages, system_prompt):
    """Get response from the chat model"""
    try:
    
        formatted_messages = [SystemMessage(content=system_prompt)]

        
        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            else:
                formatted_messages.append(AIMessage(content=msg["content"]))

       
        response = chat_model.invoke(formatted_messages)
        return response.content

    except Exception as e:
        return f"Error getting response: {str(e)}"


def instructions_page():
    """Instructions and setup page"""
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("# 🚀 NEURAL.NEXUS")
        st.markdown("### The Chatbot Blueprint")
    with col2:
        st.markdown("")
        st.markdown("")
        st.markdown("*v1.0 FUTURISTIC EDITION*")
    
    st.divider()
    st.markdown("#### 🌐 Welcome to the next generation of conversational AI")

    st.markdown("""
    ## 🔧 Installation
                

    First, install the required dependencies: (Add Additional Libraries base don your needs)
    
    ```bash
    pip install -r requirements.txt
    ```
    
    ## API Key Setup
    
    You'll need API keys from your chosen provider. Get them from:
    
    ### OpenAI
    - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
    - Create a new API key
    - Set the variables in config
    
    ### Groq
    - Visit [Groq Console](https://console.groq.com/keys)
    - Create a new API key
    - Set the variables in config
    
    ### Google Gemini
    - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
    - Create a new API key
    - Set the variables in config

    ### Tavily (Web Search)
    - Visit [Tavily](https://app.tavily.com)
    - Create a new API key
    - Set TAVILY_API_KEY in config
    
    ## 📝 Available Models
    
    ### OpenAI Models
    Check [OpenAI Models Documentation](https://platform.openai.com/docs/models) for the latest available models.
    Popular models include:
    - `gpt-4o` - Latest GPT-4 Omni model
    - `gpt-4o-mini` - Faster, cost-effective version
    - `gpt-3.5-turbo` - Fast and affordable
    
    ### Groq Models
    Check [Groq Models Documentation](https://console.groq.com/docs/models) for available models.
    Popular models include:
    - `llama-3.1-70b-versatile` - Large, powerful model
    - `llama-3.1-8b-instant` - Fast, smaller model
    - `mixtral-8x7b-32768` - Good balance of speed and capability
    
    ### Google Gemini Models
    Check [Gemini Models Documentation](https://ai.google.dev/gemini-api/docs/models/gemini) for available models.
    Popular models include:
    - `gemini-1.5-pro` - Most capable model
    - `gemini-1.5-flash` - Fast and efficient
    - `gemini-pro` - Standard model
    
    ## How to Use
    
    1. **Go to the Chat page** (use the navigation in the sidebar)
    2. **Upload documents** (optional) for RAG-based Q&A
    3. **Start chatting** once everything is configured!
    
    ## Tips
    
    - **System Prompts**: Customize the AI's personality and behavior
    - **Model Selection**: Different models have different capabilities and costs
    - **API Keys**: Can be entered in the app or set as environment variables
    - **Chat History**: Persists during your session but resets when you refresh
    - **Response Mode**: Switch between Concise and Detailed in the sidebar
    - **RAG**: Upload PDFs, TXT or DOCX files to chat with your documents
    - **Web Search**: Enabled automatically when TAVILY_API_KEY is set
    
    ## Troubleshooting
    
    - **API Key Issues**: Make sure your API key is valid and has sufficient credits
    - **Model Not Found**: Check the provider's documentation for correct model names
    - **Connection Errors**: Verify your internet connection and API service status
    
    ---
    
    Ready to start chatting? Navigate to the **Chat** page using the sidebar! 
    """)


def chat_page():
    """Main chat interface page"""
    # Header with futuristic title
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# ⚡ NEURAL.NEXUS")
    with col2:
        st.markdown("### *ACTIVE*")
    
    st.markdown("---")

    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ SYSTEM CONFIG")
        st.divider()
        
        response_mode = st.radio(
            "🎯 Response Mode",
            ["Concise", "Detailed"],
            index=1,
            help="Concise: short 2-4 sentence answers. Detailed: full in-depth responses."
        )
        
        st.divider()
        st.markdown("### 📚 KNOWLEDGE BASE")
        
        uploaded_files = st.file_uploader(
            "🔼 Upload Documents",
            type=["pdf", "txt", "md", "docx"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

 
        if uploaded_files:
            file_names = [f.name for f in uploaded_files]
            if file_names != st.session_state.get("uploaded_file_names"):
                with st.spinner("⏳ Indexing documents..."):
                    try:
                        embed_model = get_embedding_model()
                        if embed_model:
                            docs = load_documents(uploaded_files)
                            chunks = split_documents(docs)
                            st.session_state.vector_store = build_vector_store(chunks, embed_model)
                            st.session_state.uploaded_file_names = file_names
                            st.sidebar.success(f"✅ Indexed {len(chunks)} knowledge chunks")
                    except Exception as e:
                        st.sidebar.error(f"❌ Error: {e}")
        
        st.divider()
        st.markdown("### 🧹 ACTIONS")
        if st.button("🗑️ Clear Memory", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
 
    mode_instruction = CONCISE_INSTRUCTION if response_mode == "Concise" else DETAILED_INSTRUCTION
    system_prompt = SYSTEM_PROMPT_BASE + mode_instruction

    if "chat_model" not in st.session_state or st.session_state.chat_model is None:
        try:
            model, provider = get_best_available_model()
            st.session_state.chat_model = model
        except Exception:
            st.session_state.chat_model = None

    chat_model = st.session_state.get("chat_model")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "uploaded_file_names" not in st.session_state:
        st.session_state.uploaded_file_names = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not chat_model:
        st.error("❌ SYSTEM ERROR: No chat model available. Configure API keys in Streamlit secrets.")
        st.stop()

    if prompt := st.chat_input("🔮 Enter your query..."):

        st.session_state.messages.append({"role": "user", "content": prompt})

       
        with st.chat_message("user"):
            st.markdown(prompt)

  
        doc_context = ""
        if st.session_state.get("vector_store"):
            doc_context = retrieve_context(st.session_state.vector_store, prompt)
            if doc_context:
                system_prompt += f"\n\n=== DOCUMENT CONTEXT ===\n{doc_context}\n=== END CONTEXT ==="

    
        if should_search(prompt, bool(doc_context)):
            with st.spinner("🌐 Scanning the web..."):
                web_results = web_search(prompt)
                if web_results:
                    system_prompt += f"\n\n=== WEB SEARCH RESULTS ===\n{web_results}\n=== END WEB RESULTS ==="

      
        with st.chat_message("assistant"):
            with st.spinner("🧠 PROCESSING..."):
                response = get_chat_response(chat_model, st.session_state.messages, system_prompt)
                st.markdown(response)

           
            metadata_cols = st.columns(3)
            if doc_context:
                with metadata_cols[0]:
                    st.caption("📄 Knowledge base")
            if TAVILY_API_KEY and should_search(prompt, bool(doc_context)):
                with metadata_cols[1]:
                    st.caption("🌐 Web search")
            with metadata_cols[2]:
                st.caption(f"🤖 {response_mode} mode")

           
            st.session_state.messages.append({"role": "assistant", "content": response})


def main():
    st.set_page_config(
        page_title="NEURAL.NEXUS - AI Chatbot",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply futuristic theme
    apply_futuristic_theme()

    with st.sidebar:
        st.markdown("---")
        st.image("https://via.placeholder.com/250x100/0a0e27/00d9ff?text=NEURAL.NEXUS", use_column_width=True)
        st.markdown("---")
        st.title("🗺️ NAVIGATION")
        page = st.radio(
            "Select Module:",
            ["💬 Chat", "📖 Instructions"],
            index=0,
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.markdown("**BUILD INFO**")
        st.markdown("""
        - Version: 1.0 FUTURISTIC
        - Status: ONLINE ✓
        - Mode: PRODUCTION
        """)

    
    if page == "💬 Chat" or page == "Chat":
        chat_page()
    elif page == "📖 Instructions" or page == "Instructions":
        instructions_page()


if __name__ == "__main__":
    main()
