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

class AuditEngine:
    def __init__(self):
        self.ev_manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}
        self.identities = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_identities.csv'), encoding='utf-8')))
        self.audit_log = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_audit_log.csv'), encoding='utf-8')))
        self.system_activity = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'system_activity.csv'), encoding='utf-8')))
        
        self._build_identity_graph()
        self._load_image_records()
        self._parse_all_evidence()

    def _build_identity_graph(self):
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
        # Structured transcription of the 11 PNG images
        self.image_records = {
            'evidence_04': { # account_admin_console_20260926.png
                'records': [
                    {'system_id': 'account_service', 'resource_id': 'account_5762', 'user_id': 'user_11', 'email': 'haruka.s1838@zoho.com', 'category': 'USER_PROFILE', 'state': 'PRESENT'},
                    {'system_id': 'support_platform', 'resource_id': 'support_9538', 'user_id': 'user_11', 'email': 'haruka.s1838@zoho.com', 'category': 'SUPPORT_MESSAGE', 'state': 'PRESENT'}
                ]
            },
            'evidence_09': { # search_index_inspector_20260901.png
                'records': [
                    {'system_id': 'search_service', 'resource_id': 'search_428', 'user_id': 'user_13', 'email': 'g.silva76@gmail.com', 'category': 'SEARCH_INDEX_ENTRY', 'state': 'PRESENT'}
                ]
            },
            'evidence_14': { # connector_management_console_20260807.png
                'records': [
                    {'system_id': 'integration_service', 'resource_id': 'data_flow_1121', 'email': 'jain.aditi@gmail.com', 'category': 'DATA_FLOW', 'state': 'ACTIVE'},
                    {'system_id': 'integration_service', 'resource_id': 'data_flow_9846', 'email': 'lucia-torres@gmail.com', 'category': 'DATA_FLOW', 'state': 'ACTIVE'}
                ]
            },
            'evidence_18': { # analytics_profile_view_20260713.png
                'records': [
                    {'system_id': 'analytics_platform', 'resource_id': 'analytics_7438', 'user_id': 'user_20', 'email': 'darwish.omar@icloud.com', 'category': 'ANALYTICS_PROFILE', 'state': 'PRESENT'}
                ]
            },
            'evidence_23': { # customer_export_console_20260618.png
                'records': [
                    {'system_id': 'export_service', 'resource_id': 'export_1260', 'email': 'ingrid.dahl@outlook.com', 'category': 'USER_EXPORT', 'state': 'PRESENT'}
                ]
            },
            'evidence_28': { # support_ticket_console_20260524.png
                'records': [
                    {'system_id': 'support_platform', 'resource_id': 'support_1034', 'email': 'kagyeman8947@fastmail.com', 'category': 'SUPPORT_MESSAGE', 'state': 'PRESENT'}
                ]
            },
            'evidence_32': { # backup_restore_console_20260429.png
                'records': [
                    {'system_id': 'backup_service', 'resource_id': 'backup_9287', 'email': 'areed1433@gmail.com', 'category': 'BACKUP_ARCHIVE', 'state': 'ACTIVE'}
                ]
            },
            'evidence_42': { # deleted_account_reference_20260310.png
                'records': [
                    {'system_id': 'identity_service', 'resource_id': 'tombstone_user_17', 'user_id': 'user_17', 'category': 'ACCOUNT_TOMBSTONE', 'state': 'REDACTED'}
                ]
            },
            'evidence_46': { # object_storage_browser_20260213.png
                'records': [
                    {'system_id': 'support_platform', 'resource_id': 'delivery_confirmation_19.pdf', 'category': 'SUPPORT_ATTACHMENT', 'state': 'PRESENT'}
                ]
            },
            'evidence_84': { # marketing_profile_console.png
                'records': [
                    {'system_id': 'marketing_service', 'resource_id': 'marketing_001', 'email': 'sj.park@naver.com', 'category': 'MARKETING_PROFILE', 'state': 'PRESENT'}
                ]
            },
            'evidence_90': { # security_audit_explorer_20260905.png
                'records': [
                    {'system_id': 'security_service', 'resource_id': 'audit_record_003', 'user_id': 'user_03', 'category': 'SECURITY_AUDIT_LOG', 'state': 'PRESENT'}
                ]
            }
        }

    def _parse_all_evidence(self):
        # We will extract records per file_id: list of records
        self.evidence_records = {} # file_id -> list of records
        
        # 1. Add image records
        for fid, finfo in self.image_records.items():
            self.evidence_records[fid] = finfo['records']

        # 2. Parse txt handover
        p_txt = os.path.join(EVIDENCE_DIR, 'records', 'customer_account_handover_20261001.txt')
        if os.path.exists(p_txt):
            recs = []
            with open(p_txt, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line.startswith('- '):
                        continue
                    # - 2026-10-01T12:00:00Z | account_service | account_146 | USER_PROFILE | NOT_FOUND | e.lindberg18@yahoo.com
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
                            'subject': subj
                        })
            self.evidence_records['evidence_03'] = recs

        # 3. Parse PDFs
        pdf_map = {
            'evidence_58': 'delivery_correction_attachment.pdf',
            'evidence_27': 'legal_retention_register_20260529.pdf',
            'evidence_89': 'account_history_report_20260718.pdf',
            'evidence_91': 'security_retention_extract.pdf'
        }
        for fid, pdf_name in pdf_map.items():
            p = os.path.join(EVIDENCE_DIR, 'documents', pdf_name)
            if os.path.exists(p):
                reader = pypdf.PdfReader(p)
                text = "\n".join(page.extract_text() for page in reader.pages)
                recs = []
                if pdf_name == 'delivery_correction_attachment.pdf':
                    # CS-4827 / support_001
                    recs.append({
                        'system_id': 'support_platform',
                        'resource_id': 'support_001',
                        'category': 'SUPPORT_ATTACHMENT',
                        'state': 'PRESENT',
                        'email': 'priya.raman@gmail.com',
                        'phone': '+91 98765 73142'
                    })
                elif pdf_name == 'security_retention_extract.pdf':
                    # audit_record_003 / user_03
                    recs.append({
                        'system_id': 'security_service',
                        'resource_id': 'audit_record_003',
                        'category': 'SECURITY_AUDIT_LOG',
                        'state': 'PRESENT',
                        'user_id': 'user_03'
                    })
                self.evidence_records[fid] = recs

        print(f"Loaded records for {len(self.evidence_records)} evidence files so far.")

engine = AuditEngine()
