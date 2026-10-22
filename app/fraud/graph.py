from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Dict, Any
from app.fraud.nodes import fraud_detection_step

class FraudSubgraphState(TypedDict):
    extracted: Dict[str, Any]
    fraud_report: Dict[str, Any]

def build_fraud_subgraph():
    workflow = StateGraph(FraudSubgraphState)
    workflow.add_node("fraud_analysis", fraud_detection_step)
    workflow.add_edge(START, "fraud_analysis")
    workflow.add_edge("fraud_analysis", END)
    return workflow.compile()

fraud_subgraph = build_fraud_subgraph()