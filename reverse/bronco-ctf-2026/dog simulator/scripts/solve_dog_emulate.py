"""
Recover the Dog Simulator flag by emulating the finale flag-builder in Unicorn.

dog-sim-mac gates a NEON/SIMD flag-derivation block behind a large combo
state machine (score, bond, energy, per-action counters, two rolling hashes,
a "spoken word must echo the owner's name" check, etc -- see 0x100000e64
onward). Rather than hand-solving every branch of the 6-day combo puzzle,
we emulate just the flag-builder itself (0x100000ee8 - 0x1000011dc), which
takes three small integers -- mood (w22), bond (w25), energy (w26) -- runs
them through a vectorized 32-bit hash (murmur3-style finalizer, widened to
NEON lanes) to build a 24-byte keystream, and XORs it against constants
baked into __DATA_CONST/__const to produce the flag string.

The win-condition gate pins w25 (bond) to 24 exactly (score/action-count
checks force it). mood (w22) and energy (w26) have more freedom, so we brute
force small ranges of all three and keep any output that decodes to fully
printable ASCII -- the correct game-state is the only one that does.

Usage:
    python solve_dog_emulate.py
"""
from unicorn import *
from unicorn.arm64_const import *

BIN = r'..\dog-sim-mac'

raw = open(BIN, 'rb').read()
BASE = 0x100000000
MAPSZ = 0x8000  # covers __TEXT + __DATA_CONST/__const used by the routine

mu = Uc(UC_ARCH_ARM64, UC_MODE_LITTLE_ENDIAN)
mu.mem_map(BASE, MAPSZ)
mu.mem_write(BASE, raw[:MAPSZ])

STK = 0x200000000
mu.mem_map(STK, 0x100000)

# Entry: right after the "gremlin echo" + hash-checkpoint gates pass.
# Exit: right after the 24-byte flag buffer is fully written to [x29-0xe0].
START = 0x100000ee8
END = 0x1000011dc


def run(w22, w25, w26, w28=0x846ca68b):
    sp = STK + 0x80000
    x29 = sp + 0x1000
    mu.reg_write(UC_ARM64_REG_SP, sp)
    mu.reg_write(UC_ARM64_REG_X29, x29)
    mu.reg_write(UC_ARM64_REG_W22, w22 & 0xffffffff)
    mu.reg_write(UC_ARM64_REG_W25, w25 & 0xffffffff)
    mu.reg_write(UC_ARM64_REG_W26, w26 & 0xffffffff)
    mu.reg_write(UC_ARM64_REG_W28, w28 & 0xffffffff)
    mu.emu_start(START, END)
    return bytes(mu.mem_read(x29 - 0xe0, 24))


def printable(s):
    return all(0x20 <= c < 0x7f for c in s)


for w25 in range(0, 64):
    for w26 in range(0, 256):
        for w22 in range(0, 16):
            try:
                d = run(w22, w25, w26)
            except Exception:
                continue
            if printable(d):
                print(f"w22={w22} w25={w25} w26={w26} -> {d!r}")
