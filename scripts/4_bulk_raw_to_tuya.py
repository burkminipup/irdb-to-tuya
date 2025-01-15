#!/usr/bin/env python3

import io
import base64
from struct import pack, unpack
import sys
import re

# MAIN API

def encode_ir(signal: list[int], compression_level=2) -> str:
    payload = b''.join(pack('<H', t) for t in signal)
    compress(out := io.BytesIO(), payload, compression_level)
    payload = out.getvalue()
    return base64.encodebytes(payload).decode('ascii').replace('\n', '')

# COMPRESSION

def emit_literal_blocks(out: io.FileIO, data: bytes):
    for i in range(0, len(data), 32):
        emit_literal_block(out, data[i:i+32])

def emit_literal_block(out: io.FileIO, data: bytes):
    length = len(data) - 1
    assert 0 <= length < (1 << 5)
    out.write(bytes([length]))
    out.write(data)

def emit_distance_block(out: io.FileIO, length: int, distance: int):
    distance -= 1
    assert 0 <= distance < (1 << 13)
    length -= 2
    assert length > 0
    block = bytearray()
    if length >= 7:
        assert length - 7 < (1 << 8)
        block.append(length - 7)
        length = 7
    block.insert(0, length << 5 | distance >> 8)
    block.append(distance & 0xFF)
    out.write(block)

def compress(out: io.FileIO, data: bytes, level=2):
    if level == 0:
        return emit_literal_blocks(out, data)

    W = 2**13
    L = 255 + 9
    distance_candidates = lambda: range(1, min(pos, W) + 1)

    def find_length_for_distance(start: int) -> int:
        length = 0
        limit = min(L, len(data) - pos)
        while length < limit and data[pos + length] == data[start + length]:
            length += 1
        return length

    find_length_max = lambda: max(
        ((find_length_for_distance(pos - d), d) for d in distance_candidates()),
        key=lambda c: (c[0], -c[1]), default=None
    )

    pos = 0
    block_start = 0
    while pos < len(data):
        if (c := find_length_max()) and c[0] >= 3:
            emit_literal_blocks(out, data[block_start:pos])
            emit_distance_block(out, c[0], c[1])
            pos += c[0]
            block_start = pos
        else:
            pos += 1
    emit_literal_blocks(out, data[block_start:pos])

# UPDATED PARSING FUNCTION

def extract_function_and_signal(data: str):
    """
    Extracts function names and raw decimal timings from the provided formatted input.
    Adjusted for IRDB format.
    """
    pattern = r"Function\s*:\s*(.+?)\s+Raw Timing\s*:\s*\[([0-9,\s]+)\]"
    matches = re.findall(pattern, data, re.DOTALL)

    parsed_data = []
    for function_name, raw_signal in matches:
        try:
            ir_signal = [int(x.strip()) for x in raw_signal.split(",")]
            parsed_data.append((function_name.strip(), ir_signal))
        except ValueError:
            print(f"Invalid signal for {function_name}. Skipping.")
    return parsed_data

# MAIN FUNCTION

if __name__ == "__main__":
    print("\nPaste your formatted IR data below, beginning with and ending with '=' per decimal section.\n")
    print("\nPress CTRL+D twice (or CTRL+Z on Windows) when done.\n")

    input_data = sys.stdin.read().strip()
    parsed_entries = extract_function_and_signal(input_data)

    if not parsed_entries:
        print("No valid IR data found.")
        sys.exit(1)

    print("\n" + "=" * 60)

    for function_name, ir_signal in parsed_entries:
        try:
            tuya_code = encode_ir(ir_signal)
            print(f"\nFunction: {function_name}")
            print("Generated Tuya IR Code:")
            print(tuya_code)
        except Exception as e:
            print(f"Error encoding {function_name}: {e}")

    print("\n" + "=" * 60 + "\n")
