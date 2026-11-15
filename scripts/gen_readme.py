import os, sys, urllib.parse
root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CATS = [("web","Web"),("pwn","Pwn"),("reverse","Reverse Engineering"),("crypto","Cryptography"),
        ("forensics","Forensics"),("osint","OSINT"),("misc","Misc"),("boot2root","Boot2Root"),("labs","Labs")]
EVENTS = {"bronco-ctf-2026":"BroncoCTF 2026","lykn-ctf-2026":"LYKN CTF 2026","d3ctf-2026":"D³CTF 2026",
  "dantectf-2023":"DanteCTF 2023","cyber-arena-2026":"Cambodia Cyber Arena 2026","crackmes-re-ctf-2026":"Crackmes.one RE CTF 2026",
  "crackmes-one":"crackmes.one","aupp-stalker-ctf-2026":"AUPP Certified Stalker CTF 2026","breizhctf":"BreizhCTF",
  "cryptohack":"CryptoHack","vulnhub":"VulnHub","tryhackme":"TryHackMe","aupp":"AUPP"}
def entry(p):
    if os.path.isfile(p): return p
    for c in ["README.md","WRITEUP.md","writeup/README.md","Writeup.md"]:
        if os.path.isfile(os.path.join(p,c)): return os.path.join(p,c)
    mds = sorted(f for f in os.listdir(p) if f.lower().endswith(".md"))
    return os.path.join(p, mds[0]) if mds else p
def q(rel): return urllib.parse.quote(rel)
out = ["# CTF Writeups","",
"My CTF and lab writeups, collected in one place and grouped by **category**, then by **event**.",
"Each entry walks through the reasoning, the bug and the exploit, with a solve script and,",
"where useful, the original challenge files.","",
"Events covered: BroncoCTF 2026, LYKN CTF 2026, D³CTF 2026, Cambodia Cyber Arena 2026,",
"Crackmes.one RE CTF 2026, AUPP Certified Stalker CTF 2026, DanteCTF 2023, BreizhCTF, plus",
"practice on CryptoHack, crackmes.one, VulnHub and TryHackMe.","",
"> This repo was previously `crypto-writeups`; the old URL redirects here.",""]
counts = {}
body = []
for cat, title in CATS:
    cp = os.path.join(root, cat)
    if not os.path.isdir(cp): continue
    n = 0; sec = [f"## {title}", ""]
    for ev in sorted(os.listdir(cp), key=lambda e: EVENTS.get(e,e).lower()):
        ep = os.path.join(cp, ev)
        items = sorted(os.listdir(ep), key=str.lower)
        sec += [f"### {EVENTS.get(ev, ev)}", "", "| Challenge | Writeup |", "|---|---|"]
        for it in items:
            name = it[:-3] if it.endswith(".md") else it
            rel = os.path.relpath(entry(os.path.join(ep, it)), root)
            sec.append(f"| {name} | [writeup]({q(rel)}) |"); n += 1
        sec.append("")
    counts[cat] = (title, n); body += sec
out += ["| Category | Writeups |","|---|---|"]
for cat,(t,n) in counts.items():
    out.append(f"| [{t}](#{t.lower().replace(' ','-')}) | {n} |")
out += [f"| **Total** | **{sum(n for _,n in counts.values())}** |", ""] + body
out += ["## Layout","","```",
"<category>/<event>/<challenge>/   writeup README + solve scripts + challenge files",
"scripts/gen_readme.py            regenerates this README from the folder tree","```","",
"To add a writeup, drop it into `<category>/<event>/<challenge>/` and run:","",
"```bash","python3 scripts/gen_readme.py .","```",""]
open(os.path.join(root,"README.md"),"w").write("\n".join(out))
