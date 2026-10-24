import os
import sqlite3

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

def inspect_sql(sql_path):
    print(f"\n=== Inspecting {os.path.basename(sql_path)} ===")
    conn = sqlite3.connect(':memory:')
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn.executescript(sql)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("Tables:", tables)
    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({t})").fetchall()]
        print(f"  Table {t} ({count} rows): cols={cols}")
        if count > 0:
            sample = conn.execute(f"SELECT * FROM {t} LIMIT 1").fetchone()
            print(f"    sample={dict(zip(cols, sample))}")

p_93 = os.path.join(DATASET_DIR, 'evidence', 'databases', 'customer_data_inventory_20260916.sql')
inspect_sql(p_93)

p_54 = os.path.join(DATASET_DIR, 'evidence', 'databases', 'customer_accounts_failover_replica_20260902.sql')
inspect_sql(p_54)
