import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}
system_activity = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'system_activity.csv'), encoding='utf-8')))
del_acc_acts = [a for a in system_activity if a['source_system'] == 'deletion_worker' and a['target_system'] == 'account_service' and a['event_type'] == 'DELETE_RECORD']

# Look at cases 21 to 30:
# Sort them by requested_at
batch_cases = [f'case_{i}' for i in range(21, 31)]
sorted_batch = sorted([sample_reqs[int(c.split('_')[1])-1] for c in batch_cases], key=lambda x: (x['requested_at'], x['reported_at']))

print("Sorted batch requests by (requested_at, reported_at):")
for r in sorted_batch:
    steps = json.loads(sample_outs[r['case_id']]['steps_json'])
    acc_steps = [s['resource_id'] for s in steps if s['system_id'] == 'account_service']
    print(f"  {r['case_id']} | req={r['requested_at']} | rep={r['reported_at']} | email={r['email']} | acc={acc_steps}")

# What deletion_worker account deletions happened in the window for this entire batch?
min_req = min(r['requested_at'] for r in sorted_batch)
max_rep = max(r['reported_at'] for r in sorted_batch)
batch_acts = [a for a in del_acc_acts if min_req <= a['event_time'] <= max_rep]
batch_acts.sort(key=lambda x: x['event_time'])

print("\nDeletion worker account activities in batch window:")
for a in batch_acts:
    print(f"  {a['event_time']} | {a['resource_id']} | {a['reported_result']}")
