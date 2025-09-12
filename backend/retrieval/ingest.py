import glob

from backend.retrieval.vectordb import upsert_docs

def ingest_folder(path="data/guides"):
    docs = []
    for f in glob.glob(f"{path}/*.txt"):
        with open(f, "r", encoding="utf-8") as fh:
            text = fh.read()
        docs.append({"id": f, "text": text, "source": f})
    upsert_docs(docs)
    print(f"Ingested {len(docs)} docs into vector DB.")
