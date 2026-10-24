#!/usr/bin/env python3
"""
Northstar Shop Deletion Audit Agent
Challenge: Ghost Data Still Exists (HackerRank Orchestrate, October 2026)
"""

import os
import sys
import json
import csv
import sqlite3
import re
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
EVIDENCE_DIR = os.path.join(DATASET_DIR, 'evidence')
OUTPUT_PATH = os.path.join(REPO_ROOT, 'output.csv')

# Phase and Operation Sort Order according to Problem Statement
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
    return (
        PHASE_ORDER.get(s['phase'], 99),
        OP_ORDER.get(s['operation'], 99),
        s['system_id'],
        s['resource_id']
    )

class DeletionAuditEngine:
    def __init__(self):
        print("Initializing Deletion Audit Engine...")
        self.manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}
        self.identities = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_identities.csv'), encoding='utf-8')))
        self.audit_log = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_audit_log.csv'), encoding='utf-8')))
        self.system_activity = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'system_activity.csv'), encoding='utf-8')))
        
        self._build_identities()
        self._load_all_evidence_records()
        self._index_system_activities()
        print(f"Engine ready. Parsed {len(self.evidence_records)} evidence files and {len(self.system_activity)} activities.")

    def _build_identities(self):
        self.email_to_uid = {}
        for u in self.identities:
            self.email_to_uid[u['email'].lower()] = u['user_id']
        for a in self.audit_log:
            if a['field_name'] == 'email':
                self.email_to_uid[a['old_value'].lower()] = a['user_id']
                self.email_to_uid[a['new_value'].lower()] = a['user_id']

        self.uid_to_info = {}
        for u in self.identities:
            uid = u['user_id']
            self.uid_to_info[uid] = {
                'user_id': uid,
                'emails': {u['email'].lower()},
                'phones': {u['phone']},
                'names': {u['name']},
                'hashes': {u['email_hash']}
            }
        for a in self.audit_log:
            uid = a['user_id']
            if uid in self.uid_to_info:
                f = a['field_name']
                if f == 'email':
                    self.uid_to_info[uid]['emails'].add(a['old_value'].lower())
                    self.uid_to_info[uid]['emails'].add(a['new_value'].lower())
                elif f == 'phone':
                    self.uid_to_info[uid]['phones'].add(a['old_value'])
                    self.uid_to_info[uid]['phones'].add(a['new_value'])
                elif f == 'name':
                    self.uid_to_info[uid]['names'].add(a['old_value'])
                    self.uid_to_info[uid]['names'].add(a['new_value'])

    def _index_system_activities(self):
        # Index activities by resource_id and by time window
        self.activity_by_res = {}
        for a in self.system_activity:
            res = a['resource_id']
            if res:
                if res not in self.activity_by_res:
                    self.activity_by_res[res] = []
                self.activity_by_res[res].append(a)

    def _load_all_evidence_records(self):
        self.evidence_records = {} # fid -> list of parsed records
        
        # 1. Structured transcription of 11 PNG images
        self.evidence_records['evidence_04'] = [
            {'system_id': 'account_service', 'resource_id': 'account_5762', 'user_id': 'user_11', 'email': 'haruka.s1838@zoho.com', 'category': 'USER_PROFILE', 'state': 'PRESENT'},
            {'system_id': 'support_platform', 'resource_id': 'support_9538', 'user_id': 'user_11', 'email': 'haruka.s1838@zoho.com', 'category': 'SUPPORT_MESSAGE', 'state': 'PRESENT'}
        ]
        self.evidence_records['evidence_09'] = [
            {'system_id': 'search_service', 'resource_id': 'search_428', 'user_id': 'user_13', 'email': 'g.silva76@gmail.com', 'category': 'SEARCH_INDEX_ENTRY', 'state': 'PRESENT'}
        ]
        self.evidence_records['evidence_14'] = [
            {'system_id': 'integration_service', 'resource_id': 'data_flow_1121', 'email': 'jain.aditi@gmail.com', 'category': 'DATA_FLOW', 'state': 'ACTIVE'},
            {'system_id': 'integration_service', 'resource_id': 'data_flow_9846', 'email': 'lucia-torres@gmail.com', 'category': 'DATA_FLOW', 'state': 'ACTIVE'}
        ]
        self.evidence_records['evidence_18'] = [
            {'system_id': 'analytics_platform', 'resource_id': 'analytics_7438', 'user_id': 'user_20', 'email': 'darwish.omar@icloud.com', 'category': 'ANALYTICS_PROFILE', 'state': 'PRESENT'}
        ]
        self.evidence_records['evidence_23'] = [
            {'system_id': 'export_service', 'resource_id': 'export_1260', 'email': 'ingrid.dahl@outlook.com', 'category': 'USER_EXPORT', 'state': 'PRESENT'}
        ]
        self.evidence_records['evidence_28'] = [
            {'system_id': 'support_platform', 'resource_id': 'support_1034', 'email': 'kagyeman8947@fastmail.com', 'category': 'SUPPORT_MESSAGE', 'state': 'PRESENT'}
        ]
        self.evidence_records['evidence_32'] = [
            {'system_id': 'backup_service', 'resource_id': 'backup_9287', 'email': 'areed1433@gmail.com', 'category': 'BACKUP_ARCHIVE', 'state': 'ACTIVE'}
        ]
        self.evidence_records['evidence_42'] = [
            {'system_id': 'identity_service', 'resource_id': 'tombstone_user_17', 'user_id': 'user_17', 'category': 'ACCOUNT_TOMBSTONE', 'state': 'REDACTED'}
        ]
        self.evidence_records['evidence_46'] = [
            {'system_id': 'support_platform', 'resource_id': 'delivery_confirmation_19.pdf', 'category': 'SUPPORT_ATTACHMENT', 'state': 'PRESENT', 'email': 'priya.raman@gmail.com'}
        ]
        self.evidence_records['evidence_84'] = [
            {'system_id': 'marketing_service', 'resource_id': 'marketing_001', 'email': 'sj.park@naver.com', 'category': 'MARKETING_PROFILE', 'state': 'PRESENT'}
        ]
        self.evidence_records['evidence_90'] = [
            {'system_id': 'security_service', 'resource_id': 'audit_record_003', 'user_id': 'user_03', 'category': 'SECURITY_AUDIT_LOG', 'state': 'PRESENT'}
        ]

        # 2. Structured transcription of PDFs
        self.evidence_records['evidence_58'] = [
            {'system_id': 'support_platform', 'resource_id': 'support_001', 'category': 'SUPPORT_ATTACHMENT', 'state': 'PRESENT', 'email': 'priya.raman@gmail.com', 'phone': '+91 98765 73142'}
        ]
        self.evidence_records['evidence_91'] = [
            {'system_id': 'security_service', 'resource_id': 'audit_record_003', 'category': 'SECURITY_AUDIT_LOG', 'state': 'PRESENT', 'user_id': 'user_03'}
        ]

        # 3. TXT handover
        p_txt = os.path.join(EVIDENCE_DIR, 'records', 'customer_account_handover_20261001.txt')
        if os.path.exists(p_txt):
            recs = []
            with open(p_txt, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line.startswith('- '):
                        continue
                    parts = [p.strip() for p in line[2:].split('|')]
                    if len(parts) >= 6:
                        ts, sys_id, res_id, cat, res_state, subj = parts[:6]
                        st = res_state
                        if cat == 'USER_PROFILE':
                            st = 'ABSENT' if res_state == 'NOT_FOUND' else 'PRESENT'
                        elif cat == 'ANALYTICS_PROFILE':
                            st = 'ANONYMIZED' if 'ANONYMIZED' in res_state else 'PRESENT'
                        elif cat == 'SEARCH_INDEX_ENTRY':
                            st = 'ABSENT' if res_state == 'NOT_FOUND' else 'PRESENT'
                        elif cat == 'SUPPORT_ATTACHMENT':
                            st = 'ABSENT' if res_state == 'NOT_FOUND' else 'PRESENT'
                        elif cat == 'SUPPORT_MESSAGE':
                            st = 'REDACTED' if res_state == 'REDACTED' else 'PRESENT'
                        elif cat == 'DATA_FLOW':
                            st = 'DISABLED' if res_state == 'DISABLED' else 'ACTIVE'
                        elif cat == 'BACKUP_ARCHIVE':
                            st = 'BLOCKED' if res_state == 'BLOCKED' else 'ACTIVE'
                        elif cat == 'SECURITY_AUDIT_LOG':
                            st = 'PRESENT'
                        recs.append({
                            'system_id': sys_id,
                            'resource_id': res_id,
                            'category': cat,
                            'state': st,
                            'email': subj if '@' in subj else None,
                            'user_id': subj if subj.startswith('user_') else None
                        })
            self.evidence_records['evidence_03'] = recs

        # 4. Parse all remaining files
        for fid, finfo in self.manifest.items():
            if fid in self.evidence_records:
                continue
            fpath = os.path.join(DATASET_DIR, finfo['file_path'])
            if not os.path.exists(fpath):
                continue
            
            if 'service_resource_export' in finfo['file_path']:
                self.evidence_records[fid] = self._parse_service_resource_export(fpath)
            elif 'customer_data_snapshot_bundle' in finfo['file_path']:
                self.evidence_records[fid] = self._parse_snapshot_bundle(fpath)
            elif 'customer_data_inventory' in finfo['file_path']:
                self.evidence_records[fid] = self._parse_inventory_sql(fpath)
            elif 'customer_export_jobs' in finfo['file_path']:
                self.evidence_records[fid] = self._parse_export_jobs(fpath)
            elif 'customer_analytics_report' in finfo['file_path']:
                self.evidence_records[fid] = self._parse_analytics_report(fpath)
            elif 'resource_lookup_trace' in finfo['file_path']:
                self.evidence_records[fid] = self._parse_lookup_trace(fpath)
            elif fpath.endswith('.sql'):
                self.evidence_records[fid] = self._parse_replica_sql(fpath)
            elif fpath.endswith('.log'):
                self.evidence_records[fid] = self._parse_log_events(fpath)

    def _parse_service_resource_export(self, fpath):
        recs = []
        with open(fpath, 'r', encoding='utf-8') as f:
            d = json.load(f)
        sexp = d.get('service_exports', {})
        for item in sexp.get('account_service', {}).get('profile_lookups', []):
            prof = item.get('profile')
            st = 'PRESENT' if prof is not None and item.get('status_code') == 200 else 'ABSENT'
            recs.append({
                'system_id': 'account_service',
                'resource_id': item['resource_id'],
                'category': 'USER_PROFILE',
                'state': st,
                'email': prof.get('email') if prof else None,
                'user_id': prof.get('customer_reference') if prof else None
            })
        for item in sexp.get('analytics_platform', {}).get('profiles', []):
            has_pii = bool(item.get('email') or item.get('phone') or item.get('customer_reference'))
            recs.append({
                'system_id': 'analytics_platform',
                'resource_id': item['resource_id'],
                'category': 'ANALYTICS_PROFILE',
                'state': 'PRESENT' if has_pii else 'ANONYMIZED',
                'email': item.get('email'),
                'phone': item.get('phone'),
                'user_id': item.get('customer_reference')
            })
        for item in sexp.get('backup_service', {}).get('restore_entries', []):
            recs.append({
                'system_id': 'backup_service',
                'resource_id': item['resource_id'],
                'category': 'BACKUP_ARCHIVE',
                'state': 'ACTIVE' if item.get('restore_allowed') else 'BLOCKED',
                'email': item.get('customer_email'),
                'user_id': item.get('customer_reference')
            })
        for item in sexp.get('export_service', {}).get('exports', []):
            recs.append({
                'system_id': 'export_service',
                'resource_id': item['resource_id'],
                'category': 'USER_EXPORT',
                'state': 'PRESENT',
                'email': item.get('owner_email'),
                'phone': item.get('owner_phone'),
                'user_id': item.get('customer_reference')
            })
        for item in sexp.get('integration_service', {}).get('connectors', []):
            recs.append({
                'system_id': 'integration_service',
                'resource_id': item['resource_id'],
                'category': 'DATA_FLOW',
                'state': 'ACTIVE' if item.get('enabled') else 'DISABLED',
                'email': item.get('customer_email'),
                'user_id': item.get('customer_reference')
            })
        for item in sexp.get('search_service', {}).get('index_queries', []):
            hits = item.get('hits', {})
            docs = hits.get('documents', [])
            total = hits.get('total', 0)
            st = 'PRESENT' if (total > 0 or len(docs) > 0) else 'ABSENT'
            em = item.get('query')
            uid = None
            if docs:
                em = docs[0].get('email') or em
                uid = docs[0].get('customer_reference')
            recs.append({
                'system_id': 'search_service',
                'resource_id': item['resource_id'],
                'category': 'SEARCH_INDEX_ENTRY',
                'state': st,
                'email': em,
                'user_id': uid
            })
        for item in sexp.get('security_service', {}).get('audit_records', []):
            recs.append({
                'system_id': 'security_service',
                'resource_id': item['resource_id'],
                'category': 'SECURITY_AUDIT_LOG',
                'state': 'PRESENT',
                'user_id': item.get('subject_reference')
            })
        for item in sexp.get('support_platform', {}).get('tickets', []):
            has_pii = bool(item.get('requester_email') or item.get('requester_name') or item.get('requester_phone'))
            recs.append({
                'system_id': 'support_platform',
                'resource_id': item['resource_id'],
                'category': 'SUPPORT_MESSAGE',
                'state': 'PRESENT' if has_pii else 'REDACTED',
                'email': item.get('requester_email'),
                'phone': item.get('requester_phone'),
                'name': item.get('requester_name'),
                'user_id': item.get('customer_reference')
            })
        return recs

    def _parse_snapshot_bundle(self, fpath):
        recs = []
        with open(fpath, 'r', encoding='utf-8') as f:
            d = json.load(f)
        for snap in d.get('snapshots', []):
            ds = snap.get('data_store')
            coll = snap.get('collection')
            records = snap.get('records', [])
            if ds == 'account_service' and coll == 'customer_profiles':
                for r in records:
                    recs.append({
                        'system_id': 'account_service',
                        'resource_id': r.get('resource_id'),
                        'category': 'USER_PROFILE',
                        'state': 'PRESENT',
                        'email': r.get('email'),
                        'phone': r.get('phone'),
                        'user_id': r.get('customer_reference')
                    })
            elif ds == 'identity_service' and coll == 'deleted_customer_references':
                for r in records:
                    has_pii = bool(r.get('name') or r.get('email') or r.get('phone') or r.get('email_hash'))
                    recs.append({
                        'system_id': 'identity_service',
                        'resource_id': r.get('resource_id'),
                        'category': 'ACCOUNT_TOMBSTONE',
                        'state': 'PRESENT' if has_pii else 'REDACTED',
                        'email': r.get('email'),
                        'phone': r.get('phone'),
                        'user_id': r.get('subject_reference')
                    })
            elif ds == 'security_service' and coll == 'security_audit_events':
                for r in records:
                    recs.append({
                        'system_id': 'security_service',
                        'resource_id': r.get('resource_id'),
                        'category': 'SECURITY_AUDIT_LOG',
                        'state': 'PRESENT',
                        'user_id': r.get('subject_reference')
                    })
        return recs

    def _parse_export_jobs(self, fpath):
        recs = []
        with open(fpath, 'r', encoding='utf-8') as f:
            d = json.load(f)
        for r in d.get('records', []):
            recs.append({
                'system_id': 'export_service',
                'resource_id': r.get('resource_id'),
                'category': 'USER_EXPORT',
                'state': 'PRESENT',
                'email': r.get('owner_email')
            })
        return recs

    def _parse_analytics_report(self, fpath):
        recs = []
        with open(fpath, 'r', encoding='utf-8') as f:
            d = json.load(f)
        for r in d.get('records', []):
            has_pii = bool(r.get('email') or r.get('phone') or r.get('user_id'))
            recs.append({
                'system_id': 'analytics_platform',
                'resource_id': r.get('resource_id'),
                'category': 'ANALYTICS_PROFILE',
                'state': 'PRESENT' if has_pii else 'ANONYMIZED',
                'email': r.get('email'),
                'phone': r.get('phone'),
                'user_id': r.get('user_id')
            })
        return recs

    def _parse_inventory_sql(self, fpath):
        recs = []
        conn = sqlite3.connect(':memory:')
        with open(fpath, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, email, phone FROM customer_profiles").fetchall():
                recs.append({'system_id': 'account_service', 'resource_id': r[0], 'category': 'USER_PROFILE', 'state': 'PRESENT', 'user_id': r[1], 'email': r[2], 'phone': r[3]})
        except: pass
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, email, phone FROM customer_search_documents").fetchall():
                recs.append({'system_id': 'search_service', 'resource_id': r[0], 'category': 'SEARCH_INDEX_ENTRY', 'state': 'PRESENT', 'user_id': r[1], 'email': r[2], 'phone': r[3]})
        except: pass
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, email, phone, email_hash FROM customer_analytics_profiles").fetchall():
                has_pii = bool(r[2] or r[3] or r[4] or r[1])
                recs.append({'system_id': 'analytics_platform', 'resource_id': r[0], 'category': 'ANALYTICS_PROFILE', 'state': 'PRESENT' if has_pii else 'ANONYMIZED', 'user_id': r[1], 'email': r[2], 'phone': r[3]})
        except: pass
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, requester_name, requester_email, requester_phone FROM support_records").fetchall():
                has_pii = bool(r[2] or r[3] or r[4])
                recs.append({'system_id': 'support_platform', 'resource_id': r[0], 'category': 'SUPPORT_MESSAGE', 'state': 'PRESENT' if has_pii else 'REDACTED', 'user_id': r[1], 'name': r[2], 'email': r[3], 'phone': r[4]})
        except: pass
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, owner_email, owner_phone FROM customer_exports").fetchall():
                recs.append({'system_id': 'export_service', 'resource_id': r[0], 'category': 'USER_EXPORT', 'state': 'PRESENT', 'user_id': r[1], 'email': r[2], 'phone': r[3]})
        except: pass
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, customer_email, enabled FROM connector_subscriptions").fetchall():
                recs.append({'system_id': 'integration_service', 'resource_id': r[0], 'category': 'DATA_FLOW', 'state': 'ACTIVE' if r[3] else 'DISABLED', 'user_id': r[1], 'email': r[2]})
        except: pass
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, customer_email, restore_allowed FROM backup_restore_entries").fetchall():
                recs.append({'system_id': 'backup_service', 'resource_id': r[0], 'category': 'BACKUP_ARCHIVE', 'state': 'ACTIVE' if r[3] else 'BLOCKED', 'user_id': r[1], 'email': r[2]})
        except: pass
        try:
            for r in conn.execute("SELECT resource_id, subject_reference FROM security_audit_records").fetchall():
                recs.append({'system_id': 'security_service', 'resource_id': r[0], 'category': 'SECURITY_AUDIT_LOG', 'state': 'PRESENT', 'user_id': r[1]})
        except: pass
        return recs

    def _parse_lookup_trace(self, fpath):
        recs = []
        with open(fpath, 'r', encoding='utf-8') as f:
            for line in f:
                if 'completed' not in line:
                    continue
                kvs = dict(re.findall(r'(\w+)=([^\s]+)', line))
                sys_id = kvs.get('service')
                res_id = kvs.get('resource_id')
                if not sys_id or not res_id:
                    continue
                lk = kvs.get('lookup_key')
                subj = kvs.get('subject_reference') or kvs.get('customer_reference')
                em = kvs.get('email') or kvs.get('requester_email') or kvs.get('customer_email') or (lk if lk and '@' in lk else None)
                ph = kvs.get('phone') or kvs.get('requester_phone')
                uid = subj if subj and subj != 'null' else (lk if lk and lk.startswith('user_') else None)
                
                cat = None
                st = None
                if sys_id == 'account_service':
                    cat = 'USER_PROFILE'
                    rows = int(kvs.get('rows', 0))
                    status_code = int(kvs.get('http_status', 200))
                    st = 'ABSENT' if rows == 0 or status_code == 404 else 'PRESENT'
                elif sys_id == 'search_service':
                    cat = 'SEARCH_INDEX_ENTRY'
                    st = 'PRESENT' if kvs.get('result') == 'hit' or int(kvs.get('total_hits', 0)) > 0 else 'ABSENT'
                elif sys_id == 'support_platform':
                    cat = 'SUPPORT_MESSAGE'
                    has_pii = bool((em and em != 'null') or (ph and ph != 'null'))
                    st = 'PRESENT' if has_pii else 'REDACTED'
                elif sys_id == 'analytics_platform':
                    cat = 'ANALYTICS_PROFILE'
                    has_pii = bool((em and em != 'null') or (ph and ph != 'null'))
                    st = 'PRESENT' if has_pii else 'ANONYMIZED'
                elif sys_id == 'integration_service':
                    cat = 'DATA_FLOW'
                    st = 'ACTIVE' if kvs.get('enabled') == 'true' else 'DISABLED'
                elif sys_id == 'backup_service':
                    cat = 'BACKUP_ARCHIVE'
                    st = 'ACTIVE' if kvs.get('restore_allowed') == 'true' else 'BLOCKED'
                elif sys_id == 'security_service':
                    cat = 'SECURITY_AUDIT_LOG'
                    st = 'PRESENT'
                
                if cat and st:
                    recs.append({
                        'system_id': sys_id,
                        'resource_id': res_id,
                        'category': cat,
                        'state': st,
                        'email': em if em != 'null' else None,
                        'phone': ph if ph != 'null' else None,
                        'user_id': uid
                    })
        return recs

    def _parse_replica_sql(self, fpath):
        recs = []
        conn = sqlite3.connect(':memory:')
        with open(fpath, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        for t in tables:
            cols = [r[1] for r in conn.execute(f"PRAGMA table_info({t})").fetchall()]
            try:
                for row in conn.execute(f"SELECT * FROM {t}").fetchall():
                    row_dict = dict(zip(cols, row))
                    if 'record_json' in row_dict:
                        rj = json.loads(row_dict['record_json'])
                        orig = row_dict.get('origin_system', '')
                        res_id = rj.get('resource_id')
                        em = rj.get('email') or rj.get('customer_email') or rj.get('requester_email')
                        uid = rj.get('user_id') or rj.get('customer_reference') or rj.get('subject_reference')
                        cat = 'USER_PROFILE'
                        st = 'PRESENT'
                        if orig == 'search_service':
                            cat = 'SEARCH_INDEX_ENTRY'
                        elif orig == 'analytics_platform':
                            cat = 'ANALYTICS_PROFILE'
                            st = 'PRESENT' if em or rj.get('phone') else 'ANONYMIZED'
                        elif orig == 'support_platform':
                            cat = 'SUPPORT_MESSAGE'
                            st = 'PRESENT' if em or rj.get('phone') else 'REDACTED'
                        elif orig == 'backup_service':
                            cat = 'BACKUP_ARCHIVE'
                            st = 'ACTIVE' if rj.get('restore_allowed') else 'BLOCKED'
                        elif orig == 'security_service':
                            cat = 'SECURITY_AUDIT_LOG'
                            st = 'PRESENT'
                        if res_id:
                            recs.append({'system_id': orig, 'resource_id': res_id, 'category': cat, 'state': st, 'email': em, 'user_id': uid})
                    else:
                        res_id = row_dict.get('resource_id')
                        em = row_dict.get('email') or row_dict.get('customer_email') or row_dict.get('requester_email')
                        uid = row_dict.get('user_id') or row_dict.get('customer_reference') or row_dict.get('subject_reference')
                        sys_id = 'account_service'
                        cat = 'USER_PROFILE'
                        st = 'PRESENT'
                        if 'search' in t:
                            sys_id = 'search_service'
                            cat = 'SEARCH_INDEX_ENTRY'
                        elif 'analytics' in t:
                            sys_id = 'analytics_platform'
                            cat = 'ANALYTICS_PROFILE'
                            st = 'PRESENT' if em or row_dict.get('phone') else 'ANONYMIZED'
                        elif 'support' in t:
                            sys_id = 'support_platform'
                            cat = 'SUPPORT_MESSAGE'
                            st = 'PRESENT' if em or row_dict.get('phone') else 'REDACTED'
                        elif 'backup' in t:
                            sys_id = 'backup_service'
                            cat = 'BACKUP_ARCHIVE'
                            st = 'ACTIVE' if row_dict.get('restore_allowed') else 'BLOCKED'
                        elif 'security' in t:
                            sys_id = 'security_service'
                            cat = 'SECURITY_AUDIT_LOG'
                            st = 'PRESENT'
                        if res_id:
                            recs.append({'system_id': sys_id, 'resource_id': res_id, 'category': cat, 'state': st, 'email': em, 'user_id': uid})
            except: pass
        return recs

    def _parse_log_events(self, fpath):
        recs = []
        with open(fpath, 'r', encoding='utf-8') as f:
            for line in f:
                if 'resource_id=' not in line:
                    continue
                kvs = dict(re.findall(r'(\w+)=([^\s]+)', line))
                res_id = kvs.get('resource_id')
                sys_id = kvs.get('service')
                if not res_id or not sys_id:
                    continue
                em_match = re.search(r'correlation_key="([^"]+)"|matched_value="([^"]+)"|lookup_key=([^\s]+)', line)
                em = None
                if em_match:
                    val = em_match.group(1) or em_match.group(2) or em_match.group(3)
                    em = val if val and val != 'null' else None
                
                cat = 'USER_PROFILE'
                st = 'PRESENT'
                if sys_id == 'search_service':
                    cat = 'SEARCH_INDEX_ENTRY'
                    st = 'PRESENT' if 'result=hit' in line or 'total_hits=1' in line else 'ABSENT'
                elif sys_id == 'support_platform':
                    cat = 'SUPPORT_MESSAGE'
                    st = 'PRESENT'
                elif sys_id == 'integration_service':
                    cat = 'DATA_FLOW'
                    st = 'ACTIVE' if 'enabled=true' in line else 'DISABLED'
                elif sys_id == 'backup_service':
                    cat = 'BACKUP_ARCHIVE'
                    st = 'ACTIVE' if 'restore_allowed=true' in line or 'can still be restored' in line else 'BLOCKED'
                elif sys_id == 'analytics_platform':
                    cat = 'ANALYTICS_PROFILE'
                    st = 'PRESENT'
                elif sys_id == 'security_service':
                    cat = 'SECURITY_AUDIT_LOG'
                    st = 'PRESENT'

                recs.append({
                    'system_id': sys_id,
                    'resource_id': res_id,
                    'category': cat,
                    'state': st,
                    'email': em
                })
        return recs

    def audit_case(self, req):
        cid = req['case_id']
        req_text = req['request_text'].lower()
        
        # 1. Non-deletion check
        is_na = any(neg in req_text for neg in [
            'not asking for deletion', 'do not close', 'without removing', 'marketing lists only',
            'not a request to erase', 'leave my profile', 'continue using the service', 'don\'t delete',
            'leave the account active', 'keep the account as it is', 'only want my email address corrected',
            'request a full export of my personal data', 'only asking for a password reset', 'copies of my invoices'
        ])
        if is_na:
            return 'NOT_APPLICABLE', []

        # 2. Identity resolution
        u_email = req['email'].lower()
        uid = self.email_to_uid.get(u_email)
        uinfo = self.uid_to_info.get(uid, {'emails': {u_email}, 'phones': set(), 'names': set(), 'hashes': set(), 'user_id': uid})
        
        # 3. Find primary account ID from system_activity
        req_at = req['requested_at']
        rep_at = req['reported_at']
        audit_at = req['audit_at']
        
        # Deletion worker primary profile deletion in [requested_at, reported_at]
        acts = [
            a for a in self.system_activity 
            if a['source_system'] == 'deletion_worker' and a['target_system'] == 'account_service'
            and req_at <= a['event_time'] <= rep_at
        ]
        
        # Also find any other policy actions for this case in the activity window
        user_policy_acts = [
            a for a in self.system_activity
            if req_at <= a['event_time'] <= rep_at and a['resource_id']
        ]

        # 4. Find closest snapshot evidence file(s) for this batch at or before audit_at
        batch_evs = [e for e in self.manifest.values() if e['captured_at'] <= audit_at]
        batch_evs.sort(key=lambda x: x['captured_at'], reverse=True)
        primary_snap_fid = batch_evs[0]['file_id'] if batch_evs else ''
        
        # 5. Search for matching records in evidence up to audit_at
        matched_records = []
        for fid, recs in self.evidence_records.items():
            finfo = self.manifest.get(fid)
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

        # Check for remaining findings, active flows, exposed PII, restore risks
        findings = []
        remediations = []
        verifications = []

        # Determine primary account resource_id
        acc_id = None
        # Check if matched_records has an account_service entry
        acc_matched = [r for fid, r in matched_records if r['system_id'] == 'account_service']
        if acc_matched:
            acc_id = acc_matched[0]['resource_id']
        elif acts:
            acc_id = acts[0]['resource_id']
        else:
            acc_id = f"account_{cid.split('_')[1]}"

        # Process matched evidence records
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

        # Also check if reported_status was FAILED or PARTIAL in system_activity
        # or if reported_status == 'NOT_STARTED' or 'PARTIALLY_COMPLETE'
        is_incomplete = len(findings) > 0

        all_steps = []
        if is_incomplete:
            status = 'INCOMPLETE'
            all_steps.extend(findings)
            all_steps.extend(remediations)
            
            # Primary account absent check
            if acc_id and not any(s['system_id'] == 'account_service' and s['operation'] == 'REPORT_REMAINING_RECORD' for s in findings):
                verifications.append({'phase': 'VERIFICATION', 'system_id': 'account_service', 'resource_id': acc_id, 'operation': 'VERIFY_RECORD_ABSENT', 'state': 'ABSENT', 'evidence_id': ''})
            
            # Security audit record if any
            sec_recs = [r for fid, r in matched_records if r['system_id'] == 'security_service']
            if sec_recs:
                verifications.append({'phase': 'VERIFICATION', 'system_id': 'security_service', 'resource_id': sec_recs[0]['resource_id'], 'operation': 'VERIFY_RECORD_PRESENT', 'state': 'PRESENT', 'evidence_id': ''})
            
            all_steps.extend(verifications)
        else:
            status = 'COMPLETE'
            # In complete cases, cite evidence proving compliant state
            comp_ev = primary_snap_fid
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

        # Deduplicate steps
        seen = set()
        dedup_steps = []
        for s in all_steps:
            k = (s['phase'], s['system_id'], s['resource_id'], s['operation'], s['state'])
            if k not in seen:
                seen.add(k)
                dedup_steps.append(s)

        # Sort steps by official phase order, operation order, system_id, resource_id
        dedup_steps.sort(key=step_sort_key)
        for i, s in enumerate(dedup_steps):
            s['step_no'] = i + 1

        return status, dedup_steps

def run():
    engine = DeletionAuditEngine()
    reqs_path = os.path.join(DATASET_DIR, 'deletion_requests.csv')
    requests = list(csv.DictReader(open(reqs_path, encoding='utf-8')))
    print(f"Auditing {len(requests)} deletion requests...")
    
    rows = []
    status_counts = {'COMPLETE': 0, 'INCOMPLETE': 0, 'NOT_APPLICABLE': 0}
    
    for req in requests:
        cid = req['case_id']
        status, steps = engine.audit_case(req)
        status_counts[status] += 1
        rows.append({
            'case_id': cid,
            'deletion_status': status,
            'steps_json': json.dumps(steps)
        })

    # Sort rows by case_id ascending (numeric case ID)
    rows.sort(key=lambda r: int(r['case_id'].split('_')[1]))

    # Write output.csv at repository root
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['case_id', 'deletion_status', 'steps_json'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} output rows at {OUTPUT_PATH}.")
    print(f"Status distribution: {status_counts}")

if __name__ == '__main__':
    run()
