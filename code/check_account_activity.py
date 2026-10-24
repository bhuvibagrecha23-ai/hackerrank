import os
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

all_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'deletion_requests.csv'), encoding='utf-8')))
system_activity = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'system_activity.csv'), encoding='utf-8')))

# Check for each case:
# Is there an account_service activity in [requested_at, reported_at]?
matched = 0
not_matched = []
for req in all_reqs:
    cid = req['case_id']
    req_at = req['requested_at']
    rep_at = req['reported_at']
    
    # find deletion_worker activity for account_service
    acts = [a for a in system_activity if a['source_system'] == 'deletion_worker' and a['target_system'] == 'account_service' and req_at <= a['event_time'] <= rep_at]
    if acts:
        matched += 1
    else:
        not_matched.append(req)

print(f"Matched account_service activity: {matched} / {len(all_reqs)}")
print(f"Not matched: {len(not_matched)}")
for r in not_matched[:10]:
    print(f"[{r['case_id']}] req={r['requested_at']} rep={r['reported_at']} status={r['reported_status']} text={r['request_text'][:50]}")
