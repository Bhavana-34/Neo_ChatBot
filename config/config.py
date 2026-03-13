import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")


TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")


GROQ_MODEL = "llama-3.3-70b-versatile"
OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini-1.5-flash"


CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K_RESULTS = 4
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

SYSTEM_PROMPT_BASE = """You are a helpful AI assistant. 
If document context is provided below, use it to answer the user's question and cite the source.
If web search results are provided, use them to supplement your answer.
Always be accurate and transparent about where your information comes from."""

CONCISE_INSTRUCTION = "\nRespond concisely in 2-4 sentences. Focus only on the core answer."

DETAILED_INSTRUCTION = "\nRespond in detail with full explanation, context, and examples where relevant."
