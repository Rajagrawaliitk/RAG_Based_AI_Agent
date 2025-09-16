# import glob

# from backend.retrieval.vectordb import upsert_docs

# def ingest_folder(path="data/guides"):
#     docs = []
#     for f in glob.glob(f"{path}/*.txt"):
#         with open(f, "r", encoding="utf-8") as fh:
#             text = fh.read()
#         docs.append({"id": f, "text": text, "source": f})
#     upsert_docs(docs)
#     print(f"Ingested {len(docs)} docs into vector DB.")

import glob, os
from backend.retrieval.vectordb import upsert_guides

def simple_chunk(text, size=800, overlap=120):
    out=[]
    i=0
    while i < len(text):
        out.append(text[i:i+size])
        i += size - overlap
    return out

def ingest_folder(path="data/guides"):
    docs=[]
    for f in glob.glob(os.path.join(path, "*.txt")):
        with open(f, "r", encoding="utf-8") as fh:
            text = fh.read()
        for j, chunk in enumerate(simple_chunk(text)):
            docs.append({"id": f"{os.path.basename(f)}::{j}", "text": chunk, "source": os.path.basename(f)})
    upsert_guides(docs)
    return len(docs)
