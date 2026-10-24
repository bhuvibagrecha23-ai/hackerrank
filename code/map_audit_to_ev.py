import os
import json
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

all_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'deletion_requests.csv'), encoding='utf-8')))
ev_manifest = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8')))
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

print("Total requests:", len(all_reqs))
# Check unique audit_at values in deletion_requests.csv
audit_dates = sorted(list(set(r['audit_at'] for r in all_reqs)))
print("Unique audit dates in deletion_requests:", len(audit_dates))
ev_dates = sorted(list(set(e['captured_at'] for e in ev_manifest)))
print("Unique captured_at dates in evidence_files:", len(ev_dates))

# For each audit date in deletion_requests, find the closest evidence files at or before audit_at
for ad in audit_dates[:15]:
    candidates = [e for e in ev_manifest if e['captured_at'] <= ad]
    candidates.sort(key=lambda x: x['captured_at'], reverse=True)
    closest = candidates[:3]
    print(f"audit_at: {ad} -> closest evidence files:")
    for c in closest:
        dt_diff = (datetime.fromisoformat(ad.replace('Z', '+00:00')) - datetime.fromisoformat(c['captured_at'].replace('Z', '+00:00'))).total_seconds()
        print(f"   {c['file_id']:<12} | {c['captured_at']} | diff={dt_diff/3600.0:.2f}h | {c['origin']:<35} | {os.path.basename(c['file_path'])}")
