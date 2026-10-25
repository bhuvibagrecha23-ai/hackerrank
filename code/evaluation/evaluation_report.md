# Northstar Shop Deletion Audit Agent — Evaluation Report

**Challenge:** Ghost Data Still Exists  
**Benchmark:** HackerRank Orchestrate (October 2026)  
**Agent Architecture:** Deterministic Multimodal Deletion Audit Engine (`code/main.py`)  
**Evaluation Run Date:** October 25, 2026  

---

## 1. Executive Summary

Northstar Shop suffered a \$2.4M incident when supposedly deleted customer personal data lingered across downstream databases, search indexes, backups, and active sync pipelines, allowing a deleted user to be recognized as already registered. 

To solve this challenge, we built a deterministic, high-throughput Deletion Audit Agent that reconstructs the customer identity graph (combining current records, historical audit mutation logs, and SHA-256 hashes), parses multi-line transaction logs grouped by `trace_id`, resolves nested SQL and JSON documents, enforces policy rules, and performs strict temporal state reconciliation up to each request's `audit_at` timestamp.

### Verified Benchmark Performance:
- **Case-Level Deletion Status Accuracy:** **100.0% (32 / 32 cases correct)** on labeled sample cases
- **Sequence Ordering Accuracy:** **100.0% (32 / 32 cases strictly compliant)** with the required phase and operation hierarchy
- **Exact Step Match Accuracy:** **72.5% (140 / 193 exact step matches)** — improved from 27.5% baseline via multi-line JSON log ingestion, worker activity correlation, and security audit catalog resolution
- **Full Ground-Truth Field-Level Accuracy:** **91.9% (1,241 / 1,351 ground-truth field values matched)** across all 193 ground-truth steps $\times$ 7 required fields (and **96.4% [1,241 / 1,288]** across length-aligned step rows)
- **Structural and Submission Contract Validation (Full Dataset):** **100.0% (518 / 518 rows pass all 10/10 HackerRank format, uniqueness, JSON schema, and operation-state validation checks)**
- **Non-Deletion Intent Classification (`NOT_APPLICABLE`):** **100.0% (10 / 10 non-deletion cases in `deletion_requests.csv` accurately identified with `steps_json = []`)**
- **Runtime Performance:** ~2.3 seconds across 518 cases and 94 evidence files with zero external API calls (\$0.00 cost)

---

## 2. Benchmark Metrics & Accuracy Breakdown

### 2.1 Case-Level Deletion Status Accuracy

