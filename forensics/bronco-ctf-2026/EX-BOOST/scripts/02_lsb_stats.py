"""
Step 2 - LSB (bit-0) statistics per channel.

A pixel channel that's just natural image noise should have roughly a
50/50 split of 0s and 1s in its least-significant bit. A channel with an
embedded message skews away from 50% because the hidden bits aren't random
- they're mostly 0 (background) with pockets of 1 (the glyphs), or vice
versa. This is the classic first check for LSB steganography.

Run from the `challenge/` directory:
    cd ../challenge && python ../scripts/02_lsb_stats.py
"""
from PIL import Image
import numpy as np

FILES = ["Crane.png", "Snake.png", "Tiger.png"]

for name in FILES:
    im = Image.open(name).convert("RGBA")
    arr = np.array(im)
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    print(f"=== {name} === shape={arr.shape}")
    print(" alpha unique values:", np.unique(a))
    for ch, cname in zip([r, g, b, a], ["R", "G", "B", "A"]):
        lsb = ch & 1
        ones = int(lsb.sum())
        total = lsb.size
        pct = 100 * ones / total
        flag = "  <-- anomalous (far from 50%)" if abs(pct - 50) > 15 else ""
        print(f"  {cname} LSB ones: {ones}/{total} ({pct:.1f}%){flag}")
    print()

# Expected output highlights Tiger's Red channel at ~20% instead of ~50%,
# which is the first thread to pull on.
