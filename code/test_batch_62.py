import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

all_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'deletion_requests.csv'), encoding='utf-8')))
manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}
identities = {r['email'].lower(): r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'user_identities.csv'), encoding='utf-8'))}

# Batch for 2026-01-29T12:00:00Z
batch_reqs = [r for r in all_reqs if r['audit_at'] == '2026-01-29T12:00:00Z']
print(f"Batch 2026-01-29T12:00:00Z has {len(batch_reqs)} cases:")
for r in batch_reqs:
    u = identities.get(r['email'].lower())
    print(f"  {r['case_id']} | email={r['email']} | uid={u['user_id'] if u else 'none'} | reported={r['reported_status']}")

p_62 = os.path.join(DATASET_DIR, manifest['evidence_62']['file_path'])
d62 = json.load(open(p_62, encoding='utf-8'))['service_exports']

print("\n--- Resources in evidence_62 ---")
for sname, sdata in d62.items():
    print(f"System: {sname}")
    for k, v in sdata.items():
        if isinstance(v, list):
            for item in v:
                print(f"   {item}")
