# irdb-to-tuya
Scripts to convert irdb IR remote codes to decimal, as well as to Tuya IR blasters.

## Install Script
**COMING SOON...**

## ⚠️ WARNING
This script is currently only compatible with **NEC protocols** (or any other protocols in the IRDB CSV database that match `pyIRDecoder` protocol naming conventions).  

Future compatibility with additional protocols might be available with a "CSV formatting" script.

**Supported devices:**  
- Tuya ZS06  
- Tuya ZS08  
- Tuya TS1201  
- Tuya UFO-11  

---

## Workflow Overview

### "brands" Usage:
- `brands list` — List all available brands  
- `brands list [PartialName]` — Search brands by partial name (not case-sensitive)  
- `brands get [BrandName]` — Download IR codes for a brand (case-sensitive, must type the full name)  

### Single Remote Key to Tuya
```bash
1_prompt_irdb_to_raw.py
2_prompt_raw_to_tuya.py
```

### Using multiple CSV paths or entire remote to Tuya (Useful when trying to find the right remote):
```
grep -ri --include="*.csv" "term" "$HOME/IRDB/irdb/codes/[BRAND]/"
3_bulk_irdb_to_raw.py
4_bulk_raw_to_tuya.py
```
## Disclaimer
This was coded and tested in Proxmox LXC enviornment using Debian. I cannot make any guarantees that this will work in all Linux enviornments. Tested and functioning on Tuya UFO-11 (using Zigbee2MQTT).


## Credits
- Built upon the Tuya compression script by mildsunrise [mildsunrise/1d576669b63a260d2cff35fda63ec0b5]
- Original encode an NEC IR command into code for Tuya ZS06/ZS08/TS1201 by andrewcchen [andrewcchen/tuya_ir_encode.js]
- IR protocol decoding logic sourced from kdschlosser [kdschlosser/pyIRDecoder]
- Contains/accesses irdb by Simon Peter and contributors, used under permission. For licensing details and for information on how to contribute to the database, see  https://github.com/probonopd/irdb


