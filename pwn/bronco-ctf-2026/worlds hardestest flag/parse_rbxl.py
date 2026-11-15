#!/usr/bin/env python3
"""
Bronco CTF 2026 - "World's Hardestest Flag" (426 pts)

Extracts every Script/LocalScript/ModuleScript source from a binary Roblox
place file (.rbxl) without needing Roblox Studio.

Binary .rbxl format (relevant subset):
    8   bytes  magic "<roblox!"
    6   bytes  signature 89 FF 0D 0A 1A 0A
    2   bytes  version (u16, usually 0)
    ...        class count / instance count / reserved (padding out to a
               32-byte header total)
    then a stream of chunks, each:
        4   bytes  chunk name, e.g. "META", "SSTR", "INST", "PROP", "PRNT", "END\0"
        4   bytes  compressed length  (0 if stored uncompressed)
        4   bytes  uncompressed length
        4   bytes  reserved (always 0)
        N   bytes  payload - zstd-compressed if compressed length != 0

We only care about PROP chunks whose property name is "Source" - each one is:
    u32 classID
    (u32 len + bytes) property name   -> "Source"
    u8  type tag                       -> 0x01 = String for Roblox's binary format
    remaining bytes                    -> the raw Luau source text

Usage:
    python parse_rbxl.py mrdeh-hardestest.rbxl ./extracted_sources
"""
import struct
import sys
import os
import zstandard


def read_chunks(data: bytes):
    dctx = zstandard.ZstdDecompressor()
    pos = 32  # fixed header size in this file format revision
    chunks = []
    while pos + 16 <= len(data):
        name = data[pos:pos + 4]
        comp, uncomp, _reserved = struct.unpack("<III", data[pos + 4:pos + 16])
        pos += 16
        length = comp if comp else uncomp
        payload = data[pos:pos + length]
        pos += length

        raw = payload if comp == 0 else dctx.decompress(payload, max_output_size=uncomp)
        chunks.append((name.rstrip(b"\x00").decode("latin1"), raw))
        if name.startswith(b"END"):
            break
    return chunks


def read_rstr(buf: bytes, offset: int):
    (length,) = struct.unpack("<I", buf[offset:offset + 4])
    return buf[offset + 4:offset + 4 + length], offset + 4 + length


def extract_sources(chunks, outdir: str):
    os.makedirs(outdir, exist_ok=True)
    count = 0
    for name, raw in chunks:
        if name != "PROP":
            continue
        try:
            class_id = struct.unpack("<I", raw[:4])[0]
            prop_name, off = read_rstr(raw, 4)
        except (struct.error, IndexError):
            continue
        if prop_name != b"Source":
            continue

        type_tag = raw[off]
        source = raw[off + 1:]
        path = os.path.join(outdir, f"src_{count}_classid{class_id}.lua")
        with open(path, "wb") as f:
            f.write(source)
        print(f"[+] wrote {path} ({len(source)} bytes, type tag 0x{type_tag:02x})")
        count += 1
    print(f"[*] extracted {count} script source(s)")


def main():
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <file.rbxl> [outdir]")
        sys.exit(1)

    rbxl_path = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "extracted_sources"

    data = open(rbxl_path, "rb").read()
    assert data[:8] == b"<roblox!", "not a binary .rbxl file"

    chunks = read_chunks(data)
    print(f"[*] parsed {len(chunks)} chunks")
    extract_sources(chunks, outdir)


if __name__ == "__main__":
    main()
