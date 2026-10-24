import os
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

accs = ['analytics_1895', 'analytics_4566', 'analytics_4574', 'analytics_6077', 'analytics_5335']
with open(os.path.join(DATASET_DIR, 'system_activity.csv'), 'r', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        if r['resource_id'] in accs:
            print(f"{r['event_time']} | {r['resource_id']} | {r['event_type']} | {r['details']}")
