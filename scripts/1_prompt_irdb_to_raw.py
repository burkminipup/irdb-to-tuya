#!/usr/bin/env python3

import sys
import os
import csv

sys.path.insert(0, os.path.expanduser("~/irdb_to_tuya/pyIRDecoder"))

try:
    import pyIRDecoder.protocols as protocols
except ImportError as err:
    print("[FATAL] Could NOT import pyIRDecoder.protocols. Check folder structure and PYTHONPATH.")
    print("Details:", err)
    sys.exit(1)

IRDB_PATH = os.path.expanduser("~/irdb_to_tuya/IRDB/irdb/codes")

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

def generate_raw_signal(protocol_name, device_str, sub_device_str, function_str):
    try:
        proto_cls = getattr(protocols, protocol_name, None)
        if not proto_cls:
            return None, f"[ERROR] Protocol '{protocol_name}' not found in pyIRDecoder.protocols."
        proto_obj = proto_cls(parent=None)
        dev = int(device_str) if device_str else 0
        func = int(function_str) if function_str else 0

        # Here we replicate script 3's logic to only include sub_device if supported
        if hasattr(proto_obj, 'encode_parameters') and any(
            param[0] == 'sub_device' for param in proto_obj.encode_parameters
        ):
            if sub_device_str in [None, "", "-1"]:
                subdev = 0
            else:
                subdev = int(sub_device_str)
            encoded = proto_obj.encode(device=dev, sub_device=subdev, function=func)
        else:
            encoded = proto_obj.encode(device=dev, function=func)

        rlc = convert_to_positive(encoded.original_rlc)
        return rlc, None
    except Exception as exc:
        # Matches the style in script 3
        return None, f"[ERROR] {exc}"

def get_available_brands(base_path):
    return [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

def get_csv_files(brand_path):
    csv_files = []
    for rootdir, _, files in os.walk(brand_path):
        for fname in files:
            if fname.endswith(".csv"):
                rel = os.path.relpath(rootdir, brand_path)
                csv_files.append(os.path.join(rel, fname))
    return csv_files

def main():
    if not os.path.isdir(IRDB_PATH) or not os.path.exists(IRDB_PATH):
        print("You have not added any brands to your IRDB codes directory.")
        print('Please run "brands" first:\n')
        print("""Usage:
  brands get [Brand Name]   - Download IR codes for a brand
  brands list               - List all brands in irdb database
  brands list [Letter(s)]   - List brands by full or partial names - not case sensitive
""")
        return

    brands = get_available_brands(IRDB_PATH)
    if not brands:
        print("You have not added any brands to your IRDB codes directory.")
        print('Please run "brands" first:\n')
        print("""Usage:
  brands get [Brand Name]   - Download IR codes for a brand
  brands list               - List all brands in irdb database
  brands list [Letter(s)]   - List brands by full or partial names - not case sensitive
""")
        return

    print("\nAvailable Brands:")
    for b in brands:
        print(f" - {b}")

    chosen_brand = input("\nEnter the brand folder name:\n> ").strip()
    brand_path = os.path.join(IRDB_PATH, chosen_brand)
    if not os.path.isdir(brand_path):
        print("[ERROR] Invalid brand folder. Exiting.")
        return

    csv_list = get_csv_files(brand_path)
    if not csv_list:
        print(f"[ERROR] No CSV files found under {brand_path}. Exiting.")
        return

    print("\nAvailable CSV Files:")
    for c in csv_list:
        print(f" - {c}")

    chosen_csv = input("\nEnter the CSV file name:\n> ").strip()
    csv_path = os.path.join(brand_path, chosen_csv)
    if not os.path.isfile(csv_path):
        print("[ERROR] Invalid CSV file selected. Exiting.")
        return

    all_protocols_in_csv = set()
    all_rows = []
    with open(csv_path, newline='') as cf:
        reader = csv.DictReader(cf)
        for row in reader:
            all_rows.append(row)
            p = row.get("protocol", "")
            if p:
                all_protocols_in_csv.add(p)

    sanitized_list = sorted({sanitize_protocol_name(x) for x in all_protocols_in_csv if x})
    auto_list_str = ", ".join(sanitized_list) if sanitized_list else "(none)"

    print("\nHere are known valid protocols in pyIRDecoder:\n")
    print_protocols_in_columns(STATIC_PROTOCOLS, columns=4)

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

    first_output = True
    with open(csv_path, newline='') as cf:
        reader = csv.DictReader(cf)
        for row in reader:
            func_name = row.get('functionname', 'Unnamed')
            raw_proto = row.get('protocol', '')
            device_str = row.get('device', '0')
            subdev_str = row.get('subdevice', '-1')
            func_str = row.get('function', '0')

            proto_name = manual_protocol if manual_protocol else sanitize_protocol_name(raw_proto)
            rlc, err_msg = generate_raw_signal(proto_name, device_str, subdev_str, func_str)

            if first_output:
                print("\n\n")
                first_output = False

            print("=" * 75)
            if rlc is not None:
                print(f"Brand      : {chosen_brand}")
                print(f"CSV File   : {chosen_csv}")
                print(f"Function   : {func_name}")
                print(f"Protocol   : {proto_name}")
                print(f"Raw Timing : {rlc}")
            else:
                print(f"[ERROR] Could NOT generate signal for '{func_name}'")
                print(f" - Protocol : {proto_name}")
                print(f" - Device   : {device_str}")
                print(f" - SubDev   : {subdev_str}")
                print(f" - Function : {func_str}")
                print(f" - Details  : {err_msg}")
            print("=" * 75)

if __name__ == "__main__":
    main()
    
