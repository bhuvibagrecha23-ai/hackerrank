import os
import json

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

p_92 = os.path.join(DATASET_DIR, 'evidence', 'records', 'service_resource_export_20260915_114455.json')
with open(p_92, 'r', encoding='utf-8') as f:
    d = json.load(f)

print("=== SERVICE_RESOURCE_EXPORT (evidence_92) ===")
for sname, sdata in d['service_exports'].items():
    print(f"\n[{sname}] keys: {list(sdata.keys())}")
    for k, v in sdata.items():
        if isinstance(v, list) and v:
            print(f"  {k} (count={len(v)}): sample={v[0]}")
        elif isinstance(v, dict):
            print(f"  {k}: dict keys={list(v.keys())[:3]}")

p_51 = os.path.join(DATASET_DIR, 'evidence', 'records', 'customer_data_snapshot_bundle_20260915.json')
with open(p_51, 'r', encoding='utf-8') as f:
    d51 = json.load(f)

print("\n=== CUSTOMER_DATA_SNAPSHOT_BUNDLE (evidence_51) ===")
print("Keys:", list(d51.keys()))
for k, v in d51.items():
    if isinstance(v, list) and v:
        print(f"[{k}] (count={len(v)}): sample={v[0]}")
    elif isinstance(v, dict):
        print(f"[{k}] dict keys: {list(v.keys())[:5]}")
