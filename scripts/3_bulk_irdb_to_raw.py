#!/usr/bin/env python3

import sys
import pyIRDecoder.protocols as protocols
import os
import subprocess
import io

STATIC_PROTOCOLS = [
    "AdNotham", "Aiwa", "Akai", "Akord", "Amino", "Amino56", "Anthem", "Apple",
    "Archer", "Audiovox", "Barco", "Blaupunkt", "Bose", "Bryston", "CanalSat",
    "CanalSatLD", "Denon2", "Denon", "Denon1", "DenonK", "Dgtec", "Digivision",
    "DirecTV", "DishNetwork", "DishPlayer", "Dyson", "Dyson2", "Elan",
    "Elunevision", "Emerson", "Entone", "F12", "F120", "F121", "F32", "Fujitsu",
    "Fujitsu128", "Fujitsu56", "GICable", "GIRG", "GuangZhou", "GwtS", "GXB",
    "Humax4Phase", "InterVideoRC201", "IODATAn", "Jerrold", "JVC", "JVC48",
    "JVC56", "Kaseikyo", "Kaseikyo56", "Kathrein", "Konka", "Logitech",
    "Lumagen", "Lutron", "Matsui", "MCE", "MCIR2kbd", "MCIR2mouse", "Metz19",
    "Mitsubishi", "MitsubishiK", "Motorola", "NEC", "NEC48", "NECf16", "NECrnc",
    "NECx", "NECxf16", "Nokia", "Nokia12", "Nokia32", "NovaPace", "NRC16",
    "NRC1632", "NRC17", "Ortek", "OrtekMCE", "PaceMSS", "Panasonic", "Panasonic2",
    "PanasonicOld", "PCTV", "PID0001", "PID0003", "PID0004", "PID0083", "Pioneer",
    "Proton", "Proton40", "RC5", "RC57F", "RC57F57", "RC5x", "RC6", "RC6620",
    "RC6624", "RC6632", "RC6M16", "RC6M28", "RC6M32", "RC6M56", "RCA", "RCA38",
    "RCA38Old", "RCAOld", "RECS800045", "RECS800068", "RECS800090", "Revox",
    "Roku", "RTIRelay", "Sampo", "Samsung20", "Samsung36", "SamsungSMTG", "ScAtl6",
    "Sharp", "Sharp1", "Sharp2", "SharpDVD", "SIM2", "Sky", "SkyHD", "SkyPlus",
    "Somfy", "Sony12", "Sony15", "Sony20", "Sony8", "StreamZap", "StreamZap57",
    "Sunfire", "TDC38", "TDC56", "TeacK", "Thomson", "Thomson7", "Tivo",
    "Viewstar", "XBox360", "XBoxOne"
]

def print_protocols_in_columns(protocols_list, columns=4):
    max_length = max(len(p) for p in protocols_list) + 3
    rows = (len(protocols_list) + columns - 1) // columns
    for r in range(rows):
        row_items = []
        for c in range(columns):
            idx = r + c * rows
            if idx < len(protocols_list):
                row_items.append(f"{protocols_list[idx]:<{max_length}}")
        print("".join(row_items))

def sanitize_protocol_name(proto_in_csv):
    return proto_in_csv.replace("{", "").replace("}", "")

def convert_to_positive(signal):
    return [abs(x) for x in signal]

def process_input(brand, base_dir, manual_protocol=None):
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

        function_name, raw_proto, device, sub_device, function = parts
        proto_name = manual_protocol if manual_protocol else sanitize_protocol_name(raw_proto)

        proto_cls = getattr(protocols, proto_name, None)
        if not proto_cls:
            if first_output:
                print("\n\n")
                first_output = False
            print("=" * 75)
            print(f"[ERROR] Could NOT generate signal for '{function_name}'")
            print(f" - Protocol : {proto_name}")
            print(f" - Device   : {device}")
            print(f" - SubDev   : {sub_device}")
            print(f" - Function : {function}")
            print(f" - Details  : [ERROR] Protocol '{proto_name}' not found.")
            print("=" * 75)
            continue

        try:
            proto_obj = proto_cls(parent=None)
            device_int = int(device)
            function_int = int(function)

            if hasattr(proto_obj, 'encode_parameters') and any(
                param[0] == 'sub_device' for param in proto_obj.encode_parameters
            ):
                sub_device_int = 0 if sub_device == "-1" else int(sub_device)
                encoded = proto_obj.encode(
                    device=device_int,
                    sub_device=sub_device_int,
                    function=function_int
                )
            else:
                encoded = proto_obj.encode(
                    device=device_int,
                    function=function_int
                )

            rlc = convert_to_positive(encoded.original_rlc)
            csv_file = os.path.relpath(filepath, brand_dir)

            if first_output:
                print("\n\n")
                first_output = False
            print("=" * 75)
            print(f"Brand      : {brand}")
            print(f"CSV File   : {csv_file}")
            print(f"Function   : {function_name}")
            print(f"Protocol   : {proto_name}")
            print(f"Raw Timing : {rlc}")
            print("=" * 75)

        except Exception as e:
            if first_output:
                print("\n\n")
                first_output = False
            print("=" * 75)
            print(f"[ERROR] Could NOT generate signal for '{function_name}'")
            print(f" - Protocol : {proto_name}")
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

    # Collect protocols from the grep lines
    detected_protocols = set()
    for line in lines_found.splitlines():
        line = line.strip()
        if not line or ':' not in line:
            continue
        _, command = line.split(":", 1)
        parts = command.split(",")
        if len(parts) == 5:
            _, proto, _, _, _ = parts
            detected_protocols.add(sanitize_protocol_name(proto))

    protocols_in_grep = sorted(detected_protocols)
    auto_list_str = ", ".join(protocols_in_grep) if protocols_in_grep else "(none)"

    print("\nHere are known valid protocols in pyIRDecoder:\n")
    print_protocols_in_columns(STATIC_PROTOCOLS)

    print(f"\nUse automatic protocol(s) ({auto_list_str})? [Y/n]: ", end="")
    ans = input().strip().lower()

    manual_protocol = None
    if ans in ("n", "no"):
        print("\nWarning: Ensure the protocol for each key matches the protocol listed on IRDB when manually changing the protocol for all keys.")
        print("\n         Manual protocol selection is useful when the protocol name on IRDB does not exactly match or is not supported in pyIRDecoder.")
        print("         Example: NEC1 is not supported with pyIRDecoder, but you can try NEC instead. I suggest looking online for best alternatives.")
        print("         Hint: Looking at the sub_device column might be a good place to start. This script will ignore sub_device when the protocol called through pyIRDecoder doesn't support it.")
        print("\n         You can run this script multiple times for each protocol.")
        print("\nEnter one protocol to use for ALL keys")
        manual_protocol = input("> ").strip()

    sys.stdin = io.StringIO(lines_found + "\n")
    process_input(brand, base_dir, manual_protocol)

if __name__ == "__main__":
    main()
