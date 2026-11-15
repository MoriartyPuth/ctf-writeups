# Magic Ways

**Category:** Forensics / Steganography

**Flag:** `bronco{wh4t_ar3_mag1c_byt3s}`

## Challenge

The challenge provides `challenge.png` — a PNG image that won't open in any image viewer.

## Solution

### Step 1: Fix the PNG signature

A hex dump reveals the file signature is `de ad be ef` instead of the valid PNG signature `89 50 4E 47`:

```
00000000  de ad be ef 0d 0a 1a 0a  ...
```

Fix it with a hex editor:

- Byte 0: `0xDE` → `0x89`
- Byte 1: `0xAD` → `0x50`
- Byte 2: `0xBE` → `0x4E`
- Byte 3: `0xEF` → `0x47`

```python
with open('challenge.png', 'rb') as f:
    data = bytearray(f.read())
data[0:4] = b'\x89PNG'
with open('fixed.png', 'wb') as f:
    f.write(data)
```

### Step 2: Fix the image height

The image still appears blank. The IHDR chunk has height set to 0. The PNG IHDR chunk (starting at byte 16) contains width (4 bytes) followed by height (4 bytes). Find and increase the height:

```python
import struct
# IHDR starts at offset 16
width = struct.unpack('>I', data[16:20])[0]
height = struct.unpack('>I', data[20:24])[0]
# height was 0, set it to 200
data[20:24] = struct.pack('>I', 200)
```

### Step 3: Decode the barcode

After fixing the height, the image reveals a barcode. Use zbar or an online barcode decoder:

```python
import pyzbar.pyzbar as pyzbar
from PIL import Image

img = Image.open('fixed.png')
barcodes = pyzbar.decode(img)
print(barcodes[0].data.decode())
# bronco{wh4t_ar3_mag1c_byt3s}
```

## Key Takeaway

Corrupted PNG files often need just their signature and/or IHDR dimensions fixed. The magic bytes `89 50 4E 47` and CRC-validated chunk structure make PNG easy to repair.
