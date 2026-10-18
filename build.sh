#!/bin/bash
set -e

# URLs
URLS=(
  "https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/pro-onlydomains.txt"
  "https://github.com/badmojr/1Hosts/releases/download/latest/1hosts-Lite_domains.txt"
  "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt"
  "https://hblock.molinero.dev/hosts_domains.txt"
  "https://v.firebog.net/hosts/AdguardDNS.txt"
  "https://raw.githubusercontent.com/bigdargon/hostsVN/refs/heads/master/filters/adservers-all.txt"
)

mkdir -p raw
rm -f raw/*.txt

echo "Downloading..."
for url in "${URLS[@]}"; do
  echo "GET $url"
  curl -L --fail --connect-timeout 30 --max-time 120 -o "raw/list_$RANDOM.txt" "$url" || echo "FAIL $url"
done

echo "Processing with your cat pipeline..."
cat raw/*.txt | \
  grep -v '^[#!]' | \
  grep -v '^$' | \
  sed -e 's/^[ \t]*//' \
      -e 's/[ \t]*$//' \
      -e 's/^0\.0\.0\.0[ \t]*//' \
      -e 's/^127\.0\.0\.1[ \t]*//' \
      -e 's/^||//' \
      -e 's/\^.*$//' \
      -e 's/\$.*$//' | \
  grep -E '^[a-z0-9._-]+\.[a-z]{2,}$' | \
  tr 'A-Z' 'a-z' | \
  sort -u > final.txt

# Also handle ADG @@ whitelist (skip @@ lines)
grep -vi '^@@' final.txt | sort -u -o final.txt

# Create gz
gzip -9 -k -f final.txt
cp -f final.txt.gz final.gz

echo "--- DONE ---"
wc -l final.txt
ls -lh final.txt final.gz final.txt.gz
