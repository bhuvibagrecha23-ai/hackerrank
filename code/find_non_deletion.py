import os
import csv
import json

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
reqs = []
with open(os.path.join(REPO_ROOT, 'dataset', 'deletion_requests.csv'), encoding='utf-8') as f:
    reqs = list(csv.DictReader(f))

# Let's search for words like 'export', 'download', 'access', 'rectif', 'correct', 'opt-out', 'marketing'
# and see if there are requests that ONLY ask for export/access/correction WITHOUT requesting deletion/erasure/close account.

patterns = []
for r in reqs:
    text = r['request_text']
    # Check if there is any mention of non-deletion
    lower = text.lower()
    is_deletion = False
    for word in ['delet', 'eras', 'clos', 'remov', 'supprim', 'elimin', 'lösch', 'entfern', 'cancell', 'exclus', 'exclu', '削除', '消去', '삭제', 'borrar']:
        if word in lower:
            is_deletion = True
            break
    if not is_deletion:
        patterns.append((r['case_id'], r['email'], text))

print(f"Non-deletion candidates count: {len(patterns)}")
for cid, em, txt in patterns:
    print(f"{cid} | {em} | {txt}")
