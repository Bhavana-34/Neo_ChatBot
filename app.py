import streamlit as st
import os
import sys
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models.llm import get_chatgroq_model, get_best_available_model
from models.embeddings import get_embedding_model
from config.config import SYSTEM_PROMPT_BASE, CONCISE_INSTRUCTION, DETAILED_INSTRUCTION, TAVILY_API_KEY
from utils.rag_utils import load_documents, split_documents, build_vector_store, retrieve_context
from utils.search_utils import web_search, should_search


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
    st.title("The Chatbot Blueprint")
    st.markdown("Welcome! Follow these instructions to set up and use the chatbot.")

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
    st.title("🤖 AI ChatBot")

 
    response_mode = st.sidebar.radio(
        "Response Mode",
        ["Concise", "Detailed"],
        index=1,
        help="Concise: short 2-4 sentence answers. Detailed: full in-depth responses."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📂 Upload Documents (RAG)")
    uploaded_files = st.sidebar.file_uploader(
        "Upload PDFs, TXT or DOCX files",
        type=["pdf", "txt", "md", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

 
    if uploaded_files:
        file_names = [f.name for f in uploaded_files]
        if file_names != st.session_state.get("uploaded_file_names"):
            with st.spinner("Processing documents..."):
                try:
                    embed_model = get_embedding_model()
                    if embed_model:
                        docs = load_documents(uploaded_files)
                        chunks = split_documents(docs)
                        st.session_state.vector_store = build_vector_store(chunks, embed_model)
                        st.session_state.uploaded_file_names = file_names
                        st.sidebar.success(f"✅ Indexed {len(chunks)} chunks")
                except Exception as e:
                    st.sidebar.error(f"Error processing documents: {e}")

 
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

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your message here..."):

        st.session_state.messages.append({"role": "user", "content": prompt})

       
        with st.chat_message("user"):
            st.markdown(prompt)

  
        doc_context = ""
        if st.session_state.get("vector_store"):
            doc_context = retrieve_context(st.session_state.vector_store, prompt)
            if doc_context:
                system_prompt += f"\n\n=== DOCUMENT CONTEXT ===\n{doc_context}\n=== END CONTEXT ==="

    
        if should_search(prompt, bool(doc_context)):
            with st.spinner("Searching the web..."):
                web_results = web_search(prompt)
                if web_results:
                    system_prompt += f"\n\n=== WEB SEARCH RESULTS ===\n{web_results}\n=== END WEB RESULTS ==="

      
        with st.chat_message("assistant"):
            with st.spinner("Getting response..."):
                response = get_chat_response(chat_model, st.session_state.messages, system_prompt)
                st.markdown(response)

           
            if doc_context:
                st.caption("📄 Answer based on uploaded documents")
            if TAVILY_API_KEY and should_search(prompt, bool(doc_context)):
                st.caption("🌐 Web search used")

       
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.info("🔧 No API keys found in environment variables. Please check the Instructions page to set up your API keys.")


def main():
    st.set_page_config(
        page_title="LangChain Multi-Provider ChatBot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Go to:",
            ["Chat", "Instructions"],
            index=0
        )

        if page == "Chat":
            st.divider()
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    
    if page == "Instructions":
        instructions_page()
    if page == "Chat":
        chat_page()


if __name__ == "__main__":
    main()
