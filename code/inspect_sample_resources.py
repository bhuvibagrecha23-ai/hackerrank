import os
import json
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}
ev_manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}
identities = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_identities.csv'), encoding='utf-8')))
audit_log = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_audit_log.csv'), encoding='utf-8')))

email_to_uid = {}
for u in identities:
    email_to_uid[u['email'].lower()] = u['user_id']
for a in audit_log:
    if a['field_name'] == 'email':
        email_to_uid[a['old_value'].lower()] = a['user_id']
        email_to_uid[a['new_value'].lower()] = a['user_id']

uid_to_idents = {}
for u in identities:
    uid = u['user_id']
    uid_to_idents[uid] = {'emails': {u['email'].lower()}, 'phones': {u['phone']}, 'names': {u['name']}, 'hashes': {u['email_hash']}}

for a in audit_log:
    uid = a['user_id']
    if uid in uid_to_idents:
        if a['field_name'] == 'email':
            uid_to_idents[uid]['emails'].add(a['old_value'].lower())
            uid_to_idents[uid]['emails'].add(a['new_value'].lower())
        elif a['field_name'] == 'phone':
            uid_to_idents[uid]['phones'].add(a['old_value'])
            uid_to_idents[uid]['phones'].add(a['new_value'])

# Check for each sample case:
# What resources appear in steps?
for req in sample_reqs:
    cid = req['case_id']
    out = sample_outs[cid]
    steps = json.loads(out['steps_json'])
    res_in_steps = [(s['system_id'], s['resource_id'], s['operation'], s['state'], s['evidence_id']) for s in steps]
    print(f"\n[{cid}] audit_at={req['audit_at']} status={out['deletion_status']}")
    for r in res_in_steps:
        print(f"   {r}")
