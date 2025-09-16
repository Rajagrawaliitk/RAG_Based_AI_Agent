# backend/retrieval/vectordb.py
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict

_client = chromadb.Client()
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"  # avoid meta/cuda issues; switch if you have a working GPU
)

_guides = None
_products = None

def guides_col():
    global _guides
    if _guides is None:
        _guides = _client.get_or_create_collection("guides", embedding_function=_ef)
    return _guides

def products_col():
    global _products
    if _products is None:
        _products = _client.get_or_create_collection("products", embedding_function=_ef)
    return _products

def upsert_guides(docs: List[Dict]):
    # docs: [{"id": "...", "text": "...", "source": "filename"}]
    c = guides_col()
    c.upsert(ids=[d["id"] for d in docs],
             documents=[d["text"] for d in docs],
             metadatas=[{"source": d["source"]} for d in docs])

def query_guides(q: str, k: int = 4):
    c = guides_col()
    res = c.query(query_texts=[q], n_results=k)
    out=[]
    for i in range(len(res["ids"][0])):
        out.append({
            "id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "source": res["metadatas"][0][i]["source"]
        })
    return out

def upsert_products(items: List[Dict]):
    # optional: index product text for semantic matching (“smartphones 8GB RAM 5G”)
    c = products_col()
    ids = [str(it["asin"]) for it in items if it.get("asin")]
    texts = [f'{it.get("title","")} {it.get("features","")}' for it in items if it.get("asin")]
    metas = [{"asin": it.get("asin"), "title": it.get("title")} for it in items if it.get("asin")]
    if ids:
        c.upsert(ids=ids, documents=texts, metadatas=metas)

def query_products_semantic(q: str, k: int = 12):
    c = products_col()
    res = c.query(query_texts=[q], n_results=k)
    hits=[]
    for i in range(len(res["ids"][0])):
        hits.append({
            "id": res["ids"][0][i],
            "title": res["metadatas"][0][i]["title"],
            "score": res["distances"][0][i] if "distances" in res else None,
            "meta": res["metadatas"][0][i]
        })
    return hits
