#!/usr/bin/env python3
import requests

# same 6 lists you have locally - no oisd
URLS = [
    'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/ultimate-onlydomains.txt',
    'https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt',
    'https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt',
    'https://hblock.molinero.dev/hosts_domains.txt',
    'https://v.firebog.net/hosts/AdguardDNS.txt',
    'https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt',
]

all_domains = set()

for url in URLS:
    print(f"Downloading {url}")
    try:
        r = requests.get(url, timeout=90)
        r.raise_for_status()
        count = 0
        for line in r.text.splitlines():
            line = line.strip().lower()
            if not line or line.startswith("#"):
                continue
            if line.startswith("0.0.0.0 "): line = line.split()[1]
            if line.startswith("127.0.0.1 "): line = line.split()[1]
            if " " in line or "/" in line:
                continue
            all_domains.add(line)
            count += 1
        print(f" -> {count} domains")
    except Exception as e:
        print(f" FAILED: {e}")

print(f"\nTotal unique: {len(all_domains)}")

# sort and save
with open("final.txt", "w", encoding="utf-8") as f:
    for d in sorted(all_domains):
        f.write(d + "\n")

print("Done -> final.txt")
