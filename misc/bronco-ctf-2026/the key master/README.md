# The Keymaster

> **Challenge:** Find all 8 keys hidden on the BroncoCTF advertisement page  
> **Flag format:** `bronco{...}`  
> **Page:** https://broncosec.com/BroncoCTF  


---

## Overview

The BroncoCTF advertisement page at `https://broncosec.com/BroncoCTF` has 8 key fragments scattered across the page in various hiding spots — visible text, HTML attributes, URL parameters, downloadable files, and JavaScript bundles. Reconstructing the flag requires inspecting every layer of the page.

---

## The 8 Keys

### Key 1 — `bronco{h` (Visible Text)

The first key fragment is right there in the page footer / credits area along with the `8` key. Scrolling to the bottom of the page reveals:

```
1 - bronco{h
8 - _4t_411}
```

**Location:** Footer text, near the site credits.

---

### Key 2 — `3y_y0u_f` (JavaScript Bundle)

Found by searching the compiled Next.js JavaScript bundles. The key was hidden in:

```
/_next/static/chunks/e785679bf8074938.js
```

A plain text search for `2 - ` inside this JS file reveals:

```js
2 - 3y_y0u_f
```

**Location:** `https://broncosec.com/_next/static/chunks/e785679bf8074938.js`

---

### Key 3 — `0und_th3` (HTML Title Attribute)

Hovering over the **"Join the Competition"** button shows a tooltip. Inspecting the element reveals:

```html
<a title="3 - 0und_th3" href="https://broncoctf.ctfd.io/">Join the Competition</a>
```

**Location:** The `title` attribute on the registration link.

---

### Key 4 — `m_4ll_w1` (JavaScript Bundle)

Same JS bundle as Key 2:

```js
4 - m_4ll_w1
```

**Location:** `https://broncosec.com/_next/static/chunks/e785679bf8074938.js`

---

### Key 5 — `th_4b501` (JavaScript Bundle)

Again in the same JS bundle:

```js
5 - th_4b501
```

**Location:** `https://broncosec.com/_next/static/chunks/e785679bf8074938.js`

> The three JS-bundle keys all live sequentially in the same file.

---

### Key 6 — `ut31y_n0` (URL Parameter)

Inspecting links on the page reveals one with a suspicious query parameter:

```
?KEY=6-ut31y_n0
```

Appended to an internal navigation link.

**Location:** Hidden as a URL parameter on an anchor tag.

---

### Key 7 — `_w0rr135` (Separate Text File)

One of the download links on the page points to:

```
/7.txt
```

Fetching `https://broncosec.com/7.txt` returns:

```
7 - _w0rr135
```

**Location:** A standalone text file accessible at `/7.txt`.

Note that `/1.txt`, `/2.txt`, `/3.txt`, `/4.txt`, `/5.txt`, `/6.txt`, `/8.txt` all return 404 — only key 7 is a file.

---

### Key 8 — `_4t_411}` (Image Alt Text)

The large decorative image on the page (the BroncoCTF status display) has an `alt` attribute:

```html
<img alt="8 - _4t_411}" ... />
```

**Location:** The `alt` text on the main page image.

---

## Key Summary

| # | Fragment | Location |
|---|----------|----------|
| 1 | `bronco{h` | Visible footer text |
| 2 | `3y_y0u_f` | JS bundle `e785679bf8074938.js` |
| 3 | `0und_th3` | `title` attr on Join button |
| 4 | `m_4ll_w1` | JS bundle `e785679bf8074938.js` |
| 5 | `th_4b501` | JS bundle `e785679bf8074938.js` |
| 6 | `ut31y_n0` | URL param `?KEY=6-ut31y_n0` |
| 7 | `_w0rr135` | File `/7.txt` |
| 8 | `_4t_411}` | Image `alt` text |

---

## Flag Assembly

Concatenating in numerical order:

```
bronco{h  +  3y_y0u_f  +  0und_th3  +  m_4ll_w1  +  th_4b501  +  ut31y_n0  +  _w0rr135  +  _4t_411}
```

**Final flag:**

```
bronco{h3y_y0u_f0und_th3m_4ll_w1th_4b501ut31y_n0_w0rr135_4t_411}
```

**Decoded:** *"hey you found them all with absolutely no worries at all"*

Breaking down the leetspeak:

| Leet | Plain |
|------|-------|
| h3y | hey |
| y0u | you |
| f0und | found |
| th3m | them |
| 4ll | all |
| w1th | with |
| 4b501ut31y | absolutely |
| n0 | no |
| w0rr135 | worries |
| 4t 411 | at all |

---

## Tools Used

| Tool | Purpose |
|------|---------|
| **curl** / **python urllib** | Fetch the page, text files, JS bundles, and SVGs |
| **Browser DevTools** | Inspect element attributes (title, alt, href, data-*) |
| **Python re (regex)** | Search HTML, JS, and SVG content for key patterns |
| **Manual inspection** | Read visible page content, hover over links |

