"""
WTF_ELECTRICALENGINEERING - bronco CTF (misc, 376 pts)
Stage 2: turn inputsequence.b into the flag.

https://tinyurl.com/hnexnehb (extracted by extract_stego_url.py from
Challenge.png's row 0) redirects to a Google Drive folder named
"BroncoCtfChallengeNonCircuit" containing two files:

  hintstable.txt
    "Hey You found the embedded link inside the image I sent you congrats.
    Unforuntaly its not the end. You'll see a binary file listed in there
    with some very weird formating. That is your input sequences so when
    you are feeding that input sequence into the verilog the order should
    go into something like this. The MSB will be negi, then xj then
    nxj-1 then the lsb should be oti. Also zeroi in the circuit will
    always be zero so don't worry about that as well. If you don't have
    access to a verilog compiler fret not. There is a free version at
    https://www.edaplayground.com/x/ZpgQ as this challenge was designed
    using this free one. [...] use Systemverilog/Verilog for the
    testbench + design and for Tools and simulator use Icarus Verilog 12
    having the Output.txt option will make your life easier."

  inputsequence.b (738 bytes, included in this folder)
    144 whitespace-separated 4-bit binary tokens, each either "0000" or
    "1110" -- the stimulus for the testbench.

The EDA Playground project at the link above has the real design +
testbench pre-loaded (pulled straight out of the page's CodeMirror editor
state via the browser):

    design.sv
    -----------------------------------------------------------
    module mux(A,B,S,Y);
        input  A,B;
        output  Y;
        input S;
        assign Y = (S)? B : A;
    endmodule

    module Bronoc(input negi,input xj,input nxj,input ot, output pp);
        wire xorout;
        assign xorout = negi ^ xj;
        mux a1 (nxj, xorout, ot, pp);
    endmodule
    -----------------------------------------------------------
    => pp = ot ? (negi ^ xj) : nxj

    testbench.sv (relevant excerpt)
    -----------------------------------------------------------
    reg negi, xj, nxj, ot;
    ...
    r = $fscanf(in_fd, "%b", v);   // one 4-bit binary token per read
    {negi, xj, nxj, ot} = v;       // MSB->LSB, matches the hint text
    #1;
    $fwrite(out_fd, "%b", pp);     // one '0'/'1' char per cycle, no separator
    -----------------------------------------------------------

This *looks* like it needs an actual Verilog simulator (Icarus Verilog,
per the hint) -- but it doesn't. Since inputsequence.b only ever contains
the tokens "0000" and "1110":

  - negi always equals xj  ->  xorout = negi ^ xj = 0, always
  - ot is always the token's last bit, which is always 0
  - the mux's select line (ot) is therefore always 0, so it *always*
    picks its A input (nxj) and ignores xorout entirely

    pp = ot ? xorout : nxj  =  nxj  =  1 if token == "1110" else 0

So the whole 4-input combinational circuit collapses, for this specific
input file, to "is this token 1110 or not" -- one bit per token, no
simulator required. 144 tokens = 144 bits = exactly 18 bytes.

Usage:
    python decode_inputsequence.py inputsequence.b
"""
import sys


def decode(path):
    tokens = open(path, encoding="ascii").read().split()
    assert set(tokens) <= {"0000", "1110"}, "unexpected token in input file"

    bits = "".join("1" if t == "1110" else "0" for t in tokens)
    n = len(bits) - (len(bits) % 8)
    return bytes(int(bits[i : i + 8], 2) for i in range(0, n, 8))


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "inputsequence.b"
    print(decode(path))

# Expected output: b'bronco{ov2hhU6mBY}'
