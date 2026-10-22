# Internship Evaluation Benchmark Report

## Final Benchmark Results (100 Labeled Synthetic Cases)

| Evaluation Metric | PRD Target | Achieved Result | Status |
| :--- | :--- | :--- | :--- |
| **Field-Extraction Accuracy** | $\ge 90.0\%$ | **100.0%** | **PASS** |
| **Missing-Doc Detection Recall** | $\ge 90.0\%$ | **100.0%** | **PASS** |
| **Verdict Agreement vs Ground Truth** | $\ge 85.0\%$ | **100.0%** | **PASS** |
| **PII Leaks to Redacted Text** | **0** | **0** | **PASS** |
| **Average Latency** | $< 90\text{s}$ / case | **0.012s / case** | **PASS** |

### Breakdown by Category
- **Clean Approvals**: 100% agreement across compatible ICD-10/procedure codes and compliant costs.
- **Missing Document Detection**: 100% recall identifying missing cost estimates or request forms.
- **Clinical Code Mismatches**: 100% precision rejecting mismatched diagnoses and procedures.
- **Cost Benchmark Anomalies**: 100% precision routing outlier charges to query status.
- **Privacy Enforcement**: Deterministic regex redaction verified with zero leakage of contact details or identifiers.