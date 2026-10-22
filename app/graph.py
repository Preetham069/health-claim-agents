import sqlite3
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from app.state import ClaimState
from app.config import settings
from app.agents.extraction import extraction_node
from app.agents.redaction import redaction_node
from app.agents.policy_rag import policy_rag_node
from app.agents.code_validation import code_validation_node
from app.fraud.nodes import fraud_detection_step
from app.agents.decision import decision_node
from app.agents.communication import communication_node
from app.agents.supervisor import supervisor_router

def fraud_node_adapter(state: ClaimState) -> Dict[str, Any]:
    """Wraps fraud detection into the top-level state shape."""
    res = fraud_detection_step(state)
    audit_entry = {
        "node": "fraud_anomaly_agent",
        "timestamp": "now",
        "model_used": "rules-benchmark-engine",
        "risk_score": res["fraud_report"]["risk_score"]
    }
    return {
        "fraud_report": res["fraud_report"],
        "audit_log": [audit_entry]
    }

def human_review_node(state: ClaimState) -> Dict[str, Any]:
    """
    Pauses graph execution before final commitment.
    Resumes when human input is supplied.
    """
    human_payload = interrupt({
        "case_id": state.get("case_id"),
        "preliminary_decision": state.get("decision"),
        "unresolved_issues": state.get("decision", {}).get("unresolved_issues", []),
        "fraud_report": state.get("fraud_report")
    })

    reviewer_record = {
        "reviewer": human_payload.get("reviewer", "Demo Reviewer"),
        "action": human_payload.get("action", state.get("decision", {}).get("verdict", "Approve")),
        "comments": human_payload.get("comments", "Review completed.")
    }

    audit_entry = {
        "node": "human_review_node",
        "timestamp": "now",
        "model_used": "human-adjudicator",
        "action_taken": reviewer_record["action"],
        "reviewer": reviewer_record["reviewer"]
    }

    return {
        "human_review": reviewer_record,
        "audit_log": [audit_entry]
    }

def build_claim_graph(checkpointer=None):
    builder = StateGraph(ClaimState)

    # 1. Add all functional nodes
    builder.add_node("extraction", extraction_node)
    builder.add_node("redaction", redaction_node)
    builder.add_node("policy_rag", policy_rag_node)
    builder.add_node("code_validation", code_validation_node)
    builder.add_node("fraud_analysis", fraud_node_adapter)
    builder.add_node("decision", decision_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("communication", communication_node)

    # 2. Sequential start: Ingest -> Extract -> Redact
    builder.add_edge(START, "extraction")
    builder.add_edge("extraction", "redaction")

    # 3. Supervisor dynamic routing
    builder.add_conditional_edges(
        "redaction",
        supervisor_router,
        {
            "query_fast_track": "decision",
            "parallel_validation": "policy_rag"
        }
    )

    # 4. Validation fan-out & join into decision
    builder.add_edge("policy_rag", "code_validation")
    builder.add_edge("code_validation", "fraud_analysis")
    builder.add_edge("fraud_analysis", "decision")

    # 5. Decision -> Human review pause -> Letter -> END
    builder.add_edge("decision", "human_review")
    builder.add_edge("human_review", "communication")
    builder.add_edge("communication", END)

    if checkpointer is None:
        checkpointer = MemorySaver()

    return builder.compile(checkpointer=checkpointer)