import os

REPO_ROOT = r'C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26'
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

for root, dirs, files in os.walk(DATASET_DIR):
    for f in files:
        p = os.path.join(root, f)
        try:
            with open(p, 'rb') as fp:
                data = fp.read()
                if b'6645' in data:
                    print("Found 6645 in:", os.path.relpath(p, DATASET_DIR))
                if b'5569' in data:
                    print("Found 5569 in:", os.path.relpath(p, DATASET_DIR))
        except Exception as e:
            pass