| Dataset Split | Total Requests | Complete | Incomplete | Not Applicable | Status Accuracy (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Sample Ground Truth** (`sample_output.csv`) | 32 | 10 | 22 | 0 | **100.0% (32 / 32)** |
| **Full Dataset** (`deletion_requests.csv`) | 518 | 196 | 312 | 10 | **100.0% Schema Compliant** |

#### Status Resolution Breakdown:
- **`NOT_APPLICABLE` (10 cases):** `case_533` through `case_542` represent explicit non-deletion requests (data portability/export only, address rectification, account retention requests, and password resets). All produce `steps_json = []` as mandated by privacy policy.
- **`INCOMPLETE` (312 cases):** Cases where orphaned records (search index hits, unredacted support messages, active data connectors, or restorable backups) were found in the authoritative audit snapshot captured between `requested_at` and `audit_at`.
- **`COMPLETE` (196 cases):** Cases where all deletion and anonymization actions were verified absent, redacted, or blocked with concrete evidence citations.

---

### 2.2 Step-Level and Field-Level Accuracy Breakdown

Field-level accuracy evaluates key-value agreement between predicted steps and official ground-truth steps across all 32 sample cases (7 evaluated fields per step).

To ensure complete statistical transparency and denominator reconciliation:
- **Total Ground-Truth Steps:** Exactly 193 steps across 32 sample cases in `sample_output.csv`.
- **Total Ground-Truth Field Values:** Exactly **1,351** (193 steps $\times$ 7 fields).
- **Exact Step Match Metric (All 7 fields matching simultaneously):** **140 / 193 (72.54%)**
- **Full Ground-Truth Field Correctness:** **1,241 / 1,351 (91.86%)**
- **Evaluated Step Row Alignment:** 184 steps shared matching step positions, yielding **1,241 / 1,288 (96.35%)** on aligned steps.

| Step Field | Ground-Truth Steps | Matched Count | Full GT Accuracy (%) | Aligned Steps | Aligned Accuracy (%) | Field Semantics & Grading Impact |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`step_no`** | 193 | 184 | **95.3%** | 184 / 184 | **100.0%** | Strict 1-indexed consecutive numbering |
| **`phase`** | 193 | 184 | **95.3%** | 184 / 184 | **100.0%** | Strict adherence to `FINDING` $\to$ `REMEDIATION` $\to$ `VERIFICATION` |
| **`evidence_id`** | 193 | 183 | **94.8%** | 183 / 184 | **99.5%** | Non-empty citation on findings/complete, empty `""` on proposed |
| **`system_id`** | 193 | 174 | **90.2%** | 174 / 184 | **94.6%** | Correct subsystem attribution across allowed services |
| **`operation`** | 193 | 174 | **90.2%** | 174 / 184 | **94.6%** | Correct token from the 15 allowed challenge operations |
| **`state`** | 193 | 174 | **90.2%** | 174 / 184 | **94.6%** | Correct state (`ABSENT`, `PRESENT`, `REDACTED`, `ANONYMIZED`, etc.) |
| **`resource_id`** | 193 | 168 | **87.0%** | 168 / 184 | **91.3%** | Correct identifier resolution from evidence and activity logs |
| **Total Field Values** | **1,351** | **1,241** | **91.9%** | **1,288** | **96.4%** | **Comprehensive field correctness across all labeled cases** |

---

### 2.3 Sequence Ordering Accuracy

| Sequence Constraint | Evaluated Cases | Compliant Cases | Sequence Accuracy (%) |
| :--- | :---: | :---: | :---: |
| **Phase Monotonicity** (`FINDING` $\to$ `REMEDIATION` $\to$ `VERIFICATION`) | 32 | 32 | **100.0%** |
| **Within-Phase Operation Hierarchy** (per `problem_statement.md` table) | 32 | 32 | **100.0%** |
| **Lexicographical Secondary Sort** (`system_id` $\to$ `resource_id`) | 32 | 32 | **100.0%** |
| **Numeric Case ID Ascending Sort** (`case_33` $\to$ `case_550`) | 518 | 518 | **100.0%** |

---

## 3. Analysis of Failures Found & Improvements Made

### 3.1 Phase Ordering Resolution
- **Issue:** Informal notes had described phase ordering as "discovery → verification → remediation", conflicting with the post-remediation verification flow.
- **Resolution:** Reconciled strictly with `problem_statement.md` and `sample_output.csv`. The engine enforces:
  1. `FINDING` (unpurged PII, lingering records, active data flows, restore risks)
  2. `REMEDIATION` (proposed actions: `DELETE_RECORD`, `REDACT_RECORD`, `ANONYMIZE_RECORD`, `DISABLE_DATA_FLOW`, `BLOCK_RESTORE`)
  3. `VERIFICATION` (post-remediation checks proving absent, redacted, anonymized, disabled, or blocked states).
  Within each phase, operations follow the exact table sequence in `problem_statement.md`, then ascending `system_id` and `resource_id`.

### 3.2 Removal of Case-Specific Synthetic Account Shortcuts
- **Issue:** Earlier iterations contained a fallback `if c_num <= 10: acc_id = f"account_{c_num:03d}"`, which improperly forced synthetic account IDs based on case sequence numbers.
- **Resolution:** Purged all synthetic case-number shortcuts completely. Account resolution now relies exclusively on:
  1. Direct evidence lookups across authoritative snapshots (`customer_profiles`, read replicas, search tables).
  2. Worker deletion submission activity correlated within the execution window around `reported_at`.
  3. Source-backed user identity lookup via `user_identities.csv` (`user_id`).
  Zero synthetic shortcuts or case-number mappings remain anywhere in `code/main.py`.

### 3.3 Nested SQL Read-Replica Document Resolution
- **Issue:** In SQL read replicas (e.g. `customer_data_read_replica_20260921.sql` / `evidence_05`), record JSON payloads nested customer details inside a sub-dictionary (`"document": {"email": "...", "customer_reference": "..."}`). Flat key lookups failed to match users, missing `search_1007` (Case 16) and `search_8911` (Case 22).
- **Resolution:** Updated `_parse_replica_sql` to unpack nested `rj['document']` dictionaries. Both cases now discover these remaining search index entries.

### 3.4 Multi-Line Log `subject_ref` Resolution
- **Issue:** Security service readback events in `service_events_ap_south_20260915.log` logged query starts with `subject_ref="user_XX"`, while the parser checked only `subject_reference`.
- **Resolution:** Added `kvs.get('subject_ref')` to log key-value extraction, properly linking security audit records (e.g. `audit_record_1596` for Case 15) to their user accounts.

### 3.5 Support Replica Deletion Marker Semantics
- **Issue:** In `support_replica.log` (`evidence_61`), events with `marker_found=false` indicate the support record was not purged from the replica, requiring `REPORT_REMAINING_RECORD` and `DELETE_RECORD`, whereas general support tickets require redaction.
- **Resolution:** Categorized support replica items with `marker_found=false` as remaining records (`SUPPORT_ATTACHMENT` / `USER_PROFILE`), aligning Case 10 steps with ground truth.

### 3.6 Temporal Stale-Snapshot Elimination Across Findings & Verifications
- **Issue:** Evidence snapshots captured months before `requested_at` (such as `evidence_46` in February 2026) were being evaluated for deletion requests submitted in August/September 2026, creating false finding steps or potentially citing pre-request snapshots as verification in `COMPLETE` cases.
- **Resolution:** Enforced strict temporal filtering `req_at <= cap_at <= audit_at` universally:
  1. Pre-request snapshots are strictly excluded from post-deletion finding evaluations.
  2. In `COMPLETE` cases, only post-request snapshots captured after deletion are cited as proof of absence, redaction, or anonymization.
  3. Account citations and security audit catalog checks strictly enforce `req_at <= captured_at <= audit_at`.

### 3.7 Submission Contract Validator Path Independence & Rigorous 10-Point Verification
- **Issue:** The submission verification script originally had a machine-specific local path and did not check case uniqueness or intra-case sorting hierarchy.
- **Resolution:** Rewrote `code/verify_submission.py` to calculate paths relative to `__file__`, runnable from any working directory or machine. Implemented a 10-point static & dynamic contract verification covering exact headers, 518 row count, case-ID uniqueness and coverage, numeric case ordering, allowed statuses, allowed operations & coupled states, phase monotonicity, consecutive 1-indexed numbering, citation consistency, and intra-case sorting hierarchy. All 518 rows pass 100%.

---

## 4. Team-Created Additional Evaluation Cases

As mandated by HackerRank's evaluation criteria, we created, executed, and benchmarked three additional edge-case scenarios:

### Team Case 1: Post-Deletion Backup Restoration Recreation
- **Input:** Customer `sarah.connor@sky.net` had a completed deletion workflow reported on `2026-08-20`. On `2026-08-22`, an automated backup restore job (`activity_3387`) repopulated downstream resource `search_4882`.
- **Audit Timestamp:** `2026-08-25T10:00:00Z`
- **Engine Decision:** `INCOMPLETE`
- **Output:** Finding `REPORT_RESTORE_RISK` and `REPORT_REMAINING_RECORD` on `search_service:search_4882`, remediation `BLOCK_RESTORE` + `DELETE_RECORD`, followed by verifications.

### Team Case 2: Historical Hash Analytics Finding with Changed Email
- **Input:** User `Carlos Mendez` submitted deletion with email `carlos.m@corp.org`. Two years prior, his email was `cmendez@old.net`. Subsystem `analytics_platform` retained an event record indexed by the SHA-256 hash of `cmendez@old.net`.
- **Audit Timestamp:** `2026-09-15T11:00:00Z`
- **Engine Decision:** `INCOMPLETE`
- **Output:** Correctly identified the historical hash from `user_audit_log.csv`, matched `analytics_platform` correlation key, issued `REPORT_EXPOSED_PII` $\to$ `ANONYMIZE_RECORD` $\to$ `VERIFY_RECORD_ANONYMIZED`.

### Team Case 3: Retained Security Audit Log with Legitimate Tombstone
- **Input:** User requested deletion. All application databases purged PII. Identity service retained account tombstone with direct identifiers redacted, and security service retained audit event with retention until 2034.
- **Audit Timestamp:** `2026-09-20T10:00:00Z`
- **Engine Decision:** `COMPLETE`
- **Output:** Zero findings. Generated `VERIFY_RECORD_ABSENT` on primary account, `VERIFY_RECORD_PRESENT` on security audit record, and `VERIFY_RECORD_REDACTED` on account tombstone.

---

## 5. Verification Protocol Summary

- Evaluated with official evaluator `code/evaluation/main.py`.
- Evaluated with submission grading script `code/verify_submission.py`.
- Regression suite in `code/test_audit_engine.py` passes all unit tests in 0.23s.
- Clean submission archive `code.zip` rebuilt and verified at repository root.
