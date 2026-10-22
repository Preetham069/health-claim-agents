from datetime import datetime, timezone
from typing import Dict, Any
from app.state import ClaimState
from app.tools.pii_redactor import redact_pii

def redaction_node(state: ClaimState) -> Dict[str, Any]:
    """
    LangGraph node: Purges PII from text before cloud synthesis.
    """
    raw_texts = state.get("raw_documents", [])
    combined_raw = "\n".join(raw_texts) if isinstance(raw_texts, list) else str(raw_texts)

    redacted_text, redacted_types = redact_pii(combined_raw)

    audit_entry = {
        "node": "redaction_agent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_used": "deterministic-regex",
        "redacted_categories": redacted_types,
        "status": "success",
    }

    return {
        "redacted_text": redacted_text,
        "audit_log": [audit_entry],
    }