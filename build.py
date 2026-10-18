#!/usr/bin/env python3
import requests, pathlib, subprocess, glob

URLS = [
    'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/pro-onlydomains.txt',
    'https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt',
    'https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt',
    'https://hblock.molinero.dev/hosts_domains.txt',
    'https://v.firebog.net/hosts/AdguardDNS.txt',
    'https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt',
]

DIR = pathlib.Path("lists")
DIR.mkdir(exist_ok=True)

# 1. DOWNLOAD each list as separate txt in lists/ dir
for i, url in enumerate(URLS):
    name = DIR / f"{i}.txt"
    print(f"[+] Download {url} -> {name}")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    cleaned = []
    for line in r.text.splitlines():
        line = line.strip().lower()
        if not line or line.startswith("#"): continue
        if line.startswith("0.0.0.0 "): line = line.split()[1]
        if line.startswith("127.0.0.1 "): line = line.split()[1]
        if " " in line or "/" in line: continue
        cleaned.append(line)
    name.write_text("\n".join(cleaned) + "\n")

# 2. CAT all txt in directory
print("CAT all txt files in lists/")
cat_file = pathlib.Path("all.txt")
with open(cat_file, "w") as out:
    for f in glob.glob(str(DIR / "*.txt")):
        out.write(open(f).read() + "\n")

print(f"Before dedup: {sum(1 for _ in open(cat_file))} lines")

# 3. DEDUPE with GNU sort -u -> final.txt
print("DEDUPE -> final.txt")
subprocess.run(["sort", "-u", str(cat_file), "-o", "final.txt"], check=True)

# 4. Cleanup temp files
cat_file.unlink()
# keep or delete source lists - delete to keep repo clean
for f in glob.glob(str(DIR / "*.txt")):
    pathlib.Path(f).unlink()
DIR.rmdir()

# 5. GZ final.txt -> final.txt.gz
subprocess.run(["gzip", "-9", "-k", "-f", "final.txt"], check=True)
# gzip makes final.txt.gz, need rename to final.gz spec
subprocess.run(["mv", "-f", "final.txt.gz", "final.gz"], check=True)
# recreate final.txt.gz as well for compatibility
subprocess.run(["gzip", "-9", "-k", "-f", "final.txt"], check=True)
subprocess.run(["cp", "final.txt.gz", "final.gz"], check=True)

import os
print(f"final.txt: {os.path.getsize('final.txt')/1024/1024:.2f} MiB - {sum(1 for _ in open('final.txt'))} lines")
print(f"final.gz: {os.path.getsize('final.gz')/1024/1024:.2f} MiB")
