from typing import Dict, Any
from app.tools.fraud_rules import evaluate_fraud_risk

def fraud_detection_step(state: Dict[str, Any]) -> Dict[str, Any]:
    extracted = state.get("extracted", {})
    proc_code = extracted.get("procedure_code")
    cost = extracted.get("estimated_cost")

    risk_score, flags = evaluate_fraud_risk(proc_code, cost)

    return {
        "fraud_report": {
            "risk_score": risk_score,
            "flags": flags,
            "requires_escalation": risk_score >= 50
        }
    }