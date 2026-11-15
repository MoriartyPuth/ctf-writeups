#!/usr/bin/env python3
"""Regenerate the root README and one README per category from the folder tree.

Layout:  <category>/<event>/<challenge>/   (or <category>/<event>/<challenge>.md)
Technique blurbs come from scripts/topics.tsv  (path<TAB>one-liner).

Usage:   python3 scripts/gen_readme.py
"""
import os
import sys
import urllib.parse

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# folder, title, emoji, what it covers
CATEGORIES = [
    ("web",       "Web",                 "🌐", "Bugs in websites and APIs: SQL/NoSQL injection, JWT, auth bypass, race conditions"),
    ("pwn",       "Pwn",                 "💥", "Exploiting memory bugs in binaries: buffer overflows, format strings, heap, kernel"),
    ("reverse",   "Reverse Engineering", "🔍", "Taking programs apart to find the flag: crackmes, obfuscation, VMs, keygens"),
    ("crypto",    "Cryptography",        "🔐", "Breaking weak or misused crypto: RSA, AES modes, PRNGs, lattices, classic ciphers"),
    ("forensics", "Forensics",           "🧪", "Recovering hidden data from files, images, audio and packet captures"),
    ("osint",     "OSINT",               "🌍", "Finding answers from public information: geolocation, ships, blockchains"),
    ("misc",      "Misc",                "🧩", "Everything else: jails, encodings, puzzles, protocol tricks"),
    ("boot2root", "Boot2Root",           "🖥️", "Full machine takeovers on VulnHub / TryHackMe: recon → foothold → root"),
    ("labs",      "Labs",                "🧑‍🔬", "University (AUPP) security lab reports"),
]

# folder -> (display name, kind, year)
EVENTS = {
    "bronco-ctf-2026":       ("BroncoCTF 2026", "CTF", "2026"),
    "lykn-ctf-2026":         ("LYKN CTF 2026", "CTF", "2026"),
    "d3ctf-2026":            ("D³CTF 2026", "CTF", "2026"),
    "cyber-arena-2026":      ("Cambodia Cyber Arena 2026", "CTF", "2026"),
    "crackmes-re-ctf-2026":  ("Crackmes.one RE CTF 2026", "CTF", "2026"),
    "aupp-stalker-ctf-2026": ("AUPP Certified Stalker CTF 2026", "CTF", "2026"),
    "dantectf-2023":         ("DanteCTF 2023", "CTF", "2023"),
    "breizhctf":             ("BreizhCTF", "CTF", ""),
    "cryptohack":            ("CryptoHack", "Practice platform", ""),
    "crackmes-one":          ("crackmes.one", "Practice platform", ""),
    "vulnhub":               ("VulnHub", "Practice platform", ""),
    "tryhackme":             ("TryHackMe", "Practice platform", ""),
    "aupp":                  ("AUPP coursework", "University labs", ""),
}

# good first reads, by path
START_HERE = [
    "pwn/bronco-ctf-2026/pwntutorial",
    "web/lykn-ctf-2026/Discord Nitro",
    "crypto/lykn-ctf-2026/Hash & Dash",
    "reverse/crackmes-one/Catgirl.crack-Lab",
    "forensics/bronco-ctf-2026/Magic Ways",
    "boot2root/vulnhub/DC1-Lab",
]


def load_topics():
    topics = {}
    path = os.path.join(ROOT, "scripts", "topics.tsv")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if line and not line.startswith("#") and "\t" in line:
                k, v = line.split("\t", 1)
                topics[k] = v
    return topics


def entry(p):
    """The markdown file a reader should open for this challenge."""
    if os.path.isfile(p):
        return p
    for c in ("README.md", "WRITEUP.md", "writeup/README.md", "Writeup.md"):
        if os.path.isfile(os.path.join(p, c)):
            return os.path.join(p, c)
    mds = sorted(f for f in os.listdir(p) if f.lower().endswith(".md"))
    return os.path.join(p, mds[0]) if mds else p


def link(target, base):
    return urllib.parse.quote(os.path.relpath(target, base))


def pretty(name):
    name = name[:-3] if name.endswith(".md") else name
    if name.endswith("-Lab"):
        name = name[:-4]
    name = name.replace("_", " ").replace("-", " ") if " " not in name else name
    return name[:1].upper() + name[1:]


def ev_name(ev):
    return EVENTS.get(ev, (ev, "", ""))[0]


def scan():
    """{cat: {event: [(challenge_path_rel, name)]}}"""
    tree = {}
    for cat, *_ in CATEGORIES:
        cp = os.path.join(ROOT, cat)
        if not os.path.isdir(cp):
            continue
        tree[cat] = {}
        for ev in sorted(os.listdir(cp), key=lambda e: ev_name(e).lower()):
            ep = os.path.join(cp, ev)
            if not os.path.isdir(ep):
                continue
            items = [it for it in os.listdir(ep) if it.lower() != "readme.md" or os.path.isdir(os.path.join(ep, it))]
            tree[cat][ev] = sorted(((f"{cat}/{ev}/{it}", pretty(it)) for it in items), key=lambda x: x[1].lower())
    return tree


