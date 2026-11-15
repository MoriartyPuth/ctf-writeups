# Negative Bread — Bronco CTF Writeup

**Category:** Binary Exploitation / Reverse Engineering    
**Flag:** `bronco{th3_b4nk_0w3s_m3_m0n3y}`

---

## Description

```
Your account starts at $100. The flag costs $1,000,000. Deposits are capped.
Withdrawals can't go below zero.

No strings attached.

We don't even need to guard the vault. This bank is impenetrable!
```

We are given a single ELF binary called `bank` — a menu-driven banking program. The goal is to get our balance above $1,000,000 to buy the flag.

---

## Tools Used

- **file** — identify binary type
- **strings** — extract embedded strings and the flag
- **objdump** — disassemble the binary
- **GDB / manual tracing** — understand control flow

---

## Step 1 — Reconnaissance

### Check the binary

```bash
$ file bank
bank: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), ... not stripped
```

It is a 64-bit ELF, dynamically linked, **not stripped** — function names are preserved.

### Extract strings

```bash
$ strings bank
```

Key strings found:

```
[!] TRANSACTION APPROVED
bronco{th3_b4nk_0w3s_m3_m0n3y}
Welcome! Starting balance: $%d
Looking for the flag? It costs $%u.
Balance : $%d
[1] Deposit          (max $%d per txn, %d remaining)
[2] Withdraw
[3] Dispute a Charge (up to $%u, one-time)
[4] Invest           (fixed 0.5%% return)
[5] Buy Flag         ($%u)
[6] Exit
```

Already we see the flag string is embedded. But the challenge is to trigger the `win()` function legally through the program's logic.

---

## Step 2 — Reverse Engineering

Disassemble `main` and `win`:

```bash
$ objdump -d bank
```

### `win()` function (0x4011d6)

```asm
4011d6: lea    0xe23(%rip),%rax        # "TRANSACTION APPROVED"
4011ed: lea    0xe34(%rip),%rax        # flag string
```

Simply prints the flag and returns. Called from the "Buy Flag" branch of `main`.

### Stack layout in `main()`

| Offset | Variable        | Initial Value |
|--------|-----------------|---------------|
| -0x4   | balance         | 100 (0x64)    |
| -0x8   | dispute_used    | 0 (no)        |
| -0xc   | deposits_left   | 3             |
| -0x10  | invest_return   | (uninit)      |
| -0x14  | menu_choice     | (read)        |
| -0x18  | amount          | (read)        |
| -0x1a  | basis_points    | (read, short) |

### Menu overview

| Option | Action | Constraints |
|--------|--------|-------------|
| 1 | Deposit     | amount > 0, <= 10000, 3 max |
| 2 | Withdraw    | amount > 0, balance >= amount |
| 3 | Dispute     | one-time, abs(amount) <= 999999, balance += amount |
| 4 | Invest      | basis_points 1–500, balance += (balance * bps) / 10000 |
| 5 | Buy Flag    | balance > 999999 → call `win()` |
| 6 | Exit        | |

### How `Buy Flag` works (address 0x401713)

```asm
401716: cmp    $0xf423f,%eax     ; compare balance to 999999
40171b: jbe    401731            ; if balance <= 999999, "insufficient funds"
40171d: call   win               ; otherwise, print flag
```

The check is: **balance > 999999** (i.e., balance >= 1,000,000).

---

## Step 3 — Finding the Bug

The challenge name is **"Negative Bread"** and the hint says *"simplest bug"*.

Analyzing each option:

- **Deposit** — capped at $10,000 per transaction, only 3 uses. Max = $30,000 added = $100,300 total. Not enough.
- **Withdraw** — checks `amount > 0` and `balance >= amount`. No integer underflow possible.
- **Invest** — 0.5% return max at 500 basis points. Too slow.
- **Dispute** — one-time, `abs(amount) <= 999999`, then **adds the original amount** to balance.

The **Dispute** option is the exploit path.

### Dispute decompiled logic

```asm
4015e2: mov    -0x18(%rbp),%eax     ; load amount (user input)
4015e5: mov    %eax,%edx
4015e7: neg    %edx                  ; negate
4015e9: cmovns %edx,%eax            ; if -amount >= 0, eax = -amount (i.e., abs)
4015ec: cmp    $0xf423f,%eax        ; abs(amount) <= 999999 ?
4015f1: jle    401611               ; if yes, proceed

401611: mov    -0x18(%rbp),%eax     ; load ORIGINAL amount
401614: add    %eax,-0x4(%rbp)      ; balance += original_amount
```

The check computes `abs(amount) <= 999999` — but then adds the **original signed amount** to the balance!

### The fencepost error

- Maximum dispute check passes: **999,999** (0xF423F)
- Flag price: **1,000,000** (0xF4240)
- Starting balance: **$100**

Disputing $999,999 adds it directly to balance:

```
100 + 999999 = 1,000,099
```

Since 1,000,099 > 999,999, the Buy Flag check passes.

---

## Step 4 — Exploitation

### Reproduction steps

```
1. Run the binary
2. Choose option [3] — Dispute a Charge
3. Enter: 999999
4. Choose option [5] — Buy Flag
5. Flag is printed
```

### Automated session

```bash
$ echo -e "3\n999999\n5\n6" | ./bank
```

Output:

```
+------------------------------------------+
|       BRONCO NATIONAL BANK  v3.0         |
|   "We take security seriously."         |
+------------------------------------------+
Welcome! Starting balance: $100
Looking for the flag? It costs $1000000.
Good luck.
--------------------------------------------
Balance : $100
...
> Enter the charge amount you are disputing: $[+] Dispute processed. Refund of $999999 applied.
    New balance: $1000099
...
> [!] TRANSACTION APPROVED
bronco{th3_b4nk_0w3s_m3_m0n3y}
```

### Python exploit script

```python
#!/usr/bin/env python3
from pwn import *

p = process("./bank")

p.sendlineafter(b"> ", b"3")
p.sendlineafter(b"$ ", b"999999")
p.sendlineafter(b"> ", b"5")
p.recvuntil(b"TRANSACTION APPROVED")
flag = p.recvline().strip().decode()
print(f"Flag: {flag}")
p.close()
```

---

## Root Cause

The dispute function has a **fencepost error**: the advertised maximum in the UI is $1,000,000 but the internal bound check is `<= 999999`, one less. Combined with a starting balance of $100, the player can reach $1,000,099 — just enough to cross the flag purchase threshold of $1,000,000.

---

## Key Takeaways

1. **Fencepost / off-by-one errors** are everywhere — even in security-critical "cannot go below zero" logic.
2. **Always check bounds against the actual action performed**, not the displayed description.
3. **`abs()` validation is not the same as range validation** — the absolute value check passes negative numbers, but the subsequent addition uses the original signed value.
4. **Never trust the menu; reverse the binary.**
