import time
import json
from pathlib import Path
from app.agents.extraction import local_extract_fields, detect_missing_documents
from app.agents.redaction import redact_pii
from app.agents.code_validation import validate_codes
from app.fraud.nodes import fraud_detection_step

def run_evaluation_benchmark():
    data_path = Path(__file__).resolve().parent.parent / "data" / "synthetic_cases" / "sample_claims.json"
    with open(data_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    total = len(cases)
    extraction_correct = 0
    missing_doc_correct = 0
    verdict_correct = 0
    pii_violations = 0

    start_time = time.time()

    for c in cases:
        # 1. Field Extraction Accuracy
        text_corpus = f"""
        Age: {c.get('age', 45)}
        Gender: {c.get('gender', 'Male')}
        Diagnosis Code: {c.get('diagnosis_code')}
        Procedure Code: {c.get('procedure_code')}
        Cost: INR {c.get('estimated_cost')}
        Policy Number: {c.get('policy_number', 'CARE-SHIELD-2026')}
        Hospital Name: {c.get('hospital_name', 'City Care Hospital')}
        """
        extracted = local_extract_fields(text_corpus)
        if extracted.diagnosis_code == c.get("diagnosis_code") and extracted.procedure_code == c.get("procedure_code"):
            extraction_correct += 1

        # 2. Missing Document Recall
        docs = c.get("submitted_documents", [])
        missing = detect_missing_documents(docs)
        note = str(c.get("ground_truth_note", "")).lower()
        expected_missing = "cost_estimate" in note or "missing" in note or not docs

        if bool(missing) == bool(expected_missing):
            missing_doc_correct += 1

        # 3. PII Scrubbing Zero-Tolerance
        test_pii_text = f"Patient Phone: +91 9876543210, Aadhaar: 1234-5678-9012. {text_corpus}"
        redacted_output, _ = redact_pii(test_pii_text)
        if "9876543210" in redacted_output:
            pii_violations += 1

        # 4. Verdict Ground-Truth Agreement
        is_valid_code, _ = validate_codes(c.get("diagnosis_code"), c.get("procedure_code"))
        mock_state = {
            "extracted": {
                "procedure_code": c.get("procedure_code"),
                "estimated_cost": float(c.get("estimated_cost", 0))
            }
        }
        fraud_rep = fraud_detection_step(mock_state)["fraud_report"]

        # Adjudication rules matching workflow
        if bool(missing):
            pred = "Query"
        elif not is_valid_code:
            pred = "Reject"
        elif fraud_rep.get("risk_score", 0) > 50:
            pred = "Query"
        else:
            pred = "Approve"

        # Check against whichever key exists in the JSON schema
        gt_verdict = (
            c.get("expected_verdict") 
            or c.get("ground_truth_verdict") 
            or c.get("verdict")
            or c.get("decision")
            or ""
        )

        if pred.lower() == str(gt_verdict).lower():
            verdict_correct += 1

    elapsed = time.time() - start_time

    print("=" * 50)
    print("        INTERNSHIP EVALUATION REPORT RESULTS      ")
    print("=" * 50)
    print(f"Total Evaluated Cases:                {total}")
    print(f"Field-Extraction Accuracy:            {(extraction_correct / total) * 100:.1f}% (Target: >=90%)")
    print(f"Missing-Doc Detection Recall:         {(missing_doc_correct / total) * 100:.1f}% (Target: >=90%)")
    print(f"Verdict Agreement vs Ground Truth:    {(verdict_correct / total) * 100:.1f}% (Target: >=85%)")
    print(f"PII Leaks to Redacted Text:           {pii_violations} (Target: 0)")
    print(f"Total Processing Time:                {elapsed:.2f}s ({elapsed / total:.3f}s / case)")
    print("=" * 50)

if __name__ == "__main__":
    run_evaluation_benchmark()