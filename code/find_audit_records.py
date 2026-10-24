import os
import glob

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

audit_ids = [
    'audit_record_2016', 'audit_record_4902', 'audit_record_9394', 'audit_record_2945',
    'audit_record_4816', 'audit_record_987', 'audit_record_1596', 'audit_record_9528',
    'audit_record_1797', 'audit_record_6645', 'audit_record_6793', 'audit_record_5569',
    'audit_record_3737', 'audit_record_3482', 'audit_record_4128', 'audit_record_7095',
    'audit_record_451', 'audit_record_5416', 'audit_record_3830', 'audit_record_9265',
    'audit_record_3954', 'audit_record_1707', 'audit_record_6909', 'audit_record_7068'
]

# Search in all dataset files
found = {}
for aid in audit_ids:
    found[aid] = []

for root, dirs, files in os.walk(DATASET_DIR):
    for f in files:
        if f.endswith(('.csv', '.json', '.sql', '.log', '.txt')):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
                for aid in audit_ids:
                    if aid in content:
                        found[aid].append(os.path.relpath(p, DATASET_DIR))

for aid, paths in found.items():
    print(f"{aid:<20} -> {paths}")
