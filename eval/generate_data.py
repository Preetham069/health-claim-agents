import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic_cases"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PROCEDURES = [
    {"diag": "K35.80", "diag_desc": "Acute appendicitis", "proc": "47.09", "proc_desc": "Appendectomy", "cat": "Surgical", "cost": 55000},
    {"diag": "H25.9", "diag_desc": "Cataract unspecified", "proc": "13.41", "proc_desc": "Phacoemulsification", "cat": "Ophthalmology", "cost": 32000},
    {"diag": "M17.11", "diag_desc": "Osteoarthritis knee", "proc": "81.54", "proc_desc": "Total knee replacement", "cat": "Orthopedic", "cost": 160000},
    {"diag": "I21.9", "diag_desc": "Myocardial infarction", "proc": "36.06", "proc_desc": "Coronary artery stent", "cat": "Cardiology", "cost": 140000},
]

HOSPITALS = ["City Care Hospital", "Apex Super Specialty", "Metro General Clinic", "Sunrise Hospital"]
FIRST_NAMES = ["Amit", "Rohit", "Ananya", "Kavita", "Suresh", "Pooja", "Vikram", "Deepa"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Reddy", "Nair", "Rao", "Gupta", "Singh"]

def generate_100_cases():
    cases = []
    for i in range(1, 101):
        case_id = f"CASE-{i:03d}"
        p = random.choice(PROCEDURES)
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        age = random.randint(22, 75)
        gender = random.choice(["Male", "Female"])
        phone = f"98{random.randint(10000000, 99999999)}"
        # Synthetic government ID formatted with standard 12 digits
        govt_id = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        hosp = random.choice(HOSPITALS)

        # Distribute realistic edge cases
        case_type = i % 4
        if case_type == 0:
            # Clean case
            diag_code = p["diag"]
            proc_code = p["proc"]
            cost = p["cost"]
            docs = ["pre_auth_form.txt", "cost_estimate.txt"]
            expected = "Approve"
            note = "Clean claim matching coverage."
        elif case_type == 1:
            # Missing document
            diag_code = p["diag"]
            proc_code = p["proc"]
            cost = p["cost"]
            docs = ["pre_auth_form.txt"]
            expected = "Query"
            note = "Missing cost estimate document."
        elif case_type == 2:
            # Clinical mismatch
            diag_code = "H25.9"  # Cataract
            proc_code = "81.54"  # Knee replacement
            cost = 175000
            docs = ["pre_auth_form.txt", "cost_estimate.txt"]
            expected = "Reject"
            note = "Clinical mismatch between diagnosis and procedure."
        else:
            # Inflated cost
            diag_code = p["diag"]
            proc_code = p["proc"]
            cost = p["cost"] * 3.5  # Grossly inflated
            docs = ["pre_auth_form.txt", "cost_estimate.txt"]
            expected = "Query"
            note = "Cost exceeds benchmark ceiling."

        cases.append({
            "case_id": case_id,
            "patient_name": name,
            "age": age,
            "gender": gender,
            "phone": phone,
            "govt_id": govt_id,
            "policy_id": "CARE-SHIELD-2026",
            "diagnosis_code": diag_code,
            "diagnosis_desc": p["diag_desc"],
            "procedure_code": proc_code,
            "procedure_desc": p["proc_desc"],
            "hospital": hosp,
            "estimated_cost": cost,
            "submitted_documents": docs,
            "expected_verdict": expected,
            "ground_truth_note": note
        })

    out_file = DATA_DIR / "sample_claims.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)
    print(f"Successfully generated {len(cases)} cases at {out_file}")

if __name__ == "__main__":
    generate_100_cases()