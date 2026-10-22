from datetime import datetime, timezone
from typing import Dict, Any
from app.state import ClaimState
from app.tools.policy_ingestion import query_policies

def policy_rag_node(state: ClaimState) -> Dict[str, Any]:
    extracted = state.get("extracted", {})
    query = f"{extracted.get('diagnosis_description', '')} {extracted.get('procedure_description', '')}"
    if not query.strip():
        query = "Coverage and standard surgical benefits"

    clauses = query_policies(query_text=query, top_k=2)

    audit_entry = {
        "node": "policy_rag_agent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_used": "ollama-nomic-embed-text",
        "retrieved_clauses_count": len(clauses)
    }

    return {
        "policy_clauses": clauses,
        "audit_log": [audit_entry]
    }