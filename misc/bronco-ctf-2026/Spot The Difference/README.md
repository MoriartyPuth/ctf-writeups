# Spot The Difference

**Category:** Misc

**Flag:** `bronco{y@yyy_Y0u_f0und_m3!!}`

> My friend said that she updated file1 to send me a top-secret message, but
> I don't get it. File2 is still just a bunch of random characters?

## Challenge

Two attachments, `file1.txt` and `file2.txt`, each formatted as one
character per line (as if piped through `cat -n`). Both look like random
base64-alphabet noise — letters, digits, `_`, `-`, `{`, `}`, `@`, `[`, `]`.
`file1.txt` has 350 lines; `file2.txt` has 351.

## Reasoning

The prompt frames it as "spot the difference" between the two blobs, so the
obvious first move is `diff`. That's a trap:

```
$ diff file1.txt file2.txt | head
2,3c2,3
< e
< c
---
> E
> C
9c9
< g
---
> b
...
```

Running a plain `diff` reports on the order of 100 changed lines. Almost
all of them are pure **case flips** (`e`→`E`, `V`→`v`, `L`→`l`, ...) —
harmless noise designed to bury the real signal. On top of that, `file2`
has **one more line than file1**, so every line-diff after the insertion
point is bogus (`diff` is comparing shifted content against unshifted
content once the extra line throws off the alignment).

So there are really two problems to solve, in order:

1. **Find where the extra character was inserted**, and remove it so the
   two files are the same length and properly aligned again.
2. **Filter out the case-flip noise** from the real edits, by comparing
   case-*insensitively* — real signal changes the letter/digit entirely,
   noise only changes its case.

### Step 1 — locate the insertion

`file2` is `file1` plus one inserted character somewhere. Brute-force it:
for every candidate index `k`, delete `file2[k]` and count how many lines
match `file1` case-insensitively. The `k` that maximizes that score is
where the insertion happened.

```python
def find_insertion(a, b):
    best = None
    for k in range(len(b)):
        trial = b[:k] + b[k + 1:]
        score = sum(1 for x, y in zip(a, trial) if x.lower() == y.lower())
        if best is None or score > best[0]:
            best = (score, k)
    return best
```

This finds `k = 348` (0-indexed) — i.e. **file2 line 349**, which is a
`}` — with **323 / 350** lines then matching case-insensitively. That's a
92% match rate for essentially zero real effort, confirming the alignment
is right (a wrong `k` gives a much worse score).

### Step 2 — filter case-noise from real substitutions

With the extra `}` removed, re-run the comparison case-insensitively and
keep only the **27** positions that are still different — those are the
real edits, not case noise:

```python
b_aligned = b[:k] + b[k + 1:]
diffs = [(i, y) for i, (x, y) in enumerate(zip(a, b_aligned)) if x.lower() != y.lower()]
```

Reading `file2`'s character at each of those 27 positions, **in order**,
plus the inserted `}` slotted back into its true position, spells:

```
b r o n c o { y @ y y y _ Y 0 u _ f 0 u n d _ m 3 ! ! }
```

i.e. `bronco{y@yyy_Y0u_f0und_m3!!}` — leetspeak for *"yayyy, you found
me!!"* (`@`=a, `0`=o, `3`=e), with `bronco{...}` as the flag wrapper.

## PoC / Reproduction

```
$ python solve.py
file1: 350 lines, file2: 351 lines
best alignment: removing file2 line 349 ('}') gives 323/350 case-insensitive matches

27 genuine substitutions found (position, file1->file2):
  line 9: 'g' -> 'b'
  line 18: 'd' -> 'r'
  line 37: '6' -> 'o'
  ...
  line 330: '5' -> '!'
  line 332: 'q' -> '!'

recovered message: bronco{y@yyy_Y0u_f0und_m3!!}
```

`solve.py` and both input files are included in this folder — just run it,
no arguments needed.

## Tools

- Python 3 (stdlib only — file I/O, byte comparison)
- The key idea (delete-and-rescore to locate a single insertion) is a tiny
  bespoke edit-distance heuristic, not a library — a full Levenshtein/LCS
  diff (e.g. Python's `difflib`) gets confused by the sheer amount of
  case-flip noise and doesn't cleanly surface the one real insertion the
  way this targeted search does.

## Key Takeaway

When a "spot the difference" file pair has way too many diff lines to be
the real signal, check for (a) noise that a case-*insensitive* comparison
would filter out, and (b) a length mismatch meaning the files are
mis-aligned rather than just edited in place. Fix the alignment first
(find the single insertion/deletion), *then* diff.
