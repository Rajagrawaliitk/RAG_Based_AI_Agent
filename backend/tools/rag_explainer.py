# backend/tools/rag_explainer.py
from typing import List, Dict
from backend.retrieval.vectordb import query_guides
from backend.llm.models import get_llm
from backend.llm.prompts import EXPLAIN_SYSTEM, EXPLAIN_USER
from backend.schemas import Product

_llm = get_llm()

def _fmt_snippets(snips):
    # S1, S2...
    lines=[]
    for i, s in enumerate(snips, start=1):
        sid=f"S{i}"
        lines.append(f"[{sid}] ({s['source']}) {s['text'][:280]}...")
    return "\n".join(lines)

def explain_products(topk: List[Product], prefs: Dict) -> Dict[str, str]:
    explanations = {}
    for p in topk:
        q = f"Key factors for {prefs.get('free_query') or prefs.get('category','product')} similar to '{p.title}'"
        snips = query_guides(q, k=3)
        user = EXPLAIN_USER.format(
            category=prefs.get("free_query") or prefs.get("category",""),
            constraints=f"budget<={prefs.get('budget_max')} rating>={prefs.get('rating_min')}",
            title=p.title,
            price=p.price, currency=p.currency,
            rating=p.rating, reviews=p.reviews_count,
            snippets=_fmt_snippets(snips)
        )

        resp = _llm.invoke(f"{EXPLAIN_SYSTEM}\n\n{user}")

        # 🔹 Normalize output regardless of provider
        if hasattr(resp, "content"):              # Gemini returns AIMessage
            explanations[p.id] = resp.content
        elif isinstance(resp, dict):              # Just in case JSON/dict
            explanations[p.id] = resp.get("content", str(resp))
        else:                                     # Ollama usually returns str
            explanations[p.id] = str(resp).strip()

    return explanations

