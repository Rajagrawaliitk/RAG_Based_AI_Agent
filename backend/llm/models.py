import os
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_llm():
    # If Ollama is running locally
    try:
        return Ollama(model="llama3")   # or mistral, gemma
    except Exception:
        # Fallback stub (echo-like behavior)
        class DummyLLM:
            def invoke(self, text): return f"[LLM disabled] {text}"
        return DummyLLM()

def get_embeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    return HuggingFaceEmbeddings(model_name=model_name)
