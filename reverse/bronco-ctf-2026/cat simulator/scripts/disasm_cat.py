"""
Annotated x86-64 disassembler for cat-sim-linux.

Walks the ELF .text section with capstone, and for every `lea reg, [rip+disp]`
instruction resolves the RIP-relative target against .rodata and prints the
referenced string inline as a comment. This is what let us read the game's
flow (prompts, day loop, win/lose branches) directly from the disassembly
without a full decompiler.

Usage:
    python disasm_cat.py > dis.txt
"""
from elftools.elf.elffile import ELFFile
from capstone import *
import re

BIN = r'..\cat-sim-linux'

f = open(BIN, 'rb')
e = ELFFile(f)
secs = {s.name: s for s in e.iter_sections()}
text = secs['.text']
taddr = text['sh_addr']
tdata = text.data()
ro = secs['.rodata']
roaddr = ro['sh_addr']
rodata = ro.data()


def getstr(a):
    off = a - roaddr
    if 0 <= off < len(rodata):
        end = rodata.find(b'\0', off)
        return rodata[off:end].decode('latin1')
    return None


md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = True
insns = list(md.disasm(tdata, taddr))

for i in insns:
    line = f"0x{i.address:x}:\t{i.mnemonic}\t{i.op_str}"
    if i.mnemonic == 'lea' and 'rip' in i.op_str:
        m = re.search(r'\[rip \+ (0x[0-9a-f]+)\]', i.op_str) or \
            re.search(r'\[rip \- (0x[0-9a-f]+)\]', i.op_str)
        if m:
            disp = int(m.group(1), 16)
            if '-' in i.op_str.split('rip')[1].split(']')[0]:
                disp = -disp
            tgt = i.address + i.size + disp
            s = getstr(tgt)
            if s is not None:
                line += f'   ; "{s}"  @{hex(tgt)}'
    print(line)
