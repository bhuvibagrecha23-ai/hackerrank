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
identities = load_csv('user_identities.csv')
audit_log = load_csv('user_audit_log.csv')
activities = load_csv('system_activity.csv')
evidence_files = load_csv('evidence_files.csv')

# Build user maps
# Map email -> user_id
email_to_user = {}
for u in identities:
    email_to_user[u['email'].lower()] = u['user_id']
# Also map historical emails from audit_log
for a in audit_log:
    if a['field_name'] == 'email':
        email_to_user[a['old_value'].lower()] = a['user_id']
        email_to_user[a['new_value'].lower()] = a['user_id']

# Map user_id -> all identities
user_to_emails = {}
for u in identities:
    uid = u['user_id']
    user_to_emails[uid] = set([u['email'].lower()])
for a in audit_log:
    if a['field_name'] == 'email':
        uid = a['user_id']
        if uid not in user_to_emails:
            user_to_emails[uid] = set()
        user_to_emails[uid].add(a['old_value'].lower())
        user_to_emails[uid].add(a['new_value'].lower())

print("Mapping sample cases to user_ids:")
for req in sample_reqs[:15]:
    cid = req['case_id']
    email = req['email'].lower()
    uid = email_to_user.get(email)
    print(f"{cid}: email={email} -> user_id={uid}")
    out = sample_outs[cid]
    steps = json.loads(out['steps_json'])
    res_ids = [s['resource_id'] for s in steps]
    print(f"   Status: {out['deletion_status']}, Resources in steps: {res_ids}")
    # Find matching activities
    matching_acts = [a for a in activities if any(r in a['resource_id'] or r in a['details'] for r in res_ids)]
    print(f"   Matching activities in system_activity.csv: {len(matching_acts)}")
    for a in matching_acts[:3]:
        print(f"     act: {a['activity_id']} | {a['event_time']} | {a['event_type']} | {a['source_system']}->{a['target_system']} | res={a['resource_id']} | res_claim={a['reported_result']} | det={a['details']}")
