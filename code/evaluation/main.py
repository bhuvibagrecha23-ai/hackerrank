#!/usr/bin/env python3
"""
Evaluator for Northstar Shop Deletion Audit Agent
Computes case-level, step-level, sequence-exact, and field-level accuracy against ground truth.
Generates code/evaluation/sample_pred.csv for independent audit and tolerant evaluation.
Reproduces all published metrics across strict, holdout, and order-tolerant benchmarks.
"""

import os
import sys
import json
import csv
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(REPO_ROOT, 'code'))
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
OUTPUT_PATH = os.path.join(REPO_ROOT, 'output.csv')
SAMPLE_REQUESTS_PATH = os.path.join(DATASET_DIR, 'sample_deletion_requests.csv')
SAMPLE_OUTPUT_PATH = os.path.join(DATASET_DIR, 'sample_output.csv')
SAMPLE_PRED_PATH = os.path.join(REPO_ROOT, 'code', 'evaluation', 'sample_pred.csv')

FIELDS = ['step_no', 'phase', 'evidence_id', 'system_id', 'operation', 'state', 'resource_id']
TOLERANT_FIELDS = ('phase', 'system_id', 'resource_id', 'operation', 'state', 'evidence_id')
HOLDOUT_FROM = 25

def _case_num(cid):
    try:
        return int(cid.split('_')[1])
    except Exception:
        return 9999

def _lcs(a, b):
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[-1]))
        prev = cur
    return prev[-1]

