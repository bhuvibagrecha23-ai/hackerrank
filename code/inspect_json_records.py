import os
import glob
import json

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
records_dir = os.path.join(REPO_ROOT, 'dataset', 'evidence', 'records')

for p in sorted(glob.glob(os.path.join(records_dir, '*.json'))):
    fname = os.path.basename(p)
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        keys = list(data.keys())
        counts = {k: len(v) if isinstance(v, (list, dict)) else type(v).__name__ for k, v in data.items()}
        print(f"=== {fname} (dict) ===")
        print(f"  Keys: {counts}")
    elif isinstance(data, list):
        print(f"=== {fname} (list of {len(data)}) ===")
        if data:
            print(f"  Sample item keys: {list(data[0].keys())}")
