import os
import csv
from collections import defaultdict

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'deletion_requests.csv'), encoding='utf-8')))

batches = defaultdict(list)
for r in reqs:
    batches[r['audit_at']].append(r)

print(f"Total batches: {len(batches)}")
for b_time, b_reqs in sorted(batches.items())[:10]:
    print(f"Batch {b_time} ({len(b_reqs)} cases): {[r['case_id'] for r in b_reqs]}")
