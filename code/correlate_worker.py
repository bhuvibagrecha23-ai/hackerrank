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
system_activity = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'system_activity.csv'), encoding='utf-8')))

# Check how deletion_worker activities correlate with requests
# Let's inspect each sample case:
# What deletion_worker activities occurred between requested_at and reported_at?
for req in sample_reqs[:15]:
    cid = req['case_id']
    req_at = req['requested_at']
    rep_at = req['reported_at']
    out = sample_outs[cid]
    steps = json.loads(out['steps_json'])
    res_in_steps = set(s['resource_id'] for s in steps)
    
    # deletion_worker activities in window
    acts = [a for a in system_activity if a['source_system'] == 'deletion_worker' and req_at <= a['event_time'] <= rep_at]
    res_in_acts = set(a['resource_id'] for a in acts)
    common = res_in_steps.intersection(res_in_acts)
    print(f"[{cid}] Steps res: {res_in_steps}")
    print(f"       Acts res in window: {res_in_acts}")
    print(f"       Intersection: {common}")
