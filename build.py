import gzip
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set

# Source filter lists
SOURCES: List[str] = [
    "https://adaway.org/hosts.txt",
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
    "https://easylist.to/easylist/easylist.txt",
]

OUTPUT_DIR = "output"
OUTPUT_TXT = os.path.join(OUTPUT_DIR, "deduped.txt")
OUTPUT_GZ = os.path.join(OUTPUT_DIR, "deduped.gz")


def fetch_url(url: str) -> List[str]:
    """Fetch an adblock list and split into stripped lines."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; AdBlockAggregator/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8", errors="ignore")
            return content.splitlines()
    except Exception as e:
        print(f"[!] Warning: Failed fetching {url}: {e}")
        return []


def is_valid_rule(line: str) -> bool:
    """Filter out empty lines and comments."""
    if not line:
        return False
    if line.startswith(("!", "#", "[", "%")):
        return False
    return True


def clean_line(line: str) -> str:
    """Normalize line by stripping surrounding whitespace."""
    return line.strip()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    seen_rules: Set[str] = set()
    deduped_rules: List[str] = []

    print("[*] Downloading lists...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_url, url): url for url in SOURCES}
        for future in as_completed(futures):
            url = futures[future]
            lines = future.result()
            print(f"[+] Loaded {len(lines):,} lines from {url}")

            for raw_line in lines:
                cleaned = clean_line(raw_line)
                if is_valid_rule(cleaned) and cleaned not in seen_rules:
                    seen_rules.add(cleaned)
                    deduped_rules.append(cleaned)

    print(f"\n[*] Unique rules: {len(deduped_rules):,}")

    header = (
        "! Title: Combined Deduped Filterlist\n"
        f"! Total Rules: {len(deduped_rules)}\n"
        "! ----------------------------------------\n"
    )

    full_content = header + "\n".join(deduped_rules) + "\n"

    # 1. Plain text format: deduped.txt
    print(f"[*] Writing text to {OUTPUT_TXT}...")
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write(full_content)

    # 2. Gzip format: deduped.gz
    print(f"[*] Writing gzip to {OUTPUT_GZ}...")
    with gzip.open(OUTPUT_GZ, "wt", encoding="utf-8") as f_gz:
        f_gz.write(full_content)

    print("[✓] Finished generating deduped.txt and deduped.gz")


if __name__ == "__main__":
    main()
