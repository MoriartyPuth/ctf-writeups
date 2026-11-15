# Static Web Basic — auppCTF 2026 Writeup

**Category:** Web
**Points:** 75
**Difficulty:** Beginner ("This is really basic tbh. But yea, try harder lol")


## Flag

```
auppCTF{static_web_instance}
```

## TL;DR

```
GET /admin?key=letmein
```

`/admin` is a Flask route that checks a query parameter (`request.args.get('key') == 'letmein'`) and returns the flag directly on success, "Access denied" otherwise. No headers, cookies, auth, path traversal, or crypto involved. The entire challenge is solvable in under 10 requests once you know to look for a query-parameter gate instead of a network/auth-level one.

This writeup covers **both** the clean solve path and the full messy real path taken (many hours, thousands of requests, several completely wrong technique categories) — the wrong turns are documented because they're the more useful part for understanding *why* this "basic" challenge resisted so much effort.

---

## Challenge Info

```
Static Web Basic
75 POINTS
Secret auppCTF 2026

This is really basic tbh. But yea, try harder lol

Connection Info: <IP>:<PORT>   (dynamic — new instance per connection, ~15 min lifetime)
```

---

## Tools Used

- `curl` — primary recon tool, request crafting, header inspection
- Python 3 — `urllib.request` + `concurrent.futures.ThreadPoolExecutor` for all bulk scanning
- `itsdangerous` + `flask` (session forging attempt)
- `flask-unsign` / `flask-unsign-wordlist` (56,982-entry weak-secret-key wordlist)
- SecLists — `Discovery/Web-Content/common.txt` (~4,750 words), `Discovery/Web-Content/raft-small-directories.txt` (~20,100 words)
- Claude in-app Browser tool — real browser rendering / network tab verification, no dev server needed
- Raw Python `socket` — to rule out curl-level request normalization
- `taskkill` — cleanup of stale background scans when CTF instances expired mid-scan
- WebSearch / WebFetch — checked for public writeups / leaked source, checked a shared NahamConCTF writeup for pattern-matching

---

## Part 1 — What Actually Worked (Clean Solve Path)

### Step 1: Baseline recon

```bash
curl -v http://<host>:<port>/
```

Response:
```
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.12.13
Content-Type: text/html; charset=utf-8
Content-Length: 15

Try harder 😉
```

Confirmed via hex dump that this is *exactly* 15 bytes — `"Try harder "` + the raw 4-byte UTF-8 encoding of U+1F609 (😉), nothing appended, no hidden bytes, no HTML at all. This isn't a page to "view-source" — it's a flavor-text string literal in the Flask route. Don't linger here; move to enumeration immediately.

### Step 2: Directory brute force

```bash
gobuster dir -u http://<host>:<port>/ -w common.txt
# (we used a hand-rolled Python threaded scanner with the same wordlist)
```

Every path 404s **except**:

```
GET /admin → 200 "Access denied"
```

That a plain word returns `200` instead of `404` is the signal to stop and think, not to keep scanning.

### Step 3: Read the `/admin` response like a detective, not a scanner

```bash
curl -i http://<host>:<port>/admin
```

```
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.12.13
Content-Type: text/html; charset=utf-8
Content-Length: 13

Access denied
```

The critical detail: **no `WWW-Authenticate` header**. If this were real HTTP Basic Auth, the server would reply `401` with a challenge header. Getting a friendly `200 Access denied` instead means this is hand-rolled application logic — literally an `if` statement inside the Flask view function. For a challenge explicitly labeled "basic," the simplest thing a beginner-level author would reach for is `request.args.get(...)`, not session/cookie logic, not IP-address logic, not cryptographic signing.

### Step 4: Guess parameter name and value *together*

The mistake to avoid: don't test "50 parameter names" and "50 passwords" as two separate sweeps. Test them as **pairs**.

```bash
for param in key password pass pwd secret token code pin auth access; do
  for val in admin password letmein 123456 secret changeme; do
    curl -s -G --data-urlencode "$param=$val" http://<host>:<port>/admin
  done
done
```

Hit:
```
?key=letmein → auppCTF{static_web_instance}
```

`letmein` is a classic "textbook example" weak password — exactly the kind of value a challenge author would pick for a "really basic" gate.

**Total request count for the clean path: well under 100.**

---

## Part 2 — Everything That Went Wrong (and Why It Seemed Reasonable at the Time)

This challenge had **zero solves** at the time it was being worked, despite being labeled the easiest tier. The following is a full account of the wrong turns, in order, with the reasoning that led to each one — because the reasoning wasn't unreasonable, it was just answering the wrong question.

### 2.1 — Anchoring on IP/header-based access control

