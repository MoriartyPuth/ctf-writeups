"""
Step 1 - Basic PNG forensics.

Parses the PNG chunk structure of each challenge file and checks for the
usual quick wins in a forensics challenge:
  - non-standard chunks (tEXt/zTXt/iTXt) that might hold a flag directly
  - data appended after the IEND chunk
  - anything odd in IHDR (dimensions, color type, interlacing)

Run from the `challenge/` directory (or pass paths as argv), e.g.:
    cd ../challenge && python ../scripts/01_inspect_png.py
"""
import struct
import sys


def read_chunks(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a valid PNG"
    pos = 8
    chunks = []
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8].decode("latin1")
        cdata = data[pos + 8:pos + 8 + length]
        chunks.append((ctype, length, cdata))
        pos += 12 + length
        if ctype == "IEND":
            if pos < len(data):
                print(f"  ### {len(data) - pos} bytes appended after IEND: "
                      f"{data[pos:pos + 200]!r}")
            break
    return chunks, data


def main(files):
    for f in files:
        print(f"==== {f} ====")
        chunks, data = read_chunks(f)
        print(f"  total file size: {len(data)} bytes")
        for ctype, length, cdata in chunks:
            info = ""
            if ctype == "IHDR":
                w, h, bd, ct, comp, filt, inter = struct.unpack(">IIBBBBB", cdata)
                info = (f"w={w} h={h} bitdepth={bd} colortype={ct} "
                        f"compression={comp} filter={filt} interlace={inter}")
            elif ctype in ("tEXt", "zTXt", "iTXt"):
                info = repr(cdata[:200])
            print(f"  {ctype:6s} len={length:6d}  {info}")
        print()


if __name__ == "__main__":
    files = sys.argv[1:] or ["Crane.png", "Snake.png", "Tiger.png"]
    main(files)
