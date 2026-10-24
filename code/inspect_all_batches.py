import os
import csv
from collections import defaultdict

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'deletion_requests.csv'), encoding='utf-8')))
manifest = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8')))

batches = defaultdict(list)
for r in reqs:
    batches[r['audit_at']].append(r)

print(f"Total batches in deletion_requests.csv: {len(batches)}")

# Check for each batch what evidence files are available at or right before audit_at
for audit_at in sorted(batches.keys()):
    b_reqs = batches[audit_at]
    ev_candidates = [e for e in manifest if e['captured_at'] <= audit_at]
    ev_candidates.sort(key=lambda x: x['captured_at'], reverse=True)
    closest = ev_candidates[0] if ev_candidates else None
    closest_2 = ev_candidates[1] if len(ev_candidates) > 1 else None
    print(f"Audit {audit_at} ({len(b_reqs)} cases): closest={closest['file_id']} ({closest['captured_at']}, {os.path.basename(closest['file_path'])})")
