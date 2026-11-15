#!/usr/bin/env python3
"""
Zip, Zip, Hooray! — CTF Challenge Solver
=========================================
Automated extraction of 1001 nested archive layers to find the flag.

Archive cycle per iteration:
  gzip → tar → bz2 → 7z (password-protected) → zip → gzip → ...

7z password rule: the password is the name of the file inside the 7z.

Usage:
    pip install py7zr
    python3 solve.py challenge.zip

"""

import py7zr
import zipfile
import gzip
import tarfile
import io
import os
import subprocess
import sys
import shutil


def extract_nested(archive_path, max_layers=1100):
    """
    Recursively extract nested archives until the innermost file is reached.

    Returns:
        (content: str, total_layers: int)
    """
    workdir = os.path.join(os.path.dirname(os.path.abspath(archive_path)), 'extracted')
    os.makedirs(workdir, exist_ok=True)

    current = archive_path
    layer = 0

    while True:
        layer += 1

        with open(current, 'rb') as f:
            magic = f.read(6)

        sz = os.path.getsize(current)

        # ── Gzip ──────────────────────────────────────────────
        if magic[:2] == b'\x1f\x8b':
            next_file = os.path.join(workdir, f'layer_{layer}')
            with gzip.open(current, 'rb') as gf:
                data = gf.read()
            tar = tarfile.open(fileobj=io.BytesIO(data))
            for member in tar.getmembers():
                if member.isfile():
                    with tar.extractfile(member) as ef:
                        content = ef.read()
                    with open(next_file, 'wb') as out:
                        out.write(content)
                    current = next_file
                    break
            tar.close()

        # ── Bzip2 ─────────────────────────────────────────────
        elif magic[:3] == b'BZh':
            next_file = os.path.join(workdir, f'layer_{layer}')
            subprocess.run(
                ['bunzip2', '-k', '-f', '-c', current],
                stdout=open(next_file, 'wb'),
                stderr=subprocess.DEVNULL,
            )
            current = next_file

        # ── 7-Zip (password-protected) ────────────────────────
        elif magic == b'7z\xbc\xaf\x27\x1c':
            with py7zr.SevenZipFile(current, mode='r', password='x') as z:
                names = z.getnames()
            inner_name = names[0]

            out_dir = os.path.join(workdir, f'layer_{layer}_dir')
            os.makedirs(out_dir, exist_ok=True)
            with py7zr.SevenZipFile(current, mode='r', password=inner_name) as z:
                z.extractall(path=out_dir)
            current = os.path.join(out_dir, inner_name)

        # ── Zip ───────────────────────────────────────────────
        elif magic[:2] == b'PK':
            with zipfile.ZipFile(current) as zf:
                names = zf.namelist()
                out_dir = os.path.join(workdir, f'layer_{layer}_dir')
                os.makedirs(out_dir, exist_ok=True)
                zf.extractall(out_dir)
                current = os.path.join(out_dir, names[0])

        # ── Tar ───────────────────────────────────────────────
        elif magic[:5] == b'ustar' or magic[:6] == b'././@P':
            next_file = os.path.join(workdir, f'layer_{layer}')
            tar = tarfile.open(current)
            for member in tar.getmembers():
                if member.isfile():
                    with tar.extractfile(member) as ef:
                        content = ef.read()
                    with open(next_file, 'wb') as out:
                        out.write(content)
                    current = next_file
                    break
            tar.close()

        # ── Final file (unknown / plaintext) ──────────────────
        else:
            with open(current, 'rb') as f:
                content = f.read(2000)

            print(f'\n{"="*60}')
            print(f'  Layer {layer}: INNERMOST FILE REACHED')
            print(f'{"="*60}')
            print(f'  File:   {current}')
            print(f'  Size:   {sz} bytes')
            print(f'  Magic:  {content[:20].hex()}')
            print(f'{"="*60}')

            text = content.decode('utf-8', errors='replace')
            print(f'\n  Content:\n  {text[:500]}')

            shutil.copy2(current, os.path.join(workdir, 'flag.txt'))
            return text, layer

        if layer % 100 == 0:
            print(f'  ...layer {layer}, size: {sz} bytes', file=sys.stderr)

        if layer > max_layers:
            print(f'Stopped at layer {layer} (max reached)')
            return None, layer


def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <challenge.zip>')
        sys.exit(1)

    archive = sys.argv[1]
    if not os.path.isfile(archive):
        print(f'Error: {archive} not found')
        sys.exit(1)

    print(f'[*] Extracting nested archives from: {archive}')
    content, total_layers = extract_nested(archive)
    print(f'\n[*] Done. Total layers extracted: {total_layers}')

    if content and 'flag' in content.lower() or 'ctf' in content.lower() or 'bronco' in content.lower():
        # Extract flag from curly braces
        import re
        match = re.search(r'flag\{[^}]+\}|bronco\{[^}]+\}', content, re.IGNORECASE)
        if match:
            print(f'\n[+] FLAG: {match.group(0)}')


if __name__ == '__main__':
    main()
