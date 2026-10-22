from datetime import datetime, timezone
from typing import Dict, Any
from app.state import ClaimState
from app.tools.code_lookup import validate_codes

def code_validation_node(state: ClaimState) -> Dict[str, Any]:
    extracted = state.get("extracted", {})
    diag_code = extracted.get("diagnosis_code")
    proc_code = extracted.get("procedure_code")

    is_valid, reason = validate_codes(diag_code, proc_code)

    validation_result = {
        "valid": is_valid,
        "reason": reason,
        "diagnosis_code": diag_code,
        "procedure_code": proc_code
    }

    audit_entry = {
        "node": "code_validation_agent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_used": "deterministic-reference-lookup",
        "valid": is_valid,
        "reason": reason
    }

    return {
        "code_validation": validation_result,
        "audit_log": [audit_entry]
    }