#!/usr/bin/env python3
"""Preprocess hosts/domain blocklists into a sorted truncated-FNV-1a hash blob
for the ESP32-C3 ad-blocker. Hashes live in flash and are binary-searched on the
device, so no PSRAM is needed.

HASH_BYTES MUST match the firmware (src/main.cpp). 5 bytes (40-bit) keeps
~0 collisions up to ~500k domains while fitting half a million in <3 MB.

Usage: build_blocklist.py [out.bin] [src ...]
  src = local file or URL. With none given, downloads a balanced daily-driver set
  (StevenBlack base + Hagezi Pro) ~= 200k domains: blocks ads/trackers/malware
  but leaves WhatsApp/Instagram/social/messaging working.

  For the aggressive "test the limits" build (~500k, also blocks social/messaging):
    build_blocklist.py blocklist.bin \\
      https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling-porn-social/hosts \\
      https://raw.githubusercontent.com/hagezi/dns-blocklists/main/domains/ultimate.txt
"""
import sys, os, math, urllib.request

HASH_BYTES = 5                          # 40-bit hashes -- must match firmware
MASK = (1 << (HASH_BYTES * 8)) - 1
FNV_OFFSET = 0xcbf29ce484222325
FNV_PRIME  = 0x100000001b3
U64 = (1 << 64) - 1

# Daily driver that FITS alongside dual-OTA firmware slots (~250k domain budget):
# ads + trackers + malware, WhatsApp/social keep working. ~140k domains / 0.67 MB.
# Want more (up to ~250k)? swap light.txt -> pro.txt is 370k and ONLY fits the
# single-app (no-OTA) partition table.
DEFAULT_SOURCES = [
     'https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt',            
    'https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/wildcard/pro.plus-onlydomains.txt',
    'https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt',
    'https://gitlab.com/quidsup/notrack-blocklists/-/raw/master/trackers.list?ref_type=heads',
    'https://raw.githubusercontent.com/bongochong/CombinedPrivacyBlockLists/refs/heads/master/NoFormatting/BlacklistedDomains.txt',
    'https://big.oisd.nl/domainswild2',
    'https://raw.githubusercontent.com/ShadowWhisperer/BlockLists/refs/heads/master/Lists/Tracking',
    'https://raw.githubusercontent.com/ShadowWhisperer/BlockLists/refs/heads/master/Lists/Ads',
    'https://raw.githubusercontent.com/ShadowWhisperer/BlockLists/refs/heads/master/Lists/Wild_Ads',
    'https://raw.githubusercontent.com/ShadowWhisperer/BlockLists/refs/heads/master/Lists/Wild_Tracking',
    'https://raw.githubusercontent.com/ShadowWhisperer/BlockLists/refs/heads/master/Lists/Chat',
    'https://phishing.army/download/phishing-army-domains.txt',
    'https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/refs/heads/master/generated/hosts_full',
    'https://blocklistproject.github.io/Lists/alt-version/ads-nl.txt',
    'https://blocklistproject.github.io/Lists/alt-version/ransomware-nl.txt',
    'https://blocklistproject.github.io/Lists/alt-version/tracking-nl.txt',
    'https://blocklistproject.github.io/Lists/alt-version/smart-tv-nl.txt',
    'https://hblock.molinero.dev/hosts_domains.txt',
    'https://raw.githubusercontent.com/AdguardTeam/cname-trackers/master/data/combined_disguised_trackers_justdomains.txt',
   
'https://v.firebog.net/hosts/AdguardDNS.txt',
    'https://v.firebog.net/hosts/Admiral.txt',
    'https://v.firebog.net/hosts/Easylist.txt',
    'https://v.firebog.net/hosts/Easyprivacy.txt',
    'https://v.firebog.net/hosts/Prigent-Ads.txt',
 
'https://raw.githubusercontent.com/Spam404/lists/master/main-blacklist.txt',
    'https://v.firebog.net/hosts/Prigent-Malware.txt',
   
'https://v.firebog.net/hosts/static/w3kbl.txt',
    'https://badblock.celenity.dev/wildcards-no-star/brave.txt',
    'https://badblock.celenity.dev/wildcards-no-star/apple.txt',
    'https://badblock.celenity.dev/wildcards-no-star/mozilla.txt',
    'https://badblock.celenity.dev/wildcards-no-star/personal.txt',
    'https://badblock.celenity.dev/wildcards-no-star/monitoring.txt',
    'https://badblock.celenity.dev/wildcards-no-star/badblock.txt',
    'https://paulgb.github.io/BarbBlock/blacklists/domain-list.txt',
    'https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Other%20domains%20versions/BrowseWebsitesWithoutLoggingInDomains.txt',
    'https://raw.githubusercontent.com/austinheap/sophos-xg-block-lists/master/dan-pollock-someonewhocares-org.txt',
    'https://raw.githubusercontent.com/austinheap/sophos-xg-block-lists/master/mvps-hosts-file.txt',
    'https://pgl.yoyo.org/adservers/serverlist.php?hostformat=nohtml&showintro=1&mimetype=plaintext',
    'https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling/hosts',
    'https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/refs/heads/master/SmartTV.txt',
    'https://raw.githubusercontent.com/anudeepND/blacklist/refs/heads/master/adservers.txt',
    'https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt',
    'https://raw.githubusercontent.com/lassekongo83/Frellwits-filter-lists/refs/heads/master/lists/main-hosts.txt',
   
'https://codeberg.org/ZingyAwesome/easylists-for-pihole/raw/branch/master/cookies.txt',

'https://codeberg.org/ZingyAwesome/easylists-for-pihole/raw/branch/master/easylist.txt',
'https://codeberg.org/ZingyAwesome/easylists-for-pihole/raw/branch/master/easyprivacy.txt',
'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/tif.medium-onlydomains.txt',
'https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt',
'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/fake-onlydomains.txt',
'https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/dyndns-onlydomains.txt',
'https://blocklistproject.github.io/Lists/alt-version/redirect-nl.txt',

'https://blocklistproject.github.io/Lists/alt-version/basic-nl.txt',
'https://lists.purge.cc/mobile.txt',
'https://lists.purge.cc/devices.txt',
'https://lists.purge.cc/general.txt',
'https://lists.purge.cc/apple.txt',
'https://lists.purge.cc/microsoft.txt',
'https://raw.githubusercontent.com/FiltersHeroes/KADhosts/refs/heads/master/KADomains.txt',


]

