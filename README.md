# Multi-Agent Health Insurance Claim Pre-Authorization & Denial Prevention System

A production-style multi-agent pre-authorization engine built with **LangGraph**, **Ollama**, **ChromaDB**, and **Streamlit**.

## Key Features
- **Local Privacy-First Processing**: Raw text and PII redaction processed locally via Ollama; zero sensitive identifiers reach cloud prompts.
- **LangGraph Checkpointing**: StateGraph orchestration with dynamic supervisor routing and human-in-the-loop interrupts.
- **Policy Grounding (RAG)**: ChromaDB retrieval with exact page and clause citations.
- **Clinical Code Validation**: Deterministic ICD-10 to procedure compatibility checks.
- **Fraud & Cost Anomaly Detection**: Subgraph screening for bill inflation against benchmark baselines.

## Quickstart

### 1. Environment Setup
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt