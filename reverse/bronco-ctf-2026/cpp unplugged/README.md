# C++ Unplugged

| | |
|---|---|
| **Category** | Reverse Engineering |
| **Flag** | `bronco{i_c@m3_1n_lik3_@_s3gfAult}` |

> I can understand getting a song stuck in your head, but when your life revolves around music
> so much that you start writing code using song titles, there may be a problem. I mean, what
> does this file even print?
>
> Hint: All song titles to replace begin with a capital letter.

## Files

- [`totallynormalcode.cpp`](./totallynormalcode.cpp) — the challenge source

## Tools

- Eyes, a keyboard, and Ctrl+F (this challenge is pure static substitution — no
  disassembler needed, the "binary" is C++ source code with every keyword and
  operator token swapped for a song title)

## Approach

The file is valid C++ where every reserved keyword, punctuation token, and operator has
been replaced with a **song title** (per the hint: each substituted token starts with a
capital letter — `EndGame`, `IsItOverNow`, `Starboy`, etc., all Taylor Swift / The Weeknd
titles). The actual logic underneath is completely ordinary control flow.

### Step 1 — Recover the token dictionary

Working from the most syntactically-constrained lines first (the ones with the fewest
plausible substitutions) pins the whole grammar down quickly:

```cpp
using namespace std EndGame
```

This can only be `using namespace std;` → **`EndGame` = `;`**

```cpp
void updateNum FromTheStart CountingStars Starboy start IsItOverNow BeginAgain
```

Matches `void updateNum(int *start) {` → **`FromTheStart`=`(`**, **`IsItOverNow`=`)`**,
**`BeginAgain`=`{`**, **`CountingStars`=`int`**, **`Starboy`=`*`** (pointer/multiply — the
same token is reused for both meanings of `*` in C).

Continuing the same way across the file (full table, cross-checked against every call
site until nothing was ambiguous):

| Token | Meaning | Token | Meaning |
|---|---|---|---|
| `EndGame` | `;` | `ShouldveSaidNo` | `else` |
| `FromTheStart` | `(` | `ComeBackBeHere` | `return` |
| `IsItOverNow` | `)` | `CountingStars` | `int` |
| `BeginAgain` | `{` | `Starboy` | `*` (ptr/mul) |
| `EndOfTime` | `}` | `WithoutMe` | `-` |
| `PleasePleasePlease` | `if` | `ThisIsMe` | `=` |
| `SameOldLove` | `==` | `Higher` | `>` |
| `SmallerThanThis` | `<` | `Greedy` | `&&` |
| `ThisOrThat` | `\|\|` | `PartOfMe` | `%` |
| `DejaVu` | `while` | `Positions` | `switch` |
| `CaseClosed` | `case` | `AsItWas` | `default` |
| `YouBrokeMeFirst` | `break` | `BreakUpWithYourGirlfriendImBored` | `/` |
| `Mine` | `+=` | `PieceByPiece` | `[` |
| `FreshOutTheSlammer` | `]` | `TruthHurts` | `false` |
| `FalseGod` | `true` | `Abcdefu` | `char` |

### Step 2 — Translate function by function

Rewriting each `CallItWhatYouWant partN(...)` (`CallItWhatYouWant` = `string`) function
in plain C++ using the dictionary reveals six small helpers, each computing one
substring of the flag:

- **`part1()`** — a nested `if`/`switch` maze that, after evaluating a series of boolean
  gates on hardcoded constants, always lands on `case 2`. That branch calls
  `updateNum(&var5)` (which bumps `var5` from `1` to `5` since `1 < 5`), then adds `2` via
  a loop, landing on `var5 == 7`, which is `true` — selecting `"bron"`.
- **`part2()`** — walks a hardcoded `char` array (`'b','#','c','i','u','&','e','@',...`)
  with an index math expression, producing `"co{"`.
- **`part3()`** — a `switch(i)` over `i = 0..5` indexing into a lowercase-alphabet +
  digits + symbols table (`smallerParts`), with one entry (`case 2`) again calling
  `updateNum(&var3)` first. `var3` starts at `52`; `52/5=10`, `+2 → 12`;
  `smallerParts[12] == 'm'`. Concatenated result: `"i_c@m3"`.
- **`part4()`** — a `for`-style loop (`i = 21..27`) with several `if`/`else if` branches
  appending one character per iteration based on arithmetic on `i` (mod, comparisons
  against powers, etc.) → `"_1n_lik3"`.
- **`part5()`** — 3 iterations, alternating between a literal `char(120)` (`'x'`→ actually
  resolves to `'_'` per the constant used) and a call into `secretMath(i)`, a tiny
  `switch` returning `100-5`, `32*2`, or `19*5` depending on `idx` → `"_@_"`.
- **`part6()`** — a long straight-line sequence of `char`-arithmetic appends
  (`char(65)`, `char(100+15)`, `char(110-7)`, …) plus a `do...while` loop, spelling out
  `"s3gfAult}"`.

### Step 3 — Concatenate

`main()` is just:

```cpp
cout << part1() << part2() << part3() << part4() << part5() << part6() << endl;
```

```
part1: bron
part2: co{
part3: i_c@m3
part4: _1n_lik3
part5: _@_
part6: s3gfAult}
```

## Flag

```
bronco{i_c@m3_1n_lik3_@_s3gfAult}
```

Reads as *"I came in like a segfault"* — a programmer's parody of Miley Cyrus's
**Wrecking Ball** ("I came in like a wrecking ball"), fitting the song-title theme baked
into the obfuscation itself.