**Reasoning:** `/admin` → `Access denied`, `200` status, no auth challenge. The single most common beginner-tutorial pattern for this exact behavior is:
```python
if request.remote_addr == '127.0.0.1':
    return FLAG
return "Access denied"
```
This is *also* an extremely common real pattern, so it was a reasonable first hypothesis.

**What was tried:**
- `X-Forwarded-For`, `X-Real-IP`, `CF-Connecting-IP`, `True-Client-IP`, `X-Originating-IP`, `Client-IP`, `X-Remote-IP`, `X-Remote-Addr`, `X-Forwarded`, `X-Forwarded-Host`, `X-ProxyUser-Ip`, `X-Custom-IP-Authorization`, and RFC 7239 `Forwarded: for=127.0.0.1` — all with `127.0.0.1` / `localhost` values
- HTTP Basic Auth: `admin:admin`, then later a 13-credential sweep (`admin:password`, `admin:toor`, `root:root`, etc.)
- 8 different cookie name/value pairs (`admin=true`, `role=admin`, `is_admin=true`, etc.)
- 4 `Host` header variants
- `Referer` header
- User-Agent spoofing (browser UA vs curl vs empty)
- Case sensitivity (`/Admin`, `/ADMIN`, `/AdMiN`) — confirmed routing is case-sensitive, ruled out as irrelevant
- **150 repeated identical requests** to rule out a random-chance/probabilistic access grant

**Result:** 100% dead. Every single technique returned identical `Access denied`, re-verified on multiple fresh instances to rule out stale-container false negatives.

**Why this failed:** the check was never IP- or header-based at all. No amount of header manipulation was ever going to work, because the actual condition being checked was a query string value. This whole branch was answering "how do I spoof a trusted network position" when the real question was "what does this app's `if` statement compare against."

### 2.2 — Large-scale directory/file enumeration

**Reasoning:** The paid hint literally said "Directories maybe?" — taken at face value, this meant "there are more hidden paths to find."

