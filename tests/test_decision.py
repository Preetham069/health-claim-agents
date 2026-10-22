import pytest
from app.agents.decision import evaluate_deterministic_verdict
from app.agents.communication import communication_node
from app.state import ClaimState

def test_missing_document_verdict():
    state: ClaimState = {
        "case_id": "CASE-002",
        "raw_documents": [],
        "extracted": {},
        "redacted_text": "",
        "missing_documents": ["cost_estimate"],
        "policy_clauses": [{"policy_id": "CARE-SHIELD-2026", "section": "Sub-limits", "page": 4}],
        "code_validation": {"valid": True},
        "fraud_report": {"risk_score": 0, "flags": []},
        "decision": {},
        "human_review": {},
        "letter_draft": "",
        "audit_log": [],
        "iteration_count": 0
    }
    verdict = evaluate_deterministic_verdict(state)
    assert verdict.verdict == "Query"
    assert "cost_estimate" in verdict.unresolved_issues

def test_code_mismatch_rejection():
    state: ClaimState = {
        "case_id": "CASE-003",
        "raw_documents": [],
        "extracted": {},
        "redacted_text": "",
        "missing_documents": [],
        "policy_clauses": [],
        "code_validation": {"valid": False, "reason": "Clinical mismatch"},
        "fraud_report": {"risk_score": 0, "flags": []},
        "decision": {},
        "human_review": {},
        "letter_draft": "",
        "audit_log": [],
        "iteration_count": 0
    }
    verdict = evaluate_deterministic_verdict(state)
    assert verdict.verdict == "Reject"
    assert "Clinical mismatch" in verdict.rationale

def test_communication_drafting():
    state: ClaimState = {
        "case_id": "CASE-001",
        "raw_documents": [],
        "extracted": {},
        "redacted_text": "",
        "missing_documents": [],
        "policy_clauses": [{"policy_id": "CARE-SHIELD-2026", "section": "Coverage", "page": 3}],
        "code_validation": {"valid": True},
        "fraud_report": {"risk_score": 10, "flags": []},
        "decision": {"verdict": "Approve", "rationale": "Eligible procedure", "citations": ["CARE-SHIELD-2026: Coverage"]},
        "human_review": {"action": "Approve", "reviewer": "Dr. Kumar", "comments": "Approved"},
        "letter_draft": "",
        "audit_log": [],
        "iteration_count": 0
    }
    res = communication_node(state)
    assert "PRE-AUTHORIZATION APPROVAL LETTER" in res["letter_draft"]
    assert "Dr. Kumar" in res["letter_draft"]