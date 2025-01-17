#!/usr/bin/env python3

import io
import base64
import sys
import re
from struct import pack

def encode_ir(signal: list[int]) -> str:
    """
    Convert integer microsecond timings (clamped >65535) into a Tuya IR code string.
    """
    clamped = [min(t, 65535) for t in signal]
    payload = b''.join(pack('<H', t) for t in clamped)
    out = io.BytesIO()
    compress(out, payload, level=2)
    return base64.b64encode(out.getvalue()).decode('ascii')

def compress(out: io.BytesIO, data: bytes, level=2):
    """
    Tuya's LZ-like compression used by many Tuya IR devices.
    """
    if level == 0:
        emit_literal_blocks(out, data)
        return

    W = 2**13
    L = 255 + 9

    pos = 0
    block_start = 0

    def find_length_for_distance(start: int) -> int:
        length = 0
        limit = min(L, len(data) - pos)
        while length < limit and data[pos + length] == data[start + length]:
            length += 1
        return length

    def find_length_max():
        candidates = (
            (find_length_for_distance(pos - d), d)
            for d in range(1, min(pos, W) + 1)
        )
        return max(candidates, key=lambda c: (c[0], -c[1]), default=None)

    while pos < len(data):
        match = find_length_max()
        if match and match[0] >= 3:
            emit_literal_blocks(out, data[block_start:pos])
            emit_distance_block(out, match[0], match[1])
            pos += match[0]
            block_start = pos
        else:
            pos += 1

    emit_literal_blocks(out, data[block_start:pos])

def emit_literal_blocks(out: io.BytesIO, data: bytes):
    for i in range(0, len(data), 32):
        emit_literal_block(out, data[i:i+32])

def emit_literal_block(out: io.BytesIO, data: bytes):
    length = len(data) - 1
    assert 0 <= length < (1 << 5)
    out.write(bytes([length]))
    out.write(data)

def emit_distance_block(out: io.BytesIO, length: int, distance: int):
    distance -= 1
    length -= 2
    block = bytearray()
    if length >= 7:
        block.append(length - 7)
        length = 7
    block.insert(0, (length << 5) | (distance >> 8))
    block.append(distance & 0xFF)
    out.write(block)

def extract_entries(text: str):
    pattern = re.compile(
        r"Brand\s*:\s*(?P<brand>[^\r\n]+)\r?\n"
        r"CSV\s*File\s*:\s*(?P<csv>[^\r\n]+)\r?\n"
        r"Function\s*:\s*(?P<function>[^\r\n]+)\r?\n"
        r"Protocol\s*:\s*[^\r\n]+\r?\n"
        r"Raw\s+Timing\s*:\s*\[(?P<timings>[0-9,\s]+)\]",
        flags=re.MULTILINE
    )

    results = []
    for match in pattern.finditer(text):
        brand = match.group("brand").strip()
        csv_file = match.group("csv").strip()
        function = match.group("function").strip()
        timings_str = match.group("timings")

        try:
            timings = [int(x) for x in re.split(r"[,\s]+", timings_str) if x.strip()]
        except ValueError:
            continue

        results.append((brand, csv_file, function, timings))
    return results

if __name__ == "__main__":
    print("\nPaste your formatted IR data below, beginning with and ending with '=' per decimal section.")
    print("Press CTRL+D twice when done. (CTRL+Z on Windows)\n")

    input_data = sys.stdin.read()
    parsed = extract_entries(input_data)

    if not parsed:
        print("No valid IR data found.")
        sys.exit(1)

    print("\n\n")

    for brand, csv_file, function, timings in parsed:
        code = encode_ir(timings)

        sep_line = "=" * 90

        print(sep_line)
        print(f"Brand                   : {brand}")
        print(f"CSV File                : {csv_file}")
        print(f"Function                : {function}")
        print(f"Generated Tuya IR Code  : {code}")
        print(sep_line, "\n")
