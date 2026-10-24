import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}

# Check steps for cases 12, 15, 17, 19
ev01_cases = ['case_12', 'case_15', 'case_17', 'case_19']
for cid in ev01_cases:
    s = json.loads(sample_outs[cid]['steps_json'])
    print(f"\n[{cid}] Expected steps:")
    for step in s:
        print(f"  {step['system_id']} {step['resource_id']} {step['operation']} {step['state']} ev={step['evidence_id']}")

p_01 = os.path.join(DATASET_DIR, 'evidence', 'logs', 'service_events_ap_south_20260915.log')
with open(p_01, 'r', encoding='utf-8') as f:
    for line in f:
        if any(res in line for res in ['analytics_9914', 'data_flow_9846', 'support_9553', 'search_2352', 'search_6083']):
            print(f"Ev01 line: {line.strip()}")
