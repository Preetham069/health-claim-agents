from typing import Dict, Any, List, Tuple
from pathlib import Path
import pandas as pd
from app.config import settings

def load_benchmarks() -> pd.DataFrame:
    path = settings.data_dir / "benchmarks" / "cost_benchmarks.csv"
    if not path.exists():
        return pd.DataFrame(columns=["procedure_code", "min_cost", "max_cost", "typical_stay_days"])
    # Read procedure_code explicitly as str to avoid float conversion
    return pd.read_csv(path, dtype={"procedure_code": str})

def evaluate_fraud_risk(proc_code: str | None, cost: float | None) -> Tuple[int, List[str]]:
    risk_score = 0
    flags = []

    if not cost or cost <= 0:
        flags.append("Missing or zero estimated cost on record.")
        risk_score += 25
        return risk_score, flags

    benchmarks = load_benchmarks()
    target_code = str(proc_code).strip() if proc_code else ""
    matched = benchmarks[benchmarks["procedure_code"].astype(str).str.strip() == target_code]

    if not matched.empty:
        max_cost = float(matched.iloc[0]["max_cost"])
        min_cost = float(matched.iloc[0]["min_cost"])
        if cost > max_cost * 1.5:
            risk_score += 60
            flags.append(f"Severely inflated cost: Claimed INR {cost:,.2f} exceeds benchmark ceiling of INR {max_cost:,.2f} by >50%.")
        elif cost > max_cost:
            risk_score += 35
            flags.append(f"Inflated cost: Claimed INR {cost:,.2f} exceeds upper benchmark of INR {max_cost:,.2f}.")
        elif cost < min_cost * 0.5:
            risk_score += 20
            flags.append(f"Unusually low cost estimate: INR {cost:,.2f} is significantly below expected minimum.")
    else:
        flags.append(f"No benchmark baseline registered for procedure code '{proc_code}'.")
        risk_score += 10

    return min(risk_score, 100), flags