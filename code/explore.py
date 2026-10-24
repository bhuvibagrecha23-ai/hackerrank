import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

def load_csv(name):
    path = os.path.join(DATASET_DIR, name)
    with open(path, mode='r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

sample_reqs = load_csv('sample_deletion_requests.csv')
sample_outs = {r['case_id']: r for r in load_csv('sample_output.csv')}
deletion_rules = load_csv('deletion_rules.csv')
user_identities = load_csv('user_identities.csv')
user_audit_log = load_csv('user_audit_log.csv')
evidence_files = load_csv('evidence_files.csv')
system_activity = load_csv('system_activity.csv')

print(f"Loaded: {len(sample_reqs)} sample requests, {len(sample_outs)} sample outputs")
print(f"Loaded: {len(deletion_rules)} rules, {len(user_identities)} identities, {len(user_audit_log)} audit logs")
print(f"Loaded: {len(evidence_files)} evidence files, {len(system_activity)} system activities")

for req in sample_reqs[:10]:
    cid = req['case_id']
    out = sample_outs[cid]
    print(f"\n=== {cid} | Reported: {req['reported_status']} -> Actual: {out['deletion_status']} ===")
    print(f"Email: {req['email']} | ReqAt: {req['requested_at']} | AuditAt: {req['audit_at']}")
    print(f"Text: {req['request_text']}")
    steps = json.loads(out['steps_json'])
    print(f"Steps ({len(steps)}):")
    for s in steps:
        print(f"  [{s.get('phase')}] op={s.get('operation')} sys={s.get('system_id')} res={s.get('resource_id')} state={s.get('state')} ev={s.get('evidence_id')}")
