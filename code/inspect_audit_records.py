import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}

# For every sample case that has an audit_record_ in its steps:
# print case_id, audit_record_id, evidence_id
for req in sample_reqs:
    cid = req['case_id']
    steps = json.loads(sample_outs[cid]['steps_json'])
    audit_steps = [s for s in steps if s['system_id'] == 'security_service']
    if audit_steps:
        for s in audit_steps:
            print(f"[{cid}] status={sample_outs[cid]['deletion_status']} res={s['resource_id']} op={s['operation']} ev={s['evidence_id']}")
