#!/usr/bin/env python
import sys
import traceback

print("Python version:", sys.version)
print("=" * 60)

try:
    print("Attempting to import langchain_groq...")
    from langchain_groq import ChatGroq
    print("✓ langchain_groq imported successfully")
except Exception as e:
    print(f"✗ Error importing langchain_groq: {e}")
    traceback.print_exc()

print("=" * 60)
try:
    print("Attempting to import all LLM functions...")
    from models.llm import get_chatgroq_model, get_openai_model, get_gemini_model, get_best_available_model
    print("✓ All LLM functions imported successfully")
    print("Functions available:", [get_chatgroq_model, get_openai_model, get_gemini_model, get_best_available_model])
except Exception as e:
    print(f"✗ Error importing LLM functions: {e}")
    traceback.print_exc()
