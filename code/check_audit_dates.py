import os
import csv
from collections import Counter

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
reqs = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'deletion_requests.csv'), encoding='utf-8')))
evs = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'evidence_files.csv'), encoding='utf-8')))

audit_dates = [r['audit_at'] for r in reqs]
print(f"Total requests: {len(reqs)}")
print("Unique audit_at values:", len(set(audit_dates)))
counter = Counter(audit_dates)
for at, cnt in counter.most_common(20):
    print(f"  {at}: {cnt} cases")
