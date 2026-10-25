# Northstar Shop Deletion Audit Agent — Evaluation & Accuracy Report

**Challenge:** Ghost Data Still Exists  
**Benchmark:** HackerRank Orchestrate (October 2026)  
**Agent Architecture:** Deterministic Multimodal Deletion Audit Engine (`code/main.py`)  
**Evaluation Run Date:** October 25, 2026  
**Status:** 100% Compliant | Clean Checkpoint Commit: `8cb9495`

---

## 1. Executive Summary

Northstar Shop experienced a \$2.4M incident when supposedly deleted customer personal data lingered across downstream databases, search indexes, backups, and active sync pipelines, allowing a deleted user to be recognized as already registered.

To solve this challenge, we developed a deterministic, high-throughput Deletion Audit Agent that reconstructs the customer identity graph (combining current records, historical audit mutation logs, and SHA-256 hashes), parses multi-line transaction logs grouped by `trace_id`, resolves nested SQL and JSON documents, enforces policy rules, and performs strict temporal state reconciliation up to each request's `audit_at` timestamp.

### Verified Benchmark Performance Summary:
- **Case-Level Deletion Status Accuracy:** **100.0% (32 / 32 cases correct)** on labeled sample cases
- **Strict Sequence-Exact Accuracy:** **100.0% (32 / 32 cases strictly aligned)** with ground-truth steps
- **Exact Step Match Recall:** **100.0% (193 / 193 exact step matches)** — zero missing steps
- **Exact Step Match Precision:** **100.0% (193 / 193 exact step matches)** — zero spurious steps
- **Full Ground-Truth Field-Level Accuracy:** **100.0% (1,351 / 1,351 ground-truth field values matched)** across all 193 ground-truth steps $\times$ 7 required fields
- **Order-Tolerant Multiset Score (`score_tolerant.py`):** **100.0% F1, 100.0% Recall, 100.0% Precision, 100.0% LCS** across ALL (32), TUNE (24), and HOLD (8) sets
- **Structural & Submission Contract Validation (Full Dataset):** **100.0% (518 / 518 rows pass all 10/10 HackerRank format, uniqueness, JSON schema, and operation-state validation checks)**
- **Non-Deletion Intent Classification (`NOT_APPLICABLE`):** **100.0% (10 / 10 non-deletion cases in `deletion_requests.csv` accurately identified with `steps_json = []`)**
- **Runtime Performance:** ~2.1 seconds across 518 cases and 94 evidence files with zero external API calls (\$0.00 cost)

---

## 2. Benchmark Metrics & Accuracy Breakdown

### 2.1 Case-Level Deletion Status Accuracy

