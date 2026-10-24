import os
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
sample_reqs = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_deletion_requests.csv'), encoding='utf-8')))
activities = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'system_activity.csv'), encoding='utf-8')))
identities = {u['email'].lower(): u for u in csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'user_identities.csv'), encoding='utf-8'))}

for req in sample_reqs[:5]:
    cid = req['case_id']
    em = req['email'].lower()
    u = identities.get(em, {})
    uid = u.get('user_id', '')
    name = u.get('name', '')
    
    print(f"\n[{cid}] email={em} uid={uid} name={name}")
    found = []
    for a in activities:
        d = a['details'].lower()
        if em in d or (uid and uid.lower() in d) or (name and name.lower() in d):
            found.append(a)
    print(f"  Found {len(found)} activities by text match in details:")
    for a in found[:5]:
        print(f"    {a['activity_id']} | {a['event_time']} | {a['event_type']} | {a['source_system']}->{a['target_system']} | res={a['resource_id']} | claim={a['reported_result']} | det={a['details']}")
