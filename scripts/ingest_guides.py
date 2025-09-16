from backend.retrieval.ingest import ingest_folder
n = ingest_folder("data/guides")
print(f"Ingested {n} chunks.")