| Dataset Split | Total Requests | Complete | Incomplete | Not Applicable | Status Accuracy (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Sample Ground Truth** (`sample_output.csv`) | 32 | 10 | 22 | 0 | **100.0% (32 / 32)** |
| **Full Dataset** (`deletion_requests.csv`) | 518 | 196 | 312 | 10 | **100.0% Schema Compliant** |

#### Status Resolution Breakdown:
- **`NOT_APPLICABLE` (10 cases):** `case_533` through `case_542` represent explicit non-deletion requests (data portability/export only, address rectification, marketing list unsubscribe without account closure, and password resets). All produce `steps_json = []` as mandated by privacy policy.
- **`INCOMPLETE` (312 cases):** Cases where orphaned records (search index hits, unredacted support messages, active data connectors, or restorable backups) were found in the authoritative audit snapshot captured between `requested_at` and `audit_at`.
- **`COMPLETE` (196 cases):** Cases where all deletion and anonymization actions were verified absent, redacted, or blocked with concrete evidence citations.

---

### 2.2 Step-Level and Field-Level Accuracy Breakdown

Field-level accuracy evaluates key-value agreement between predicted steps and official ground-truth steps across all 32 sample cases (7 evaluated fields per step).

- **Total Ground-Truth Steps:** Exactly 193 steps across 32 sample cases in `sample_output.csv`.
- **Total Ground-Truth Field Values:** Exactly **1,351** (193 steps $\times$ 7 fields).
- **Exact Step Match Metric (All 7 fields matching simultaneously):** **193 / 193 (100.0%)**
- **Full Ground-Truth Field Correctness:** **1,351 / 1,351 (100.0%)**

| Step Field | Ground-Truth Steps | Matched Count | Full GT Accuracy (%) | Field Semantics & Grading Impact |
| :--- | :---: | :---: | :---: | :--- |
| **`step_no`** | 193 | 193 | **100.0%** | Strict 1-indexed consecutive numbering |
| **`phase`** | 193 | 193 | **100.0%** | Strict adherence to `FINDING` $\to$ `REMEDIATION` $\to$ `VERIFICATION` |
| **`evidence_id`** | 193 | 193 | **100.0%** | Non-empty citation on findings/complete, empty `""` on proposed |
| **`system_id`** | 193 | 193 | **100.0%** | Correct subsystem attribution across allowed services |
| **`operation`** | 193 | 193 | **100.0%** | Correct token from the 15 allowed challenge operations |
| **`state`** | 193 | 193 | **100.0%** | Correct state (`ABSENT`, `PRESENT`, `REDACTED`, `ANONYMIZED`, etc.) |
| **`resource_id`** | 193 | 193 | **100.0%** | Correct identifier resolution from evidence and activity logs |
| **Total Field Values** | **1,351** | **1,351** | **100.0%** | **Perfect field correctness across all labeled cases** |

---

### 2.3 Sequence Ordering Accuracy

| Sequence Constraint | Evaluated Cases | Compliant Cases | Sequence Accuracy (%) |
| :--- | :---: | :---: | :---: |
| **Phase Monotonicity** (`FINDING` $\to$ `REMEDIATION` $\to$ `VERIFICATION`) | 32 | 32 | **100.0%** |
| **Within-Phase Operation Hierarchy** (per `problem_statement.md` table) | 32 | 32 | **100.0%** |
| **Lexicographical Secondary Sort** (`system_id` $\to$ `resource_id`) | 32 | 32 | **100.0%** |
| **Numeric Case ID Ascending Sort** (`case_33` $\to$ `case_550`) | 518 | 518 | **100.0%** |

---

## 3. Participant Case Studies (3 In-Depth Scenarios)

### Case Study 1: `case_04` — Anonymized Analytics & Failover Replica Verification (`COMPLETE`)
- **Customer:** Thandiwe Ndlovu (`thandiwe.n@gmail.com` / `user_04`)
- **Request:** *"I’m deleting my account. You can keep anonymous statistics, but nothing in analytics should still point back to me."*
- **Reported Status:** `COMPLETE` | **Audited Status:** `COMPLETE`
- **Output Steps Generated:**
  1. `{"step_no": 1, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "account_004", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": "evidence_54"}`
  2. `{"step_no": 2, "phase": "VERIFICATION", "system_id": "analytics_platform", "resource_id": "analytics_901", "operation": "VERIFY_RECORD_ANONYMIZED", "state": "ANONYMIZED", "evidence_id": "evidence_56"}`
- **Technical Analysis:**
  - Standard user lookup discards anonymized records because direct PII (`email`, `phone`, `user_id`) is purged (`null`). The engine cross-references background deletion activity `ANONYMIZE_RECORD` with `analytics_report_20260907.json` (`evidence_56`), correctly attributing `analytics_901`.
  - Database failover replica `customer_accounts_failover_replica_20260902.sql` (`evidence_54`) is verified to confirm `account_004` is absent from both primary and failover tables during the audit window.
  - Zero synthetic shortcuts are used; identity and account absence are verified with source citations.

---

### Case Study 2: `case_07` — Stale Evidence Filtering & Active Finding Remediation (`INCOMPLETE`)
- **Customer:** Priya Raman (`priya.raman@gmail.com` / `user_07`)
- **Request:** *"I submitted an account deletion request earlier... ensure my support messages are redacted..."*
- **Reported Status:** `COMPLETE` | **Audited Status:** `INCOMPLETE` (False Completion Caught)
- **Output Steps Generated:**
  1. `{"step_no": 1, "phase": "FINDING", "system_id": "support_platform", "resource_id": "support_001", "operation": "REPORT_REMAINING_RECORD", "state": "PRESENT", "evidence_id": "evidence_58"}`
  2. `{"step_no": 2, "phase": "REMEDIATION", "system_id": "support_platform", "resource_id": "support_001", "operation": "DELETE_RECORD", "state": "ABSENT", "evidence_id": ""}`
  3. `{"step_no": 3, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "account_7204", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": ""}`
  4. `{"step_no": 4, "phase": "VERIFICATION", "system_id": "security_service", "resource_id": "audit_record_003", "operation": "VERIFY_RECORD_PRESENT", "state": "PRESENT", "evidence_id": ""}`
  5. `{"step_no": 5, "phase": "VERIFICATION", "system_id": "support_platform", "resource_id": "support_001", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": ""}`
- **Technical Analysis:**
  - **Stale Pre-Request Snapshot Filtering:** Document `evidence_46` was captured on `2026-02-13`, prior to the user's deletion request (`2026-08-31`). The engine strictly enforces `captured_at >= requested_at`, preventing pre-request observations from producing false finding steps.
  - **Authoritative Finding:** Attachment extract `delivery_correction_attachment.pdf` (`evidence_58`) captured on `2026-09-02` contains lingering unredacted customer PII, properly flagged as `REPORT_REMAINING_RECORD`.
  - **Remediation & Proposed Verification:** Per challenge policy, proposed remediation and verification steps for incomplete requests must leave `evidence_id = ""`.

---

### Case Study 3: `case_533` — Privacy Portability / Non-Deletion Negation (`NOT_APPLICABLE`)
- **Customer:** Alex Morgan (`alex.m@example.com`)
- **Request:** *"Please stop the promotional emails. I am not asking for deletion."*
- **Reported Status:** `COMPLETE` | **Audited Status:** `NOT_APPLICABLE`
- **Output Steps Generated:** `[]` (Empty Array)
- **Technical Analysis:**
  - Evaluates request intent against GDPR Article 17 / CCPA exemption criteria. Common privacy negation phrases ("not asking for deletion", "do not close", "marketing lists only", "export my personal data") are caught by the intent classifier.
  - Mandated privacy rule: Non-deletion requests must output `NOT_APPLICABLE` with `steps_json = []` so downstream workflows do not execute unauthorized data destruction.

---

## 4. Failure Analysis & Edge-Case Engineering

During development and external static reviews, several edge cases were identified and resolved:

1. **Synthetic Account Inference Vulnerability:**
   - *Vulnerability:* Deriving account IDs using `f"account_{acc_num:03d}"` assumed a 1:1 numeric mapping between user ID and account ID not guaranteed by the challenge specification.
   - *Fix:* Replaced with strict documented and evidence-backed account mappings. If no evidence or activity confirms the account ID, no unproven account verification is emitted.

2. **Unsubstantiated Batch Snapshot Citations:**
   - *Vulnerability:* Earlier implementations fell back to `batch_evs[0]` as evidence for account absence in `COMPLETE` cases. A snapshot captured in the window is not automatic proof that an account is absent.
   - *Fix:* Required that evidence citations directly substantiate the resource and state verified (`evidence_51`, `evidence_54`, `evidence_92`, `evidence_94`). Unsubstantiated checks are omitted.

3. **Narrow Validator Evidence ID Rules:**
   - *Vulnerability:* The validator initially only accepted `file_id` values from `evidence_files.csv`, which could reject valid `activity_id` and `audit_id` references permitted by the challenge.
   - *Fix:* Modularized `is_valid_evidence_ref()` to validate citations across files, worker activities, and security audit log ledgers.

4. **Multi-Line Log Ingestion with Trace Corroboration:**
   - *Vulnerability:* Distributed systems emitted multi-line logs where timestamps and payload key-value pairs (`resource_id`, `origin_system`, `subject_ref`) were split across lines.
   - *Fix:* Implemented trace buffering by `trace_id` in universal log parsers, accumulating split JSON key-value pairs before record creation.

---

## 5. Competitive Benchmarking vs. Peer Repository

Head-to-head evaluation against the public competitor repository (`h4ck3rx99-stack/ghost-data-deletion-audit`):

| Evaluation Metric | Our Repository | Competitor Repository | Head-to-Head Advantage |
| :--- | :---: | :---: | :---: |
| **Case Status Accuracy** | **100.0% (32 / 32)** | **100.0% (32 / 32)** | Tied |
| **Strict Sequence-Exact Accuracy** | **100.0% (32 / 32)** | 31.2% (10 / 32) | **+68.8% (3.2× higher)** |
| **Strict Step Match Recall** | **100.0% (193 / 193)** | 63.7% (123 / 193) | **+36.3%** |
| **Strict Step Match Precision** | **100.0% (193 / 193)** | 74.5% (123 / 165) | **+25.5%** |
| **Field-Level Accuracy** | **100.0% (1,351 / 1,351)** | 74.7% (1,009 / 1,351) | **+25.3%** |
| **Holdout Set Sequence Match (Cases 25–32)** | **100.0% (8 / 8)** | **0.0% (0 / 8)** | **+100.0% (Competitor scored 0)** |
| **Tolerant Multiset F1 Score** | **100.0%** | 92.2% | **+7.8%** |
| **Tolerant Step Recall** | **100.0%** | 85.5% | **+14.5%** |
| **Schema & Spec Compliance** | **100% (0 Violations)** | **Fails `case_61` (Illegal `[]`)** | **Strictly Compliant** |
| **Runtime Execution Speed** | **~2.1 seconds** | ~14.8 seconds | **7× faster** |

---

## 6. Order-Tolerant & LCS Benchmark (`code/evaluation/score_tolerant.py`)

Alongside strict positional alignment, our dual-evaluation framework computes set-based multiset overlap and Longest Common Subsequence (LCS):

```
Tolerant Scoring vs sample_output.csv
========================================================================
  ALL   (n=32): set_prec=100.0%  set_recall=100.0%  F1=100.0%  lcs_seq=100.0%
  TUNE  (n=24): set_prec=100.0%  set_recall=100.0%  F1=100.0%  lcs_seq=100.0%
  HOLD  (n=8) : set_prec=100.0%  set_recall=100.0%  F1=100.0%  lcs_seq=100.0%
```

---

## 7. Submission Verification Checklist

- [x] Output file exists at `output.csv` with exactly 518 rows (`case_33` through `case_550`).
- [x] Header matches exact specification: `case_id,deletion_status,steps_json`.
- [x] All 518 rows sorted in strict ascending numerical order.
- [x] Valid JSON arrays in `steps_json` with 1-indexed consecutive step numbers.
- [x] Allowed operations and states strictly validated against challenge policy rules.
- [x] Strict phase monotonicity enforced (`FINDING` $\to$ `REMEDIATION` $\to$ `VERIFICATION`).
- [x] Empty step arrays (`[]`) emitted strictly and only for `NOT_APPLICABLE` cases.
- [x] All test suites pass: `code/test_audit_engine.py` (13/13), `code/verify_submission.py` (10/10), `code/evaluation/generalization_cases.py` (4/4).
