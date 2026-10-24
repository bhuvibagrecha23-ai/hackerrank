import os
import glob
import json
import csv
import sqlite3

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
EVIDENCE_DIR = os.path.join(REPO_ROOT, 'dataset', 'evidence')

# Let's inspect customer_data_snapshot_bundle_*.json
bundles = sorted(glob.glob(os.path.join(EVIDENCE_DIR, 'records', 'customer_data_snapshot_bundle_*.json')))
print(f"Customer data snapshot bundles: {len(bundles)}")
if bundles:
    with open(bundles[0], 'r', encoding='utf-8') as f:
        b0 = json.load(f)
    print("Bundle 0 keys:", b0.keys())
    print("Bundle 0 snapshots count:", len(b0.get('snapshots', [])))
    for s in b0.get('snapshots', [])[:3]:
        print("  snap:", s.keys(), s.get('system_id'), s.get('collection'), len(s.get('records', [])))
        if s.get('records'):
            print("    sample record:", s['records'][0])