def evaluate():
    print("=" * 76)
    print("Northstar Shop Deletion Audit Agent — Reproducible Benchmark Suite")
    print("=" * 76)
    if not os.path.exists(OUTPUT_PATH):
        print(f"Error: {OUTPUT_PATH} does not exist. Run python code/main.py first.")
        sys.exit(1)

    # 1. Evaluate Full Dataset Output Structure
    with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
        out_rows = list(csv.DictReader(f))

    print(f"\n1. Full Dataset Submission Contract (518 Cases):")
    print(f"  Total output rows:       {len(out_rows)} (expected: 518)")
    assert len(out_rows) == 518, f"Expected 518 rows, found {len(out_rows)}"

    status_counts = {}
    for r in out_rows:
        st = r['deletion_status']
        status_counts[st] = status_counts.get(st, 0) + 1
    print(f"  Status distribution:     {status_counts}")

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
        total_steps_pred = 0
        total_steps_matched = 0
        sequence_exact_cases = 0
        field_matches = {k: 0 for k in FIELDS}
        total_fields_truth = 0
        total_fields_matched = 0

        tune_seq_exact = 0
        tune_total_cases = 0
        hold_seq_exact = 0
        hold_total_cases = 0

        pred_rows = []
        per_case_tolerant = {}

        for req in sample_reqs:
            cid = req['case_id']
            cnum = _case_num(cid)
            truth = sample_truth[cid]
            pred_status, pred_steps = engine.audit_case(req)
            pred_rows.append({
                'case_id': cid,
                'deletion_status': pred_status,
                'steps_json': json.dumps(pred_steps)
            })

            if pred_status == truth['deletion_status']:
                status_correct += 1
            
            t_steps = json.loads(truth['steps_json'])
            total_steps_truth += len(t_steps)
            total_steps_pred += len(pred_steps)
            total_fields_truth += len(t_steps) * len(FIELDS)

            case_seq_match = (pred_status == truth['deletion_status'] and len(t_steps) == len(pred_steps))
            if len(t_steps) == len(pred_steps):
                for ts, ps in zip(t_steps, pred_steps):
                    step_match = True
                    for k in FIELDS:
                        if ts.get(k) == ps.get(k):
                            total_fields_matched += 1
                            field_matches[k] += 1
                        else:
                            step_match = False
                    if step_match:
                        total_steps_matched += 1
                    else:
                        case_seq_match = False
            else:
                case_seq_match = False

            if case_seq_match:
                sequence_exact_cases += 1
                if cnum < HOLDOUT_FROM:
                    tune_seq_exact += 1
                else:
                    hold_seq_exact += 1

            if cnum < HOLDOUT_FROM:
                tune_total_cases += 1
            else:
                hold_total_cases += 1

            # Tolerant calculation for this case
            g_tuples = [tuple(str(s.get(k, "")) for k in TOLERANT_FIELDS) for s in t_steps]
            p_tuples = [tuple(str(s.get(k, "")) for k in TOLERANT_FIELDS) for s in pred_steps]
            inter = sum((Counter(g_tuples) & Counter(p_tuples)).values())
            per_case_tolerant[cid] = {
                "inter": inter,
                "gold": len(g_tuples),
                "pred": len(p_tuples),
                "lcs": _lcs(p_tuples, g_tuples),
                "max": max(len(p_tuples), len(g_tuples))
            }

        # Write sample_pred.csv for independent auditability
        with open(SAMPLE_PRED_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['case_id', 'deletion_status', 'steps_json'])
            writer.writeheader()
            writer.writerows(pred_rows)

        recall = total_steps_matched / total_steps_truth if total_steps_truth else 1.0
        precision = total_steps_matched / total_steps_pred if total_steps_pred else 1.0

        print(f"\n2. Strict Index-Aligned Benchmark (32 Labeled Cases):")
        print(f"  Case Status Accuracy:    {status_correct} / {len(sample_reqs)} ({status_correct / len(sample_reqs) * 100:.1f}%)")
        print(f"  Sequence-Exact Accuracy: {sequence_exact_cases} / {len(sample_reqs)} ({sequence_exact_cases / len(sample_reqs) * 100:.1f}%)")
        print(f"  Step Match Recall:       {total_steps_matched} / {total_steps_truth} ({recall * 100:.1f}%)")
        print(f"  Step Match Precision:    {total_steps_matched} / {total_steps_pred} ({precision * 100:.1f}%)")
        print(f"  Total Fields Matched:    {total_fields_matched} / {total_fields_truth} ({total_fields_matched / total_fields_truth * 100:.1f}%)")

        print(f"\n3. Field-Level Accuracy Breakdown (7 Required Fields across 193 Steps):")
        print(f"  {'Field Name':<16} | {'Target Steps':<12} | {'Matched Count':<14} | {'Accuracy':<10}")
        print(f"  {'-'*16}-+-{'-'*12}-+-{'-'*14}-+-{'-'*10}")
        for k in FIELDS:
            acc = (field_matches[k] / total_steps_truth * 100) if total_steps_truth else 100.0
            print(f"  {k:<16} | {total_steps_truth:<12} | {field_matches[k]:<14} | {acc:>8.1f}%")
        print(f"  {'-'*16}-+-{'-'*12}-+-{'-'*14}-+-{'-'*10}")
        print(f"  {'TOTAL':<16} | {total_fields_truth:<12} | {total_fields_matched:<14} | {total_fields_matched / total_fields_truth * 100:>8.1f}%")

        print(f"\n4. Dataset Splits:")
        print(f"  Tune Set (Cases 1-24):   {tune_seq_exact} / {tune_total_cases} ({tune_seq_exact / tune_total_cases * 100:.1f}%) sequence exact")
        print(f"  Holdout Set (Cases 25-32):{hold_seq_exact} / {hold_total_cases} ({hold_seq_exact / hold_total_cases * 100:.1f}%) sequence exact")

        # Tolerant Aggregations
        def _agg_tolerant(case_ids):
            inter = sum(per_case_tolerant[c]["inter"] for c in case_ids)
            g = sum(per_case_tolerant[c]["gold"] for c in case_ids)
            p = sum(per_case_tolerant[c]["pred"] for c in case_ids)
            lcs = sum(per_case_tolerant[c]["lcs"] for c in case_ids)
            mx = sum(per_case_tolerant[c]["max"] for c in case_ids)
            prec = inter / p if p else 1.0
            rec = inter / g if g else 1.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
            return len(case_ids), prec, rec, f1, lcs / mx if mx else 1.0

        all_ids = sorted(per_case_tolerant.keys(), key=_case_num)
        tune_ids = [c for c in all_ids if _case_num(c) < HOLDOUT_FROM]
        hold_ids = [c for c in all_ids if _case_num(c) >= HOLDOUT_FROM]

        print(f"\n5. Order-Tolerant Multiset & LCS Benchmark:")
        for name, ids in [("ALL (Cases 1-32)", all_ids), ("TUNE (Cases 1-24)", tune_ids), ("HOLD (Cases 25-32)", hold_ids)]:
            n, p, r, f1, lcs = _agg_tolerant(ids)
            print(f"  {name:<20}: Precision={p*100:.1f}%  Recall={r*100:.1f}%  F1={f1*100:.1f}%  LCS={lcs*100:.1f}%")

        print(f"\nSaved sample predictions to {SAMPLE_PRED_PATH}")
        print("=" * 76)

if __name__ == '__main__':
    evaluate()
