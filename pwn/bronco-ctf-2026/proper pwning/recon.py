#!/usr/bin/env python3
"""
Recon script used to derive the offsets in exploit.py from the binary itself,
without objdump/gdb/readelf installed (pwntools' ELF() + capstone only).

Run: python recon.py ./proper
"""
import sys
from pwn import ELF, context
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

context.arch = "amd64"


def main(path="proper"):
    e = ELF(path, checksec=False)
    md = Cs(CS_ARCH_X86, CS_MODE_64)

    print("=== symbols ===")
    for s in ("win", "gate1", "gate2", "gate3", "treasure_room", "main"):
        print(f"{s:15s} {hex(e.symbols[s])}")

    print("\n=== gate1/gate2/gate3/treasure_room prologues (find buffer offsets) ===")
    for fn in ("gate1", "gate2", "gate3", "treasure_room"):
        addr = e.symbols[fn]
        code = e.read(addr, 0x60)
        print(f"---- {fn} @ {hex(addr)} ----")
        for i in md.disasm(code, addr):
            print(f"  {hex(i.address)}  {i.mnemonic} {i.op_str}")
            if i.mnemonic == "call" and "gets" not in (i.op_str or "") and i.address - addr > 0x20:
                break

    print("\n=== hunting a bare `ret` gadget near win() (for stack re-alignment) ===")
    win = e.symbols["win"]
    for a in range(win, win + 0x200):
        if e.read(a, 1) == b"\xc3":
            print(f"ret gadget @ {hex(a)}")
            break


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "proper")
