# Multi-Agent Health Insurance Claim Pre-Authorization System
## Architectural Design & Agent Topology

### 1. High-Level Agent Topology
The system orchestrates 9 specialized components built with LangGraph:
- **Supervisor / Router**: Evaluates claim state completeness; fast-tracks incomplete claims directly to Query triage.
- **Document Extraction Agent**: Processes raw PDFs, images, and text locally via Ollama into a validated Pydantic schema.
- **PII Redaction Agent**: Deterministic regex-based sanitization stripping all direct identifiers prior to cloud transit.
- **Policy RAG Agent**: ChromaDB vector store powered by local embeddings (`nomic-embed-text`) retrieving clauses with page citations.
- **Code Validation Agent**: Deterministic cross-referencing of ICD-10 diagnosis against procedure specialties.
- **Fraud & Anomaly Subgraph**: Evaluates procedure cost benchmarks and detects bill inflation.
- **Decision Agent**: Synthesizes multi-agent evidence into Approve / Query / Reject verdicts with confidence and citations.
- **Human Review Node**: LangGraph interrupt pause ensuring human medical officer sign-off before commitment.
- **Communication Agent**: Generates professional adjudication letters based on the finalized human decision.

### 2. Privacy Guardrail Pipeline
1. Ingest Documents (Local Filesystem)
2. Local Extraction (Ollama / Regex)
3. Deterministic Redaction (Strips Names, Phone Numbers, Government IDs)
4. Safe State Transition (Only redacted metadata passed to cloud synthesis)
5. Zero-Canary Verification (Verified by automated pytest suite)