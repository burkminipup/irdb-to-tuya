#!/usr/bin/env python3

import sys
import os
import csv

# Insert local pyIRDecoder path so we can do "import pyIRDecoder.protocols"
sys.path.insert(0, os.path.expanduser("~/pyIRDecoder"))

try:
    import pyIRDecoder.protocols as protocols
except ImportError as err:
    print("[FATAL] Could NOT import pyIRDecoder.protocols. Check folder structure and PYTHONPATH.")
    print("Details:", err)
    sys.exit(1)


# Point this at your IRDB codes folder
IRDB_PATH = os.path.expanduser("~/IRDB/irdb/codes")

# A static list of known protocols in kdschlosser/pyIRDecoder (for easy reference).
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
    """
    Print the known static protocols in columns for easy scanning.
    """
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
    """
    Remove curly braces. E.g. "Sharp{1}" -> "Sharp1".
    If you need more mapping, do it here, e.g. if "NEC1" -> "NEC".
    """
    name = proto_in_csv.replace("{", "").replace("}", "")
    return name


def convert_to_positive(signal):
    """Convert negative RLC timings to positive."""
    return [abs(x) for x in signal]


def generate_raw_signal(protocol_name, device_str, sub_device_str, function_str):
    """
    1) proto_cls(parent=None) so that 'parent' is set (matching your success).
    2) If sub_device_str == '-1', we force sub_device=0 (like your proof-of-concept).
    """
    try:
        proto_cls = getattr(protocols, protocol_name, None)
        if not proto_cls:
            return None, f"[ERROR] Protocol '{protocol_name}' not found in pyIRDecoder.protocols."

        # Create protocol object with parent=None
        proto_obj = proto_cls(parent=None)

        dev = int(device_str) if device_str else 0
        func = int(function_str) if function_str else 0

        # If CSV said sub_device=-1 or empty, we force sub_device=0
        if sub_device_str in [None, "", "-1"]:
            subdev = 0
        else:
            subdev = int(sub_device_str)

        # Now call encode(...) with those exact named arguments
        encoded = proto_obj.encode(
            device=dev,
            sub_device=subdev,
            function=func
        )

        rlc = convert_to_positive(encoded.original_rlc)
        return rlc, None

    except Exception as exc:
        err_msg = (f"[ERROR] Could not encode with protocol '{protocol_name}' "
                   f"(device={device_str}, sub={sub_device_str}, function={function_str}): {exc}")
        return None, err_msg


def get_available_brands(base_path):
    """Return subdirectories under IRDB as brand names."""
    return [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]


def get_csv_files(brand_path):
    """Return all .csv files (recursively) under the brand folder."""
    csv_files = []
    for rootdir, _, files in os.walk(brand_path):
        for fname in files:
            if fname.endswith(".csv"):
                rel = os.path.relpath(rootdir, brand_path)
                csv_files.append(os.path.join(rel, fname))
    return csv_files


def main():
    # Step 1: choose brand folder
    brands = get_available_brands(IRDB_PATH)
    if not brands:
        print("[ERROR] No brands found at", IRDB_PATH)
        return

    print("\nAvailable Brands:")
    for b in brands:
        print(f" - {b}")

    chosen_brand = input("\nEnter the brand folder name:\n> ").strip()
    brand_path = os.path.join(IRDB_PATH, chosen_brand)
    if not os.path.isdir(brand_path):
        print("[ERROR] Invalid brand folder. Exiting.")
        return

    # Step 2: choose CSV file
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

    # Step 3: read the CSV once to see which protocols are in it (for auto-mode)
    all_protocols_in_csv = set()
    all_rows = []
    with open(csv_path, newline='') as cf:
        reader = csv.DictReader(cf)
        for row in reader:
            all_rows.append(row)
            p = row.get("protocol", "")
            if p:
                all_protocols_in_csv.add(p)

    # Show them sanitized
    sanitized_list = sorted({sanitize_protocol_name(x) for x in all_protocols_in_csv if x})
    auto_list_str = ", ".join(sanitized_list) if sanitized_list else "(none)"

    # Step 4: ALWAYS show known protocols in columns for reference
    print("\nHere are known valid protocols in pyIRDecoder:\n")
    print_protocols_in_columns(STATIC_PROTOCOLS, columns=4)

    # Ask for auto/manual
    print(f"\nUse automatic protocol(s) ({auto_list_str})? [Y/n]: ", end="")
    ans = input().strip().lower()

    manual_protocol = None
    if ans in ("n", "no"):
        print("\nEnter one protocol to use for ALL rows (e.g. 'NEC', 'Sharp', 'Sharp1', etc.):")
        manual_protocol = input("> ").strip()

    # We'll add some spacing before the first success/error block
    first_output = True

    # Step 5: process CSV rows
    with open(csv_path, newline='') as cf:
        reader = csv.DictReader(cf)
        for row in reader:
            func_name = row.get('functionname', 'Unnamed')
            raw_proto = row.get('protocol', '')
            device_str = row.get('device', '0')
            subdev_str = row.get('subdevice', '-1')
            func_str = row.get('function', '0')

            # Decide which protocol to use
            if manual_protocol:
                proto_name = manual_protocol
            else:
                proto_name = sanitize_protocol_name(raw_proto)

            rlc, err_msg = generate_raw_signal(proto_name, device_str, subdev_str, func_str)

            # Print spacing before the first output block
            if first_output:
                print("\n\n")
                first_output = False

            print("=" * 75)
            if rlc is not None:
                # Success
                print(f"Brand      : {chosen_brand}")
                print(f"CSV File   : {chosen_csv}")
                print(f"Function   : {func_name}")
                print(f"Protocol   : {proto_name}")
                print(f"Raw Timing : {rlc}")
            else:
                # Error
                print(f"[ERROR] Could NOT generate signal for '{func_name}'")
                print(f" - Protocol : {proto_name}")
                print(f" - Device   : {device_str}")
                print(f" - SubDev   : {subdev_str}")
                print(f" - Function : {func_str}")
                print(f" - Details  : {err_msg}")
            print("=" * 75)

if __name__ == "__main__":
    main()
