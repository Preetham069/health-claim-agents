import pytest
from app.tools.pii_redactor import redact_pii
from app.agents.redaction import redaction_node
from app.state import ClaimState

def test_deterministic_pii_redaction():
    sample_text = (
        "Patient Name: Johnathan Doe\n"
        "Phone: 9876543210\n"
        "Govt ID: 1234 5678 9012\n"
        "Email: patient.test@example.com\n"
        "Diagnosis: Acute Appendicitis\n"
        "Hospital: City Care Hospital"
    )

    clean_text, scrubbed_types = redact_pii(sample_text)

    # Asserts that sensitive raw values are absent
    assert "Johnathan Doe" not in clean_text
    assert "9876543210" not in clean_text
    assert "1234 5678 9012" not in clean_text
    assert "patient.test@example.com" not in clean_text

    # Asserts that medical and administrative context is retained
    assert "Acute Appendicitis" in clean_text
    assert "City Care Hospital" in clean_text

    # Confirms logged types
    assert "PATIENT_NAME" in scrubbed_types
    assert "PHONE_NUMBER" in scrubbed_types
    assert "GOVERNMENT_ID" in scrubbed_types

def test_redaction_node_state_update():
    state: ClaimState = {
        "case_id": "CASE-101",
        "raw_documents": ["Patient Name: Jane Roe, Phone: 9123456780, Diagnosis: Cataract"],
        "extracted": {},
        "redacted_text": "",
        "missing_documents": [],
        "policy_clauses": [],
        "code_validation": {},
        "fraud_report": {},
        "decision": {},
        "human_review": {},
        "letter_draft": "",
        "audit_log": [],
        "iteration_count": 0,
    }

    result = redaction_node(state)

    assert "Jane Roe" not in result["redacted_text"]
    assert "9123456780" not in result["redacted_text"]
    assert "Cataract" in result["redacted_text"]
    assert len(result["audit_log"]) == 1
    assert result["audit_log"][0]["status"] == "success"