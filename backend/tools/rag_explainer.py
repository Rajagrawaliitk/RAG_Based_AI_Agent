# Retrieves relevant guide chunks and generates cited rationale for each product.
from backend.retrieval.vectordb import query_texts

def explain_products(topk, prefs):
    # For a free MVP, return a short placeholder rationale from guides.
    # Replace with LC chain calling your local LLM via Ollama.
    explanations = {}
    for p in topk:
        q = f"Key buying factors for {prefs.get('category','product')} under {prefs.get('budget_max','NA')}"
        hits = query_texts(q, k=2)
        cite = "\n".join([f"- [{h['source']}] {h['snippet']}" for h in hits])
        explanations[p.id] = f"Matches your constraints; see:\n{cite}"
    return explanations
