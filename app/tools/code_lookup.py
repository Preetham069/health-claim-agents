from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
from app.config import settings

def load_code_table() -> pd.DataFrame:
    path = settings.data_dir / "codes" / "icd10_codes.csv"
    if not path.exists():
        return pd.DataFrame(columns=["code", "description", "type", "category"])
    return pd.read_csv(path)

# Consistent pairs based on medical specialty
CONSISTENT_SPECIALTIES = {
    "Surgical": ["Surgical", "General"],
    "Ophthalmology": ["Ophthalmology", "General"],
    "Orthopedic": ["Orthopedic", "General"],
    "Cardiology": ["Cardiology", "General"],
    "Endocrine": ["General"]
}

def validate_codes(diag_code: str | None, proc_code: str | None) -> Tuple[bool, str]:
    if not diag_code or not proc_code:
        return False, "Missing diagnosis or procedure code for validation."

    df = load_code_table()
    diag_row = df[(df["code"] == diag_code) & (df["type"] == "diagnosis")]
    proc_row = df[(df["code"] == proc_code) & (df["type"] == "procedure")]

    if diag_row.empty:
        return False, f"Diagnosis code '{diag_code}' is not recognized in reference standard."
    if proc_row.empty:
        return False, f"Procedure code '{proc_code}' is not recognized in reference standard."

    diag_cat = diag_row.iloc[0]["category"]
    proc_cat = proc_row.iloc[0]["category"]

    allowed = CONSISTENT_SPECIALTIES.get(diag_cat, [])
    if proc_cat not in allowed:
        return False, f"Clinical mismatch: Diagnosis category '{diag_cat}' is incompatible with Procedure category '{proc_cat}'."

    return True, f"Codes valid: {diag_cat} diagnosis matches {proc_cat} procedure."