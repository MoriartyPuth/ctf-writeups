# Mirror Mirror

| | |
|---|---|
| **Category** | Reverse Engineering |
| **Flag** | `bronco{wh0_1s_th3_f@ir3st_r3v3rs3r}` |

> I've been told that this magic mirror will only clear when I give it the flag. Can you
> help me figure out what I should say?

## Files

- [`mirror.py`](./mirror.py) — the challenge source, distributed as plain Python

## Tools

- Python 3 + `hashlib` (standard library only — no disassembler needed, the challenge is
  a Python script)

## Approach

### Step 1 — Read the source

```python
def verify(attempt):
    try:
        with open(__file__, 'r') as f:
            src = f.read()
            pivot = src.index("MIRROR_SURFACE_DO_NOT_SCRATCH")
            specular_map = hashlib.sha256(src[pivot:pivot+300].encode()).digest()
    except (FileNotFoundError, ValueError):
        return "The mirror has been shattered."

    if sys.gettrace() is not None:
        return "Nice try, but the glass turns opaque. No observers allowed!"
    if sys._getframe().f_code.co_name != 'verify' or __name__ != "__main__":
        return "You are looking at the mirror from a distorted angle."

    blob = [17, 241, 10, 247, ...]          # 35 bytes
    looking_glass = "MirrorMirror"
    flag = ""
    for i, b in enumerate(blob):
        reflection_byte = specular_map[i % len(specular_map)] ^ ord(looking_glass[i % len(looking_glass)])
        flag += chr(b ^ reflection_byte)

    if attempt == flag:
        return "The reflection clears!"
    return "All you see is a distorted blur. (Wrong Password)"
```

Three things jump out:

1. **The key isn't hardcoded.** `specular_map` is a SHA-256 digest of 300 bytes of the
   script's *own source*, read fresh from disk (`open(__file__)`) starting at the literal
   string `"MIRROR_SURFACE_DO_NOT_SCRATCH"` — which, notably, only appears **once** in the
   whole file: inside the very `src.index(...)` call that looks it up. That string is
   effectively acting as a self-referential salt/marker rather than an actual constant
   anywhere else in the file.
2. **The anti-debug checks are decoration.** `sys.gettrace()`, the frame co_name check,
   and the `__name__` check exist purely to discourage stepping through `verify()` in a
   debugger or importing it from another module — the flavor text's "no observers
   allowed" / "distorted angle" messages. None of them affect the XOR math, so they can
   simply be ignored: reimplement the computation standalone instead of executing the
   guarded function.
3. **It's a pure XOR stream cipher**: `flag[i] = blob[i] ^ specular_map[i % 32] ^
   "MirrorMirror"[i % 12]`. XOR is its own inverse, so recomputing this expression *is*
   solving for the flag — `verify()` never needs to run at all.

### Step 2 — Reproduce the hash and decode

[`scripts/solve_mirror.py`](./scripts/solve_mirror.py) opens the real challenge file,
finds the same pivot, hashes the same 300-byte window, and XOR-decodes `blob` exactly as
`verify()` would — all without touching the guarded function:

```python
src = open('mirror.py', 'r').read()
pivot = src.index("MIRROR_SURFACE_DO_NOT_SCRATCH")
specular_map = hashlib.sha256(src[pivot:pivot + 300].encode()).digest()

blob = [17, 241, 10, 247, 215, 233, 146, 221, 156, 40, 37, 198, 153, 173, 10,
        103, 20, 56, 232, 116, 208, 121, 53, 12, 122, 86, 127, 164, 109, 62,
        88, 200, 127, 234, 5]
looking_glass = "MirrorMirror"

flag = "".join(
    chr(b ^ specular_map[i % 32] ^ ord(looking_glass[i % 12]))
    for i, b in enumerate(blob)
)
```

```
$ python scripts/solve_mirror.py
FLAG: bronco{wh0_1s_th3_f@ir3st_r3v3rs3r}
```

Because the hash is computed over the file exactly as distributed (300 bytes starting at
the marker, byte-for-byte), the only requirement for this to work is having an unmodified
copy of `mirror.py` — which we do.

## Flag

```
bronco{wh0_1s_th3_f@ir3st_r3v3rs3r}
```

"Who is the fairest reverser?" — you are. 🪞
