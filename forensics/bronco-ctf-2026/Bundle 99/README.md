# Bundle 99

**Category:** Forensics / File Assembly

**Flag:** `bronco{3ve4yth1ng_1s_aw3s0me}`

## Challenge

The challenge provides `lego_bricks_challenge.zip` containing 250 files named `part_000` through `part_249`, each containing a fragment of data. They need to be reassembled in the correct order.

## Solution

1. Extract the zip:
```bash
unzip lego_bricks_challenge.zip -d parts/
```

2. The parts are named with zero-padded numeric suffixes (`part_000`, `part_001`, ..., `part_249`). Sort them numerically and concatenate:

```bash
for i in $(seq -w 0 249); do cat "parts/part_$i" >> assembled; done
```

Or in Python:
```python
with open('assembled', 'wb') as out:
    for i in range(250):
        with open(f'part_{i:03d}', 'rb') as f:
            out.write(f.read())
```

3. The concatenated output is a valid zip file. Extract it:

```bash
unzip assembled
```

4. Read the flag:

```bash
cat flag.txt
# bronco{3ve4yth1ng_1s_aw3s0me}
```

## Key Takeaway

File-splitting challenges are straightforward when fragments have sequential numeric names — just sort and concatenate. The `.part_XXX` naming scheme directly encodes the order.
