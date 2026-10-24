import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}
system_activity = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'system_activity.csv'), encoding='utf-8')))

# For each sample case, what was its account_service resource in steps?
for req in sample_reqs:
    cid = req['case_id']
    steps = json.loads(sample_outs[cid]['steps_json'])
    acc_steps = [s['resource_id'] for s in steps if s['system_id'] == 'account_service']
    acc_id = acc_steps[0] if acc_steps else None
    
    # What DELETE_RECORD account_service activities happened in [requested_at, reported_at]?
    acts = [a for a in system_activity if a['source_system'] == 'deletion_worker' and a['target_system'] == 'account_service' and req['requested_at'] <= a['event_time'] <= req['reported_at']]
    act_res = [a['resource_id'] for a in acts]
    
    match = acc_id in act_res if acc_id else False
    print(f"[{cid}] req={req['requested_at']} rep={req['reported_at']} -> acc_step={acc_id} | act_candidates={act_res} | match={match}")
