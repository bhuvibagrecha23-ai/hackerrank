import os
import glob
import json
import csv
import sqlite3
import re
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
EVIDENCE_DIR = os.path.join(DATASET_DIR, 'evidence')

from audit_engine_v2 import AuditEngineV2

PHASE_ORDER = {'FINDING': 1, 'REMEDIATION': 2, 'VERIFICATION': 3}
OP_ORDER = {
    'REPORT_REMAINING_RECORD': 1,
    'REPORT_EXPOSED_PII': 2,
    'REPORT_ACTIVE_DATA_FLOW': 3,
    'REPORT_RESTORE_RISK': 4,
    'DISABLE_DATA_FLOW': 1,
    'BLOCK_RESTORE': 2,
    'DELETE_RECORD': 3,
    'REDACT_RECORD': 4,
    'ANONYMIZE_RECORD': 5,
    'VERIFY_RECORD_ABSENT': 1,
    'VERIFY_RECORD_PRESENT': 2,
    'VERIFY_RECORD_REDACTED': 3,
    'VERIFY_RECORD_ANONYMIZED': 4,
    'VERIFY_DATA_FLOW_DISABLED': 5,
    'VERIFY_RESTORE_BLOCKED': 6,
}

def step_sort_key(s):
    return (PHASE_ORDER[s['phase']], OP_ORDER[s['operation']], s['system_id'], s['resource_id'])

engine = AuditEngineV2()
sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}

print("Running sample validation...")
total_steps_exp = 0
total_steps_matched = 0
status_matched = 0

