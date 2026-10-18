#!/usr/bin/env python3
import requests, pathlib, subprocess

URLS = [
    'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/pro-onlydomains.txt',
    'https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt',
    'https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt',
    'https://hblock.molinero.dev/hosts_domains.txt',
    'https://v.firebog.net/hosts/AdguardDNS.txt',
    'https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt',
]

TMP = pathlib.Path("all.tmp")
FINAL = pathlib.Path("blocklist.txt")

# 1. DOWNLOAD + CAT to one temp raw file
with open(TMP, "w") as out:
    for url in URLS:
        print(f"[+] {url}")
        r = requests.get(url, timeout=120)
        for line in r.text.splitlines():
            line = line.strip().lower()
            if not line or line.startswith("#"): continue
            if line.startswith("0.0.0.0 "): line = line.split()[1]
            if line.startswith("127.0.0.1 "): line = line.split()[1]
            if " " in line or "/" in line: continue
            out.write(line + "\n")

# 2. DEDUPE with GNU - this is the ONLY file you keep
subprocess.run(["sort", "-u", str(TMP), "-o", str(FINAL)], check=True)

# 3. DELETE raw file
TMP.unlink()

# 4. GZ deduped file only
subprocess.run(["gzip", "-9", "-k", "-f", str(FINAL)], check=True)

print(f"DONE: {FINAL.stat().st_size/1024/1024:.2f} MiB deduped")
