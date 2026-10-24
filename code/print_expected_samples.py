import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}

# Compare fields of all sample cases
for req in sample_reqs:
    cid = req['case_id']
    expected = sample_outs[cid]
    exp_status = expected['deletion_status']
    exp_steps = json.loads(expected['steps_json'])
    
    # Print summary of expected
    print(f"\n[{cid}] Expected status: {exp_status} (steps count: {len(exp_steps)})")
    for s in exp_steps:
        print(f"   step {s['step_no']}: phase={s['phase']} sys={s['system_id']} res={s['resource_id']} op={s['operation']} st={s['state']} ev={s['evidence_id']}")
