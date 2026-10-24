import os
import json
import csv
from evidence_parser import EvidenceParser

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

parser = EvidenceParser()
sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}

# Operation sort order
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

def step_sort_key(step):
    p_ord = PHASE_ORDER.get(step['phase'], 99)
    op_ord = OP_ORDER.get(step['operation'], 99)
    return (p_ord, op_ord, step['system_id'], step['resource_id'])

# Check matching for each sample case
matched_cases = 0
total_cases = len(sample_reqs)

for req in sample_reqs:
    cid = req['case_id']
    exp_out = sample_outs[cid]
    exp_status = exp_out['deletion_status']
    exp_steps = json.loads(exp_out['steps_json'])
    
    # Check identifiers
    u_email = req['email'].lower()
    uid = parser.email_to_uid.get(u_email)
    uinfo = parser.uid_to_info.get(uid, {'emails': {u_email}, 'phones': set(), 'names': set(), 'hashes': set(), 'user_id': uid})
    
    # What evidence was cited in expected?
    exp_evs = sorted(list(set(s['evidence_id'] for s in exp_steps if s['evidence_id'])))
    print(f"\n[{cid}] Expected status: {exp_status} | Cited ev: {exp_evs}")
    
    # What records in parser.evidence_records match uinfo?
    found_records = []
    for fid, recs in parser.evidence_records.items():
        if fid not in exp_evs:
            continue
        for r in recs:
            # check match
            r_em = (r.get('email') or '').lower()
            r_uid = r.get('user_id')
            matched = False
            if r_em and r_em in uinfo['emails']:
                matched = True
            elif r_uid and r_uid == uid:
                matched = True
            if matched:
                found_records.append((fid, r))
    
    print(f"   Parser found {len(found_records)} matching records in cited evidence:")
    for fid, r in found_records:
        print(f"     {fid} -> {r['system_id']} {r['resource_id']} {r['category']} {r['state']}")
