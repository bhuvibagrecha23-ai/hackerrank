import os
import json
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
sample_reqs = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_output.csv'), encoding='utf-8'))}
evs = {r['file_id']: r for r in csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'evidence_files.csv'), encoding='utf-8'))}

# For each sample, let's look at the cited evidence_id
for req in sample_reqs:
    cid = req['case_id']
    out = sample_outs[cid]
    audit_at = req['audit_at']
    steps = json.loads(out['steps_json'])
    cited_eids = list(set(s['evidence_id'] for s in steps if s['evidence_id']))
    for eid in cited_eids:
        c_at = evs[eid]['captured_at']
        diff = (datetime.fromisoformat(audit_at.replace('Z', '+00:00')) - datetime.fromisoformat(c_at.replace('Z', '+00:00'))).total_seconds()
        print(f"[{cid}] audit_at={audit_at} -> cited={eid} ({evs[eid]['origin']}, captured_at={c_at}, diff={diff/3600.0:.2f}h)")
