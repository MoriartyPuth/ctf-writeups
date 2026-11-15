"""
WTF_ELECTRICALENGINEERING - bronco CTF (misc, 376 pts)
Stage 1: pull the hidden URL out of row 0 of each challenge image.

The challenge gives two images (a table and a circuit diagram, both real
excerpts from an academic paper on Booth-encoder multiplier design) with
flavor text about not knowing electrical engineering. That's the joke: the
EE content is a red herring, and the real puzzle is standard steganalysis.

What was checked and came back clean (see README for the full narrative):
  - PNG chunk structure (no tEXt/zTXt/iTXt, no trailing bytes after IEND)
  - zlib/IDAT payload size (matches width*height*channels exactly)
  - LSB bit-planes 0-3 of R/G/B/A, visualized -- just faint copies of the
    picture, no hidden text/QR pattern
  - Saturation-channel boost -- only revealed the *existing* visible text
    labels, nothing new

What actually hid the data: pixel row 0 (the very top row, which should
just be blank white margin) contains exactly two colors -- pure white
(255,255,255) and a marker cyan (127,255,255) -- across both images. A
non-background color sitting in a row that should be 100% empty margin is
the tell.

Reading row 0 left-to-right as a bitstream (marker pixel = 1, white = 0),
inverting it, and packing 8 bits/byte MSB-first decodes cleanly to ASCII:
a tinyurl link, once per image.

Usage:
    python extract_stego_url.py Challenge.png ChallengeCircuit.png
"""
import sys
from PIL import Image
import numpy as np

MARKER = (127, 255, 255)


def extract(path):
    im = Image.open(path).convert("RGB")
    arr = np.array(im)
    row0 = arr[0]
    w = arr.shape[1]

    bits = [1 if tuple(row0[x]) == MARKER else 0 for x in range(w)]
    last_marked = max(i for i, b in enumerate(bits) if b == 1)
    region = bits[: last_marked + 1]
    inverted = [1 - b for b in region]  # marker bits read inverted

    n = len(inverted) - (len(inverted) % 8)  # drop any incomplete trailing bits
    out = bytearray()
    for i in range(0, n, 8):
        val = 0
        for bit in inverted[i : i + 8]:
            val = (val << 1) | bit
        out.append(val)
    return bytes(out)


if __name__ == "__main__":
    paths = sys.argv[1:] or ["Challenge.png", "ChallengeCircuit.png"]
    for path in paths:
        print(f"{path} -> {extract(path)}")

# Expected output:
# Challenge.png -> b'https://tinyurl.com/hnexnehb'   (-> Google Drive folder, the real next step)
# ChallengeCircuit.png -> b'https://tinyurl.com/3pya79w'  (dead link / link rot -- a red herring)
