import os
import glob
import json
import sqlite3

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
EVIDENCE_DIR = os.path.join(REPO_ROOT, 'dataset', 'evidence')

print("=== Evidence Summary ===")
for root, dirs, files in os.walk(EVIDENCE_DIR):
    for f in files:
        p = os.path.join(root, f)
        rel = os.path.relpath(p, REPO_ROOT)
        size = os.path.getsize(p)
        print(f"{rel} ({size} bytes)")
