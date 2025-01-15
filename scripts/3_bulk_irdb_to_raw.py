#!/usr/bin/env python3

import sys
import pyIRDecoder.protocols as protocols
import os
import subprocess
import io

def convert_to_positive(signal):
    return [abs(x) for x in signal]

def process_input():
    first_output = True
    for line in sys.stdin:
        line = line.strip()
        if not line or ':' not in line:
            continue
        filepath, command = line.split(":", 1)
        parts = command.split(",")
        if len(parts) != 5:
            print(f"[ERROR] Invalid format: {command}")
            continue
        function_name, protocol_name, device, sub_device, function = parts
        proto_cls = getattr(protocols, protocol_name, None)
        if not proto_cls:
            print(f"[ERROR] Protocol '{protocol_name}' not found.")
            continue
        try:
            proto_obj = proto_cls(parent=None)
            device = int(device)
            sub_device = 0 if sub_device == "-1" else int(sub_device)
            function = int(function)
            encoded = proto_obj.encode(device=device, sub_device=sub_device, function=function)
            rlc = convert_to_positive(encoded.original_rlc)
            if first_output:
                print("\n\n")
                first_output = False
            print("=" * 75)
            print(f"File Path  : {filepath}")
            print(f"Function   : {function_name}")
            print(f"Raw Timing : {rlc}")
            print("=" * 75)
        except Exception as e:
            print(f"[ERROR] Failed to encode '{function_name}' with protocol '{protocol_name}': {e}")

def main():
    home = os.path.expanduser("~")
    base_dir = os.path.join(home, "irdb_to_tuya", "IRDB", "irdb", "codes")

    if not os.path.isdir(base_dir) or not os.listdir(base_dir):
        print("You have not added any brands to your IRDB codes directory.")
        print('Please run "brands" first:\n')
        print("""Usage:
  brands get [Brand Name]   - Download IR codes for a brand
  brands list               - List all brands in irdb database
  brands list [Letter(s)]   - List brands by full or partial names - not case sensitive
""")
        return

    print("\nAvailable Brands:")
    brands = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not brands:
        print("You have not added any brands to your IRDB codes directory.")
        print('Please run "brands" first:\n')
        print("""Usage:
  brands get [Brand Name]   - Download IR codes for a brand
  brands list               - List all brands in irdb database
  brands list [Letter(s)]   - List brands by full or partial names - not case sensitive
""")
        return

    for b in brands:
        print(f" - {b}")

    brand = input("\nEnter the brand folder name:\n> ").strip()
    key = input("\nEnter remote key name: ").strip()

    cmd = ["grep", "-ri", "--include=*.csv", key, os.path.join(base_dir, brand)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines_found = result.stdout.strip()

    if not lines_found:
        print(f"\n[ERROR] No lines found for '{key}' in '{brand}'. Exiting.")
        return

    print(f"\n{lines_found}")
    ans = input("\nDo you want to convert the above keys? [Y/n]: ").strip().lower()
    if ans == "n":
        print("Exiting.")
        return

    sys.stdin = io.StringIO(lines_found + "\n")
    process_input()

if __name__ == "__main__":
    main()
