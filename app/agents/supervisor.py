from typing import Dict, Any, Literal
from app.state import ClaimState

def supervisor_router(state: ClaimState) -> Literal["query_fast_track", "parallel_validation"]:
    """
    Directs workflow execution based on state completeness.
    """
    iteration = state.get("iteration_count", 0)
    if iteration > 5:
        return "query_fast_track"

    missing_docs = state.get("missing_documents", [])
    if missing_docs:
        # Route missing mandatory document cases immediately to query path
        return "query_fast_track"

    return "parallel_validation"