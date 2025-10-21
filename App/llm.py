import sys
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE

try:
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=LLM_MODEL,
        temperature=LLM_TEMPERATURE
    )
    print(f"LLM Initialized ({LLM_MODEL}).")
    sys.stdout.flush()
except Exception as e:
    print(f"Error initializing LLM: {e}")
    sys.stdout.flush()
    exit()