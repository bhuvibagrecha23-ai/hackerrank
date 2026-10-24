import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

sample_reqs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8'))}
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}
p_92 = os.path.join(DATASET_DIR, 'evidence', 'records', 'service_resource_export_20260915_114455.json')
d92 = json.load(open(p_92, encoding='utf-8'))['service_exports']

print("--- Inspecting evidence_92 resources vs cases 21-30 ---")
cases = [f'case_{i}' for i in range(21, 31)]
for cid in cases:
    req = sample_reqs[cid]
    out = sample_outs[cid]
    steps = json.loads(out['steps_json'])
    res_list = [f"{s['system_id']}:{s['resource_id']}" for s in steps]
    print(f"\n[{cid}] email={req['email']} status={out['deletion_status']}")
    print(f"   Steps: {res_list}")

print("\n--- Evidence_92 contents: ---")
for sys_name, sys_dict in d92.items():
    print(f"\nSystem: {sys_name}")
    for k, v in sys_dict.items():
        if isinstance(v, list):
            for item in v:
                print(f"  {item}")
