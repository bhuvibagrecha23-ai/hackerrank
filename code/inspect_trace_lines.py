import os

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

p_94 = os.path.join(DATASET_DIR, 'evidence', 'logs', 'resource_lookup_trace_20260926_103856.log')
with open(p_94, 'r', encoding='utf-8') as f:
    for line in f:
        # Check resources from case_03, case_18, case_20
        # case_03: account_7566, audit_record_2016, analytics_9406
        # case_18: search_6302, support_4887, data_flow_7495, account_5661, audit_record_5674
        # case_20: search_7455, analytics_9069, data_flow_6846, account_4911, audit_record_4894
        if any(res in line for res in ['account_7566', 'audit_record_2016', 'analytics_9406', 'search_6302', 'support_4887', 'data_flow_7495', 'account_5661', 'search_7455', 'analytics_9069', 'data_flow_6846', 'account_4911']):
            print(line.strip())
