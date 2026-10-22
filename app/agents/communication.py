from datetime import datetime, timezone
from typing import Dict, Any
from app.state import ClaimState

def communication_node(state: ClaimState) -> Dict[str, Any]:
    decision = state.get("decision", {})
    human = state.get("human_review", {})
    case_id = state.get("case_id", "CASE-UNKNOWN")
    final_verdict = human.get("action") or decision.get("verdict", "Query")

    citations_str = "\n".join([f"- {c}" for c in decision.get("citations", [])])
    issues_str = "\n".join([f"- {i}" for i in decision.get("unresolved_issues", [])])

    if final_verdict == "Approve":
        letter = (
            f"PRE-AUTHORIZATION APPROVAL LETTER\n"
            f"Case Reference: {case_id}\n"
            f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
            f"Dear Healthcare Provider / Insured,\n\n"
            f"We are pleased to inform you that the pre-authorization request has been APPROVED.\n\n"
            f"Clinical Rationale:\n{decision.get('rationale')}\n\n"
            f"Applicable Policy Provisions:\n{citations_str}\n\n"
            f"Human Reviewer Sign-off: {human.get('reviewer', 'Adjudicator')}\n"
            f"Reviewer Notes: {human.get('comments', 'Verified standard protocol.')}\n"
        )
    elif final_verdict == "Query":
        letter = (
            f"PRE-AUTHORIZATION ADDITIONAL INFORMATION REQUEST (QUERY)\n"
            f"Case Reference: {case_id}\n"
            f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
            f"Dear Healthcare Provider / Insured,\n\n"
            f"Additional information or documentation is required before pre-authorization can proceed.\n\n"
            f"Pending Items / Queries:\n{issues_str}\n\n"
            f"Rationale:\n{decision.get('rationale')}\n\n"
            f"Please upload the required records within 24 hours to resume adjudication.\n"
        )
    else:  # Reject
        letter = (
            f"PRE-AUTHORIZATION ADVERSE DETERMINATION NOTICE (REJECTION)\n"
            f"Case Reference: {case_id}\n"
            f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
            f"Dear Healthcare Provider / Insured,\n\n"
            f"We regret to inform you that the pre-authorization request cannot be approved as submitted.\n\n"
            f"Grounds for Adverse Determination:\n{decision.get('rationale')}\n\n"
            f"Governing Policy Clauses:\n{citations_str}\n\n"
            f"Confirmed by Medical Reviewer: {human.get('reviewer', 'Medical Officer')}\n"
            f"Reviewer Comments: {human.get('comments', 'Criteria for coverage not met.')}\n"
        )

    audit_entry = {
        "node": "communication_agent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_used": "template-engine",
        "verdict_communicated": final_verdict
    }

    return {
        "letter_draft": letter,
        "audit_log": [audit_entry]
    }