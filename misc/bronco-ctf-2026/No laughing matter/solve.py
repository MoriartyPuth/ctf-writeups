#!/usr/bin/env python3
"""
Challenge 1: No Laughing Matter
Decodes A/H binary (A=0, H=1) in 7-bit ASCII chunks.
"""

with open("aha.txt", "r") as f:
    data = f.read().strip()

blocks = data.split()

result = ""
for block in blocks:
    binary = block.replace("A", "0").replace("H", "1")
    decimal = int(binary, 2)
    result += chr(decimal)

print("Decoded:", result)
