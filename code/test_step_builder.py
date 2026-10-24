import os
import json
import csv
from audit_engine_v2 import AuditEngineV2

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

engine = AuditEngineV2()
sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}

# Phase & Op orders
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

# Check for each sample case:
# What steps does sample_output.csv produce?
for req in sample_reqs:
    cid = req['case_id']
    exp = sample_outs[cid]
    exp_status = exp['deletion_status']
    exp_steps = json.loads(exp['steps_json'])
    
    u_email = req['email'].lower()
    uid = engine.email_to_uid.get(u_email)
    uinfo = engine.uid_to_info.get(uid, {'emails': {u_email}, 'phones': set(), 'names': set(), 'hashes': set(), 'user_id': uid})
    
    # Check matching in evidence
    # Find closest evidence file for audit_at
    audit_at = req['audit_at']
    candidates = [e for e in engine.manifest.values() if e['captured_at'] <= audit_at]
    candidates.sort(key=lambda x: x['captured_at'], reverse=True)
    closest_fid = candidates[0]['file_id'] if candidates else None
    
    print(f"\n[{cid}] audit_at={audit_at} status={exp_status} closest={closest_fid}")
    print(f"   Expected steps ({len(exp_steps)}):")
    for s in exp_steps:
        print(f"     step {s['step_no']}: {s['phase']} {s['system_id']} {s['resource_id']} {s['operation']} {s['state']} ev='{s['evidence_id']}'")
