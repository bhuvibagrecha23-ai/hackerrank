import os
import glob
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
EVIDENCE_DIR = os.path.join(DATASET_DIR, 'evidence')
ev_manifest = {r['file_path']: r['file_id'] for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}

# Let's inspect all service_resource_export files
for p in sorted(glob.glob(os.path.join(EVIDENCE_DIR, 'records', 'service_resource_export_*.json'))):
    rel = os.path.relpath(p, DATASET_DIR).replace('\\', '/')
    fid = ev_manifest.get(rel)
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(f"File {fid} ({rel}): services = {list(d.get('service_exports', {}).keys())}")
