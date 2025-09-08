import chromadb
from chromadb.utils import embedding_functions

_client = chromadb.Client()
_collection = None

def get_collection(name="guides"):
    global _collection
    if _collection is None:
        _collection = _client.get_or_create_collection(name=name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                device="cpu"
            )
        )
    return _collection

def upsert_docs(docs):
    col = get_collection()
    col.add(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        metadatas=[{"source": d["source"]} for d in docs]
    )

def query_texts(q, k=3):
    col = get_collection()
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
