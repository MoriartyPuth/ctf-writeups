#!/usr/bin/env python3
"""
Full exploration / investigation script for The Keymaster challenge.

This is the raw investigative tool used during the CTF to probe
every corner of the page — HTML, JS bundles, SVGs, /N.txt files,
response headers, data attributes, and more. Covers far more than
just the final extraction.
"""

import re
import urllib.request
from urllib.error import HTTPError

BASE = "https://broncosec.com"
PAGE = f"{BASE}/BroncoCTF"


def fetch(url):
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        return f"HTTP {e.code}"
    except Exception as e:
        return f"Error: {e}"


print("=" * 60)
print("1. FETCH MAIN PAGE")
print("=" * 60)
html = fetch(PAGE)
print(f"   Page size: {len(html)} bytes")

print("\n" + "=" * 60)
print("2. CHECK FOR KEY-LIKE TEXT IN HTML (pat: 'N - fragment')")
print("=" * 60)
for m in re.finditer(r'(\d)\s*[-–—]\s*([a-zA-Z0-9_{}]+)', html):
    print(f"   Key {m.group(1)}: {m.group(2)}")

print("\n" + "=" * 60)
print("3. CHECK ALL TITLE ATTRIBUTES")
print("=" * 60)
for m in re.finditer(r'title="([^"]*)"', html):
    val = m.group(1)
    if any(c.isalnum() for c in val):
        print(f"   title: {val}")

print("\n" + "=" * 60)
print("4. CHECK ALL ALT ATTRIBUTES")
print("=" * 60)
for m in re.finditer(r'alt="([^"]*)"', html):
    val = m.group(1)
    if val:
        print(f"   alt: {val}")

print("\n" + "=" * 60)
print("5. CHECK ALL HREFS FOR KEY PARAMETERS")
print("=" * 60)
for m in re.finditer(r'href="([^"]*)"', html):
    val = m.group(1)
    if "KEY" in val.upper() or "key" in val.lower():
        print(f"   href: {val}")

print("\n" + "=" * 60)
print("6. CHECK /N.txt FILES (1-10)")
print("=" * 60)
for n in range(1, 11):
    url = f"{BASE}/{n}.txt"
    resp = fetch(url)
    if resp and resp != "HTTP 404" and "Error" not in resp:
        print(f"   [{n}.txt] {resp.strip()}")
    elif "404" in str(resp):
        print(f"   [{n}.txt] 404")
    else:
        print(f"   [{n}.txt] {resp[:200]}")

print("\n" + "=" * 60)
print("7. FETCH JS BUNDLES AND SEARCH FOR KEY FRAGMENTS")
print("=" * 60)
js_bundles = set(re.findall(r'/_next/static/chunks/([a-f0-9]+\.js)', html))
for js_file in sorted(js_bundles):
    url = f"{BASE}/_next/static/chunks/{js_file}"
    js = fetch(url)
    for m in re.finditer(r'(\d)\s*[-–—]\s*([a-zA-Z0-9_{}]+)', js):
        print(f"   [{js_file}] Key {m.group(1)}: {m.group(2)}")

print("\n" + "=" * 60)
print("8. CHECK SVG FILES")
print("=" * 60)
svg_files = set(re.findall(r'(/[a-zA-Z0-9_-]+\.svg)', html))
for svg in sorted(svg_files):
    url = f"{BASE}{svg}"
    content = fetch(url)
    for m in re.finditer(r'[Kk][Ee][Yy]', content):
        ctx = content[max(0, m.start() - 30):m.end() + 100]
        print(f"   [{svg}] {ctx}")

print("\n" + "=" * 60)
print("9. CHECK RESPONSE HEADERS")
print("=" * 60)
req = urllib.request.Request(PAGE)
try:
    with urllib.request.urlopen(req) as resp:
        for h, v in resp.headers.items():
            if any(kw in h.lower() for kw in ["key", "flag", "bronco", "hint"]):
                print(f"   {h}: {v}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("10. CHECK DATA ATTRIBUTES")
print("=" * 60)
for m in re.finditer(r'data-[\w-]+="([^"]*)"', html):
    val = m.group(1)
    if len(val) > 2 and any(c.isalpha() for c in val):
        print(f"   data-*: {val}")

print("\n" + "=" * 60)
print("11. ASSEMBLE FLAG")
print("=" * 60)
keys = {
    1: "bronco{h", 2: "3y_y0u_f", 3: "0und_th3",
    4: "m_4ll_w1", 5: "th_4b501", 6: "ut31y_n0",
    7: "_w0rr135", 8: "_4t_411}",
}
flag = "".join(keys[i] for i in sorted(keys))
print(f"   Flag: {flag}")
print(f"   Decoded: hey you found them all with absolutely no worries at all")
