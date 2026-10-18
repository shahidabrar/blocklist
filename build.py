#!/usr/bin/env python3
import requests, gzip, pathlib

URLS = [
    'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/ultimate-onlydomains.txt',
    'https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt',
    'https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt',
    'https://hblock.molinero.dev/hosts_domains.txt',
    'https://v.firebog.net/hosts/AdguardDNS.txt',
    'https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt',
]

TXT = pathlib.Path("blocklist.txt")
GZ = pathlib.Path("blocklist.txt.gz")

all_domains = set()
for url in URLS:
    print(f"[+] {url}")
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        c = 0
        for line in r.text.splitlines():
            line = line.strip().lower()
            if not line or line.startswith("#"): continue
            if line.startswith("0.0.0.0 "): line = line.split()[1]
            if line.startswith("127.0.0.1 "): line = line.split()[1]
            if " " in line or "/" in line: continue
            all_domains.add(line)
            c += 1
        print(f"    {c}")
    except Exception as e:
        print(f"    FAIL {e}")

unique = sorted(all_domains)
print(f"Total unique: {len(unique)}")

TXT.write_text("\n".join(unique) + "\n", encoding="utf-8")

with open(TXT, "rb") as f_in:
    with gzip.open(GZ, "wb", compresslevel=9) as f_out:
        f_out.write(f_in.read())

print(f"TXT: {TXT.stat().st_size/1024/1024:.2f} MiB")
print(f"GZ: {GZ.stat().st_size/1024/1024:.2f} MiB")
