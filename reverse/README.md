# Reverse Engineering

[← Back to all categories](../README.md)

**Taking programs apart to find the flag: crackmes, obfuscation, VMs, keygens.**

38 writeups from 6 events. Click a challenge name to read the writeup.

## BroncoCTF 2026

| Challenge | What it's about |
|---|---|
| [Cat simulator](bronco-ctf-2026/cat%20simulator/README.md) | Stripped binary game with a decoy string |
| [Cpp unplugged](bronco-ctf-2026/cpp%20unplugged/README.md) | C++ with every token replaced by song titles |
| [Dog simulator](bronco-ctf-2026/dog%20simulator/README.md) | Obfuscated game state + rolling hashes |
| [Mirror mirror](bronco-ctf-2026/mirror%20mirror/README.md) | Python script whose key is a hash of its own source |

## Cambodia Cyber Arena 2026

| Challenge | What it's about |
|---|---|
| [Deathnote](cyber-arena-2026/deathnote/README.md) | Garble-obfuscated Go with a custom cipher (decoy trap) |
| [Nevergonna](cyber-arena-2026/nevergonna/README.md) | PyInstaller unpacking + XOR-chain cipher |

## crackmes.one

| Challenge | What it's about |
|---|---|
| [Bobs Gambling](crackmes-one/Bobs-Gambling-Lab/README.md) | Integer handling flaws in a Windows PE |
| [Catgirl.crack](crackmes-one/Catgirl.crack-Lab/README.md) | .NET IL analysis, bypassing decoy passwords |
| [CryMore](crackmes-one/CryMore-Lab/README.md) | Spoofing a network killswitch response |
| [Lack Level Series](crackmes-one/Lack-Level-Series-Lab/README.md) | 12-level Windows x64 crackme series |
| [MalwareTech VM1](crackmes-one/MalwareTech-VM1-Lab/README.md) | Custom 8-bit VM, pure static analysis |
| [Roullete Simulator](crackmes-one/Roullete-Simulator-Lab/README.md) | Java PRNG seed recovery + integer overflow |
| [The Alchemist Lock](crackmes-one/The-Alchemist-Lock-Lab/README.md) | Packed Windows x64 binary, patching the check |
| [Willy Wonka Chocolate Factory](crackmes-one/Willy-Wonka-Chocolate-Factory-Lab/README.md) | Anti-debug + 4-stage validation, keygen |

## Crackmes.one RE CTF 2026

| Challenge | What it's about |
|---|---|
| [A matter of time](crackmes-re-ctf-2026/a_matter_of_time/README.md) | Obfuscated crackme, AES key leaked via PDB path |
| [Bitcalc](crackmes-re-ctf-2026/bitcalc/README.md) | Self-modifying code built from input bits |
| [Bubbly](crackmes-re-ctf-2026/bubbly/README.md) | Find the swap sequence that sorts an array |
| [Connected](crackmes-re-ctf-2026/connected/README.md) | Simulated network of PCs/routers validating a message |
| [CryptPad](crackmes-re-ctf-2026/cryptPad/WRITEUP.md) | "Custom" cipher that reduces to plain RC4 |
| [Date of birth](crackmes-re-ctf-2026/date_of_birth/README.md) | Time-based date checks (strptime/mktime) |
| [FLRSCRNSVR](crackmes-re-ctf-2026/FLRSCRNSVR/README.md) | Windows screensaver password transform |
| [Httpd](crackmes-re-ctf-2026/httpd/README.md) | Go backdoor triggered by a magic ICMP knock |
| [Matryoshka v2](crackmes-re-ctf-2026/Matryoshka_v2/README.md) | Four nested layers of heavily obfuscated shellcode |
| [Maze](crackmes-re-ctf-2026/maze/README.md) | Maze of chained assembly jump nodes |
| [Wallpaper](crackmes-re-ctf-2026/wallpaper/README.md) | 15-puzzle validator, find the move sequence |

## D³CTF 2026

| Challenge | What it's about |
|---|---|
| [D3gomoku](d3ctf-2026/d3gomoku.md) | Windows kernel driver with a hidden second stage |
| [D3llvm](d3ctf-2026/d3llvm.md) | Android OLLVM library + on-device ML model check |
| [Pacman](d3ctf-2026/pacman.md) | iOS bytecode VM built on Mach messages |

## LYKN CTF 2026

| Challenge | What it's about |
|---|---|
| [Control freak 1](lykn-ctf-2026/control%20freak%201/README.md) | Invert 3 rounds of bijective transforms |
| [Control freak 2](lykn-ctf-2026/control%20freak%202/README.md) | Control-flow flattening + anti-debug seed |
| [Control freak 3](lykn-ctf-2026/control%20freak%203/README.md) | Flattened bytecode VM driven by a SIGTRAP handler |
| [Cr4ck 1](lykn-ctf-2026/cr4ck%201/README.md) | Windows KeygenMe with anti-debug |
| [Cr4ck 2](lykn-ctf-2026/cr4ck%202/README.md) | Windows activator serial check |
| [Cr4ck 3](lykn-ctf-2026/cr4ck%203/README.md) | Bytecode VM behind a .text self-hash |
| [I hate this app](lykn-ctf-2026/i%20hate%20this%20app/README.md) | Defeating SetWindowDisplayAffinity screenshot blocking |
| [I hate this app revenge](lykn-ctf-2026/i%20hate%20this%20app%20revenge/README.md) | Rust binary with default AES-CTR keys in .rdata |
| [Inferior student](lykn-ctf-2026/inferior%20student/README.md) | Python matryoshka: ChaCha20 + LZMA layers, anti-debug |
| [Waguri 2](lykn-ctf-2026/waguri%202/README.md) | Names mapped to Brainfuck, recover the input |
