import pytest
from pathlib import Path
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from app.graph import build_claim_graph
from app.state import ClaimState

@pytest.fixture
def test_graph():
    checkpointer = MemorySaver()
    return build_claim_graph(checkpointer=checkpointer)

def test_missing_doc_workflow_interrupt_and_resume(test_graph, tmp_path):
    # Create synthetic single document file
    doc_file = tmp_path / "patient_pre_auth_form.txt"
    doc_file.write_text(
        "Hospital: Vision Eye Clinic\n"
        "Policy Number: CARE-SHIELD-2026\n"
        "Age: 58\n"
        "Diagnosis Code: H25.9\n"
        "Procedure Code: 13.41\n"
        "Estimated Cost: 30,000"
    )

    initial_state = {
        "case_id": "CASE-TEST-001",
        "raw_documents": [str(doc_file)],
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
        "iteration_count": 0
    }

    config = {"configurable": {"thread_id": "thread-case-001"}}

    # Run until human_review interrupt
    events = list(test_graph.stream(initial_state, config))
    assert len(events) > 0

    state = test_graph.get_state(config)
    assert len(state.next) > 0
    assert state.next[0] == "human_review"

    # Human sign-off action
    resume_payload = {
        "reviewer": "Dr. Sarah",
        "action": "Query",
        "comments": "Requesting cost breakdown and admission slip."
    }

    # Resume graph execution
    final_events = list(test_graph.stream(Command(resume=resume_payload), config))
    final_state = test_graph.get_state(config)

    assert final_state.next == ()
    assert "PRE-AUTHORIZATION ADDITIONAL INFORMATION REQUEST" in final_state.values["letter_draft"]
    assert final_state.values["human_review"]["reviewer"] == "Dr. Sarah"
    assert len(final_state.values["audit_log"]) >= 3