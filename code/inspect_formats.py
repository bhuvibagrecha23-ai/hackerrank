import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}

def get_path(fid):
    return os.path.join(DATASET_DIR, manifest[fid]['file_path'])

# 1. Inspect evidence_92 (service_resource_export)
p_92 = get_path('evidence_92')
with open(p_92, 'r', encoding='utf-8') as f:
    d92 = json.load(f)
print("--- evidence_92 keys ---")
print(d92.keys())
for k in list(d92.keys())[:4]:
    print(f"Service {k}: length {len(d92[k])}, sample item: {d92[k][0] if d92[k] else None}")

# 2. Inspect evidence_51 (customer_data_snapshot_bundle)
p_51 = get_path('evidence_51')
with open(p_51, 'r', encoding='utf-8') as f:
    d51 = json.load(f)
print("\n--- evidence_51 keys ---")
print(d51.keys())
for k in list(d51.keys())[:4]:
    val = d51[k]
    if isinstance(val, list):
        print(f"Key {k}: length {len(val)}, sample item: {val[0] if val else None}")
    elif isinstance(val, dict):
        print(f"Key {k}: keys {list(val.keys())[:5]}")

# 3. Inspect evidence_94 (resource_lookup_trace log)
p_94 = get_path('evidence_94')
with open(p_94, 'r', encoding='utf-8') as f:
    lines94 = [f.readline() for _ in range(10)]
print("\n--- evidence_94 sample lines ---")
for l in lines94:
    print(l.strip())

# 4. Inspect evidence_54 (failover replica sql)
p_54 = get_path('evidence_54')
with open(p_54, 'r', encoding='utf-8') as f:
    lines54 = [f.readline() for _ in range(25)]
print("\n--- evidence_54 sample lines ---")
for l in lines54:
    if l.strip():
        print(l.strip()[:100])