def main():
    topics = load_topics()
    tree = scan()
    total = sum(len(v) for evs in tree.values() for v in evs.values())
    missing = [p for evs in tree.values() for v in evs.values() for p, _ in v if p not in topics]

    # ---------- per-category READMEs ----------
    for cat, title, emoji, desc in CATEGORIES:
        if cat not in tree:
            continue
        n = sum(len(v) for v in tree[cat].values())
        base = os.path.join(ROOT, cat)
        out = [f"# {emoji} {title}", "",
               f"[← Back to all categories](../README.md)", "",
               f"**{desc}.**", "",
               f"{n} writeups from {len(tree[cat])} events. Click a challenge name to read the writeup.", ""]
        for ev, items in tree[cat].items():
            out += [f"## {ev_name(ev)}", "", "| Challenge | What it's about |", "|---|---|"]
            for rel, name in items:
                out.append(f"| [{name}]({link(entry(os.path.join(ROOT, rel)), base)}) | {topics.get(rel, '')} |")
            out.append("")
        open(os.path.join(base, "README.md"), "w", encoding="utf-8").write("\n".join(out))

    # ---------- root README ----------
    out = [
        "<div align=\"center\">", "",
        "# 🚩 CTF Writeups", "",
        "**Step-by-step solutions to the CTF challenges and hacking labs I've solved,**<br>",
        "**sorted by category so you can find what you want quickly.**", "",
        f"![Writeups](https://img.shields.io/badge/writeups-{total}-blue?style=for-the-badge)",
        f"![Categories](https://img.shields.io/badge/categories-{len(tree)}-green?style=for-the-badge)",
        f"![Events](https://img.shields.io/badge/events-{len({e for evs in tree.values() for e in evs})}-orange?style=for-the-badge)",
        "", "</div>", "",
        "## 👋 What is this?", "",
        "A **CTF** (Capture The Flag) is a hacking competition: each challenge hides a secret string, the",
        "*flag*, and you have to break something to get it. Each writeup here explains **how I found the",
        "bug, why it works, and how to exploit it**, usually with a working solve script you can run yourself.", "",
        "## Pick a category", "",
        "| Category | What you'll find | Writeups |",
        "|---|---|:-:|",
    ]
    for cat, title, emoji, desc in CATEGORIES:
        if cat in tree:
            n = sum(len(v) for v in tree[cat].values())
            out.append(f"| **[{title}]({cat}/)** | {desc} | {n} |")
    out += ["", "## New here? Start with these", "",
            "Easier challenges that explain the basics of each category.", "",
            "| Challenge | Category | What it's about |", "|---|---|---|"]
    titles = {c: (t, e) for c, t, e, _ in CATEGORIES}
    for rel in START_HERE:
        if os.path.exists(os.path.join(ROOT, rel)):
            cat = rel.split("/")[0]
            out.append(f"| [{pretty(rel.split('/')[-1])}]({link(entry(os.path.join(ROOT, rel)), ROOT)}) | "
                       f"{titles[cat][0]} | {topics.get(rel, '')} |")

    # events table
    ev_cats = {}
    for cat, evs in tree.items():
        for ev, items in evs.items():
            ev_cats.setdefault(ev, {})[cat] = len(items)
    out += ["", "## Events", "", "| Event | Type | Categories | Writeups |", "|---|---|---|:-:|"]
    order = sorted(ev_cats, key=lambda e: (EVENTS.get(e, ("", "", ""))[1] != "CTF", -int(EVENTS.get(e, ("", "", "0"))[2] or 0), ev_name(e).lower()))
    for ev in order:
        cats = ", ".join(f"[{titles[c][0]}]({c}/README.md#{anchor(ev_name(ev))})" for c in ev_cats[ev])
        out.append(f"| {ev_name(ev)} | {EVENTS.get(ev, ('', '', ''))[1]} | {cats} | {sum(ev_cats[ev].values())} |")

    out += ["", "## How the repo is laid out", "", "```",
            "web/                         ← a category",
            "└── lykn-ctf-2026/           ← the event it came from",
            "    └── Discord Nitro/       ← one challenge",
            "        ├── README.md        ← the writeup (start here)",
            "        ├── solve.py         ← solve / exploit script",
            "        └── ...              ← original challenge files when available",
            "```", "",
            "Each category folder has its own README listing every challenge with a one-line summary.", "",
            "<details>", "<summary><b>Adding a new writeup</b></summary>", "",
            "1. Put it in `<category>/<event>/<challenge>/README.md` (plus any scripts or files).",
            "2. Add a one-line summary to `scripts/topics.tsv`.",
            "3. Run `python3 scripts/gen_readme.py` to rebuild every README.", "",
            "</details>", "",
            "---", "",
            "<sub>Formerly `crypto-writeups`. Old links redirect here. For education only: only attack systems you have permission to test.</sub>",
            ""]
    open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write("\n".join(out))

    print(f"{total} writeups across {len(tree)} categories")
    if missing:
        print("No summary in scripts/topics.tsv for:", *missing, sep="\n  ")


def anchor(text):
    """GitHub heading anchor."""
    s = "".join(ch for ch in text.lower() if ch.isalnum() or ch in " -_")
    return urllib.parse.quote(s.replace(" ", "-"))


if __name__ == "__main__":
    main()