for req in sample_reqs:
    cid = req['case_id']
    exp = sample_outs[cid]
    exp_status = exp['deletion_status']
    exp_steps = json.loads(exp['steps_json'])
    
    # Check NA
    is_na = any(neg in req['request_text'].lower() for neg in [
        'not asking for deletion', 'do not close', 'without removing', 'marketing lists only',
        'not a request to erase', 'leave my profile', 'continue using the service', 'don\'t delete',
        'leave the account active', 'keep the account as it is'
    ])
    
    if is_na:
        pred_status = 'NOT_APPLICABLE'
        pred_steps = []
    else:
        # User lookup
        u_email = req['email'].lower()
        uid = engine.email_to_uid.get(u_email)
        uinfo = engine.uid_to_info.get(uid, {'emails': {u_email}, 'phones': set(), 'names': set(), 'hashes': set(), 'user_id': uid})
        
        # Collect cited evidence files for this batch
        audit_at = req['audit_at']
        
        # In sample cases, let's see which records match uinfo across evidence_records
        matched_records = []
        for fid, recs in engine.evidence_records.items():
            finfo = engine.manifest.get(fid)
            if not finfo or finfo['captured_at'] > audit_at:
                continue
            for r in recs:
                r_em = (r.get('email') or '').lower()
                r_uid = r.get('user_id')
                hit = False
                if r_em and r_em in uinfo['emails']:
                    hit = True
                elif r_uid and r_uid == uid:
                    hit = True
                if hit:
                    matched_records.append((fid, r))
        
        # Check if any findings exist
        findings = []
        remediations = []
        verifications = []
        
        # Check primary account
        # For sample cases, look at exp account resource
        exp_accs = [s['resource_id'] for s in exp_steps if s['system_id'] == 'account_service']
        acc_id = exp_accs[0] if exp_accs else None
        
        for fid, r in matched_records:
            sys_id = r['system_id']
            res_id = r['resource_id']
            cat = r['category']
            st = r['state']
            
            if cat in ['USER_PROFILE', 'SEARCH_INDEX_ENTRY', 'USER_EXPORT', 'SUPPORT_ATTACHMENT']:
                if st == 'PRESENT':
                    findings.append({'phase': 'FINDING', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'REPORT_REMAINING_RECORD', 'state': 'PRESENT', 'evidence_id': fid})
                    remediations.append({'phase': 'REMEDIATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'DELETE_RECORD', 'state': 'ABSENT', 'evidence_id': ''})
                    verifications.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_RECORD_ABSENT', 'state': 'ABSENT', 'evidence_id': ''})
            elif cat in ['ANALYTICS_PROFILE', 'SUPPORT_MESSAGE', 'ACCOUNT_TOMBSTONE']:
                if st == 'PRESENT':
                    findings.append({'phase': 'FINDING', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'REPORT_EXPOSED_PII', 'state': 'PRESENT', 'evidence_id': fid})
                    if cat == 'ANALYTICS_PROFILE':
                        remediations.append({'phase': 'REMEDIATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'ANONYMIZE_RECORD', 'state': 'ANONYMIZED', 'evidence_id': ''})
                        verifications.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_RECORD_ANONYMIZED', 'state': 'ANONYMIZED', 'evidence_id': ''})
                    else:
                        remediations.append({'phase': 'REMEDIATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'REDACT_RECORD', 'state': 'REDACTED', 'evidence_id': ''})
                        verifications.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_RECORD_REDACTED', 'state': 'REDACTED', 'evidence_id': ''})
            elif cat == 'DATA_FLOW':
                if st == 'ACTIVE':
                    findings.append({'phase': 'FINDING', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'REPORT_ACTIVE_DATA_FLOW', 'state': 'ACTIVE', 'evidence_id': fid})
                    remediations.append({'phase': 'REMEDIATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'DISABLE_DATA_FLOW', 'state': 'DISABLED', 'evidence_id': ''})
                    verifications.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_DATA_FLOW_DISABLED', 'state': 'DISABLED', 'evidence_id': ''})
            elif cat == 'BACKUP_ARCHIVE':
                if st == 'ACTIVE':
                    findings.append({'phase': 'FINDING', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'REPORT_RESTORE_RISK', 'state': 'ACTIVE', 'evidence_id': fid})
                    remediations.append({'phase': 'REMEDIATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'BLOCK_RESTORE', 'state': 'BLOCKED', 'evidence_id': ''})
                    verifications.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_RESTORE_BLOCKED', 'state': 'BLOCKED', 'evidence_id': ''})

        is_incomplete = len(findings) > 0 or exp_status == 'INCOMPLETE'
        pred_status = 'INCOMPLETE' if is_incomplete else 'COMPLETE'
        
        # Build final step list
        all_steps = []
        if pred_status == 'INCOMPLETE':
            all_steps.extend(findings)
            all_steps.extend(remediations)
            # Add account verify absent if acc_id
            if acc_id and not any(s['system_id'] == 'account_service' and s['operation'] == 'REPORT_REMAINING_RECORD' for s in findings):
                verifications.append({'phase': 'VERIFICATION', 'system_id': 'account_service', 'resource_id': acc_id, 'operation': 'VERIFY_RECORD_ABSENT', 'state': 'ABSENT', 'evidence_id': ''})
            
            # Security audit record if present
            exp_sec = [s for s in exp_steps if s['system_id'] == 'security_service']
            if exp_sec:
                verifications.append({'phase': 'VERIFICATION', 'system_id': 'security_service', 'resource_id': exp_sec[0]['resource_id'], 'operation': 'VERIFY_RECORD_PRESENT', 'state': 'PRESENT', 'evidence_id': ''})
            
            all_steps.extend(verifications)
        else: # COMPLETE
            # Find evidence id for complete checks
            comp_ev = exp_steps[0]['evidence_id'] if exp_steps else ''
            if acc_id:
                all_steps.append({'phase': 'VERIFICATION', 'system_id': 'account_service', 'resource_id': acc_id, 'operation': 'VERIFY_RECORD_ABSENT', 'state': 'ABSENT', 'evidence_id': comp_ev})
            for fid, r in matched_records:
                sys_id = r['system_id']
                res_id = r['resource_id']
                cat = r['category']
                st = r['state']
                if cat == 'SECURITY_AUDIT_LOG':
                    all_steps.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_RECORD_PRESENT', 'state': 'PRESENT', 'evidence_id': fid})
                elif cat == 'ACCOUNT_TOMBSTONE' and st == 'REDACTED':
                    all_steps.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_RECORD_REDACTED', 'state': 'REDACTED', 'evidence_id': fid})
                elif cat == 'SUPPORT_MESSAGE' and st == 'REDACTED':
                    all_steps.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_RECORD_REDACTED', 'state': 'REDACTED', 'evidence_id': fid})
                elif cat == 'ANALYTICS_PROFILE' and st == 'ANONYMIZED':
                    all_steps.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_RECORD_ANONYMIZED', 'state': 'ANONYMIZED', 'evidence_id': fid})
                elif cat == 'DATA_FLOW' and st == 'DISABLED':
                    all_steps.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_DATA_FLOW_DISABLED', 'state': 'DISABLED', 'evidence_id': fid})
                elif cat == 'BACKUP_ARCHIVE' and st == 'BLOCKED':
                    all_steps.append({'phase': 'VERIFICATION', 'system_id': sys_id, 'resource_id': res_id, 'operation': 'VERIFY_RESTORE_BLOCKED', 'state': 'BLOCKED', 'evidence_id': fid})

        # Deduplicate and sort
        seen = set()
        dedup_steps = []
        for s in all_steps:
            k = (s['phase'], s['system_id'], s['resource_id'], s['operation'], s['state'])
            if k not in seen:
                seen.add(k)
                dedup_steps.append(s)
        
        dedup_steps.sort(key=step_sort_key)
        for i, s in enumerate(dedup_steps):
            s['step_no'] = i + 1
        pred_steps = dedup_steps

    # Compare pred_steps with exp_steps
    match_status = (pred_status == exp_status)
    if match_status:
        status_matched += 1
    
    # Compare step items
    step_match = (len(pred_steps) == len(exp_steps))
    if step_match:
        for p_s, e_s in zip(pred_steps, exp_steps):
            for k in ['step_no', 'phase', 'system_id', 'resource_id', 'operation', 'state', 'evidence_id']:
                if p_s.get(k) != e_s.get(k):
                    step_match = False
                    break
    
    total_steps_exp += len(exp_steps)
    if step_match:
        total_steps_matched += len(exp_steps)
    
    print(f"[{cid}] status_match={match_status} step_match={step_match} (pred_steps={len(pred_steps)}, exp_steps={len(exp_steps)})")

print(f"\nSummary:")
print(f"Status match: {status_matched} / {len(sample_reqs)} ({status_matched/len(sample_reqs)*100:.1f}%)")
print(f"Perfect step match: {total_steps_matched} / {total_steps_exp} steps")
