import os
import json
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

def load_csv(name):
    path = os.path.join(DATASET_DIR, name)
    with open(path, mode='r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

sample_reqs = load_csv('sample_deletion_requests.csv')
sample_outs = {r['case_id']: r for r in load_csv('sample_output.csv')}
identities = load_csv('user_identities.csv')
audit_log = load_csv('user_audit_log.csv')
evidence_files = {r['file_id']: r for r in load_csv('evidence_files.csv')}
system_activity = load_csv('system_activity.csv')
deletion_rules = load_csv('deletion_rules.csv')

# Build user mapping
email_to_uid = {}
for u in identities:
    email_to_uid[u['email'].lower()] = u['user_id']
for a in audit_log:
    if a['field_name'] == 'email':
        email_to_uid[a['old_value'].lower()] = a['user_id']
        email_to_uid[a['new_value'].lower()] = a['user_id']

uid_to_identities = {}
for u in identities:
    uid = u['user_id']
    uid_to_identities[uid] = {
        'user_id': uid,
        'names': set([u['name']]),
        'emails': set([u['email'].lower()]),
        'phones': set([u['phone']]),
        'hashes': set([u['email_hash']])
    }

for a in audit_log:
    uid = a['user_id']
    if uid not in uid_to_identities:
        continue
    f = a['field_name']
    if f == 'name':
        uid_to_identities[uid]['names'].add(a['old_value'])
        uid_to_identities[uid]['names'].add(a['new_value'])
    elif f == 'email':
        uid_to_identities[uid]['emails'].add(a['old_value'].lower())
        uid_to_identities[uid]['emails'].add(a['new_value'].lower())
    elif f == 'phone':
        uid_to_identities[uid]['phones'].add(a['old_value'])
        uid_to_identities[uid]['phones'].add(a['new_value'])

print("Analyzing sample cases...")
for req in sample_reqs:
    cid = req['case_id']
    out = sample_outs[cid]
    uid = email_to_uid.get(req['email'].lower())
    steps = json.loads(out['steps_json'])
    status = out['deletion_status']
    
    phases = [s['phase'] for s in steps]
    ops = [s['operation'] for s in steps]
    systems = [s['system_id'] for s in steps]
    res_ids = [s['resource_id'] for s in steps]
    ev_ids = [s['evidence_id'] for s in steps]
    
    print(f"\n[{cid}] Status: {status} | User: {uid} | Steps: {len(steps)}")
    for s in steps:
        print(f"  step {s['step_no']}: phase={s['phase']:<12} sys={s['system_id']:<20} res={s['resource_id']:<20} op={s['operation']:<25} st={s['state']:<10} ev={s['evidence_id']}")
