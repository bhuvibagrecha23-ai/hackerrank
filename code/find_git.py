import os
import shutil

git_path = shutil.which("git")
print("shutil.which('git'):", git_path)

common_paths = [
    r"C:\Program Files\Git\bin\git.exe",
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files (x86)\Git\bin\git.exe",
    r"C:\Program Files (x86)\Git\cmd\git.exe",
    r"C:\Users\bhuvi\AppData\Local\Programs\Git\bin\git.exe",
    r"C:\Users\bhuvi\AppData\Local\Programs\Git\cmd\git.exe",
    r"C:\Users\bhuvi\AppData\Local\GitHubDesktop\app-3.4.12\resources\app\git\cmd\git.exe",
]

for p in common_paths:
    if os.path.exists(p):
        print("Found git at:", p)

# Check all paths in PATH
print("\nScanning PATH environment variable:")
for p in os.environ.get("PATH", "").split(os.pathsep):
    if "git" in p.lower():
        print("  git in PATH:", p)
