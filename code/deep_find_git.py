import os

search_roots = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Users\bhuvi\AppData",
    r"C:\Users\bhuvi\bin",
    r"C:\tools",
    r"C:\Git"
]

found_gits = []
for root_dir in search_roots:
    if not os.path.exists(root_dir):
        continue
    for root, dirs, files in os.walk(root_dir):
        if "git.exe" in files:
            found_gits.append(os.path.join(root, "git.exe"))
        if len(found_gits) >= 5:
            break

print("Found gits:", found_gits)
