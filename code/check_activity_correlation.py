import os
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
sample_reqs = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_deletion_requests.csv'), encoding='utf-8')))
activities = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'system_activity.csv'), encoding='utf-8')))

print("Checking activity correlation around reported_at / requested_at:")
for req in sample_reqs[:10]:
    cid = req['case_id']
    req_at = req['requested_at']
    rep_at = req['reported_at']
    em = req['email']
    
    # find activities around rep_at
    rep_dt = datetime.fromisoformat(rep_at.replace('Z', '+00:00'))
    req_dt = datetime.fromisoformat(req_at.replace('Z', '+00:00'))
    
    nearby_acts = []
    for a in activities:
        a_dt = datetime.fromisoformat(a['event_time'].replace('Z', '+00:00'))
        # If event is between req_dt and rep_dt + 1 hour
        if req_dt <= a_dt <= rep_dt:
            if a['source_system'] == 'deletion_worker':
                nearby_acts.append((abs((a_dt - rep_dt).total_seconds()), a))
                
    nearby_acts.sort(key=lambda x: x[0])
    print(f"\n[{cid}] req={req_at} rep={rep_at} status={req['reported_status']}")
    for diff, a in nearby_acts[:5]:
        print(f"   diff={diff:6.1f}s | {a['activity_id']} | {a['event_time']} | {a['event_type']} | {a['target_system']} | res={a['resource_id']} | claim={a['reported_result']}")
