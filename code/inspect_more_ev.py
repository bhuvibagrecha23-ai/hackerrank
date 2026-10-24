import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}

# 1. evidence_59 (customer_export_jobs)
p_59 = os.path.join(DATASET_DIR, manifest['evidence_59']['file_path'])
d59 = json.load(open(p_59, encoding='utf-8'))
print("=== evidence_59 ===")
for k, v in d59.items():
    if isinstance(v, list):
        print(k, len(v), v[0] if v else 'empty')
    else:
        print(k, v)

# 2. evidence_56 (customer_analytics_report)
p_56 = os.path.join(DATASET_DIR, manifest['evidence_56']['file_path'])
d56 = json.load(open(p_56, encoding='utf-8'))
print("\n=== evidence_56 ===")
for k, v in d56.items():
    if isinstance(v, list):
        print(k, len(v), v[0] if v else 'empty')
    else:
        print(k, v)

# 3. Check evidence_05 (read replica sql)
p_05 = os.path.join(DATASET_DIR, manifest['evidence_05']['file_path'])
print("\n=== evidence_05 ===")
import sqlite3
conn = sqlite3.connect(':memory:')
with open(p_05, 'r', encoding='utf-8') as f:
    conn.executescript(f.read())
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables in evidence_05:", tables)
for t in tables:
    cnt = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({t})").fetchall()]
    print(f"  {t} ({cnt} rows): cols={cols}")
    if cnt > 0:
        print(f"    sample={dict(zip(cols, conn.execute(f'SELECT * FROM {t} LIMIT 1').fetchone()))}")
