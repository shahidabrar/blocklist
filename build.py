import requests, pathlib, re

DOMAIN = re.compile(r'^[a-z0-9._-]+\.[a-z]{2,}$')
URLS = [
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt",
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/wildcard/pro.plus-onlydomains.txt",
    "https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.wildcards",
     "https://v.firebog.net/hosts/AdguardDNS.txt",
    "https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/source/hosts.txt",
"https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling/hosts",
    "https://raw.githubusercontent.com/bongochong/CombinedPrivacyBlockLists/master/NoFormatting/BlacklistedDomains.txt",
  
    
    
    
    
    
    
]

def clean(s: str):
    s = s.strip().lower()
    if not s or s[0] in '#!':
        return None
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
            if d:
                out.add(d)
    except Exception as e:
        print(f"FAIL {url} - {e}")

pathlib.Path("only.txt").write_text("\n".join(sorted(out)) + "\n")
print(f"DONE {len(out)} -> only.txt")
