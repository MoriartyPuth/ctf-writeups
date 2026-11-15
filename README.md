<div align="center">

# 🚩 CTF Writeups

**Step-by-step solutions to the CTF challenges and hacking labs I've solved,**<br>
**sorted by category so you can find what you want quickly.**

![Writeups](https://img.shields.io/badge/writeups-134-blue?style=for-the-badge)
![Categories](https://img.shields.io/badge/categories-8-green?style=for-the-badge)
![Events](https://img.shields.io/badge/events-12-orange?style=for-the-badge)

</div>

## 👋 What is this?

A **CTF** (Capture The Flag) is a hacking competition: each challenge hides a secret string, the
*flag*, and you have to break something to get it. Each writeup here explains **how I found the
bug, why it works, and how to exploit it**, usually with a working solve script you can run yourself.

## Pick a category

| Category | What you'll find | Writeups |
|---|---|:-:|
| **[Web](web/)** | Bugs in websites and APIs: SQL/NoSQL injection, JWT, auth bypass, race conditions | 12 |
| **[Pwn](pwn/)** | Exploiting memory bugs in binaries: buffer overflows, format strings, heap, kernel | 17 |
| **[Reverse Engineering](reverse/)** | Taking programs apart to find the flag: crackmes, obfuscation, VMs, keygens | 38 |
| **[Cryptography](crypto/)** | Breaking weak or misused crypto: RSA, AES modes, PRNGs, lattices, classic ciphers | 28 |
| **[Forensics](forensics/)** | Recovering hidden data from files, images, audio and packet captures | 9 |
| **[OSINT](osint/)** | Finding answers from public information: geolocation, ships, blockchains | 8 |
| **[Misc](misc/)** | Everything else: jails, encodings, puzzles, protocol tricks | 8 |
| **[Boot2Root](boot2root/)** | Full machine takeovers on VulnHub / TryHackMe: recon → foothold → root | 14 |

## New here? Start with these

Easier challenges that explain the basics of each category.

| Challenge | Category | What it's about |
|---|---|---|
| [Pwntutorial](pwn/bronco-ctf-2026/pwntutorial/README.md) | Pwn | Beginner gets() buffer overflow |
| [Discord Nitro](web/lykn-ctf-2026/Discord%20Nitro/README.md) | Web | JWT alg:none forgery to become admin |
| [Hash & Dash](crypto/lykn-ctf-2026/Hash%20%26%20Dash/README.md) | Cryptography | Hash length-extension attack |
| [Catgirl.crack](reverse/crackmes-one/Catgirl.crack-Lab/README.md) | Reverse Engineering | .NET IL analysis, bypassing decoy passwords |
| [Magic Ways](forensics/bronco-ctf-2026/Magic%20Ways/README.md) | Forensics | Repairing a PNG signature and height |
| [DC1](boot2root/vulnhub/DC1-Lab/README.md) | Boot2Root | Drupalgeddon2 (CVE-2018-7600) RCE |

## Events

| Event | Type | Categories | Writeups |
|---|---|---|:-:|
| AUPP Certified Stalker CTF 2026 | CTF | [Web](web/README.md#aupp-certified-stalker-ctf-2026) | 1 |
| BroncoCTF 2026 | CTF | [Web](web/README.md#broncoctf-2026), [Pwn](pwn/README.md#broncoctf-2026), [Reverse Engineering](reverse/README.md#broncoctf-2026), [Cryptography](crypto/README.md#broncoctf-2026), [Forensics](forensics/README.md#broncoctf-2026), [OSINT](osint/README.md#broncoctf-2026), [Misc](misc/README.md#broncoctf-2026) | 33 |
| Cambodia Cyber Arena 2026 | CTF | [Web](web/README.md#cambodia-cyber-arena-2026), [Pwn](pwn/README.md#cambodia-cyber-arena-2026), [Reverse Engineering](reverse/README.md#cambodia-cyber-arena-2026), [Cryptography](crypto/README.md#cambodia-cyber-arena-2026) | 6 |
| Crackmes.one RE CTF 2026 | CTF | [Reverse Engineering](reverse/README.md#crackmesone-re-ctf-2026), [Forensics](forensics/README.md#crackmesone-re-ctf-2026) | 12 |
| D³CTF 2026 | CTF | [Web](web/README.md#d%C2%B3ctf-2026), [Pwn](pwn/README.md#d%C2%B3ctf-2026), [Reverse Engineering](reverse/README.md#d%C2%B3ctf-2026), [Cryptography](crypto/README.md#d%C2%B3ctf-2026), [Misc](misc/README.md#d%C2%B3ctf-2026) | 9 |
| LYKN CTF 2026 | CTF | [Web](web/README.md#lykn-ctf-2026), [Pwn](pwn/README.md#lykn-ctf-2026), [Reverse Engineering](reverse/README.md#lykn-ctf-2026), [Cryptography](crypto/README.md#lykn-ctf-2026), [Forensics](forensics/README.md#lykn-ctf-2026), [OSINT](osint/README.md#lykn-ctf-2026), [Misc](misc/README.md#lykn-ctf-2026) | 36 |
| DanteCTF 2023 | CTF | [Web](web/README.md#dantectf-2023), [Pwn](pwn/README.md#dantectf-2023), [Cryptography](crypto/README.md#dantectf-2023), [Misc](misc/README.md#dantectf-2023) | 4 |
| BreizhCTF | CTF | [Cryptography](crypto/README.md#breizhctf) | 4 |
| crackmes.one | Practice platform | [Reverse Engineering](reverse/README.md#crackmesone) | 8 |
| CryptoHack | Practice platform | [Cryptography](crypto/README.md#cryptohack) | 7 |
| TryHackMe | Practice platform | [Boot2Root](boot2root/README.md#tryhackme) | 1 |
| VulnHub | Practice platform | [Boot2Root](boot2root/README.md#vulnhub) | 13 |

## How the repo is laid out

```
web/                         ← a category
└── lykn-ctf-2026/           ← the event it came from
    └── Discord Nitro/       ← one challenge
        ├── README.md        ← the writeup (start here)
        ├── solve.py         ← solve / exploit script
        └── ...              ← original challenge files when available
```

Each category folder has its own README listing every challenge with a one-line summary.
