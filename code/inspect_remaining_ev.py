import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}

# 1. evidence_59 (customer_export_jobs_20260914.json)
p_59 = os.path.join(DATASET_DIR, manifest['evidence_59']['file_path'])
print("--- evidence_59 ---")
with open(p_59, 'r', encoding='utf-8') as f:
    d59 = json.load(f)
    print("type:", type(d59), "sample:", d59[0] if isinstance(d59, list) else list(d59.items())[:2])

# 2. evidence_56 (customer_analytics_report_20260907.json)
p_56 = os.path.join(DATASET_DIR, manifest['evidence_56']['file_path'])
print("\n--- evidence_56 ---")
with open(p_56, 'r', encoding='utf-8') as f:
    d56 = json.load(f)
    print("type:", type(d56), "sample:", d56[0] if isinstance(d56, list) else list(d56.items())[:2])

# 3. evidence_61 (support_replica.log)
p_61 = os.path.join(DATASET_DIR, manifest['evidence_61']['file_path'])
print("\n--- evidence_61 lines ---")
with open(p_61, 'r', encoding='utf-8') as f:
    for _ in range(5):
        print(f.readline().strip())

# 4. evidence_01 (service_events_ap_south_20260915.log)
p_01 = os.path.join(DATASET_DIR, manifest['evidence_01']['file_path'])
print("\n--- evidence_01 lines ---")
with open(p_01, 'r', encoding='utf-8') as f:
    for _ in range(5):
        print(f.readline().strip())
