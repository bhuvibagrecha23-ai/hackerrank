import os
import glob
import json
import csv
import sqlite3
import re
from datetime import datetime
from audit_engine_v2 import AuditEngineV2

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

engine = AuditEngineV2()
sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}

PHASE_ORDER = {'FINDING': 1, 'REMEDIATION': 2, 'VERIFICATION': 3}
OP_ORDER = {
    'REPORT_REMAINING_RECORD': 1,
    'REPORT_EXPOSED_PII': 2,
    'REPORT_ACTIVE_DATA_FLOW': 3,
    'REPORT_RESTORE_RISK': 4,
    'DISABLE_DATA_FLOW': 1,
    'BLOCK_RESTORE': 2,
    'DELETE_RECORD': 3,
    'REDACT_RECORD': 4,
    'ANONYMIZE_RECORD': 5,
    'VERIFY_RECORD_ABSENT': 1,
    'VERIFY_RECORD_PRESENT': 2,
    'VERIFY_RECORD_REDACTED': 3,
    'VERIFY_RECORD_ANONYMIZED': 4,
    'VERIFY_DATA_FLOW_DISABLED': 5,
    'VERIFY_RESTORE_BLOCKED': 6,
}

def step_sort_key(s):
    return (PHASE_ORDER[s['phase']], OP_ORDER[s['operation']], s['system_id'], s['resource_id'])

# Check how closely our generated steps match sample_output.csv
matched_cases = 0
total_cases = len(sample_reqs)

for req in sample_reqs:
    cid = req['case_id']
    exp = sample_outs[cid]
    exp_status = exp['deletion_status']
    exp_steps = json.loads(exp['steps_json'])
    
    # 1. Check NA
    is_na = any(neg in req['request_text'].lower() for neg in [
        'not asking for deletion', 'do not close', 'without removing', 'marketing lists only',
        'not a request to erase', 'leave my profile', 'continue using the service', 'don\'t delete',
        'leave the account active', 'keep the account as it is'
    ])
    if is_na:
        gen_status = 'NOT_APPLICABLE'
        gen_steps = []
    else:
        # User lookup
        u_email = req['email'].lower()
        uid = engine.email_to_uid.get(u_email)
        uinfo = engine.uid_to_info.get(uid, {'emails': {u_email}, 'phones': set(), 'names': set(), 'hashes': set(), 'user_id': uid})
        
        # In sample cases, what records were cited in exp?
        exp_evs = sorted(list(set(s['evidence_id'] for s in exp_steps if s['evidence_id'])))
        
        # Check agreement
        print(f"[{cid}] Exp status={exp_status:<11} Exp steps count={len(exp_steps)} Cited={exp_evs}")

print("Done inspecting.")
