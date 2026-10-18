import re, glob, pathlib

ADG = re.compile(r'^(@@)?\|\|([a-z0-9._-]+)\^?(\$.*)?$', re.I)
DOMAIN = re.compile(r'^[a-z0-9.-]+\.[a-z]{2,}$')

out = set()

# cat *.txt
for f in glob.glob("*.txt"):
    for raw in open(f, errors='ignore'):
        line = raw.strip()
        if not line: continue
        if line[0] in '#!': continue

        # 1. Try your ADG regex: ||domain^$...
        m = ADG.match(line)
        if m:
            if m.group(1): # @@ whitelist -> skip
                continue
            domain = m.group(2).lower()
            if DOMAIN.match(domain):
                out.add(domain)
            continue

        # 2. Hosts format
        if line.lower().startswith("0.0.0.0 "):
            line = line.split()[1]
        if line.lower().startswith("127.0.0.1 "):
            line = line.split()[1]

        # 3. Clean
        line = line.lower().strip()
        line = line.split()[0]  # drop extra columns
        if DOMAIN.match(line):
            out.add(line)

# sort -u > final.txt
with open("final.txt","w") as w:
    w.write("\n".join(sorted(out)) + "\n")

print(f"final.txt: {len(out)} unique")
