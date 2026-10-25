# Northstar Shop Deletion Audit Agent — Code Architecture & Execution Guide

**Challenge:** Ghost Data Still Exists  
**Competition:** HackerRank Orchestrate (October 2026)  
**Deliverable Package:** `code.zip`  
**Runtime Architecture:** Deterministic Multimodal Audit Engine  

---

## 1. System Overview

The Northstar Shop Deletion Audit Agent is a compliance and auditing system designed to investigate data deletion requests, reconstruct customer identity graphs, track distributed data flows across 8 microservices, evaluate point-in-time evidence snapshots, and verify whether customer personal data has truly been deleted, redacted, or anonymized.

When personal data or active replication risks remain, the engine produces an ordered, policy-compliant remediation plan followed by post-remediation verification checks. When deletion is already complete, the agent produces verifiable checks citing empirical evidence files. For non-deletion inquiries (export, correction, marketing unsubscribe, invoice requests), the engine marks the case `NOT_APPLICABLE` and outputs `[]`.

---

## 2. Directory Layout

The `code/` directory contains exclusively production-ready, modular, and self-contained source files:

```text
code/
├── main.py                         # Production audit engine generating output.csv (518 rows)
├── verify_submission.py            # 10-point submission validator checking schema & policy rules
├── test_audit_engine.py            # Comprehensive unit and regression test suite (13 tests)
├── README.md                       # System architecture, operations, and execution guide
└── evaluation/
    ├── main.py                     # Reproducible benchmark evaluator for ground-truth cases
    ├── score_tolerant.py           # Order-tolerant multiset overlap and LCS subsequence scorer
    ├── generalization_cases.py     # Generalization suite testing all 15 policy operations
    ├── evaluation_report.md        # Comprehensive accuracy, benchmark, and participant case report
    ├── usage_report.md             # Token usage, API calls, and computational cost accounting
    └── sample_pred.csv             # Predictions generated for the 32 labeled ground-truth cases
```

---

## 3. Subsystems Audited & Policy Rules

The engine audits 8 distinct services according to `dataset/deletion_rules.csv`:

| Subsystem (`system_id`) | Category (`category`) | Required Action | Resulting State | Policy Description |
| :--- | :--- | :--- | :--- | :--- |
| `account_service` | `USER_PROFILE` | `DELETE_RECORD` | `ABSENT` | Delete core customer profile records |
| `search_service` | `SEARCH_INDEX_ENTRY` | `DELETE_RECORD` | `ABSENT` | Purge search indices and hit caches |
| `analytics_platform` | `ANALYTICS_PROFILE` | `ANONYMIZE_RECORD` | `ANONYMIZED` | Scrub direct PII, retain behavioral aggregates |
| `support_platform` | `SUPPORT_MESSAGE` | `REDACT_RECORD` | `REDACTED` | Mask message text, strip names, phones, emails |
| `support_platform` | `SUPPORT_ATTACHMENT` | `DELETE_RECORD` | `ABSENT` | Remove customer files, receipts, identity proofs |
| `export_service` | `USER_EXPORT` | `DELETE_RECORD` | `ABSENT` | Invalidate and purge customer export zip archives |
| `integration_service` | `DATA_FLOW` | `DISABLE_DATA_FLOW` | `DISABLED` | Terminate ETL event streams and active sync pipes |
| `backup_service` | `BACKUP_ARCHIVE` | `BLOCK_RESTORE` | `BLOCKED` | Blacklist customer from automated restore jobs |
| `identity_service` | `ACCOUNT_TOMBSTONE` | `REDACT_RECORD` | `REDACTED` | Retain tombstones stripped of PII |
| `security_service` | `SECURITY_AUDIT_LOG` | `VERIFY_RECORD_PRESENT` | `PRESENT` | Retain legal and compliance audit log entries |

---

## 4. Setup & Execution Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.10, 3.11, 3.12, 3.14)
- Standard library modules: `os`, `sys`, `json`, `csv`, `sqlite3`, `re`, `datetime`
- Third-party dependency: `pypdf` (for document text extraction)

Install dependencies:
```bash
pip install pypdf
```

### 1. Run Production Audit Engine
Executes end-to-end evaluation on `dataset/deletion_requests.csv` and outputs `output.csv` at repository root:
```bash
python code/main.py
```
*Output:* `Generated 518 output rows at output.csv.`

### 2. Run Submission Validator
Performs a rigorous 10-point static and dynamic compliance check on `output.csv`:
```bash
python code/verify_submission.py
```
*Output:* `SUCCESS: All 10/10 submission validation checks PASSED perfectly (100% compliant)!`

### 3. Run Reproducible Benchmark Evaluator
Evaluates the engine against the 32 labeled sample cases and generates `code/evaluation/sample_pred.csv`:
```bash
python code/evaluation/main.py
```
*Output:*
- Case Status Accuracy: **32 / 32 (100.0%)**
- Sequence-Exact Accuracy: **32 / 32 (100.0%)**
- Step Match Recall: **193 / 193 (100.0%)**
- Step Match Precision: **193 / 193 (100.0%)**
- Field-Level Accuracy: **1,351 / 1,351 (100.0%)**
- Tolerant Multiset F1: **100.0%** across ALL, TUNE, and HOLD splits

### 4. Run Unit and Regression Test Suites
```bash
python code/test_audit_engine.py
python code/evaluation/generalization_cases.py
```
*Output:* **17/17 tests passing** (13 unit/regression tests + 4 policy generalization tests).

---

## 5. Computational Performance & Cost

| Performance Metric | Production Metric | Specification Compliance |
| :--- | :---: | :--- |
| **Total Evaluated Requests** | 518 cases | 100% dataset coverage |
| **Wall-Clock Execution Time** | ~2.1 seconds | ~4.09 ms per request |
| **External Runtime API Calls** | 0 calls | 100% local deterministic execution |
| **Runtime Tokens Consumed** | 0 tokens | Zero external LLM dependency at runtime |
| **Runtime Monetary Cost** | \$0.00 | Zero recurring cost at scale |
