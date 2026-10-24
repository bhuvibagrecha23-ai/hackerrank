# Northstar Shop Deletion Audit Agent

**Challenge:** Ghost Data Still Exists  
**Competition:** HackerRank Orchestrate (October 2026)  
**Deliverable Package:** `code.zip`  

---

## 1. Project Overview

The Northstar Shop Deletion Audit Agent is an AI-powered compliance and audit system designed to investigate data deletion requests, reconstruct customer identity graphs, track distributed data flows across 8 microservices, evaluate point-in-time evidence snapshots, and prove whether customer personal data has truly been deleted, redacted, or anonymized.

When personal data or active replication risks remain, the agent produces an ordered, policy-compliant remediation plan followed by post-remediation verification checks. When the deletion is already complete, the agent produces verifiable checks citing empirical evidence files. For non-deletion inquiries (export, correction, opt-out, invoice requests), the agent marks the case `NOT_APPLICABLE` and outputs `[]`.

---

## 2. Directory Structure

```text
code/
├── main.py                     # Entry point executing end-to-end audit on deletion_requests.csv
├── audit_engine_v2.py          # Core deletion audit engine and snapshot parser
├── evidence_parser.py          # Unified parser for SQL dumps, JSON records, logs, PDFs, PNGs
├── verify_submission.py        # Submission validation and grading compliance checker
├── validate_samples.py         # Ground-truth validator against sample_output.csv
├── evaluation/
│   ├── evaluation_report.md    # Case, step, sequence accuracy, custom cases, error analysis
│   └── usage_report.md         # Token usage, call counts, model costs, and efficiency metrics
└── README.md                   # System documentation and execution guide
```

---

## 3. Subsystems Audited

The agent audits 8 distinct services according to `deletion_rules.csv`:
1. `account_service` (`USER_PROFILE`): Primary user profiles. Required treatment: `DELETE`.
2. `search_service` (`SEARCH_INDEX_ENTRY`): Elasticsearch/OpenSearch indices. Required treatment: `DELETE`.
3. `analytics_platform` (`ANALYTICS_PROFILE`): Tracking and cohort profiles. Required treatment: `ANONYMIZE`.
4. `support_platform` (`SUPPORT_MESSAGE` / `SUPPORT_ATTACHMENT`): Tickets and image/PDF uploads. Required treatment: `REDACT` message PII, `DELETE` attachments.
5. `export_service` (`USER_EXPORT`): Historical customer data archive zip files. Required treatment: `DELETE`.
6. `integration_service` (`DATA_FLOW`): ETL connectors and event bridges. Required treatment: `DISABLE`.
7. `backup_service` (`BACKUP_ARCHIVE`): Cold storage archives and database dumps. Required treatment: `BLOCK_RESTORE`.
8. `identity_service` (`ACCOUNT_TOMBSTONE`): Account tombstones. Required treatment: `REDACT` (user_id preserved, all direct PII stripped).
9. `security_service` (`SECURITY_AUDIT_LOG`): Compliance audit records. Required treatment: `RETAIN` (must remain present).

---

## 4. How to Run

### Requirements
- Python 3.10+
- Dependencies: `pypdf` (installed via `pip install pypdf`)

### Execution
From the repository root:
```bash
python code/main.py
```
This generates `output.csv` at the repository root containing exactly 518 data rows (+1 header row), sorted by `case_id`.

### Verification
To verify the output against all challenge rules:
```bash
python code/verify_submission.py
```
To validate against the official 32 sample cases:
```bash
python code/validate_samples.py
```
