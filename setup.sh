#!/bin/bash
#
# GitHub Source: https://github.com/burkminipup/irdb-to-tuya
#
# IRDB database codes to Tuya IR Blaster (Tuya ZS06/ZS08/TS1201/UFO-11)
#
# WARNING: This script is currently only compatible with NEC protocols (Or any other protocol in irdb CSV database that matches pyIRDecoder protocol naming conventions.
#          Future compatibility with additional protocols might be available with a "CSV formatting" script
#
# BEGIN OF SCRIPT
#
set -e
#
# -------------------------
#
# 1. Install dependencies
#
apt update && apt upgrade -y
apt install -y git python3 python3-pip python3-numpy nano wget
#
# NOTICE: For macOS users:
#         brew install git python3 nano wget
#
# -------------------------
#
# 2. Install pyIRDecoder
#
if [ ! -d "$HOME/irdb_to_tuya/pyIRDecoder" ]; then
    git clone https://github.com/kdschlosser/pyIRDecoder.git "$HOME/irdb_to_tuya/pyIRDecoder"
else
    echo "pyIRDecoder is already cloned."
fi
#
# NOTICE: pyIRDecoder is most likely to be your bug if you run into issues due to the cloning install -- No official pyPI package or installer.
#
# -------------------------
#
# 3. Add "brands" bash script and all python3 conversion scripts
#
mkdir -p "$HOME/irdb_to_tuya/IRDB/irdb" "$HOME/irdb_to_tuya/scripts"

wget --no-check-certificate --content-disposition -P "$HOME/irdb_to_tuya/scripts" \
    "https://raw.githubusercontent.com/burkminipup/irdb-to-tuya/main/scripts/1_prompt_irdb_to_raw.py"

wget --no-check-certificate --content-disposition -P "$HOME/irdb_to_tuya/scripts" \
    "https://raw.githubusercontent.com/burkminipup/irdb-to-tuya/main/scripts/2_prompt_raw_to_tuya.py"

wget --no-check-certificate --content-disposition -P "$HOME/irdb_to_tuya/scripts" \
    "https://raw.githubusercontent.com/burkminipup/irdb-to-tuya/main/scripts/3_bulk_irdb_to_raw.py"

wget --no-check-certificate --content-disposition -P "$HOME/irdb_to_tuya/scripts" \
    "https://raw.githubusercontent.com/burkminipup/irdb-to-tuya/main/scripts/4_bulk_raw_to_tuya.py"

wget --no-check-certificate --content-disposition -P "$HOME/irdb_to_tuya/scripts" \
    "https://raw.githubusercontent.com/burkminipup/irdb-to-tuya/main/scripts/brands"

chmod +x \
    "$HOME/irdb_to_tuya/scripts/brands" \
    "$HOME/irdb_to_tuya/scripts/1_prompt_irdb_to_raw.py" \
    "$HOME/irdb_to_tuya/scripts/2_prompt_raw_to_tuya.py" \
    "$HOME/irdb_to_tuya/scripts/3_bulk_irdb_to_raw.py" \
    "$HOME/irdb_to_tuya/scripts/4_bulk_raw_to_tuya.py"
#
# -------------------------
#
# 4. Add scripts and pyIRDecoder to PATH
#
if [[ $SHELL == *"zsh"* ]]; then
    PROFILE_FILE="$HOME/.zshrc"
else
    PROFILE_FILE="$HOME/.bashrc"
fi
# Scripts PATH
if ! grep -q 'export PATH="$PATH:$HOME/irdb_to_tuya/scripts"' "$PROFILE_FILE"; then
    echo 'export PATH="$PATH:$HOME/irdb_to_tuya/scripts"' >> "$PROFILE_FILE"
fi
# pyIRDecoder PATH
if ! grep -q 'export PYTHONPATH="$HOME/irdb_to_tuya/pyIRDecoder:$PYTHONPATH"' "$PROFILE_FILE"; then
    echo 'export PYTHONPATH="$HOME/irdb_to_tuya/pyIRDecoder:$PYTHONPATH"' >> "$PROFILE_FILE"
fi
#
# -------------------------
#
# END OF SCRIPT
