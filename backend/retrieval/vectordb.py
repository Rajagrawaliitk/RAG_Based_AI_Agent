import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict

_client = chromadb.Client()

_guides = None
_products = None

def _embedder():
    # force CPU to avoid meta / CUDA issues
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )

# -------- Guides collection (unchanged behavior) --------
def get_guides_collection(name="guides"):
    global _guides
    if _guides is None:
        _guides = _client.get_or_create_collection(
            name=name,
            embedding_function=_embedder()
        )
    return _guides

def upsert_docs(docs: List[Dict]):
    col = get_guides_collection()
    col.add(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        metadatas=[{"source": d["source"]} for d in docs]
    )

def query_texts(q: str, k: int = 3):
    col = get_guides_collection()
    res = col.query(query_texts=[q], n_results=k)
    out = []
    for i in range(len(res["ids"][0])):
        out.append({
            "id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "source": res["metadatas"][0][i]["source"],
            "snippet": res["documents"][0][i][:240] + "..."
        })
    return out

# -------- Products collection (NEW) --------
def get_products_collection(name="products"):
    global _products
    if _products is None:
        _products = _client.get_or_create_collection(
            name=name,
            embedding_function=_embedder()
        )
    return _products

def upsert_products(items: List[Dict]):
    """
    items: raw provider dicts. We index title + description + category for semantic search.
    """
    col = get_products_collection()
    ids = []
    texts = []
    metas = []
    for it in items:
        pid = str(it.get("id"))
        title = it.get("title") or ""
        desc = it.get("description") or ""
        cat = it.get("category") or ""
        text = f"{title}\n\n{desc}\n\nCategory: {cat}"
        ids.append(pid)
        texts.append(text)
        metas.append({
            "source": "fakestore",
            "title": title,
            "price": it.get("price"),
            "rating": (it.get("rating") or {}).get("rate"),
            "reviews_count": (it.get("rating") or {}).get("count", 0),
            "image": it.get("image"),
            "link": f"https://fakestoreapi.com/products/{pid}",
            "category": cat,
        })
    # Add or update (Chroma will dedupe by id)
    col.upsert(ids=ids, documents=texts, metadatas=metas)


def query_products_semantic(q: str, k: int = 30, max_distance: float | None = 0.8):
    col = get_products_collection()
    res = col.query(query_texts=[(q or "").strip()], n_results=k)
    hits = []
    for i in range(len(res["ids"][0])):
        dist = res["distances"][0][i] if "distances" in res else None
        if max_distance is not None and dist is not None and dist > max_distance:
            continue  # drop weak matches
        hits.append({
            "id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "meta": res["metadatas"][0][i],
            "distance": dist,
        })
    hits = sorted(hits, key=lambda x: x["distance"])
    return hits
