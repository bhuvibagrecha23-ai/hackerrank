import os
import json
import csv
import sqlite3
import re
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
EVIDENCE_DIR = os.path.join(DATASET_DIR, 'evidence')

sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}
ev_manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}
identities = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_identities.csv'), encoding='utf-8')))
audit_log = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_audit_log.csv'), encoding='utf-8')))
system_activity = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'system_activity.csv'), encoding='utf-8')))

print("Setup complete. Testing sample parsing logic...")
