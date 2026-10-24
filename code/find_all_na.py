import os
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
reqs = []
with open(os.path.join(REPO_ROOT, 'dataset', 'deletion_requests.csv'), encoding='utf-8') as f:
    reqs = list(csv.DictReader(f))

for i, r in enumerate(reqs):
    t = r['request_text'].lower()
    # Check if text does NOT contain any deletion intent, or explicitly says not to delete / keep
    if any(neg in t for neg in ['not asking for deletion', 'do not close', 'without removing', 'marketing lists only', 'not a request to erase', 'leave my profile', 'continue using the service', 'don\'t delete', 'leave the account active', 'keep the account as it is']):
        print(f"Index {i} | {r['case_id']}: {r['request_text']}")
