import requests, pathlib, subprocess, re

DOMAIN = re.compile(r'^[a-z0-9._-]+\.[a-z]{2,}$')

URLS = [
    "https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.wildcards",
    "https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt",
    "https://hblock.molinero.dev/hosts_domains.txt",
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt",
    "https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/ultimate-onlydomains.txt",
  
def clean(s: str):
    s = s.strip().lower()
    if not s or s[0] in '#!': return None
    # handle hosts format + adguard ||domain^
    s = re.sub(r'^0\.0\.0\.0[ \t]+', '', s)
    s = re.sub(r'^127\.0\.0\.1[ \t]+', '', s)
    s = re.sub(r'^\|\|', '', s)
    s = re.sub(r'\^.*$', '', s)
    s = re.sub(r'\$.*$', '', s)
    s = s.split()[0].strip('.')
    return s if DOMAIN.match(s) else None

out = set()
for url in URLS:
    print(f"GET {url}")
    try:
        txt = requests.get(url, timeout=180).text
        for line in txt.splitlines():
            d = clean(line)
            if d: out.add(d)
    except Exception as e:
        print(f"FAIL {e}")

pathlib.Path("final.txt").write_text("\n".join(sorted(out)) + "\n")
subprocess.run(["gzip", "-9", "-k", "-f", "final.txt"], check=True)
subprocess.run(["cp", "-f", "final.txt.gz", "final.gz"], check=True)
print(f"DONE {len(out)} domains")