def fnv(b: bytes) -> int:
    h = FNV_OFFSET
    for c in b:
        h = ((h ^ c) * FNV_PRIME) & U64
    return h & MASK                      # truncate to HASH_BYTES

def norm(d: str) -> str:
    d = d.strip().lower().lstrip('|*.').rstrip('.^/')
    return d[4:] if d.startswith('www.') else d

def read_source(src: str) -> str:
    if os.path.exists(src):
        return open(src, errors='ignore').read()
    print(f'  downloading {src} ...', file=sys.stderr)
    return urllib.request.urlopen(src, timeout=180).read().decode('utf-8', 'ignore')

def main():
    args = sys.argv[1:]
    out = args[0] if args else 'blocklist.bin'
    sources = args[1:] if len(args) > 1 else DEFAULT_SOURCES

    domains = set()
    for src in sources:
        try:
            data = read_source(src)
        except Exception as e:
            print(f'  !! skipped {src}: {e}', file=sys.stderr); continue
        for line in data.splitlines():
            line = line.split('#', 1)[0].strip()
            if not line or line[0] in '!/':
                continue
            parts = line.split()
            d = parts[1] if len(parts) >= 2 and parts[0] in ('0.0.0.0','127.0.0.1','::1','::') \
                else parts[0] if len(parts) == 1 else None
            if d:
                d = norm(d)
                if '.' in d and ' ' not in d:
                    domains.add(d)

    hashes = sorted(fnv(d.encode()) for d in domains)
    collisions = len(hashes) - len(set(hashes))
    uniq = sorted(set(hashes))                       # one entry per distinct hash
    with open(out, 'wb') as f:
        for h in uniq:
            f.write(h.to_bytes(HASH_BYTES, 'little'))

    n, size = len(uniq), len(uniq) * HASH_BYTES
    print(f'source domains   : {len(domains):,}')
    print(f'hash entries     : {n:,}  ({HASH_BYTES}-byte / {HASH_BYTES*8}-bit)')
    print(f'collisions       : {collisions}  (domains sharing a hash -> over-block)')
    print(f'flash blob       : {size:,} bytes  ({size/1024/1024:.2f} MB)  -> {out}')
    print(f'lookup           : ~{math.ceil(math.log2(max(n,2)))} reads/query')

if __name__ == '__main__':
    main()
