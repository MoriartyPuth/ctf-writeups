"""
Recover the Mirror Mirror flag.

mirror.py XOR-decodes an embedded byte blob against a keystream derived by
hashing the script's *own source code*. There's no real vulnerability here,
we just need to reproduce verify()'s key derivation exactly and run it once
against the real mirror.py file:

    pivot         = src.index("MIRROR_SURFACE_DO_NOT_SCRATCH")
    specular_map  = sha256(src[pivot:pivot+300]).digest()      # 32-byte key
    flag[i]       = blob[i] ^ specular_map[i % 32] ^ "MirrorMirror"[i % 12]

The sys.gettrace()/frame-name/__name__ checks in verify() are anti-debugger
flavor only -- they don't affect the math, so we can just recompute the XOR
directly in a throwaway script instead of running the target under a
debugger.

Usage:
    python solve_mirror.py
"""
import hashlib

SRC_PATH = r'..\mirror.py'

src = open(SRC_PATH, 'r').read()
pivot = src.index("MIRROR_SURFACE_DO_NOT_SCRATCH")
specular_map = hashlib.sha256(src[pivot:pivot + 300].encode()).digest()

blob = [17, 241, 10, 247, 215, 233, 146, 221, 156, 40, 37, 198, 153, 173, 10,
        103, 20, 56, 232, 116, 208, 121, 53, 12, 122, 86, 127, 164, 109, 62,
        88, 200, 127, 234, 5]

looking_glass = "MirrorMirror"
flag = ""
for i, b in enumerate(blob):
    reflection_byte = specular_map[i % len(specular_map)] ^ ord(looking_glass[i % len(looking_glass)])
    flag += chr(b ^ reflection_byte)

print("FLAG:", flag)
