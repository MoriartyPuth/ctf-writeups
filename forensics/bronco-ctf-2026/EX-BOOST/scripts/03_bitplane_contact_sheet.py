"""
Step 3 - Bit-plane contact sheets.

LSB stats only flagged Tiger.png's red channel as anomalous - Crane and
Snake looked statistically normal at bit 0. That's because their hidden
text isn't in the LSB at all, it's in a higher bit-plane (bit 2, bit 4,
...), where the skew is diluted by whatever the "real" image data happens
to contain at that bit.

Rather than guess, render every bit (0-7) of every channel (R,G,B) as a
black/white image and lay them out in a grid so the hidden text jumps out
visually wherever it lives.

Run from the `challenge/` directory:
    cd ../challenge && python ../scripts/03_bitplane_contact_sheet.py
Output PNGs are written next to the challenge files as <name>_bitplanes.png
"""
from PIL import Image
import numpy as np

FILES = ["Crane.png", "Snake.png", "Tiger.png"]
BITS = range(8)


def make_sheet(name):
    im = Image.open(name).convert("RGBA")
    arr = np.array(im)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    cells, labels = [], []
    for cname, ch in zip(["R", "G", "B"], [r, g, b]):
        for bit in BITS:
            plane = ((ch >> bit) & 1) * 255
            cells.append(plane.astype(np.uint8))
            labels.append(f"{cname}{bit}")

    h, w = cells[0].shape
    cols, rows = 8, 3
    sheet = np.zeros((rows * h, cols * w), dtype=np.uint8)
    for i, cell in enumerate(cells):
        rr, cc = divmod(i, cols)
        sheet[rr * h:(rr + 1) * h, cc * w:(cc + 1) * w] = cell

    out = f"{name}_bitplanes.png"
    Image.fromarray(sheet).resize((sheet.shape[1] * 3, sheet.shape[0] * 3),
                                   Image.NEAREST).save(out)
    print(f"{name}: saved {out}")
    print(f"  grid layout (8 cols x 3 rows): {labels}")


if __name__ == "__main__":
    for f in FILES:
        make_sheet(f)

# Reading the resulting sheets:
#   Tiger_bitplanes.png  -> "F33L" sits in cell R0 (row 0, col 0)
#   Snake_bitplanes.png  -> "TH3"  sits in cell G2 (row 1, col 2)
#   Crane_bitplanes.png  -> "H34T" sits in cell B4 (row 2, col 4)
