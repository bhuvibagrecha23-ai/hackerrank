import os
import json
import csv
from datetime import datetime

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

sample_reqs = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
sample_outs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}
manifest = {r['file_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'evidence_files.csv'), encoding='utf-8'))}
identities = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_identities.csv'), encoding='utf-8')))
audit_log = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'user_audit_log.csv'), encoding='utf-8')))

email_to_uid = {}
for u in identities:
    email_to_uid[u['email'].lower()] = u['user_id']
for a in audit_log:
    if a['field_name'] == 'email':
        email_to_uid[a['old_value'].lower()] = a['user_id']
        email_to_uid[a['new_value'].lower()] = a['user_id']

uid_to_info = {}
for u in identities:
    uid = u['user_id']
    uid_to_info[uid] = {
        'user_id': uid,
        'emails': {u['email'].lower()},
        'phones': {u['phone']},
        'names': {u['name']},
        'hashes': {u['email_hash']}
    }
for a in audit_log:
    uid = a['user_id']
    if uid in uid_to_info:
        if a['field_name'] == 'email':
            uid_to_info[uid]['emails'].add(a['old_value'].lower())
            uid_to_info[uid]['emails'].add(a['new_value'].lower())
        elif a['field_name'] == 'phone':
            uid_to_info[uid]['phones'].add(a['old_value'])
            uid_to_info[uid]['phones'].add(a['new_value'])
        elif a['field_name'] == 'name':
            uid_to_info[uid]['names'].add(a['old_value'])
            uid_to_info[uid]['names'].add(a['new_value'])

# Index text of all evidence files
file_texts = {}
for fid, finfo in manifest.items():
    p = os.path.join(DATASET_DIR, finfo['file_path'])
    if not os.path.exists(p):
        continue
    if p.endswith('.pdf'):
        import pypdf
        reader = pypdf.PdfReader(p)
        file_texts[fid] = "\n".join(page.extract_text() for page in reader.pages)
    elif p.endswith(('.sql', '.json', '.log', '.txt')):
        with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
            file_texts[fid] = fp.read()

# For each sample case, check each resource in steps
for req in sample_reqs:
    cid = req['case_id']
    out = sample_outs[cid]
    steps = json.loads(out['steps_json'])
    u_email = req['email'].lower()
    uid = email_to_uid.get(u_email)
    uinfo = uid_to_info.get(uid, {'emails': {u_email}, 'phones': set(), 'names': set(), 'hashes': set(), 'user_id': uid})
    
    # Collect cited evidence
    cited_evs = sorted(list(set(s['evidence_id'] for s in steps if s['evidence_id'])))
    
    print(f"\n[{cid}] uid={uid} email={u_email} status={out['deletion_status']} cited_ev={cited_evs}")
    for s in steps:
        res = s['resource_id']
        sys_id = s['system_id']
        op = s['operation']
        ev = s['evidence_id']
        
        # Where does res appear?
        in_cited = False
        if ev and ev in file_texts and res in file_texts[ev]:
            in_cited = True
        
        # Check where in all evidence files res appears
        all_ev_with_res = [fid for fid, txt in file_texts.items() if res in txt and manifest[fid]['captured_at'] <= req['audit_at']]
        
        print(f"   step {s['step_no']:<2} {sys_id:<20} {res:<20} {op:<25} ev={ev:<12} in_cited={in_cited} all_ev={all_ev_with_res}")
