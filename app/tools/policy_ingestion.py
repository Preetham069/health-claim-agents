import json
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.llm import LLMFactory

def init_policy_vector_db():
    client = chromadb.PersistentClient(
        path=str(settings.chroma_dir),
        settings=ChromaSettings(anonymized_telemetry=False)
    )
    collection = client.get_or_create_collection(name="fictional_policies")

    # Ingest if empty
    if collection.count() == 0:
        policy_file = settings.data_dir / "policies" / "fictional_policies.json"
        if policy_file.exists():
            with open(policy_file, "r", encoding="utf-8") as f:
                docs = json.load(f)

            embed_fn = LLMFactory.get_ollama_embeddings()
            texts = [d["clause"] for d in docs]
            embeddings = embed_fn.embed_documents(texts)
            ids = [f"{d['policy_id']}_{i}" for i, d in enumerate(docs)]
            metadatas = [
                {
                    "policy_id": d["policy_id"],
                    "policy_name": d["policy_name"],
                    "section": d["section"],
                    "page": d["page"]
                }
                for d in docs
            ]

            collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
    return collection

def query_policies(query_text: str, top_k: int = 2) -> List[Dict[str, Any]]:
    collection = init_policy_vector_db()
    embed_fn = LLMFactory.get_ollama_embeddings()
    query_emb = embed_fn.embed_query(query_text)

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )

    clauses = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
        for doc, meta in zip(docs, metas):
            clauses.append({
                "text": doc,
                "policy_id": meta.get("policy_id", "N/A"),
                "section": meta.get("section", "General"),
                "page": meta.get("page", 1)
            })
    return clauses