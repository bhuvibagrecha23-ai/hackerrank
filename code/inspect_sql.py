import os
import glob
import sqlite3

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
sql_files = glob.glob(os.path.join(REPO_ROOT, 'dataset', 'evidence', 'databases', '*.sql'))

print(f"Total SQL files: {len(sql_files)}")
for p in sql_files:
    fname = os.path.basename(p)
    conn = sqlite3.connect(':memory:')
    try:
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            script = f.read()
        conn.executescript(script)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print(f"=== {fname} ===")
        for t in tables:
            tname = t[0]
            count = conn.execute(f"SELECT count(*) FROM {tname}").fetchone()[0]
            cols = [c[1] for c in conn.execute(f"PRAGMA table_info({tname})").fetchall()]
            print(f"  Table {tname} ({count} rows): {cols}")
    except Exception as e:
        print(f"Error in {fname}: {e}")
    finally:
        conn.close()
