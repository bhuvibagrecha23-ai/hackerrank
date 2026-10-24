import urllib.request
import zipfile
import os

url = "https://github.com/git-for-windows/git/releases/download/v2.56.0.windows.3/MinGit-2.56.0.3-64-bit.zip"
target_dir = r"C:\Users\bhuvi\.gemini\antigravity\tools\mingit"
os.makedirs(target_dir, exist_ok=True)
zip_path = os.path.join(target_dir, "mingit.zip")

print(f"Downloading MinGit from {url}...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp, open(zip_path, 'wb') as out_file:
    out_file.write(resp.read())

print("Extracting MinGit...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(target_dir)

os.remove(zip_path)
git_exe = os.path.join(target_dir, "cmd", "git.exe")
print("MinGit installed successfully at:", git_exe)
print("git.exe exists:", os.path.exists(git_exe))
