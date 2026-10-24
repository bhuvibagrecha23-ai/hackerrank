import os
import csv
import re

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
reqs = []
with open(os.path.join(REPO_ROOT, 'dataset', 'deletion_requests.csv'), encoding='utf-8') as f:
    reqs = list(csv.DictReader(f))

print(f"Total requests: {len(reqs)}")

# Let's inspect diverse request texts
non_deletion_keywords = [
    'access', 'export', 'download', 'copy', 'rectify', 'correct', 'update', 'opt-out', 'marketing', 'unsubscribe',
    'newsletter', 'preference', 'portability', 'object', 'restrict'
]

deletion_keywords = [
    'delete', 'remove', 'erase', 'erasure', 'forget', 'close', 'supprimer', 'suppression', 'eliminar', 'eliminaci',
    'löschen', 'entfernen', 'cancellare', '削除', '消去', '삭제', 'borrar'
]

suspect_non_deletion = []
for r in reqs:
    text = r['request_text'].lower()
    # Check if text does NOT contain any deletion keyword
    has_del = any(dk in text for dk in deletion_keywords)
    if not has_del:
        suspect_non_deletion.append(r)

print(f"Requests without obvious deletion keywords: {len(suspect_non_deletion)}")
for r in suspect_non_deletion[:20]:
    print(f"[{r['case_id']}] {r['email']}: {r['request_text']}")
