# Cryptography

[← Back to all categories](../README.md)

**Breaking weak or misused crypto: RSA, AES modes, PRNGs, lattices, classic ciphers.**

28 writeups from 7 events. Click a challenge name to read the writeup.

## BreizhCTF

| Challenge | What it's about |
|---|---|
| [Authentification 1](breizhctf/authentification-1/writeup/README.md) | AES-GCM with fixed key + IV: keystream reuse, cookie forgery |
| [Authentification 2](breizhctf/authentification-2/writeup/README.md) | Broken GCM: tag mask reuses the first data counter block |
| [Do you have good eyes](breizhctf/do-you-have-good-eyes/writeup/README.md) | Dilithium in the wrong ring (x^256 - 1) |
| [U turn](breizhctf/u-turn/writeup/README.md) | Fully linear hash, invert with linear algebra |

## BroncoCTF 2026

| Challenge | What it's about |
|---|---|
| [Blorg multiplier](bronco-ctf-2026/blorg%20multiplier/README.md) | MD5 collision (HashClash fastcoll) to bypass a whitelist |
| [Consistently static pseudo random number generator](bronco-ctf-2026/consistently%20static%20pseudo%20random%20number%20generator/README.md) | PRNG seeded with the flag behind a modular oracle |
| [Custom cipher](bronco-ctf-2026/custom%20cipher/README.md) | Polynomial "encryption": divide out the public key |
| [Emojibius](bronco-ctf-2026/emojibius/README.md) | Polybius square disguised as emojis |
| [Garbage in flag out](bronco-ctf-2026/garbage%20in%20flag%20out/README.md) | Reused key, known-plaintext recovery |
| [Grandmas secret](bronco-ctf-2026/grandmas%20secret/README.md) | ADFGVX cipher hidden in a letter |
| [Probably unbreakable](bronco-ctf-2026/probably%20unbreakable/README.md) | Restricted key alphabet, intersect candidates per byte |
| [Shifting away](bronco-ctf-2026/shifting%20away/README.md) | Caesar with a growing shift |

## Cambodia Cyber Arena 2026

| Challenge | What it's about |
|---|---|
| [Trojanhorse](cyber-arena-2026/trojanhorse/README.md) | Custom protocol + RSA-CRT fault attack (Bellcore) |

## CryptoHack

| Challenge | What it's about |
|---|---|
| [Bespoke padding](cryptohack/bespoke-padding/writeup/README.md) | RSA with known affine padding (Franklin-Reiter) |
| [Blinding light](cryptohack/blinding-light/writeup/README.md) | Textbook RSA signing, blinding attack |
| [Lets decrypt](cryptohack/lets-decrypt/writeup/README.md) | RSA signature "forgery" by choosing your own modulus |
| [Lets decrypt again](cryptohack/lets-decrypt-again/writeup/README.md) | Pohlig-Hellman discrete log under a chosen modulus |
| [Null or never](cryptohack/null-or-never/writeup/README.md) | RSA e=3 with null-byte padding (Coppersmith) |
| [Rsa backdoor viability](cryptohack/rsa-backdoor-viability/writeup/README.md) | Specially shaped RSA prime, factor it |
| [Vote for pedro](cryptohack/vote-for-pedro/writeup/README.md) | RSA e=3 signature forgery |

## DanteCTF 2023

| Challenge | What it's about |
|---|---|
| [Adventurers knapsack](dantectf-2023/adventurers-knapsack.md) | Merkle-Hellman knapsack broken with LLL |

## D³CTF 2026

| Challenge | What it's about |
|---|---|
| [D3hferp](d3ctf-2026/d3hferp.md) | Multivariate quadratic system over F3, XL algorithm |

## LYKN CTF 2026

| Challenge | What it's about |
|---|---|
| [Hash & Dash](lykn-ctf-2026/Hash%20%26%20Dash/README.md) | Hash length-extension attack |
| [Noisy broadcast](lykn-ctf-2026/Noisy%20broadcast/README.md) | Majority vote over noisy copies, then cube root |
| [Postbox](lykn-ctf-2026/Postbox/README.md) | AES-CBC padding oracle |
| [Shortcut](lykn-ctf-2026/Shortcut/README.md) | RSA small d, Wiener's attack |
| [Twelve steps](lykn-ctf-2026/twelve%20steps/README.md) | Recover LCG parameters from outputs |
| [Whispering](lykn-ctf-2026/whispering/README.md) | NTRU-style key from a side-channel leak |
