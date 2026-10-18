#!/usr/bin/env python3
# build.py - download + dedup + merge + gzip
import requests, gzip, pathlib
from datetime import datetime

BLOCKLISTS = [
     'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/ultimate-onlydomains.txt',
    'https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt',
    'https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt',
     'https://hblock.molinero.dev/hosts_domains.txt',
     'https://raw.githubusercontent.com/AdguardTeam/cname-trackers/master/data/combined_disguised_trackers_justdomains.txt',
     'https://v.firebog.net/hosts/AdguardDNS.txt',
     'https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt',
    ]
OUTPUT_TXT = pathlib.Path("blocklist.txt")
OUTPUT_GZ = pathlib.Path("blocklist.txt.gz")

def get_domains(url):
    print(f"[+] {url.split('/')[-1]}")
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        domains = []
        for line in r.text.splitlines():
            line = line.strip().lower()
            if not line or line.startswith("#"):
                continue
            # handle dnsmasq format local=/domain/ or address=/domain/
            if "/" in line and line.count("/") >= 2:
                try:
                    domain = line.split("/")[1]
                    if domain:
                        domains.append(domain)
                        continue
                except:
                    pass
            # handle hosts format
            if line.startswith("0.0.0.0 "):
                line = line.split()[1]
            if line.startswith("127.0.0.1 "):
                line = line.split()[1]
            
            if " " in line or "/" in line:
                continue
            domains.append(line)
        print(f"    {len(domains)} domains")
        return domains
    except Exception as e:
        print(f"    FAILED: {e}")
        return []

def main():
    all_domains = []
    for url in BLOCKLISTS:
        all_domains.extend(get_domains(url))

    print(f"\nTotal before dedup: {len(all_domains)}")

    unique = sorted(set(all_domains))
    
    # Limit for 128MB router safety - remove if you want full
    MAX_DOMAINS = 250000
    if len(unique) > MAX_DOMAINS:
        print(f"Trimming to {MAX_DOMAINS} for router safety")
        unique = unique[:MAX_DOMAINS]

    print(f"Total after dedup: {len(unique)}")
    
    # Write plain
    OUTPUT_TXT.write_text("\n".join(unique) + "\n")
    print(f"Saved {OUTPUT_TXT} - {OUTPUT_TXT.stat().st_size/1024/1024:.2f} MB")

    # Write gzip -9
    with open(OUTPUT_TXT, 'rb') as f_in:
        with gzip.open(OUTPUT_GZ, 'wb', compresslevel=9) as f_out:
            f_out.writelines(f_in)
    
    print(f"Saved {OUTPUT_GZ} - {OUTPUT_GZ.stat().st_size/1024/1024:.2f} MB")

    # stats file for release notes
    pathlib.Path("stats.txt").write_text(
        f"Date: {datetime.utcnow().isoformat()}\n"
        f"Count: {len(unique)}\n"
        f"Raw size: {OUTPUT_TXT.stat().st_size/1024:.1f} KB\n"
        f"Gz size: {OUTPUT_GZ.stat().st_size/1024:.1f} KB\n"
    )

if __name__ == "__main__":
    main()
