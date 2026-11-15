"""
Annotated ARM64 disassembler for dog-sim-mac (Mach-O).

Uses LIEF to parse Mach-O sections and capstone to disassemble __text.
Tracks `adrp` results per-register so a following `add`/`ldr` that completes
a PC-relative address can be resolved against __cstring and annotated
inline -- this is how the prompts, win-branch strings, and combo dialogue
were identified without a decompiler.

Usage:
    python disasm_dog.py > dis.txt
"""
import lief
from capstone import *

BIN = r'..\dog-sim-mac'

b = lief.parse(BIN)
raw = open(BIN, 'rb').read()
secs = {}
for s in b.sections:
    secs[s.name] = (s.virtual_address, s.offset, s.size)

tva, toff, tsz = secs['__text']
cva, coff, csz = secs['__cstring']
cstr = raw[coff:coff + csz]


def getcstr(va):
    off = va - cva
    if 0 <= off < len(cstr):
        end = cstr.find(b'\0', off)
        return cstr[off:end].decode('latin1')
    return None


md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
md.detail = True
code = raw[toff:toff + tsz]
insns = list(md.disasm(code, tva))

adrp = {}
for i in insns:
    line = f"0x{i.address:x}:\t{i.mnemonic}\t{i.op_str}"
    if i.mnemonic == 'adrp':
        parts = i.op_str.split(', ')
        reg = parts[0]
        imm = int(parts[1].replace('#', ''), 0)
        adrp[reg] = imm  # capstone already resolves the page target
    elif i.mnemonic in ('add', 'ldr') and len(i.op_str.split(', ')) >= 3:
        parts = i.op_str.split(', ')
        reg, srcreg = parts[0], parts[1]
        if srcreg in adrp and '#' in parts[2]:
            try:
                off = int(parts[2].replace('#', ''), 0)
            except ValueError:
                off = None
            if off is not None:
                tgt = adrp[srcreg] + off
                s = getcstr(tgt)
                line += f'   ; "{s}"' if s is not None else f'   ; @{hex(tgt)}'
    print(line)
