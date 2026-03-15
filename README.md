# NEURAL.NEXUS - AI Chatbot

A futuristic conversational AI platform with advanced RAG and web search capabilities.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Keys
Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_key"
OPENAI_API_KEY = "your_key"
GOOGLE_API_KEY = "your_key"
TAVILY_API_KEY = "your_key"
```

Or set environment variables:
```bash
set GROQ_API_KEY=your_key
set OPENAI_API_KEY=your_key
# etc...
```

### 3. Run the App
```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

## Features
- ⚡ Multiple AI models (OpenAI, Groq, Google Gemini)
- 📚 RAG with document upload (PDF, TXT, DOCX, MD)
- 🌐 Auto web search integration
- 🎨 Futuristic neon UI
- 💬 Chat history & response modes

## Supported Models
- **Groq**: llama-3.1-70b, llama-3.1-8b, mixtral-8x7b
- **OpenAI**: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- **Google**: gemini-1.5-pro, gemini-1.5-flash

---
**Need help?** Check the Instructions page in the app!
