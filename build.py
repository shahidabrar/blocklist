import re
import requests
import pathlib
import subprocess
import glob

# Your regex
ADG = re.compile(r'^(@@)?\|\|([a-z0-9._-]+)\^?(\$.*)?$', re.I)
DOMAIN = re.compile(r'^[a-z0-9._-]+\.[a-z]{2,}$')

URLS = [
    'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/pro-onlydomains.txt',
    'https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt',
    'https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt',
    'https://hblock.molinero.dev/hosts_domains.txt',
    'https://v.firebog.net/hosts/AdguardDNS.txt',
    'https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt',
]

def clean_line(raw: str):
    line = raw.strip()
    if not line: return None
    if line[0] in '#!': return None

    m = ADG.match(line)
    if m:
        if m.group(1): return None
        domain = m.group(2).lower()
        return domain if DOMAIN.match(domain) else None

    # sed equivalent
    line = re.sub(r'^[ \t]+', '', line)
    line = re.sub(r'[ \t]+$', '', line)
    line = re.sub(r'^0\.0\.0\.0[ \t]+', '', line, flags=re.I)
    line = re.sub(r'^127\.0\.0\.1[ \t]+', '', line, flags=re.I)
    line = re.sub(r'^\|\|', '', line)
    line = re.sub(r'\^.*$', '', line)
    line = re.sub(r'\$.*$', '', line)
    line = line.split()[0] if line else ''
    line = line.lower().strip()
    return line if DOMAIN.match(line) else None

out = set()
for url in URLS:
    print(f"GET {url}")
    try:
        r = requests.get(url, timeout=180)
        r.raise_for_status()
        count = 0
        for raw in r.text.splitlines():
            d = clean_line(raw)
            if d:
                out.add(d)
                count += 1
        print(f" -> {count} domains")
    except Exception as e:
        print(f"FAIL {url}: {e}")

if not out:
    raise SystemExit("ERROR: No domains found, all URLs failed")

final = sorted(out)
pathlib.Path("final.txt").write_text("\n".join(final) + "\n")

# gzip
subprocess.run(["gzip", "-9", "-k", "-f", "final.txt"], check=True)
subprocess.run(["cp", "-f", "final.txt.gz", "final.gz"], check=True)

print(f"DONE: final.txt = {len(final)} lines")
print(f"Size: {pathlib.Path('final.txt').stat().st_size / 1024 / 1024:.2f} MB")
