import re, requests, pathlib, subprocess, glob

# Your ADG regex
ADG = re.compile(r'^(@@)?\|\|([a-z0-9._-]+)\^?(\$.*)?$', re.I)
DOMAIN = re.compile(r'^[a-z0-9.-]+\.[a-z]{2,}$')

URLS = [
    'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/pro-onlydomains.txt',
    'https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt',
    'https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt',
    'https://hblock.molinero.dev/hosts_domains.txt',
    'https://v.firebog.net/hosts/AdguardDNS.txt',
    'https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt',
]

def clean_line(raw: str):
    """Implements: cat | grep -v '^[#!]' | grep -v '^$' | sed ... | grep -E | tr A-Z a-z"""
    line = raw.strip()
    if not line:
        return None
    if line[0] in '#!':
        return None
    
    # ADG regex: ^(@@)?\|\|([a-z0-9._-]+)\^?(\$.*)?$
    m = ADG.match(line)
    if m:
        if m.group(1): # @@ whitelist -> skip
            return None
        domain = m.group(2).lower()
        return domain if DOMAIN.match(domain) else None

    # sed: s/^[ \t]*// , s/[ \t]*$// , s/^0.0.0.0[ \t]*// , s/^127.0.0.1[ \t]*// , s/^||// , s/\^.*$// , s/\$.*$//
    line = re.sub(r'^[ \t]+', '', line)
    line = re.sub(r'[ \t]+$', '', line)
    line = re.sub(r'^0\.0\.0\.0[ \t]+', '', line, flags=re.I)
    line = re.sub(r'^127\.0\.0\.1[ \t]+', '', line, flags=re.I)
    line = re.sub(r'^\|\|', '', line)
    line = re.sub(r'\^.*$', '', line)
    line = re.sub(r'\$.*$', '', line)
    line = line.split()[0] if line else ''
    line = line.lower().strip()

    # grep -E '^[a-z0-9.-]+\.[a-z]{2,}$'
    return line if DOMAIN.match(line) else None

out = set()
for url in URLS:
    print(f"GET {url}")
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        for raw in r.text.splitlines():
            d = clean_line(raw)
            if d:
                out.add(d)
    except Exception as e:
        print(f"FAIL {url}: {e}")

# sort -u > final.txt
final = sorted(out)
pathlib.Path("final.txt").write_text("\n".join(final) + "\n")
print(f"final.txt: {len(final)} unique")

# gzip to final.txt.gz and final.gz
subprocess.run(["gzip", "-9", "-k", "-f", "final.txt"], check=True)
subprocess.run(["cp", "-f", "final.txt.gz", "final.gz"], check=True)
print("Created final.txt, final.txt.gz, final.gz")
