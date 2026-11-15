garb_hex = "96dbcaae807788b5e3abae8e91dc467bd6b5291094a33033c7f47fb66cccf6d41b2bc01426033a73f444fa44eb412e3ee249"
flag_hex = "2d4f326d141f0c75e1ff445d23b39880581c09e0585645eab8"
garb_enc = bytes.fromhex(garb_hex)
flag_enc = bytes.fromhex(flag_hex)
N = len(flag_enc)

def deterministic(element):
    newkey = 0
    for i in range(4):
        sub = (element >> (2 * i)) & 3
        sub = (sub & 1) ^ (sub >> 1)
        newkey += sub << (7 - i)
    return newkey & 0xF0

def scramble(key):
    nums = []
    for k in key:
        num = 0
        for i in range(8):
            num |= ((k & (1 << i)) >> i) << (7 - i)
        nums.append(num)
    return bytes(nums)

# For each position, find all valid (key, flag_char) pairs
all_candidates = []
for j in range(N):
    candidates = []
    for L1 in range(ord('a'), ord('z') + 1):
        k = garb_enc[j] ^ L1
        top4_1 = deterministic(k)
        for L2 in range(ord('a'), ord('z') + 1):
            ext1 = garb_enc[N + j] ^ L2
            if (ext1 & 0xF0) == top4_1:
                fc = scramble(bytes([k]))[0] ^ flag_enc[j]
                c = chr(fc)
                if 32 <= fc < 127:
                    candidates.append((k, c))
                break
    all_candidates.append(candidates)

import itertools

best = None
for combo in itertools.product(*all_candidates):
    flag = "".join(c for _, c in combo)
    if not flag.startswith("bronco{") or not flag.endswith("}"):
        continue
    if not all(c in 'abcdefghijklmnopqrstuvwxyz0123456789_{}' for c in flag):
        continue
    key = bytes(k for k, _ in combo)
    scrambled = scramble(key)
    decrypted = bytes(f ^ s for f, s in zip(flag_enc, scrambled))
    if decrypted.decode() == flag:
        if '3nough' in flag:
            best = flag
            break
print("Flag:", best if best else "not found")
