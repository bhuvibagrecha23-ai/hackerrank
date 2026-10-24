import os
import json
import csv

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
OUTPUT_PATH = os.path.join(REPO_ROOT, 'output.csv')

ALLOWED_OPERATIONS = {
    'FINDING': {
        'REPORT_REMAINING_RECORD': 'PRESENT',
        'REPORT_EXPOSED_PII': 'PRESENT',
        'REPORT_ACTIVE_DATA_FLOW': 'ACTIVE',
        'REPORT_RESTORE_RISK': 'ACTIVE',
    },
    'REMEDIATION': {
        'DISABLE_DATA_FLOW': 'DISABLED',
        'BLOCK_RESTORE': 'BLOCKED',
        'DELETE_RECORD': 'ABSENT',
        'REDACT_RECORD': 'REDACTED',
        'ANONYMIZE_RECORD': 'ANONYMIZED',
    },
    'VERIFICATION': {
        'VERIFY_RECORD_ABSENT': 'ABSENT',
        'VERIFY_RECORD_PRESENT': 'PRESENT',
        'VERIFY_RECORD_REDACTED': 'REDACTED',
        'VERIFY_RECORD_ANONYMIZED': 'ANONYMIZED',
        'VERIFY_DATA_FLOW_DISABLED': 'DISABLED',
        'VERIFY_RESTORE_BLOCKED': 'BLOCKED',
    }
}

ALLOWED_STATUSES = {'COMPLETE', 'INCOMPLETE', 'NOT_APPLICABLE'}

print("Verifying output.csv against all grading rules...")

with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Header: {reader.fieldnames}")
assert reader.fieldnames == ['case_id', 'deletion_status', 'steps_json'], f"Invalid header: {reader.fieldnames}"
print(f"Row count: {len(rows)} (expected: 518)")
assert len(rows) == 518, f"Row count is {len(rows)}, expected 518!"

# Check sorting
case_nums = [int(r['case_id'].split('_')[1]) for r in rows]
assert case_nums == sorted(case_nums), "Rows are not sorted by case_id!"
print("Sorting check: PASSED (cases sorted in ascending order)")

errors = []
status_counts = {}

for idx, r in enumerate(rows):
    cid = r['case_id']
    st = r['deletion_status']
    steps_raw = r['steps_json']
    status_counts[st] = status_counts.get(st, 0) + 1
    
    if st not in ALLOWED_STATUSES:
        errors.append(f"Row {idx} ({cid}): invalid status '{st}'")
        continue

    try:
        steps = json.loads(steps_raw)
    except Exception as e:
        errors.append(f"Row {idx} ({cid}): invalid JSON: {e}")
        continue

    if st == 'NOT_APPLICABLE':
        if steps != []:
            errors.append(f"Row {idx} ({cid}): NOT_APPLICABLE must have empty steps_json, got {len(steps)} steps")
        continue

    if not isinstance(steps, list):
        errors.append(f"Row {idx} ({cid}): steps_json is not an array")
        continue

    # Check step numbers and phases
    last_phase_val = 0
    phase_map = {'FINDING': 1, 'REMEDIATION': 2, 'VERIFICATION': 3}
    
    if st == 'COMPLETE':
        # Must only have VERIFICATION
        for s in steps:
            if s.get('phase') != 'VERIFICATION':
                errors.append(f"Row {idx} ({cid}): COMPLETE case has non-verification step {s}")

    for step_idx, s in enumerate(steps):
        expected_step_no = step_idx + 1
        if s.get('step_no') != expected_step_no:
            errors.append(f"Row {idx} ({cid}): step_no {s.get('step_no')} != expected {expected_step_no}")
        
        ph = s.get('phase')
        op = s.get('operation')
        state = s.get('state')
        ev = s.get('evidence_id')
        sys_id = s.get('system_id')
        res_id = s.get('resource_id')

        if ph not in phase_map:
            errors.append(f"Row {idx} ({cid}): unknown phase '{ph}'")
            continue

        ph_val = phase_map[ph]
        if ph_val < last_phase_val:
            errors.append(f"Row {idx} ({cid}): phase out of order at step {s['step_no']}")
        last_phase_val = ph_val

        # Check operation and state
        if op not in ALLOWED_OPERATIONS[ph]:
            errors.append(f"Row {idx} ({cid}): invalid op '{op}' for phase '{ph}'")
        elif state != ALLOWED_OPERATIONS[ph][op]:
            errors.append(f"Row {idx} ({cid}): invalid state '{state}' for op '{op}' (expected '{ALLOWED_OPERATIONS[ph][op]}')")

        # Check evidence ID
        if st == 'INCOMPLETE':
            if ph in ['REMEDIATION', 'VERIFICATION'] and ev != '':
                errors.append(f"Row {idx} ({cid}): INCOMPLETE {ph} step must have empty evidence_id, got '{ev}'")
            elif ph == 'FINDING' and not ev:
                errors.append(f"Row {idx} ({cid}): FINDING step must have non-empty evidence_id")
        elif st == 'COMPLETE':
            if not ev:
                errors.append(f"Row {idx} ({cid}): COMPLETE verification step must cite evidence_id")

if errors:
    print(f"Validation FAILED with {len(errors)} errors! First 10 errors:")
    for err in errors[:10]:
        print("  -", err)
else:
    print("ALL VALIDATION CHECKS PASSED PERFECTLY (100% compliant)!")
    print(f"Final status distribution: {status_counts}")
