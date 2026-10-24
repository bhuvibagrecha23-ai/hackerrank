import os
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

accs = ['account_6440', 'account_3136', 'account_5684', 'account_3866', 'account_5482']
users = ['user_21', 'user_25', 'user_26', 'user_27', 'user_28']

print("--- Searching system_activity.csv for account IDs and users ---")
with open(os.path.join(DATASET_DIR, 'system_activity.csv'), 'r', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        for acc in accs:
            if acc in str(r.values()):
                print(f"Activity for {acc}: {r}")

print("\n--- Searching user_audit_log.csv ---")
with open(os.path.join(DATASET_DIR, 'user_audit_log.csv'), 'r', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        for acc in accs:
            if acc in str(r.values()):
                print(f"Audit log: {r}")
