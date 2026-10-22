import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.state import ClaimState
from app.tools.schemas import DecisionVerdict
from app.llm import LLMFactory

DECISION_SYSTEM_PROMPT = """You are a senior health insurance adjudication AI.
Evaluate the claim summary, policy citations, code checks, and fraud flags.
Produce a strict JSON matching this schema:
{
  "verdict": "Approve" | "Query" | "Reject",
  "confidence": float (0.0 to 1.0),
  "rationale": "Clear clinical and policy explanation",
  "citations": ["List of referenced policy clauses/sections"],
  "unresolved_issues": ["List of missing docs or anomalies"]
}

Rules:
1. Missing mandatory documents MUST result in 'Query'.
2. Clinical mismatch or policy exclusion MUST result in 'Reject'.
3. Significant fraud risk or cost inflation above benchmark triggers 'Query' or 'Reject'.
4. Completely clean claims matching policy coverage result in 'Approve'.
Output raw JSON only without markdown formatting.
"""

def evaluate_deterministic_verdict(state: ClaimState) -> DecisionVerdict:
    missing_docs = state.get("missing_documents", [])
    code_val = state.get("code_validation", {})
    fraud_rep = state.get("fraud_report", {})
    clauses = state.get("policy_clauses", [])

    citations = [f"{c.get('policy_id')}: {c.get('section')} (p. {c.get('page')})" for c in clauses]
    unresolved = list(missing_docs) + fraud_rep.get("flags", [])

    # Rule 1: Missing mandatory files
    if missing_docs:
        return DecisionVerdict(
            verdict="Query",
            confidence=0.95,
            rationale=f"Claim is missing mandatory documentation: {', '.join(missing_docs)}.",
            citations=citations,
            unresolved_issues=unresolved
        )

    # Rule 2: Code mismatch
    if not code_val.get("valid", True):
        return DecisionVerdict(
            verdict="Reject",
            confidence=0.90,
            rationale=f"Code validation failure: {code_val.get('reason')}",
            citations=citations,
            unresolved_issues=unresolved
        )

    # Rule 3: High fraud / extreme inflation
    if fraud_rep.get("risk_score", 0) >= 60:
        return DecisionVerdict(
            verdict="Query",
            confidence=0.85,
            rationale=f"Cost anomaly detected: {'; '.join(fraud_rep.get('flags', []))}",
            citations=citations,
            unresolved_issues=unresolved
        )

    # Rule 4: Clean approval
    return DecisionVerdict(
        verdict="Approve",
        confidence=0.92,
        rationale="All mandatory documents present, codes clinically verified, cost aligns with benchmark baseline.",
        citations=citations,
        unresolved_issues=[]
    )

def decision_node(state: ClaimState) -> Dict[str, Any]:
    # Redacted safe summary for cloud LLM reasoning
    safe_summary = {
        "redacted_text": state.get("redacted_text", ""),
        "missing_documents": state.get("missing_documents", []),
        "code_validation": state.get("code_validation", {}),
        "fraud_report": state.get("fraud_report", {}),
        "policy_clauses": state.get("policy_clauses", [])
    }

    model_used = "gemini-cloud-reasoning"
    try:
        llm = LLMFactory.get_gemini_chat(temperature=0.0)
        prompt = f"{DECISION_SYSTEM_PROMPT}\n\nClaim Evidence:\n{json.dumps(safe_summary)}"
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        
        # Strip potential code fences
        clean_json = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        verdict_obj = DecisionVerdict(**data)
    except Exception:
        # Fallback to local rule engine
        model_used = "deterministic-rule-fallback"
        verdict_obj = evaluate_deterministic_verdict(state)

    audit_entry = {
        "node": "decision_agent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_used": model_used,
        "verdict": verdict_obj.verdict,
        "confidence": verdict_obj.confidence
    }

    return {
        "decision": verdict_obj.model_dump(),
        "audit_log": [audit_entry]
    }