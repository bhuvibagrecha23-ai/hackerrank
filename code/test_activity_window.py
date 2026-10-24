import os
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

all_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'deletion_requests.csv'), encoding='utf-8')))
system_activity = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'system_activity.csv'), encoding='utf-8')))

# Group deletion_worker account deletions by reported_at or window
del_acc_acts = [a for a in system_activity if a['source_system'] == 'deletion_worker' and a['target_system'] == 'account_service' and a['event_type'] == 'DELETE_RECORD']
print(f"Total deletion_worker account deletions: {len(del_acc_acts)}")

# Check for each request
matched_exact = 0
matched_multiple = 0
unmatched = 0

for req in all_reqs:
    req_at = req['requested_at']
    rep_at = req['reported_at']
    # Acts in window
    acts = [a for a in del_acc_acts if req_at <= a['event_time'] <= rep_at]
    if len(acts) == 1:
        matched_exact += 1
    elif len(acts) > 1:
        matched_multiple += 1
    else:
        unmatched += 1

print(f"Exact 1 match: {matched_exact}")
print(f"Multiple matches: {matched_multiple}")
print(f"Unmatched: {unmatched}")
