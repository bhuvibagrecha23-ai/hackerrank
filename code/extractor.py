import os
import glob
import json
import csv
import sqlite3
import re
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
EVIDENCE_DIR = os.path.join(DATASET_DIR, 'evidence')

class EvidenceIndexer:
    def __init__(self):
        self.records = [] # list of dicts: file_id, captured_at, system_id, resource_id, category, user_id, email, phone, state, raw
        self.ev_manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}
        
    def add_record(self, file_id, system_id, resource_id, category, state, user_id=None, email=None, phone=None, email_hash=None, raw=None):
        finfo = self.ev_manifest.get(file_id, {})
        captured_at = finfo.get('captured_at', '')
        self.records.append({
            'file_id': file_id,
            'captured_at': captured_at,
            'system_id': system_id,
            'resource_id': resource_id,
            'category': category,
            'state': state,
            'user_id': user_id,
            'email': email.lower() if email else None,
            'phone': phone,
            'email_hash': email_hash,
            'raw': raw
        })

print("EvidenceIndexer skeleton created.")
