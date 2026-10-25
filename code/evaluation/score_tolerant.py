#!/usr/bin/env python3
"""
Tolerant Scorer for Ghost Data Still Exists Deletion Audit Agent.
Evaluates order-tolerant set-based multiset overlap and LCS (Longest Common Subsequence).
Provides dual evaluation alongside strict index-exact alignment.

Run:
    python code/evaluation/score_tolerant.py [prediction_csv]
"""

import os
import sys
import csv
import json
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLD_PATH = REPO_ROOT / "dataset" / "sample_output.csv"
FIELDS = ("phase", "system_id", "resource_id", "operation", "state", "evidence_id")
HOLDOUT_FROM = 25

def _case_num(cid):
    try:
        return int(cid.split("_")[1])
    except Exception:
        return 9999

def _load(path):
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            steps = json.loads(r["steps_json"]) if r["steps_json"].strip() else []
            rows[r["case_id"]] = [tuple(str(s.get(k, "")) for k in FIELDS) for s in steps]
    return rows

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

def score(pred_path=None):
    gold = _load(GOLD_PATH)
    if pred_path and Path(pred_path).exists():
        pred = _load(pred_path)
    else:
        # Run live engine if no separate sample pred CSV provided
        import importlib.util
        spec = importlib.util.spec_from_file_location("code_main", REPO_ROOT / "code" / "main.py")
        code_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(code_main)
        engine = code_main.DeletionAuditEngine()
        sample_reqs_path = REPO_ROOT / "dataset" / "sample_deletion_requests.csv"
        pred = {}
        with open(sample_reqs_path, "r", encoding="utf-8") as f:
            for req in csv.DictReader(f):
                st, steps = engine.audit_case(req)
                pred[req["case_id"]] = [tuple(str(s.get(k, "")) for k in FIELDS) for s in steps]

    per_case = {}
    for cid, g in gold.items():
        p = pred.get(cid, [])
        inter = sum((Counter(g) & Counter(p)).values())
        per_case[cid] = {
            "inter": inter,
            "gold": len(g),
            "pred": len(p),
            "lcs": _lcs(p, g),
            "max": max(len(p), len(g))
        }
    return per_case

def _agg(per_case, case_ids):
    if not case_ids:
        return None
    inter = sum(per_case[c]["inter"] for c in case_ids)
    g = sum(per_case[c]["gold"] for c in case_ids)
    p = sum(per_case[c]["pred"] for c in case_ids)
    lcs = sum(per_case[c]["lcs"] for c in case_ids)
    mx = sum(per_case[c]["max"] for c in case_ids)
    prec = inter / p if p else 1.0
    rec = inter / g if g else 1.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {
        "n": len(case_ids),
        "set_prec": prec,
        "set_recall": rec,
        "f1": f1,
        "lcs_seq": lcs / mx if mx else 1.0
    }

def _print_block(name, a):
    if not a:
        print(f"  {name}: (no cases)")
        return
    print(f"  {name} (n={a['n']}): set_prec={a['set_prec']:.1%}  set_recall={a['set_recall']:.1%}  F1={a['f1']:.1%}  lcs_seq={a['lcs_seq']:.1%}")

def main():
    pred_path = sys.argv[1] if len(sys.argv) > 1 else None
    per_case = score(pred_path)
    ids = sorted(per_case, key=_case_num)
    tune = [c for c in ids if _case_num(c) < HOLDOUT_FROM]
    hold = [c for c in ids if _case_num(c) >= HOLDOUT_FROM]

    print(f"Tolerant Scoring vs {GOLD_PATH.name}")
    print("=" * 72)
    _print_block("ALL  ", _agg(per_case, ids))
    _print_block("TUNE ", _agg(per_case, tune))
    _print_block("HOLD ", _agg(per_case, hold))
    return 0

if __name__ == "__main__":
    sys.exit(main())
