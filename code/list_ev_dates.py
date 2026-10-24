import os
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
evs = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'evidence_files.csv'), encoding='utf-8')))
for e in sorted(evs, key=lambda x: x['captured_at'])[:35]:
    print(f"{e['captured_at']} | {e['file_id']:<12} | {e['origin']:<35} | {e['file_path']}")
