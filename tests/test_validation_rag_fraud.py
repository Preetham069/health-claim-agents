import pytest
from app.tools.code_lookup import validate_codes
from app.tools.fraud_rules import evaluate_fraud_risk
from app.tools.policy_ingestion import init_policy_vector_db, query_policies

def test_code_validation_mismatch():
    # Valid pair: Appendicitis and Appendectomy
    is_valid, msg = validate_codes("K35.80", "47.09")
    assert is_valid is True

    # Mismatch pair: Cataract with Knee Replacement
    is_valid_mis, msg_mis = validate_codes("H25.9", "81.54")
    assert is_valid_mis is False
    assert "Clinical mismatch" in msg_mis

def test_fraud_inflated_bill():
    # Benchmark max for 47.09 is 75,000. 195,000 exceeds benchmark by >50%
    score, flags = evaluate_fraud_risk("47.09", 195000.0)
    assert score >= 60
    assert any("Severely inflated cost" in f for f in flags)

def test_policy_rag_retrieval():
    # Verify vector store initialization and retrieval
    clauses = query_policies("cataract surgery limit", top_k=1)
    assert len(clauses) >= 1
    assert "page" in clauses[0]
    assert "CARE-SHIELD-2026" in clauses[0]["policy_id"]