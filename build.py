#!/usr/bin/env python3
import requests, gzip, pathlib
from datetime import datetime

BLOCKLISTS = [
    'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/ultimate-onlydomains.txt',
    'https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt',
    'https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt',
    'https://hblock.molinero.dev/hosts_domains.txt',
    'https://v.firebog.net/hosts/AdguardDNS.txt',
    'https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt',

]

OUTPUT_TXT = pathlib.Path("blocklist.txt")
OUTPUT_GZ = pathlib.Path("blocklist.txt.gz")

def get_domains(url):
    print(f"[+] {url}")
    try:
        r = requests.get(url, timeout=90)
        r.raise_for_status()
        domains = []
        for line in r.text.splitlines():
            line = line.strip().lower()
            if not line or line.startswith("#"):
                continue
            if "/" in line and line.count("/") >= 2:
                try:
                    d = line.split("/")[1]
                    if d: 
                        domains.append(d)
                        continue
                except: pass
            if line.startswith("0.0.0.0 "): line = line.split()[1]
            if line.startswith("127.0.0.1 "): line = line.split()[1]
            if " " in line or "/" in line: continue
            domains.append(line)
        print(f"    {len(domains)}")
        return domains
    except Exception as e:
        print(f"    FAIL {e}")
        return []

def main():
    all_domains = []
    for url in BLOCKLISTS:
        all_domains.extend(get_domains(url))

    print(f"\nBefore dedup: {len(all_domains)}")
    unique = sorted(set(all_domains))
    print(f"After dedup: {len(unique)} - NO LIMIT")

    OUTPUT_TXT.write_text("\n".join(unique) + "\n")
    with open(OUTPUT_TXT, 'rb') as f_in:
        with gzip.open(OUTPUT_GZ, 'wb', compresslevel=9) as f_out:
            f_out.writelines(f_in)

    print(f"TXT: {OUTPUT_TXT.stat().st_size/1024/1024:.2f} MB")
    print(f"GZ: {OUTPUT_GZ.stat().st_size/1024/1024:.2f} MB")

    pathlib.Path("stats.txt").write_text(
        f"Date: {datetime.utcnow().isoformat()}\n"
        f"Domains: {len(unique)}\n"
        f"TXT: {OUTPUT_TXT.stat().st_size/1024:.1f} KB\n"
        f"GZ: {OUTPUT_GZ.stat().st_size/1024:.1f} KB\n"
        f"Mode: UNLIMITED\n"
    )

if __name__ == "__main__":
    main()