**What was tried:**
- SecLists `common.txt` (4,751 words) at root — found nothing but `/admin`
- Discovered `/static/<file>` exists (Flask's default static route) via an OPTIONS-based route-detection scan (OPTIONS returns `200` + `Allow` header even for a nonexistent file, which distinguishes "route exists" from "route doesn't exist" independent of file presence)
- Scanned `/static/` with `common.txt` + curated flag-like filenames — completely empty (0 hits)
- SecLists `raft-small-directories.txt` (20,115 words) at root — still only `/admin`
- Re-ran the OPTIONS route-detection scan across the **full** 20,115-word list as prefixes (i.e., "does `/<word>/<file>` match any route pattern at all") — only `/static` matched, nothing else
- Path traversal on `/static/` — `../`, URL-encoded `%2e%2e%2f`, tested with `curl --path-as-is` specifically to defeat curl's own client-side dot-segment normalization — blocked cleanly by Werkzeug's `safe_join`
- Nested subdirectory guesses under `/static/` (`/static/secret/flag.txt` etc.) — nothing

**Result:** Confirmed, thoroughly, that no file or directory exists anywhere on this server except `/` and `/admin`. The `/static/` folder is genuinely empty — it's Flask boilerplate (registered automatically on every Flask app whether used or not), not a deliberate clue.

**Why this failed:** the hint was either a deliberate red herring (consistent with the challenge's trolling tone — "Try harder 😉") or referred to something never correctly decoded. Either way, it sent significant effort toward a technique category (path discovery) that had nothing to do with the actual bug (a query parameter).

### 2.3 — Multi-segment path combinatorics

**Reasoning:** Single-segment brute force can only ever find routes like `/admin`. A Flask route can be *any* literal string, including something like `/get/the/flag` — and no single-word wordlist would ever find that, since `/get` alone matching nothing tells you nothing about whether `/get/the/flag` exists. "Directories" (plural) was re-read as "multiple path segments."

**What was tried:** ~100-word curated list (admin, secret, flag, api, panel, backdoor, congrats, etc.) × itself = 10,000 two-segment combinations, tested against a live instance with 150-way concurrency.

**Result:** 0 hits, 0 connection errors (clean scan, so the null result is trustworthy).

**Why this failed:** same root cause as 2.2 — chasing "more paths" when the bug wasn't path-shaped at all.

### 2.4 — Werkzeug/Flask-specific technique checks

Cheap, fast checks run to rule out common framework-level footguns:
- Werkzeug interactive debugger (`?__debugger__=yes&cmd=resource&f=style.css`) — confirmed debug mode is **off**
- Silent redirect-following masking a real 301/308 route — checked explicitly with `%{redirect_url}`, none found
- Joke/troll-themed path names matching the challenge's voice (`/nope`, `/gotcha`, `/wink`, `/tryagain`, `/keep_trying`, etc.) — nothing
- `/admin/*` subpaths (`/admin/secret`, `/admin/flag`, `/admin/panel`, etc.) — all clean 404s, confirming `/admin` has zero nested routes and isn't a `<path:...>` catch-all

**Result:** all dead ends, but cheap enough (single-digit seconds each) that they were worth ruling out.

### 2.5 — Real browser + raw socket verification

**Reasoning:** rule out any possibility that `curl` was hiding or normalizing something a real client would see differently.

- Loaded the target in an actual browser (Claude's in-app Browser tool) — identical body text, empty page title, exactly one network request (no favicon fetch, no hidden JS-triggered calls)
- Sent a hand-crafted raw HTTP/1.1 request over a raw Python `socket` (bypassing curl entirely) — byte-for-byte identical response to curl's output

**Result:** Ruled out client-tooling artifacts entirely. Whatever the bug was, it wasn't something curl was obscuring.

### 2.6 — Searching for public source / similar writeups

- WebSearch for `"auppCTF" 2026` and `auppCTF github "static web" challenge` — no public footprint found (confirmed this is a private/new event, as expected from "Secret auppCTF 2026")
- Fetched and read a shared NahamConCTF writeup ([shellbr3ak.medium.com](https://shellbr3ak.medium.com/nahamconctf-web-challenges-b54bf2d153f8)) covering 8 web challenges (regex injection, XXE, SQLi, SSRF-via-render, Django SECRET_KEY leak via git history, blind XSS, SSTI) — none matched this challenge's shape. One entry (a `robots.txt` pointing to a directory with listing enabled) confirmed "directory listing" as a legitimate basic technique category in general, but our `robots.txt` was a clean 404 and no listing-enabled directory was ever found here.

**Result:** No transferable lead, but useful to rule out "this is a known template challenge."

### 2.7 — Flask session cookie forging (the deepest technique attempted)

**Reasoning:** A genuinely common Flask CTF pattern is an `/admin` route gated by `session.get('username') == 'admin'`, bypassed by *forging* a signed session cookie locally (Flask never needs to have issued you one first) if the app's `SECRET_KEY` is weak or a known default.

**What was done:**
- Installed `flask-unsign` and `flask-unsign-wordlist` (56,982 known/leaked Flask secret keys, sourced from GitHub/GitLab/StackOverflow/searchcode)
- Wrote a script replicating Flask's own session serialization (`itsdangerous.URLSafeTimedSerializer`, salt `"cookie-session"`, HMAC-SHA1 key derivation — matching `flask.sessions.SecureCookieSessionInterface` exactly) to **locally** sign candidate cookies for arbitrary secret keys, avoiding the overhead of spinning up a full Flask app per guess
- First pass: ~44 hand-picked common secrets × 9 payload shapes (`{"username": "admin"}`, `{"admin": True}`, etc.) — no hits
- Prepared (but did not complete, redirected mid-task) a run against the full 56,982-key wordlist with concurrent requests

**Result:** Inconclusive — never fully executed against the large wordlist, because the "don't go deep" guidance from the challenge author arrived around this point and correctly suggested this whole direction was over-engineered for a "basic" challenge. In hindsight this assessment was correct: the real bug required no cryptography at all.

### 2.8 — Checking the CTF platform's own page source

**Reasoning:** Given how watertight the target server was, and the trolling tone of the whole challenge, it seemed plausible the flag might be hidden directly in the CTFd-style platform's challenge-description HTML (a known pattern where beginner/joke challenges hide the answer in plain sight to punish people who jump straight to "hacking" instead of reading carefully).

**What was tried:** Attempted to view-source the platform's `/challenges` page directly — hit an authentication wall (the platform requires login). Did not attempt to log in (credential handling is out of scope for the assistant). The user checked manually (page source + DevTools Network tab on the API response) and found nothing unusual.

**Result:** Dead end, but a reasonable one given the evidence at the time (near-total server-side dead end + a genuinely common CTF trope).

### 2.9 — mitmproxy / TLS check

**Reasoning:** A throwaway question ("have you tried mitmproxy?") prompted a check of something that had never actually been verified in this entire investigation: whether the port spoke HTTPS at all.

**What was tried:** `curl -k https://<host>:<port>/` against the same port.

**Result:** TLS handshake fails immediately — plain HTTP only, as expected for a bare Werkzeug dev server. Ruled out in under a minute.

### 2.10 — The actual breakthrough

The turning point wasn't a new technique — it was **auditing previously incomplete work**. A relayed comment from the challenge author ("it doesn't require deep technique but sometimes we think too hard") prompted a full stop and a review of what had *actually* been tested versus what had only been *assumed* tested.

That review surfaced the real gap: a properly-designed query-parameter fuzzing script (covering `/admin` with a wide set of parameter names) had been written but its execution was interrupted before it ever ran. The smaller follow-up test that replaced it tested the wrong path (`/` instead of `/admin`) **and** the wrong style of values (SSRF/LFI-style: URLs and paths like `admin`, `/admin`, `http://127.0.0.1/admin` — probing for a *structural* bug) instead of credential-style values (`letmein`, `password`, `admin123` — probing for a *literal string comparison*). These are two different hypotheses that happen to both use "query parameters" as the delivery mechanism, and only one of them had ever actually been tested.

Re-running the correct version — parameter names paired with weak-password values, against `/admin` specifically — found `?key=letmein` on essentially the first properly-scoped attempt.

---

## Root Cause Analysis — Why a "Basic" Challenge Took So Long

1. **Anchoring bias.** The first plausible-sounding hypothesis (IP/header-based access control) was reasonable, but once adopted, effort went into generating *more variations within that frame* (more spoofing headers, then cookies, then crypto) rather than stepping back to question the frame itself.
2. **Hint over-trust.** "Directories maybe?" was treated as a literal instruction rather than weighed against the mounting evidence (two exhaustive wordlist scans) that it wasn't panning out. In a challenge this trollish, a hint being misleading should have been considered earlier.
3. **Not ranking hypotheses by cost.** A 75-point "basic" challenge should have exhausted the cheapest possible hypotheses (a dozen GET requests with guessed parameters) completely before spending effort on expensive ones (25,000+ word scans, 56,000-key crypto forging, 10,000-combo path fuzzing). The cost ordering was effectively inverted.
4. **An interrupted test was never properly redone.** Once a test is mentally filed as "tried, didn't work," it's easy to forget it was actually cut short or scoped incorrectly. The fix was periodically auditing "what did I actually run to completion" rather than "what do I remember trying."
5. **Two similar-looking hypotheses got merged into one mental bucket.** "Query parameter causes a structural bug" (SSRF/LFI) and "query parameter is a literal password gate" both fall under "test query parameters," but require testing completely different *values*. Marking the bucket "tested" after only covering one of the two sub-hypotheses produced a false sense of completeness.

## One-Line Takeaway

> When a "basic" challenge gates something behind plain text like `"Access denied"` with no proper auth challenge header, assume hand-rolled `if` logic over a query parameter before assuming anything network- or crypto-level — and test *guessable credential values* against it before testing *structural/injection-style* values, since they require different test designs even though both live under "query parameter fuzzing."

---

## Appendix — Full Technique Inventory (for reference)

| # | Technique | Category | Result |
|---|-----------|----------|--------|
| 1 | Root page recon (curl, hex dump) | Recon | No hidden content |
| 2 | Directory brute force, 4,751 words | Recon | Found `/admin` |
| 3 | `/admin` header inspection | Recon | No `WWW-Authenticate` — hand-rolled logic inferred |
| 4 | 12+ IP-spoofing headers | Bypass | Dead |
| 5 | HTTP Basic Auth (14 credential pairs) | Bypass | Dead |
| 6 | 8 cookie variants | Bypass | Dead |
| 7 | 4 Host header variants, Referer, UA spoofing | Bypass | Dead |
| 8 | 150x repeated request (randomness check) | Bypass | Dead — fully deterministic |
| 9 | Case sensitivity (`/Admin`, `/ADMIN`) | Recon | Confirmed case-sensitive, irrelevant |
| 10 | `common.txt` under `/static/` | Recon | Empty static folder |
| 11 | `raft-small-directories.txt` at root (20,115 words) | Recon | Only `/admin` |
| 12 | OPTIONS-based route detection (full wordlist as prefixes) | Recon | Only `/static` exists |
| 13 | Path traversal on `/static/` (raw + encoded + `--path-as-is`) | Bypass | Blocked (`safe_join`) |
| 14 | 10,000-combo 2-segment path brute force | Recon | Dead |
| 15 | Werkzeug debugger check | Bypass | Debug mode off |
| 16 | Redirect-masking check | Recon | No redirects anywhere |
| 17 | Joke/troll-themed path names | Recon | Dead |
| 18 | `/admin/*` subpath enumeration | Recon | No nested routes |
| 19 | Real browser rendering + network tab | Verification | Identical to curl |
| 20 | Raw socket request | Verification | Identical to curl |
| 21 | Public writeup / source search | Recon | No public footprint |
| 22 | Flask session cookie forging (44 secrets × 9 payloads) | Bypass | Dead (small scale) |
| 23 | Full 56,982-key wordlist forging | Bypass | Prepared, not completed |
| 24 | CTFd platform page-source check | Recon | Nothing found (by user) |
| 25 | HTTPS/TLS check on same port | Recon | Plain HTTP only |
| 26 | **Query param + weak password pairing on `/admin`** | **Bypass** | **✅ `?key=letmein` → flag** |

**Final tally:** ~40,000+ HTTP requests sent across the full investigation; the successful one was among the last ~150 sent.
