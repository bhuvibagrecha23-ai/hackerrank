import os
import glob
import json
import csv
import sqlite3
import re
import pypdf

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
EVIDENCE_DIR = os.path.join(REPO_ROOT, 'dataset', 'evidence')
ev_manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'evidence_files.csv'), encoding='utf-8'))}

# Let's inspect security_audit_ledger_20261001.json
p = os.path.join(EVIDENCE_DIR, 'records', 'security_audit_ledger_20261001.json')
if os.path.exists(p):
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print("security_audit_ledger sample:", d['records'][:2] if 'records' in d else d)

# Let's inspect connector_configurations_20260812.json
p = os.path.join(EVIDENCE_DIR, 'records', 'connector_configurations_20260812.json')
if os.path.exists(p):
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print("connector_configurations sample:", d['records'][:2] if 'records' in d else d)

# Let's inspect customer_export_manifest_20260409.json
p = os.path.join(EVIDENCE_DIR, 'records', 'customer_export_manifest_20260409.json')
if os.path.exists(p):
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print("customer_export_manifest sample:", d['records'][:2] if 'records' in d else d)

# Let's inspect customer_export_jobs_20260914.json
p = os.path.join(EVIDENCE_DIR, 'records', 'customer_export_jobs_20260914.json')
if os.path.exists(p):
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print("customer_export_jobs sample:", d['records'][:2] if 'records' in d else d)
