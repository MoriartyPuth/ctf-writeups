"""
Spot The Difference - bronco CTF (misc, 10 pts)

file1.txt and file2.txt are "cat -n"-style files with exactly one character
per line (a 350/351-line blob that looks like random base64-ish noise).

file2 is file1 with three things applied on top:
  1. A pile of harmless random case-flips sprinkled everywhere (noise/decoy).
  2. A handful of genuine, non-case substitutions.
  3. Exactly one inserted character (file2 has 1 more line than file1).

Reading the genuine substitutions + the inserted character, in position
order, spells the flag. The case-flip noise is what makes a naive
`diff file1.txt file2.txt` useless -- it reports ~100 "changes" that are
almost all irrelevant.

Usage:
    python solve.py
"""


def load(path):
    """One element per non-empty line, as raw bytes."""
    return [l for l in open(path, "rb").read().split(b"\n") if l != b""]


def find_insertion(a, b):
    """
    file2 (b) is 1 element longer than file1 (a). Find the index k such
    that deleting b[k] maximizes case-insensitive agreement between a and
    the rest of b -- that k is where the extra character was inserted.
    """
    best = None
    for k in range(len(b)):
        trial = b[:k] + b[k + 1 :]
        score = sum(1 for x, y in zip(a, trial) if x.lower() == y.lower())
        if best is None or score > best[0]:
            best = (score, k)
    return best


def main():
    a = load("file1.txt")
    b = load("file2.txt")
    print(f"file1: {len(a)} lines, file2: {len(b)} lines")

    score, k = find_insertion(a, b)
    inserted_char = b[k].decode()
    print(
        f"best alignment: removing file2 line {k + 1} ({inserted_char!r}) "
        f"gives {score}/{len(a)} case-insensitive matches"
    )

    # Re-align file2 by deleting the inserted character, then diff
    # case-insensitively against file1 to find the *genuine* substitutions
    # (everything else is just random case noise).
    b_aligned = b[:k] + b[k + 1 :]
    diffs = []
    for i, (x, y) in enumerate(zip(a, b_aligned)):
        if x.lower() != y.lower():
            diffs.append((i, y.decode()))

    print(f"\n{len(diffs)} genuine substitutions found (position, file1->file2):")
    for i, (idx, ch) in enumerate(diffs):
        print(f"  line {idx + 1}: {a[idx].decode()!r} -> {ch!r}")

    # Merge the inserted character back in at its true position (it sits
    # between aligned-index k-1 and k, hence the k - 0.5 sort key).
    diffs.append((k - 0.5, inserted_char))
    diffs.sort(key=lambda d: d[0])

    message = "".join(c for _, c in diffs)
    print("\nrecovered message:", message)


if __name__ == "__main__":
    main()
