import pytest
from app.agents.extraction import local_extract_fields, detect_missing_documents, extraction_node
from app.state import ClaimState

def test_field_extraction():
    sample_text = (
        "Hospital: City Care Hospital\n"
        "Policy Number: CARE-SHIELD-2026\n"
        "Age: 45\n"
        "Gender: Male\n"
        "Diagnosis Code: K35.80\n"
        "Diagnosis Description: Acute Appendicitis\n"
        "Procedure Code: 47.09\n"
        "Procedure Description: Appendectomy\n"
        "Estimated Cost: 55,000"
    )
    result = local_extract_fields(sample_text)
    assert result.patient_age == 45
    assert result.patient_gender == "Male"
    assert result.diagnosis_code == "K35.80"
    assert result.procedure_code == "47.09"
    assert result.estimated_cost == 55000.0
    assert result.policy_number == "CARE-SHIELD-2026"
    assert result.hospital_name == "City Care Hospital"

def test_missing_document_detection():
    # Only pre-auth submitted -> cost_estimate missing
    docs = ["patient_pre_auth_form.txt"]
    missing = detect_missing_documents(docs)
    assert "cost_estimate" in missing

    # Both submitted -> none missing
    full_docs = ["pre_auth_form.pdf", "hospital_cost_estimate.txt"]
    assert detect_missing_documents(full_docs) == []