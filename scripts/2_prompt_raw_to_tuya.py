#!/usr/bin/env python3

import io
import base64
from bisect import bisect
from struct import pack, unpack


def decode_ir(code: str) -> list[int]:
    payload = base64.decodebytes(code.encode('ascii'))
    payload = decompress(io.BytesIO(payload))
    signal = []
    while payload:
        assert len(payload) >= 2, f'garbage in decompressed payload: {payload.hex()}'
        signal.append(unpack('<H', payload[:2])[0])
        payload = payload[2:]
    return signal

def encode_ir(signal: list[int], compression_level=2) -> str:
    signal = [min(t, 65535) for t in signal]  # clamp any timing over 65535
    payload = b''.join(pack('<H', t) for t in signal)
    compress(out := io.BytesIO(), payload, compression_level)
    payload = out.getvalue()
    return base64.encodebytes(payload).decode('ascii').replace('\n', '')

def decompress(inf: io.FileIO) -> bytes:
    out = bytearray()
    while (header := inf.read(1)):
        L, D = header[0] >> 5, header[0] & 0b11111
        if not L:
            L = D + 1
            data = inf.read(L)
            assert len(data) == L
        else:
            if L == 7:
                L += inf.read(1)[0]
            L += 2
            D = (D << 8 | inf.read(1)[0]) + 1
            data = bytearray()
            while len(data) < L:
                data.extend(out[-D:][:L-len(data)])
        out.extend(data)
    return bytes(out)

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

    def find_length_max():
        return max(
            ((find_length_for_distance(pos - d), d) for d in distance_candidates()),
            key=lambda c: (c[0], -c[1]),
            default=None
        )

    pos = 0
    block_start = 0
    while pos < len(data):
        c = find_length_max()
        if c and c[0] >= 3:
            emit_literal_blocks(out, data[block_start:pos])
            emit_distance_block(out, c[0], c[1])
            pos += c[0]
            block_start = pos
        else:
            pos += 1
    emit_literal_blocks(out, data[block_start:pos])

if __name__ == "__main__":
    print("Enter 'e' for Encode (Raw Timing) or 'd' for Decode (Tuya IR Code):")
    mode = input("> ").strip().lower()

    if mode == "e":
        print("\nEnter the raw IR signal as a comma-separated list (e.g., 9000,4500,560,1690,...):")
        raw_input_signal = input("> ")
        try:
            ir_signal = [int(x.strip()) for x in raw_input_signal.split(",")]
        except ValueError:
            print("Invalid input! Please enter only numbers separated by commas.")
            exit(1)
        tuya_code = encode_ir(ir_signal)
        print("\nGenerated Tuya IR Code:")
        print(tuya_code)

    elif mode == "d":
        print("\nEnter the Tuya IR Code to decode:")
        tuya_input = input("> ").strip()
        try:
            decoded_signal = decode_ir(tuya_input)
            print("\nDecoded Raw IR Signal (µs):")
            print(decoded_signal)
        except Exception as e:
            print(f"Error decoding the Tuya IR Code: {e}")

    else:
        print("Invalid option. Please enter 'e' to encode or 'd' to decode.")
        exit(1)
