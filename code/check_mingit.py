import urllib.request
import json
import zipfile
import os

url = "https://api.github.com/repos/git-for-windows/git/releases/latest"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Latest release tag:", data.get('tag_name'))
        for asset in data.get('assets', []):
            name = asset.get('name')
            if 'MinGit' in name and '64-bit.zip' in name and 'busybox' not in name:
                print("MinGit download url:", asset.get('browser_download_url'))
                print("MinGit asset name:", name)
                break
except Exception as e:
    print("Error querying releases:", e)
