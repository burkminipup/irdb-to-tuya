#!/usr/bin/env python3

import sys
import pyIRDecoder.protocols as protocols

def convert_to_positive(signal):
    """Convert negative RLC timings to positive."""
    return [abs(x) for x in signal]

def process_input():
    first_output = True  # Flag to insert extra spacing before the first output

    for line in sys.stdin:
        line = line.strip()
        if not line or ':' not in line:
            continue  # Skip empty or invalid lines

        # Split into file path and command
        filepath, command = line.split(":", 1)
        parts = command.split(",")

        if len(parts) != 5:
            print(f"[ERROR] Invalid format: {command}")
            continue

        function_name, protocol_name, device, sub_device, function = parts

        # Prepare the protocol
        proto_cls = getattr(protocols, protocol_name, None)
        if not proto_cls:
            print(f"[ERROR] Protocol '{protocol_name}' not found.")
            continue

        try:
            proto_obj = proto_cls(parent=None)
            device = int(device)

            # Use 0 instead of None for sub_device if it's -1
            sub_device = 0 if sub_device == "-1" else int(sub_device)
            function = int(function)

            # Encode the signal
            encoded = proto_obj.encode(
                device=device,
                sub_device=sub_device,
                function=function
            )

            rlc = convert_to_positive(encoded.original_rlc)

            # Add extra spacing before the first output
            if first_output:
                print("\n\n")  # Add two blank lines before first result
                first_output = False

            # Print compact output
            print("=" * 75)
            print(f"File Path  : {filepath}")
            print(f"Function   : {function_name}")
            print(f"Raw Timing : {rlc}")
            print("=" * 75)

        except Exception as e:
            print(f"[ERROR] Failed to encode '{function_name}' with protocol '{protocol_name}': {e}")

def main():
    print("\nPaste your CSV file path lines below. Press ENTER until all codes appear and then CTRL+D to exit):\n")
    print('\nHint: Use \'grep -ri --include="*.csv" "[REMOTE KEY]" $HOME/irdb_to_tuya/IRDB/irdb/codes/[BRAND]/\' first to try multiple remotes.\n')
    process_input()

if __name__ == "__main__":
    main()
