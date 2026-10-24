import os
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}

for r in sample_reqs:
    cid = r['case_id']
    rep_st = r['reported_status']
    true_st = sample_outs[cid]['deletion_status']
    if rep_st != true_st:
        print(f"[{cid}] reported_status={rep_st:<18} true_status={true_st}")
