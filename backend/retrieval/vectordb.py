import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
# k=9
_client = chromadb.Client()

_guides = None
_products = None

def _embedder():
    # force CPU to avoid meta / CUDA issues
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )

# -------- Guides collection --------
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

def query_texts(q: str, k: int = 9):
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

# -------- Products collection (Amazon) --------
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
    items: raw Amazon scraper dicts
    """
    col = get_products_collection()
    ids, texts, metas = [], [], []

    for it in items:
        pid = str(it.get("asin") or it.get("id"))

        title = it.get("title") or ""
        desc = it.get("description") or ""

        # rating
        rat, reviews = None, 0
        raw_rating = it.get("rating")
        if isinstance(raw_rating, dict):
            rat = raw_rating.get("stars")
            reviews = raw_rating.get("count")
        elif raw_rating:
            rat = raw_rating

        # price
        price = None
        raw_price = it.get("price")
        if isinstance(raw_price, dict):
            price = raw_price.get("current")
        else:
            price = raw_price

        # text blob for semantic search
        text = f"{title}\n\n{desc}\n\nRating: {rat}\n\nPrice: {price}"

        ids.append(pid)
        texts.append(text)
        metas.append({
            "asin": pid,
            "source": "amazon",
            "title": title,
            "price": price,
            "rating": rat,
            "reviews_count": reviews,
            "image": it.get("image_url"),
            "link": it.get("product_url") or f"https://www.amazon.in/dp/{pid}",
            "discount": (raw_price or {}).get("discount") if isinstance(raw_price, dict) else None,
            "original_price": (raw_price or {}).get("original") if isinstance(raw_price, dict) else None,
            "prime": it.get("prime_eligible", False),
        })

    col.upsert(ids=ids, documents=texts, metadatas=metas)

def query_products_semantic(q: str, k: int = 9, max_distance: float | None = 0.8):
    """
    Return semantic matches with rich metadata.
    Each hit contains:
      - id
      - distance (semantic similarity)
      - text (search blob)
      - meta (metadata dict with price, rating, etc.)
    """
    col = get_products_collection()
    res = col.query(query_texts=[(q or "").strip()], n_results=k)

    hits = []
    for i in range(len(res["ids"][0])):
        dist = res["distances"][0][i] if "distances" in res else None
        if max_distance is not None and dist is not None and dist > max_distance:
            continue

        meta: Dict[str, Any] = res["metadatas"][0][i]
        hits.append({
            "id": res["ids"][0][i],
            "distance": dist,
            "text": res["documents"][0][i],
            "meta": meta,  # full Amazon product info
            "price": meta.get("price"),
            "rating": meta.get("rating"),
            "reviews_count": meta.get("reviews_count"),
            "image": meta.get("image"),
            "link": meta.get("link"),
            "discount": meta.get("discount"),
            "original_price": meta.get("original_price"),
            "prime": meta.get("prime"),
        })

    hits = sorted(hits, key=lambda x: x["distance"] if x["distance"] is not None else 1.0)
    return hits
