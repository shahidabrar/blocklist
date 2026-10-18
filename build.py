#!/usr/bin/env python3
import requests, pathlib, subprocess, gzip

URLS = [
    'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/pro-onlydomains.txt', # use pro for 1.5MB gz
    'https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt',
    'https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt',
    'https://hblock.molinero.dev/hosts_domains.txt',
    'https://v.firebog.net/hosts/AdguardDNS.txt',
    'https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt',
]

TMP = pathlib.Path("all.tmp")
TXT = pathlib.Path("blocklist.txt")
GZ = pathlib.Path("blocklist.txt.gz")

# 1. Download and cat into one file (no dedup yet)
TMP.write_text("", encoding="utf-8")
with open(TMP, "w", encoding="utf-8") as out:
    for url in URLS:
        print(f"[+] {url}")
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            count = 0
            for line in r.text.splitlines():
                line = line.strip().lower()
                if not line or line.startswith("#"): continue
                if line.startswith("0.0.0.0 "): line = line.split()[1]
                if line.startswith("127.0.0.1 "): line = line.split()[1]
                if " " in line or "/" in line: continue
                out.write(line + "\n")
                count += 1
            print(f"    {count}")
        except Exception as e:
            print(f"    FAIL {e}")

print(f"Before dedup: {sum(1 for _ in open(TMP))} lines")

# 2. GNU sort -u for dedup (uses disk, not RAM)
print("Running: sort -u all.tmp -o blocklist.txt")
subprocess.run(["sort", "-u", str(TMP), "-o", str(TXT)], check=True)

print(f"After dedup: {sum(1 for _ in open(TXT))} lines")

# 3. GNU gzip -9
print("Gzipping")
subprocess.run(["gzip", "-9", "-c", str(TXT)], stdout=open(GZ, "wb"), check=True)

print(f"TXT: {TXT.stat().st_size/1024/1024:.2f} MiB")
print(f"GZ: {GZ.stat().st_size/1024/1024:.2f} MiB")

TMP.unlink(missing_ok=True)
