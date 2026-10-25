import os
import sys
import json
import csv

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
sys.path.append(os.path.join(REPO_ROOT, 'code'))
from main import DeletionAuditEngine

def validate():
    engine = DeletionAuditEngine()
    sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
    sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}

    print("Running sample validation against dataset/sample_output.csv...")
    total_steps_exp = 0
    total_steps_matched = 0
    status_matched = 0

    for req in sample_reqs:
        cid = req['case_id']
        exp = sample_outs[cid]
        exp_status = exp['deletion_status']
        exp_steps = json.loads(exp['steps_json'])
        
        pred_status, pred_steps = engine.audit_case(req)
        
        if pred_status == exp_status:
            status_matched += 1
        
        total_steps_exp += len(exp_steps)
        if len(pred_steps) == len(exp_steps):
            for ps, es in zip(pred_steps, exp_steps):
                if all(ps.get(k) == es.get(k) for k in ['step_no', 'phase', 'system_id', 'resource_id', 'operation', 'state', 'evidence_id']):
                    total_steps_matched += 1

    print(f"\nSample Validation Results ({len(sample_reqs)} cases):")
    print(f"  Status Accuracy:     {status_matched} / {len(sample_reqs)} ({status_matched / len(sample_reqs) * 100:.1f}%)")
    print(f"  Exact Step Accuracy: {total_steps_matched} / {total_steps_exp} ({total_steps_matched / total_steps_exp * 100:.1f}%)")

if __name__ == '__main__':
    validate()
