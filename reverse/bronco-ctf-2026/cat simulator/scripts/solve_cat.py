"""
Recover the Cat Simulator flag by emulating the decoder found at 0x1422.

The game only reaches the decoder when the player finishes all 5 days with
zero invalid ("stare blankly") choices, exactly 3x Talk / 1x Eat / 1x Scratch,
and the sum of the three typed talk-message lengths equal to 32. Meeting the
gate forces a hidden accumulator r15d to a fixed value of 21 -- and it is
*only* r15d that feeds the flag, so we don't need to actually play the game,
just reproduce r15d and run the keystream generator.

Reversed algorithm (from disassembly around 0x1422-0x14c9):
    seed  = r15d * 0x11                      # = 357 when r15d == 21
    H     = lowbias32_hash(seed ^ 0xc47b4cd0)  # integer hash (murmur-style)
    r9    = 0x9e3779b9                         # Weyl sequence constant
    r10   = 0x5a                               # stepping constant
    for k, prev in enumerate(ciphertext):      # ciphertext at .rodata+0x2390
        edi  = H ^ r9
        r9  -= 0x61c88647
        edi  = rotl(edi, k % 13)
        edi ^= r10
        r10 += 0x33
        edi ^= prev
        flag_byte = edi & 0xff

Usage:
    python solve_cat.py
"""
from elftools.elf.elffile import ELFFile

BIN = r'..\cat-sim-linux'

f = open(BIN, 'rb')
e = ELFFile(f)
ro = e.get_section_by_name('.rodata')
roaddr = ro['sh_addr']
rod = ro.data()

CT_VA = 0x2390
ct_off = CT_VA - roaddr
ct = rod[ct_off:ct_off + 64]
nul = ct.find(b'\0')
ct = ct[:nul]
print("ciphertext:", ct.hex())

M32 = 0xffffffff


def rotl(v, c):
    c &= 31
    v &= M32
    return ((v << c) | (v >> (32 - c))) & M32


def lowbias32(x):
    x &= M32
    x = (x ^ (x >> 16)) & M32
    x = (x * 0x7feb352d) & M32
    x = (x ^ (x >> 15)) & M32
    x = (x * 0x846ca68b) & M32
    x = (x ^ (x >> 16)) & M32
    return x


R15 = 21  # forced by the win-condition gate (score==45, talk=3/eat=1/scratch=1)
seed = (R15 * 0x11) & M32
H = lowbias32(seed ^ 0xc47b4cd0)

out = bytearray()
r9 = 0x9e3779b9
r10 = 0x5a
for k, prev in enumerate(ct):
    edi = H ^ r9
    r9 = (r9 - 0x61c88647) & M32
    edi = rotl(edi, k % 13)
    edi ^= r10
    r10 = (r10 + 0x33) & M32
    edi ^= prev
    out.append(edi & 0xff)

print("FLAG:", out.decode('latin1'))
