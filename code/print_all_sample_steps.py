import os
import json
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
sample_reqs = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_output.csv'), encoding='utf-8'))}

# Compare all 32 samples:
# For each sample, let's see:
# - Expected status
# - Expected resources & operations
for req in sample_reqs:
    cid = req['case_id']
    out = sample_outs[cid]
    steps = json.loads(out['steps_json'])
    print(f"[{cid}] status={out['deletion_status']:<11} rep_status={req['reported_status']:<18} audit_at={req['audit_at']}")
    for s in steps:
        print(f"   {s['phase']:<12} {s['system_id']:<20} {s['resource_id']:<20} {s['operation']:<26} {s['state']:<10} {s['evidence_id']}")
