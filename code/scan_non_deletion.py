import os
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
reqs = []
with open(os.path.join(REPO_ROOT, 'dataset', 'deletion_requests.csv'), encoding='utf-8') as f:
    reqs = list(csv.DictReader(f))

# Let's inspect requests that might be non-deletion:
# 1. requests that contain 'keep the account', 'leave the account', 'continue using', 'active', 'portable format', 'invoices', 'opt-out', 'marketing', 'newsletter'
suspicious = []
for r in reqs:
    t = r['request_text'].lower()
    if any(phrase in t for phrase in [
        'leave the account', 'keep the account', 'continue using', 'leave my profile', 'leave my account',
        'do not delete', 'don\'t delete', 'portable format', 'copy of last year', 'replace it with the new one',
        'just want to update', 'only want to update', 'opt out of marketing', 'marketing emails', 'newsletter'
    ]):
        suspicious.append((r['case_id'], r['email'], r['request_text']))

print(f"Suspicious non-deletion count: {len(suspicious)}")
for cid, em, txt in suspicious:
    print(f"{cid} | {em} | {txt}")
