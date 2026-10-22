from typing import TypedDict, Annotated, List, Dict, Any
import operator

class ClaimState(TypedDict):
    case_id: str
    raw_documents: List[str]
    extracted: Dict[str, Any]
    redacted_text: str
    missing_documents: List[str]
    policy_clauses: List[Dict[str, Any]]
    code_validation: Dict[str, Any]
    fraud_report: Dict[str, Any]
    decision: Dict[str, Any]
    human_review: Dict[str, Any]
    letter_draft: str
    audit_log: Annotated[List[Dict[str, Any]], operator.add]
    iteration_count: int