#!/usr/bin/env python3

import sys
import pyIRDecoder.protocols as protocols
import os
import subprocess
import io

def convert_to_positive(signal):
    return [abs(x) for x in signal]

def process_input(brand, base_dir):
    first_output = True
    brand_dir = os.path.join(base_dir, brand)

    for line in sys.stdin:
        line = line.strip()
        if not line or ':' not in line:
            continue

        filepath, command = line.split(":", 1)
        parts = command.split(",")
        if len(parts) != 5:
            if first_output:
                print("\n\n")
                first_output = False
            print("=" * 75)
            print(f"[ERROR] Invalid format: {command}")
            print("=" * 75)
            continue

        function_name, protocol_name, device, sub_device, function = parts
        proto_cls = getattr(protocols, protocol_name, None)
        if not proto_cls:
            if first_output:
                print("\n\n")
                first_output = False
            print("=" * 75)
            print(f"[ERROR] Could NOT generate signal for '{function_name}'")
            print(f" - Protocol : {protocol_name}")
            print(f" - Device   : {device}")
            print(f" - SubDev   : {sub_device}")
            print(f" - Function : {function}")
            print(f" - Details  : [ERROR] Protocol '{protocol_name}' not found.")
            print("=" * 75)
            continue

        try:
            proto_obj = proto_cls(parent=None)
            device_int = int(device)
            sub_device_int = 0 if sub_device == "-1" else int(sub_device)
            function_int = int(function)
            encoded = proto_obj.encode(
                device=device_int,
                sub_device=sub_device_int,
                function=function_int
            )
            rlc = convert_to_positive(encoded.original_rlc)

            # Build a relative CSV path (like "Unknown_RB-SL22/60,196.csv")
            csv_file = os.path.relpath(filepath, brand_dir)

            if first_output:
                print("\n\n")
                first_output = False
            print("=" * 75)
            print(f"Brand      : {brand}")
            print(f"CSV File   : {csv_file}")
            print(f"Function   : {function_name}")
            print(f"Protocol   : {protocol_name}")
            print(f"Raw Timing : {rlc}")
            print("=" * 75)

        except Exception as e:
            if first_output:
                print("\n\n")
                first_output = False
            print("=" * 75)
            print(f"[ERROR] Could NOT generate signal for '{function_name}'")
            print(f" - Protocol : {protocol_name}")
            print(f" - Device   : {device}")
            print(f" - SubDev   : {sub_device}")
            print(f" - Function : {function}")
            print(f" - Details  : [ERROR] {e}")
            print("=" * 75)

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
    process_input(brand, base_dir)

if __name__ == "__main__":
    main()
