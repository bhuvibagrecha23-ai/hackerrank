import os
import glob
import json
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
sample_reqs = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'sample_output.csv'), encoding='utf-8'))}
identities = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'user_identities.csv'), encoding='utf-8')))
audit_log = list(csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'user_audit_log.csv'), encoding='utf-8')))
ev_manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(REPO_ROOT, 'dataset', 'evidence_files.csv'), encoding='utf-8'))}

# Build user lookup
email_to_uid = {}
for u in identities:
    email_to_uid[u['email'].lower()] = u['user_id']
for a in audit_log:
    if a['field_name'] == 'email':
        email_to_uid[a['old_value'].lower()] = a['user_id']
        email_to_uid[a['new_value'].lower()] = a['user_id']

uid_to_user = {}
for u in identities:
    uid = u['user_id']
    uid_to_user[uid] = {
        'user_id': uid,
        'emails': set([u['email'].lower()]),
        'phones': set([u['phone']]),
        'names': set([u['name']]),
        'hashes': set([u['email_hash']])
    }

for a in audit_log:
    uid = a['user_id']
    if uid not in uid_to_user:
        continue
    f = a['field_name']
    if f == 'email':
        uid_to_user[uid]['emails'].add(a['old_value'].lower())
        uid_to_user[uid]['emails'].add(a['new_value'].lower())
    elif f == 'phone':
        uid_to_user[uid]['phones'].add(a['old_value'])
        uid_to_user[uid]['phones'].add(a['new_value'])
    elif f == 'name':
        uid_to_user[uid]['names'].add(a['old_value'])
        uid_to_user[uid]['names'].add(a['new_value'])

# Index all evidence files by text content
file_texts = {}
for fid, finfo in ev_manifest.items():
    fpath = os.path.join(REPO_ROOT, 'dataset', finfo['file_path'])
    if not os.path.exists(fpath):
        continue
    if fpath.endswith('.pdf'):
        import pypdf
        reader = pypdf.PdfReader(fpath)
        text = "\n".join(page.extract_text() for page in reader.pages)
        file_texts[fid] = (finfo, text)
    elif fpath.endswith(('.sql', '.json', '.log', '.txt')):
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
            file_texts[fid] = (finfo, fp.read())

print(f"Indexed {len(file_texts)} text/pdf evidence files.")

# Test matching for sample cases
for req in sample_reqs[:10]:
    cid = req['case_id']
    audit_at = req['audit_at']
    email = req['email'].lower()
    uid = email_to_uid.get(email)
    uinfo = uid_to_user.get(uid, {'emails': {email}, 'phones': set(), 'names': set(), 'hashes': set()})
    
    # Check which evidence files mention any identifier and captured_at <= audit_at
    matches = []
    for fid, (finfo, text) in file_texts.items():
        if finfo['captured_at'] > audit_at:
            continue
        text_lower = text.lower()
        # Check matching
        matched_terms = []
        for em in uinfo['emails']:
            if em in text_lower:
                matched_terms.append(em)
        for ph in uinfo['phones']:
            if ph in text:
                matched_terms.append(ph)
        for h in uinfo['hashes']:
            if h in text:
                matched_terms.append(h)
        if uid and (f'"{uid}"' in text or f' {uid} ' in text or f'={uid}' in text or f': {uid}' in text or f':"{uid}"' in text or f"'{uid}'" in text):
            matched_terms.append(uid)
            
        if matched_terms:
            matches.append((fid, finfo['captured_at'], matched_terms))
            
    matches.sort(key=lambda x: x[1], reverse=True)
    out = sample_outs[cid]
    steps = json.loads(out['steps_json'])
    actual_evs = sorted(list(set(s['evidence_id'] for s in steps if s['evidence_id'])))
    print(f"\n[{cid}] audit_at={audit_at} | Expected ev: {actual_evs}")
    print(f"  Matched evidence files ({len(matches)}):")
    for m in matches[:5]:
        print(f"    {m[0]} ({m[1]}): {m[2]}")