---

## Reproduction Steps

1. Open `https://broncosec.com/BroncoCTF` in a browser.
2. Scroll to the bottom — see **Key 1** and **Key 8** in visible text.
3. Check the `title` attribute on the "Join the Competition" button — **Key 3**.
4. Inspect links for `?KEY=` URL parameters — **Key 6**.
5. Visit `https://broncosec.com/7.txt` — **Key 7**.
6. Check the `alt` text on the page image — **Key 8**.
7. Fetch the JS bundle `/_next/static/chunks/e785679bf8074938.js` — search for `2 - `, `4 - `, `5 - ` to find **Keys 2, 4, 5**.
8. Concatenate all 8 fragments in order.

---

## Automated Script

```python
#!/usr/bin/env python3
"""Automated key extraction for The Keymaster challenge."""

import re
import urllib.request

BASE = "https://broncosec.com"
keys = {}

# Key 1 & 8: From page HTML
req = urllib.request.Request(f"{BASE}/BroncoCTF")
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode("utf-8", errors="replace")

for m in re.finditer(r'\b[18]\s*[-–—]\s*([a-zA-Z0-9_{}]+)', html):
    text = m.group(1)
    if text == "bronco{h":
        keys[1] = text
    elif text == "_4t_411}":
        keys[8] = text

# Key 3: title attribute
match = re.search(r'title="3\s*[-–—]\s*([^"]+)"', html)
if match:
    keys[3] = match.group(1)

# Key 6: URL parameter
match = re.search(r'KEY=6-([^"&\s]+)', html)
if match:
    keys[6] = match.group(1)

# Key 7: /7.txt
req = urllib.request.Request(f"{BASE}/7.txt")
with urllib.request.urlopen(req) as resp:
    content = resp.read().decode().strip()
    match = re.search(r'7\s*[-–—]\s*(\S+)', content)
    if match:
        keys[7] = match.group(1)

# Keys 2, 4, 5: JS bundle
req = urllib.request.Request(f"{BASE}/_next/static/chunks/e785679bf8074938.js")
with urllib.request.urlopen(req) as resp:
    js = resp.read().decode("utf-8", errors="replace")

for digit in ["2", "4", "5"]:
    match = re.search(rf'{digit}\s*[-–—]\s*([a-zA-Z0-9_]+)', js)
    if match:
        keys[int(digit)] = match.group(1)

# Assemble flag
flag = "".join(keys[i] for i in sorted(keys))
print(f"Flag: {flag}")
```

---

## Investigation Script

```python
#!/usr/bin/env python3
"""
Full exploration script used during the CTF to probe every
corner of the page: HTML, JS bundles, SVGs, /N.txt files,
response headers, data attributes, and more.
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
print("2. CHECK FOR KEY-LIKE TEXT (pat: 'N - fragment')")
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
print("5. CHECK HREFS FOR KEY PARAMETERS")
print("=" * 60)
for m in re.finditer(r'href="([^"]*)"', html):
    val = m.group(1)
    if "KEY" in val.upper():
        print(f"   href: {val}")

print("\n" + "=" * 60)
print("6. CHECK /N.txt FILES (1-10)")
print("=" * 60)
for n in range(1, 11):
    url = f"{BASE}/{n}.txt"
    resp = fetch(url)
    if "HTTP 404" not in resp and "Error" not in resp:
        print(f"   [{n}.txt] {resp.strip()}")
    else:
        print(f"   [{n}.txt] 404")

print("\n" + "=" * 60)
print("7. SEARCH JS BUNDLES FOR KEY FRAGMENTS")
print("=" * 60)
js_bundles = set(re.findall(r'/_next/static/chunks/([a-f0-9]+\.js)', html))
for js_file in sorted(js_bundles):
    url = f"{BASE}/_next/static/chunks/{js_file}"
    js = fetch(url)
    for m in re.finditer(r'(\d)\s*[-–—]\s*([a-zA-Z0-9_{}]+)', js):
        print(f"   [{js_file}] Key {m.group(1)}: {m.group(2)}")

print("\n" + "=" * 60)
print("8. CHECK SVG FILES FOR 'KEY' STRINGS")
print("=" * 60)
svg_files = set(re.findall(r'(/[a-zA-Z0-9_-]+\.svg)', html))
for svg in sorted(svg_files):
    content = fetch(f"{BASE}{svg}")
    if "KEY" in content.upper():
        print(f"   [{svg}] contains KEY string")

print("\n" + "=" * 60)
print("9. ASSEMBLE FLAG")
print("=" * 60)
keys = {
    1: "bronco{h", 2: "3y_y0u_f", 3: "0und_th3",
    4: "m_4ll_w1", 5: "th_4b501", 6: "ut31y_n0",
    7: "_w0rr135", 8: "_4t_411}",
}
flag = "".join(keys[i] for i in sorted(keys))
print(f"   Flag: {flag}")
print(f"   Decoded: hey you found them all with absolutely no worries at all")
```
