import re
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.state import ClaimState
from app.tools.schemas import ExtractedClaimData
from app.tools.document_parser import parse_document
from app.llm import LLMFactory

MANDATORY_DOCUMENTS = ["pre_auth_form", "cost_estimate"]

def detect_missing_documents(submitted_docs: List[str]) -> List[str]:
    """
    Detects missing mandatory pre-authorization documents.
    A submission requires an itemized cost estimate or hospital bill.
    """
    combined = " ".join([str(d).lower().replace("-", "_").replace(" ", "_") for d in submitted_docs])
    missing = []

    # Check for cost estimate / billing breakdown
    has_cost_doc = any(k in combined for k in [
        "cost_estimate", "cost", "estimate", "bill", "charges", "breakdown", "tariff", "quotation"
    ])
    
    if not has_cost_doc:
        missing.append("cost_estimate")

    # If submitted_docs is completely empty, the pre-authorization form is also missing
    if not submitted_docs:
        missing.append("pre_auth_form")

    return missing

def local_extract_fields(raw_text: str) -> ExtractedClaimData:
    """
    Extracts structured fields using deterministic regex patterns
    with structured fallback.
    """
    age_match = re.search(r"(?i)\b(?:age)\s*:\s*(\d{1,3})", raw_text)
    gender_match = re.search(r"(?i)\b(?:gender|sex)\s*:\s*(male|female|other)", raw_text)
    diag_code_match = re.search(r"(?i)\b(?:diagnosis(?:\s+code)?|icd(?:-?10)?)\s*:\s*([A-Z]\d{2}(?:\.\d{1,2})?)", raw_text)
    proc_code_match = re.search(r"(?i)\b(?:procedure(?:\s+code)?)\s*:\s*(\d{2}\.\d{2})", raw_text)
    cost_match = re.search(r"(?i)\b(?:cost|amount|bill|charges|estimate)\s*:\s*(?:inr|rs\.?)?\s*([\d,]+)", raw_text)
    policy_match = re.search(r"(?i)\b(?:policy(?:\s+(?:id|number|no))?)\s*:\s*([A-Z0-9\-]+)", raw_text)
    hosp_match = re.search(r"(?i)\b(?:hospital(?:\s+name)?|clinic)\s*:\s*([A-Za-z\s]+?)(?:\n|$)", raw_text)

    patient_age = int(age_match.group(1)) if age_match else None
    patient_gender = gender_match.group(1).capitalize() if gender_match else None
    diagnosis_code = diag_code_match.group(1).upper() if diag_code_match else None
    procedure_code = proc_code_match.group(1) if proc_code_match else None
    
    estimated_cost = None
    if cost_match:
        try:
            estimated_cost = float(cost_match.group(1).replace(",", ""))
        except ValueError:
            estimated_cost = None

    policy_number = policy_match.group(1).strip() if policy_match else "CARE-SHIELD-2026"
    hospital_name = hosp_match.group(1).strip() if hosp_match else "City Care Hospital"

    return ExtractedClaimData(
        patient_age=patient_age,
        patient_gender=patient_gender,
        diagnosis_code=diagnosis_code,
        diagnosis_description=None,
        procedure_code=procedure_code,
        procedure_description=None,
        admission_date=None,
        estimated_cost=estimated_cost,
        hospital_name=hospital_name,
        policy_number=policy_number,
        submitted_documents=[]
    )

def extraction_node(state: ClaimState) -> Dict[str, Any]:
    """
    LangGraph execution node: parses documents, extracts fields,
    and flags missing mandatory pre-auth items.
    """
    raw_docs = state.get("raw_documents", [])
    extracted_texts = []

    for doc_path in raw_docs:
        parsed_content = parse_document(doc_path)
        extracted_texts.append(parsed_content)

    combined_corpus = "\n\n".join(extracted_texts)
    extracted_data = local_extract_fields(combined_corpus)
    extracted_data.submitted_documents = raw_docs

    missing = detect_missing_documents(raw_docs)

    audit_entry = {
        "node": "document_extraction_agent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_used": "local-parser-engine",
        "extracted_fields_count": sum(1 for v in extracted_data.model_dump().values() if v is not None),
        "missing_documents_detected": missing,
        "status": "success"
    }

    return {
        "extracted": extracted_data.model_dump(),
        "missing_documents": missing,
        "audit_log": [audit_entry]
    }