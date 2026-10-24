import json
import csv
import os

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
sample_outs = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_output.csv'), encoding='utf-8')))

PHASE_ORDER = {'FINDING': 1, 'REMEDIATION': 2, 'VERIFICATION': 3}
OP_ORDER = {
    # Findings
    'REPORT_REMAINING_RECORD': 1,
    'REPORT_EXPOSED_PII': 2,
    'REPORT_ACTIVE_DATA_FLOW': 3,
    'REPORT_RESTORE_RISK': 4,
    # Remediation
    'DISABLE_DATA_FLOW': 1,
    'BLOCK_RESTORE': 2,
    'DELETE_RECORD': 3,
    'REDACT_RECORD': 4,
    'ANONYMIZE_RECORD': 5,
    # Verification
    'VERIFY_RECORD_ABSENT': 1,
    'VERIFY_RECORD_PRESENT': 2,
    'VERIFY_RECORD_REDACTED': 3,
    'VERIFY_RECORD_ANONYMIZED': 4,
    'VERIFY_DATA_FLOW_DISABLED': 5,
    'VERIFY_RESTORE_BLOCKED': 6,
}

def sort_key(step):
    p = PHASE_ORDER.get(step['phase'], 99)
    op = OP_ORDER.get(step['operation'], 99)
    sys_id = step.get('system_id', '')
    res_id = step.get('resource_id', '')
    return (p, op, sys_id, res_id)

mismatches = 0
for row in sample_outs:
    cid = row['case_id']
    steps = json.loads(row['steps_json'])
    sorted_steps = sorted(steps, key=sort_key)
    # Check if original order equals sorted order
    orig_tuples = [(s['phase'], s['operation'], s['system_id'], s['resource_id']) for s in steps]
    sorted_tuples = [(s['phase'], s['operation'], s['system_id'], s['resource_id']) for s in sorted_steps]
    if orig_tuples != sorted_tuples:
        mismatches += 1
        print(f"Mismatch in {cid}:")
        print("  Original:", orig_tuples)
        print("  Sorted:  ", sorted_tuples)

if mismatches == 0:
    print("PERFECT MATCH! All 32 sample cases follow this exact sorting key 100%!")
