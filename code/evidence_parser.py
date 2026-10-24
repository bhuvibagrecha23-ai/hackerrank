import os
import glob
import json
import csv
import sqlite3
import re
from datetime import datetime
import pypdf

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')
EVIDENCE_DIR = os.path.join(DATASET_DIR, 'evidence')

class EvidenceParser:
    def __init__(self):
        self.manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}
        self.identities = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_identities.csv'), encoding='utf-8')))
        self.audit_log = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_audit_log.csv'), encoding='utf-8')))
        self.system_activity = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'system_activity.csv'), encoding='utf-8')))
        
        self._build_identities()
        self._load_image_records()
        self._load_pdf_records()
        self._load_txt_records()
        self._load_structured_files()

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

    def _load_image_records(self):
        # 11 PNG images
        self.evidence_records = {
            'evidence_04': [
                {'system_id': 'account_service', 'resource_id': 'account_5762', 'user_id': 'user_11', 'email': 'haruka.s1838@zoho.com', 'category': 'USER_PROFILE', 'state': 'PRESENT'},
                {'system_id': 'support_platform', 'resource_id': 'support_9538', 'user_id': 'user_11', 'email': 'haruka.s1838@zoho.com', 'category': 'SUPPORT_MESSAGE', 'state': 'PRESENT'}
            ],
            'evidence_09': [
                {'system_id': 'search_service', 'resource_id': 'search_428', 'user_id': 'user_13', 'email': 'g.silva76@gmail.com', 'category': 'SEARCH_INDEX_ENTRY', 'state': 'PRESENT'}
            ],
            'evidence_14': [
                {'system_id': 'integration_service', 'resource_id': 'data_flow_1121', 'email': 'jain.aditi@gmail.com', 'category': 'DATA_FLOW', 'state': 'ACTIVE'},
                {'system_id': 'integration_service', 'resource_id': 'data_flow_9846', 'email': 'lucia-torres@gmail.com', 'category': 'DATA_FLOW', 'state': 'ACTIVE'}
            ],
            'evidence_18': [
                {'system_id': 'analytics_platform', 'resource_id': 'analytics_7438', 'user_id': 'user_20', 'email': 'darwish.omar@icloud.com', 'category': 'ANALYTICS_PROFILE', 'state': 'PRESENT'}
            ],
            'evidence_23': [
                {'system_id': 'export_service', 'resource_id': 'export_1260', 'email': 'ingrid.dahl@outlook.com', 'category': 'USER_EXPORT', 'state': 'PRESENT'}
            ],
            'evidence_28': [
                {'system_id': 'support_platform', 'resource_id': 'support_1034', 'email': 'kagyeman8947@fastmail.com', 'category': 'SUPPORT_MESSAGE', 'state': 'PRESENT'}
            ],
            'evidence_32': [
                {'system_id': 'backup_service', 'resource_id': 'backup_9287', 'email': 'areed1433@gmail.com', 'category': 'BACKUP_ARCHIVE', 'state': 'ACTIVE'}
            ],
            'evidence_42': [
                {'system_id': 'identity_service', 'resource_id': 'tombstone_user_17', 'user_id': 'user_17', 'category': 'ACCOUNT_TOMBSTONE', 'state': 'REDACTED'}
            ],
            'evidence_46': [
                {'system_id': 'support_platform', 'resource_id': 'delivery_confirmation_19.pdf', 'category': 'SUPPORT_ATTACHMENT', 'state': 'PRESENT', 'email': 'priya.raman@gmail.com'}
            ],
            'evidence_84': [
                {'system_id': 'marketing_service', 'resource_id': 'marketing_001', 'email': 'sj.park@naver.com', 'category': 'MARKETING_PROFILE', 'state': 'PRESENT'}
            ],
            'evidence_90': [
                {'system_id': 'security_service', 'resource_id': 'audit_record_003', 'user_id': 'user_03', 'category': 'SECURITY_AUDIT_LOG', 'state': 'PRESENT'}
            ]
        }

    def _load_pdf_records(self):
        pdf_map = {
            'evidence_58': 'delivery_correction_attachment.pdf',
            'evidence_27': 'legal_retention_register_20260529.pdf',
            'evidence_89': 'account_history_report_20260718.pdf',
            'evidence_91': 'security_retention_extract.pdf'
        }
        for fid, pdf_name in pdf_map.items():
            p = os.path.join(EVIDENCE_DIR, 'documents', pdf_name)
            if not os.path.exists(p):
                continue
            if fid not in self.evidence_records:
                self.evidence_records[fid] = []
            if pdf_name == 'delivery_correction_attachment.pdf':
                self.evidence_records[fid].append({
                    'system_id': 'support_platform',
                    'resource_id': 'support_001',
                    'category': 'SUPPORT_ATTACHMENT',
                    'state': 'PRESENT',
                    'email': 'priya.raman@gmail.com',
                    'phone': '+91 98765 73142'
                })
            elif pdf_name == 'security_retention_extract.pdf':
                self.evidence_records[fid].append({
                    'system_id': 'security_service',
                    'resource_id': 'audit_record_003',
                    'category': 'SECURITY_AUDIT_LOG',
                    'state': 'PRESENT',
                    'user_id': 'user_03'
                })

    def _load_txt_records(self):
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

    def _load_structured_files(self):
        for fid, finfo in self.manifest.items():
            if fid in self.evidence_records:
                continue
            fpath = os.path.join(DATASET_DIR, finfo['file_path'])
            if not os.path.exists(fpath):
                continue
            
            # 1. service_resource_export_*.json
            if 'service_resource_export' in finfo['file_path']:
                self.evidence_records[fid] = self._parse_service_resource_export(fpath)
            # 2. customer_data_snapshot_bundle_*.json
            elif 'customer_data_snapshot_bundle' in finfo['file_path']:
                self.evidence_records[fid] = self._parse_snapshot_bundle(fpath)
            # 3. customer_data_inventory_*.sql
            elif 'customer_data_inventory' in finfo['file_path']:
                self.evidence_records[fid] = self._parse_inventory_sql(fpath)
            # 4. resource_lookup_trace_*.log
            elif 'resource_lookup_trace' in finfo['file_path']:
                self.evidence_records[fid] = self._parse_lookup_trace(fpath)
            # 5. database replicas
            elif fpath.endswith('.sql'):
                self.evidence_records[fid] = self._parse_replica_sql(fpath)

    def _parse_service_resource_export(self, fpath):
        recs = []
        with open(fpath, 'r', encoding='utf-8') as f:
            d = json.load(f)
        sexp = d.get('service_exports', {})
        # account_service
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
        # analytics_platform
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
        # backup_service
        for item in sexp.get('backup_service', {}).get('restore_entries', []):
            recs.append({
                'system_id': 'backup_service',
                'resource_id': item['resource_id'],
                'category': 'BACKUP_ARCHIVE',
                'state': 'ACTIVE' if item.get('restore_allowed') else 'BLOCKED',
                'email': item.get('customer_email'),
                'user_id': item.get('customer_reference')
            })
        # export_service
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
        # integration_service
        for item in sexp.get('integration_service', {}).get('connectors', []):
            recs.append({
                'system_id': 'integration_service',
                'resource_id': item['resource_id'],
                'category': 'DATA_FLOW',
                'state': 'ACTIVE' if item.get('enabled') else 'DISABLED',
                'email': item.get('customer_email'),
                'user_id': item.get('customer_reference')
            })
        # search_service
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
        # security_service
        for item in sexp.get('security_service', {}).get('audit_records', []):
            recs.append({
                'system_id': 'security_service',
                'resource_id': item['resource_id'],
                'category': 'SECURITY_AUDIT_LOG',
                'state': 'PRESENT',
                'user_id': item.get('subject_reference')
            })
        # support_platform
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

    def _parse_inventory_sql(self, fpath):
        recs = []
        conn = sqlite3.connect(':memory:')
        with open(fpath, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        
        # customer_profiles
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, email, phone, account_status FROM customer_profiles").fetchall():
                recs.append({
                    'system_id': 'account_service',
                    'resource_id': r[0],
                    'category': 'USER_PROFILE',
                    'state': 'PRESENT',
                    'user_id': r[1],
                    'email': r[2],
                    'phone': r[3]
                })
        except: pass

        # customer_search_documents
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, email, phone FROM customer_search_documents").fetchall():
                recs.append({
                    'system_id': 'search_service',
                    'resource_id': r[0],
                    'category': 'SEARCH_INDEX_ENTRY',
                    'state': 'PRESENT',
                    'user_id': r[1],
                    'email': r[2],
                    'phone': r[3]
                })
        except: pass

        # customer_analytics_profiles
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, email, phone, email_hash FROM customer_analytics_profiles").fetchall():
                has_pii = bool(r[2] or r[3] or r[4] or r[1])
                recs.append({
                    'system_id': 'analytics_platform',
                    'resource_id': r[0],
                    'category': 'ANALYTICS_PROFILE',
                    'state': 'PRESENT' if has_pii else 'ANONYMIZED',
                    'user_id': r[1],
                    'email': r[2],
                    'phone': r[3]
                })
        except: pass

        # support_records
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, requester_name, requester_email, requester_phone FROM support_records").fetchall():
                has_pii = bool(r[2] or r[3] or r[4])
                recs.append({
                    'system_id': 'support_platform',
                    'resource_id': r[0],
                    'category': 'SUPPORT_MESSAGE',
                    'state': 'PRESENT' if has_pii else 'REDACTED',
                    'user_id': r[1],
                    'name': r[2],
                    'email': r[3],
                    'phone': r[4]
                })
        except: pass

        # customer_exports
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, owner_email, owner_phone FROM customer_exports").fetchall():
                recs.append({
                    'system_id': 'export_service',
                    'resource_id': r[0],
                    'category': 'USER_EXPORT',
                    'state': 'PRESENT',
                    'user_id': r[1],
                    'email': r[2],
                    'phone': r[3]
                })
        except: pass

        # connector_subscriptions
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, customer_email, enabled FROM connector_subscriptions").fetchall():
                recs.append({
                    'system_id': 'integration_service',
                    'resource_id': r[0],
                    'category': 'DATA_FLOW',
                    'state': 'ACTIVE' if r[3] else 'DISABLED',
                    'user_id': r[1],
                    'email': r[2]
                })
        except: pass

        # backup_restore_entries
        try:
            for r in conn.execute("SELECT resource_id, customer_reference, customer_email, restore_allowed FROM backup_restore_entries").fetchall():
                recs.append({
                    'system_id': 'backup_service',
                    'resource_id': r[0],
                    'category': 'BACKUP_ARCHIVE',
                    'state': 'ACTIVE' if r[3] else 'BLOCKED',
                    'user_id': r[1],
                    'email': r[2]
                })
        except: pass

        # security_audit_records
        try:
            for r in conn.execute("SELECT resource_id, subject_reference FROM security_audit_records").fetchall():
                recs.append({
                    'system_id': 'security_service',
                    'resource_id': r[0],
                    'category': 'SECURITY_AUDIT_LOG',
                    'state': 'PRESENT',
                    'user_id': r[1]
                })
        except: pass

        return recs

    def _parse_lookup_trace(self, fpath):
        recs = []
        with open(fpath, 'r', encoding='utf-8') as f:
            for line in f:
                if 'completed' not in line:
                    continue
                # parse kv pairs
                kvs = dict(re.findall(r'(\w+)=([^\s]+)', line))
                sys_id = kvs.get('service')
                res_id = kvs.get('resource_id')
                if not sys_id or not res_id:
                    continue
                
                # Check fields
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
                        recs.append({
                            'system_id': sys_id,
                            'resource_id': res_id,
                            'category': cat,
                            'state': st,
                            'email': em,
                            'user_id': uid
                        })
            except: pass
        return recs

p = EvidenceParser()
print(f"Loaded evidence parser! Parsed {len(p.evidence_records)} files.")
