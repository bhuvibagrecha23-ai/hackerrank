#!/usr/bin/env python3
"""
Evaluator for Northstar Shop Deletion Audit Agent
Computes case-level, step-level, and sequence accuracy against ground truth.
"""

import os
import sys
import json
import csv

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(REPO_ROOT, 'code'))
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
OUTPUT_PATH = os.path.join(REPO_ROOT, 'output.csv')
SAMPLE_REQUESTS_PATH = os.path.join(DATASET_DIR, 'sample_deletion_requests.csv')
SAMPLE_OUTPUT_PATH = os.path.join(DATASET_DIR, 'sample_output.csv')

def evaluate():
    print("Evaluating Northstar Shop Deletion Audit Agent...")
    if not os.path.exists(OUTPUT_PATH):
        print(f"Error: {OUTPUT_PATH} does not exist. Run python code/main.py first.")
        sys.exit(1)

    # 1. Evaluate Output Structure
    with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
        out_rows = list(csv.DictReader(f))

    print(f"Total rows in output.csv: {len(out_rows)}")
    assert len(out_rows) == 518, f"Expected 518 rows, found {len(out_rows)}"

    status_counts = {}
    for r in out_rows:
        st = r['deletion_status']
        status_counts[st] = status_counts.get(st, 0) + 1
    print(f"Full Dataset Status distribution: {status_counts}")

    # 2. Run engine on sample ground truth
    if os.path.exists(SAMPLE_OUTPUT_PATH) and os.path.exists(SAMPLE_REQUESTS_PATH):
        import importlib.util
        spec = importlib.util.spec_from_file_location("code_main", os.path.join(REPO_ROOT, 'code', 'main.py'))
        code_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(code_main)
        engine = code_main.DeletionAuditEngine()
        
        with open(SAMPLE_REQUESTS_PATH, 'r', encoding='utf-8') as f:
            sample_reqs = list(csv.DictReader(f))
        with open(SAMPLE_OUTPUT_PATH, 'r', encoding='utf-8') as f:
            sample_truth = {r['case_id']: r for r in csv.DictReader(f)}

        status_correct = 0
        total_steps_truth = 0
        total_steps_matched = 0

        for req in sample_reqs:
            cid = req['case_id']
            truth = sample_truth[cid]
            pred_status, pred_steps = engine.audit_case(req)
            if pred_status == truth['deletion_status']:
                status_correct += 1
            
            t_steps = json.loads(truth['steps_json'])
            total_steps_truth += len(t_steps)
            if len(t_steps) == len(pred_steps):
                for ts, ps in zip(t_steps, pred_steps):
                    if all(ts.get(k) == ps.get(k) for k in ['step_no', 'phase', 'system_id', 'resource_id', 'operation', 'state', 'evidence_id']):
                        total_steps_matched += 1

        print(f"\nGround Truth Sample Evaluation ({len(sample_reqs)} cases):")
        print(f"  Case Status Accuracy: {status_correct} / {len(sample_reqs)} ({status_correct / len(sample_reqs) * 100:.1f}%)")
        print(f"  Step Match Accuracy:  {total_steps_matched} / {total_steps_truth} ({total_steps_matched / total_steps_truth * 100:.1f}%)")

if __name__ == '__main__':
    evaluate()
