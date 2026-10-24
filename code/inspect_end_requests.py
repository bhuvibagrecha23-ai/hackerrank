import os
import csv
from collections import Counter

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
reqs = []
with open(os.path.join(REPO_ROOT, 'dataset', 'deletion_requests.csv'), encoding='utf-8') as f:
    reqs = list(csv.DictReader(f))

# Let's inspect the last 50 cases (500 to 550)
for r in reqs[-40:]:
    print(f"[{r['case_id']}] {r['email']} | {r['reported_status']} | {r['request_text']}")
