#!/usr/bin/env python3
"""Automated key extraction for The Keymaster challenge.

Usage: python extract_keys.py
"""

import re
import urllib.request

BASE = "https://broncosec.com"
keys = {}

# Key 1 & 8: From visible page text
print("[*] Fetching page HTML...")
req = urllib.request.Request(f"{BASE}/BroncoCTF")
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode("utf-8", errors="replace")

for m in re.finditer(r'\b[18]\s*[-–—]\s*([a-zA-Z0-9_{}]+)', html):
    text = m.group(1)
    if text == "bronco{h":
        keys[1] = text
        print(f"  [+] Key 1: {text}")
    elif text == "_4t_411}":
        keys[8] = text
        print(f"  [+] Key 8: {text}")

# Key 3: title attribute on the Join button
print("[*] Searching HTML attributes...")
match = re.search(r'title="3\s*[-–—]\s*([^"]+)"', html)
if match:
    keys[3] = match.group(1)
    print(f"  [+] Key 3: {keys[3]}")

# Key 6: URL parameter
match = re.search(r'KEY=6-([^"&\s]+)', html)
if match:
    keys[6] = match.group(1)
    print(f"  [+] Key 6: {keys[6]}")

# Key 7: /7.txt
print("[*] Fetching /7.txt...")
req = urllib.request.Request(f"{BASE}/7.txt")
try:
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode().strip()
        match = re.search(r'7\s*[-–—]\s*(\S+)', content)
        if match:
            keys[7] = match.group(1)
            print(f"  [+] Key 7: {keys[7]}")
except Exception as e:
    print(f"  [-] Error: {e}")

# Keys 2, 4, 5: JavaScript bundle
print("[*] Fetching JS bundle e785679bf8074938.js...")
req = urllib.request.Request(
    f"{BASE}/_next/static/chunks/e785679bf8074938.js"
)
with urllib.request.urlopen(req) as resp:
    js = resp.read().decode("utf-8", errors="replace")

for digit in ["2", "4", "5"]:
    match = re.search(rf'{digit}\s*[-–—]\s*([a-zA-Z0-9_]+)', js)
    if match:
        keys[int(digit)] = match.group(1)
        print(f"  [+] Key {digit}: {keys[int(digit)]}")

# Assemble and print flag
if len(keys) == 8:
    flag = "".join(keys[i] for i in sorted(keys))
    print(f"\n[*] All 8 keys found!")
    print(f"[*] Flag: {flag}")
    print(f"[*] Decoded: hey you found them all with absolutely no worries at all")
else:
    print(f"\n[-] Only found {len(keys)}/8 keys: {sorted(keys.keys())}")
