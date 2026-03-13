import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import (
    GROQ_API_KEY,
    OPENAI_API_KEY, 
    GOOGLE_API_KEY,
    GROQ_MODEL,
    OPENAI_MODEL,
    GEMINI_MODEL
)


def get_chatgroq_model():
    """Initialize and return the Groq chat model"""
    try:
        from langchain_groq import ChatGroq
        groq_model = ChatGroq(
            api_key=GROQ_API_KEY,
            model=GROQ_MODEL,
        )
        return groq_model
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Groq model: {str(e)}")


def get_openai_model():
    """Initialize and return the OpenAI chat model"""
    try:
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
        return model
    except Exception as e:
        raise RuntimeError(f"Failed to initialize OpenAI model: {str(e)}")


def get_gemini_model():
    """Initialize and return the Google Gemini chat model"""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        model = ChatGoogleGenerativeAI(google_api_key=GOOGLE_API_KEY, model=GEMINI_MODEL)
        return model
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Gemini model: {str(e)}")


def get_best_available_model():
    """Return the first available model based on configured API keys"""
    if GROQ_API_KEY:
        return get_chatgroq_model(), "Groq"
    if OPENAI_API_KEY:
        return get_openai_model(), "OpenAI"
    if GOOGLE_API_KEY:
        return get_gemini_model(), "Gemini"
    return None, None
