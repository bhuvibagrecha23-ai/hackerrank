import os
import glob
import json
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

all_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'deletion_requests.csv'), encoding='utf-8')))
ev_manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}
identities = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_identities.csv'), encoding='utf-8')))
audit_log = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_audit_log.csv'), encoding='utf-8')))

email_to_uid = {}
for u in identities:
    email_to_uid[u['email'].lower()] = u['user_id']
for a in audit_log:
    if a['field_name'] == 'email':
        email_to_uid[a['old_value'].lower()] = a['user_id']
        email_to_uid[a['new_value'].lower()] = a['user_id']

uid_to_idents = {}
for u in identities:
    uid = u['user_id']
    uid_to_idents[uid] = {'emails': {u['email'].lower()}, 'phones': {u['phone']}, 'names': {u['name']}, 'hashes': {u['email_hash']}}

for a in audit_log:
    uid = a['user_id']
    if uid in uid_to_idents:
        if a['field_name'] == 'email':
            uid_to_idents[uid]['emails'].add(a['old_value'].lower())
            uid_to_idents[uid]['emails'].add(a['new_value'].lower())
        elif a['field_name'] == 'phone':
            uid_to_idents[uid]['phones'].add(a['old_value'])
            uid_to_idents[uid]['phones'].add(a['new_value'])

# Index all evidence files text
ev_texts = {}
for fid, finfo in ev_manifest.items():
    p = os.path.join(DATASET_DIR, finfo['file_path'])
    if not os.path.exists(p):
        continue
    if p.endswith('.pdf'):
        import pypdf
        reader = pypdf.PdfReader(p)
        ev_texts[fid] = "\n".join(page.extract_text() for page in reader.pages)
    elif p.endswith(('.sql', '.json', '.log', '.txt')):
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            ev_texts[fid] = f.read()

print(f"Indexed {len(ev_texts)} files. Testing matching across all 518 cases...")

found_count = 0
not_found_cases = []

for req in all_reqs:
    cid = req['case_id']
    audit_at = req['audit_at']
    em = req['email'].lower()
    uid = email_to_uid.get(em)
    
    # Check if non-deletion
    is_na = any(neg in req['request_text'].lower() for neg in ['not asking for deletion', 'do not close', 'without removing', 'marketing lists only', 'not a request to erase', 'leave my profile', 'continue using the service', 'don\'t delete', 'leave the account active', 'keep the account as it is'])
    if is_na:
        found_count += 1
        continue
        
    uinfo = uid_to_idents.get(uid, {'emails': {em}, 'phones': set(), 'names': set(), 'hashes': set()})
    
    # Search in evidence files with captured_at <= audit_at
    # Sort candidates by captured_at descending
    candidates = []
    for fid, text in ev_texts.items():
        c_at = ev_manifest[fid]['captured_at']
        if c_at > audit_at:
            continue
        # Check if any identifier is in text
        text_lower = text.lower()
        matched = False
        for e in uinfo['emails']:
            if e in text_lower:
                matched = True
                break
        if not matched and uid and (f'"{uid}"' in text or f' {uid} ' in text or f'={uid}' in text or f': {uid}' in text or f':"{uid}"' in text or f"'{uid}'" in text or f'"{uid}"' in text_lower or f'={uid.lower()}' in text_lower):
            matched = True
        if matched:
            candidates.append((fid, c_at))
            
    if candidates:
        found_count += 1
    else:
        not_found_cases.append((cid, em, uid, audit_at))

print(f"Cases with matched evidence: {found_count} / {len(all_reqs)}")
print(f"Cases without matched evidence: {len(not_found_cases)}")
for c in not_found_cases[:15]:
    print(c)
