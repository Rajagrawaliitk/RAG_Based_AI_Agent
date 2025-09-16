# backend/llm/models.py
import os
from dotenv import load_dotenv

from langchain_core.language_models import BaseLanguageModel

# Load environment variables
load_dotenv()

# Which backend to use: "gemini" or "ollama"
PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# Defaults
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")  # e.g., llama3, mistral
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Embeddings
OLLAMA_EMB_MODEL = os.getenv("OLLAMA_EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
GEMINI_EMB_MODEL = os.getenv("GEMINI_EMB_MODEL", "models/embedding-001")


def get_llm() -> BaseLanguageModel:
    if PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.2,
        )
    else:  # ollama
        from langchain_community.llms import Ollama
        return Ollama(model=OLLAMA_MODEL, base_url="http://localhost:11434")


def get_embeddings():
    if PROVIDER == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model=GEMINI_EMB_MODEL,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    else:  # ollama
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=OLLAMA_EMB_MODEL)
