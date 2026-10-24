import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
sample_reqs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_deletion_requests.csv'), encoding='utf-8'))}
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_output.csv'), encoding='utf-8'))}
evidence_files = {r['file_id']: r for r in csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'evidence_files.csv'), encoding='utf-8'))}

for cid, req in sample_reqs.items():
    out = sample_outs[cid]
    steps = json.loads(out['steps_json'])
    ev_ids = sorted(list(set(s['evidence_id'] for s in steps if s['evidence_id'])))
    ev_details = [f"{eid} ({evidence_files[eid]['captured_at']} | {os.path.basename(evidence_files[eid]['file_path'])})" for eid in ev_ids if eid in evidence_files]
    print(f"[{cid}] status={out['deletion_status']:<11} audit_at={req['audit_at']} | ev: {', '.join(ev_details)}")
