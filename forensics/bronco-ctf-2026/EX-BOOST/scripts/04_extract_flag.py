"""
Step 4 - Final extraction and flag assembly.

Each style icon hides leetspeak text in one color channel's bit-plane,
matching the icon's own color:

    Tiger.png (red)   -> R channel, bit 0  -> "F33L"
    Snake.png (green) -> G channel, bit 2  -> "TH3"
    Crane.png (blue)  -> B channel, bit 4  -> "H34T"

Reading the fragments in R -> G -> B order ("the RGB trifecta" from the
prompt) spells out F33L + TH3 + H34T = "FEEL THE HEAT".

Run from the `challenge/` directory:
    cd ../challenge && python ../scripts/04_extract_flag.py
Full-resolution proof images are written to ../output/
"""
from PIL import Image
import numpy as np
import os

OUT_DIR = os.path.join("..", "output")
os.makedirs(OUT_DIR, exist_ok=True)

# (file, channel index [0=R,1=G,2=B], bit position, expected text)
TARGETS = [
    ("Tiger.png", 0, 0, "F33L"),
    ("Snake.png", 1, 2, "TH3"),
    ("Crane.png", 2, 4, "H34T"),
]

fragments = []
for fname, ch_idx, bit, expected in TARGETS:
    im = Image.open(fname).convert("RGBA")
    arr = np.array(im)
    plane = ((arr[:, :, ch_idx] >> bit) & 1) * 255
    out_path = os.path.join(OUT_DIR, f"{fname.replace('.png', '')}_bit{bit}_ch{ch_idx}.png")
    Image.fromarray(plane.astype(np.uint8)).resize(
        (im.width * 8, im.height * 8), Image.NEAREST
    ).save(out_path)
    fragments.append(expected)
    print(f"{fname}: channel={'RGB'[ch_idx]} bit={bit} -> '{expected}' (saved {out_path})")

message = "".join(fragments)
print(f"\nassembled message: {' '.join(fragments)}  ->  \"FEEL THE HEAT\"")

# Prompt says "if you find multiple parts, no spaces" -> concatenate directly,
# lowercase to match this CTF's flag convention.
flag = "bronco{" + message.lower() + "}"
print(f"flag: {flag}")
