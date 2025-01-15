# irdb-to-tuya
Scripts to convert irdb IR remote codes to decimal, as well as to Tuya IR blasters.

## 🛠️ Install Script

Linux: <pre><code>bash &lt;(curl -k "https://raw.githubusercontent.com/burkminipup/irdb-to-tuya/main/setup.sh") && source "$HOME/.bashrc"</code></pre>

macOS: <pre><code>bash &lt;(curl -k "https://raw.githubusercontent.com/burkminipup/irdb-to-tuya/main/setup.sh") && source "$HOME/.zshrc"</code></pre>

Note: macOS is currently untested. Dependencies: ```brew install git python3 nano wget```


## ⚠️ WARNING
This script is currently only compatible with **NEC protocols** (or any other protocols in the IRDB CSV database that match `pyIRDecoder` protocol naming conventions).  

Future compatibility with additional protocols might be available with a "CSV formatting" script.

Folder paths are not relative (yet). Scripts will have to be rewritten to run outside of `$HOME`.

**Supported devices:**  
- Tuya ZS06  
- Tuya ZS08  
- Tuya TS1201  
- Tuya UFO-11  

## ⚡ Workflow Overview

The scripts are split into four individual python scripts to help manupulate the data in different ways. There is currently no single irdb to Tuya script, which is by design.

### Single Remote Key to Tuya
```
1_prompt_irdb_to_raw.py
2_prompt_raw_to_tuya.py
```

### Using multiple CSV paths or entire remote to Tuya:
Useful when trying to find the right remote
```
3_bulk_irdb_to_raw.py
4_bulk_raw_to_tuya.py
```

## 🚀 Script Usage

### brands
```
root@debian-irdb:~# brands
Usage:
  brands get [Brand Name]   - Download IR codes for a brand
  brands list               - List all brands in irdb database
  brands list [Letter(s)]   - List brands by full or partial names - not case sensitive]
root@debian-irdb:~# brands list San
Fetching available brands...
Sansonic
Sansui
Sanyo
root@debian-irdb:~# brands get Sanyo
Downloading all IR codes for brand: Sanyo
Download complete for Sanyo.
root@debian-irdb:~#
```

### 1_prompt_irdb_to_raw.py
```
root@irdb-tuya:~# 1_prompt_irdb_to_raw.py 

Available Brands:
 - Sanyo

Enter the brand folder name:
> Sanyo

Available CSV Files:
 - TV/56,-1.csv
 - Unknown_Sanyo-JXZB/56,-1.csv

[OMMITED FILES]

 - Unknown_B13540/49,-1.csv
 - Unknown_RB-SL22/60,196.csv
 - Unknown_B01004/49,-1.csv
   
[OMMITED FILES]

 - Unknown_B01007/49,-1.csv

Enter the CSV file name:
> Unknown_RB-SL22/60,196.csv

Here are known valid protocols in pyIRDecoder:

AdNotham          Fujitsu128        Nokia12           RECS800045        
Aiwa              Fujitsu56         Nokia32           RECS800068        

                    [OMMITED PROTOCOLS]
        
F32               NECxf16           RCA38Old          XBox360           
Fujitsu           Nokia             RCAOld            XBoxOne           

Use automatic protocol(s) (NEC)? [Y/n]: Y

===========================================================================
Brand      : Sanyo
CSV File   : Unknown_RB-SL22/60,196.csv
Function   : PictureMode
Protocol   : NEC
Raw Timing : [9024, 4512, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 40884]
===========================================================================
===========================================================================
Brand      : Sanyo
CSV File   : Unknown_RB-SL22/60,196.csv
Function   : KEY_ZOOM
Protocol   : NEC
Raw Timing : [9024, 4512, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 40884]
===========================================================================
===========================================================================
Brand      : Sanyo
CSV File   : Unknown_RB-SL22/60,196.csv
Function   : KEY_SUBTITLE
Protocol   : NEC
Raw Timing : [9024, 4512, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 40884]
===========================================================================
```

### 2_prompt_raw_to_tuya.py
```
root@debian-irdb:~# 2_prompt_raw_to_tuya.py 
Enter 'e' for Encode (Raw Timing) or 'd' for Decode (Tuya IR Code):
> e

Enter the raw IR signal as a comma-separated list (e.g., 9000,4500,560,1690,...):
> 9024, 4512, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 40884

Generated Tuya IR Code:
BUAjoBE0AsABAZwG4AUD4AcB4AcT4AMn4AcH4AsT4AMH4AMLAbSf
Enter 'e' for Encode (Raw Timing) or 'd' for Decode (Tuya IR Code):
> d

Enter the Tuya IR Code to decode:
> BUAjoBE0AsABAZwG4AUD4AcB4AcT4AMn4AcH4AsT4AMH4AMLAbSf

Decoded Raw IR Signal (µs):
[9024, 4512, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 40884]
root@debian-irdb:~# 
```

### 3_bulk_irdb_to_raw.py
```
root@debian-irdb:~# 3_bulk_irdb_to_raw.py 

Available Brands:
 - Sanyo

Enter the brand folder name:
> Sanyo

Enter remote key name: setup

/root/irdb_to_tuya/IRDB/irdb/codes/Sanyo/Unknown_sanyo-tv01/56,-1.csv:KEY_SETUP,NEC,56,-1,23
/root/irdb_to_tuya/IRDB/irdb/codes/Sanyo/Unknown_RB-SL22/60,196.csv:KEY_SETUP,NEC,60,196,2

Do you want to convert the above keys? [Y/n]: 

===========================================================================
File Path  : /root/irdb_to_tuya/IRDB/irdb/codes/Sanyo/Unknown_sanyo-tv01/56,-1.csv
Function   : KEY_SETUP
Raw Timing : [9024, 4512, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 45396]
===========================================================================
===========================================================================
File Path  : /root/irdb_to_tuya/IRDB/irdb/codes/Sanyo/Unknown_RB-SL22/60,196.csv
Function   : KEY_SETUP
Raw Timing : [9024, 4512, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 40884]
===========================================================================
root@debian-irdb:~# 
```

### 4_bulk_raw_to_tuya.py
```
root@irdb-tuya:~# 4_bulk_raw_to_tuya.py 

Paste your formatted IR data below, beginning with and ending with '=' per decimal section.


Press CTRL+D twice (or CTRL+Z on Windows) when done.

===========================================================================
File Path  : /root/irdb_to_tuya/IRDB/irdb/codes/Sanyo/Unknown_sanyo-tv01/56,-1.csv
Function   : KEY_SETUP
Raw Timing : [9024, 4512, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 45396]
===========================================================================

===========================================================================
File Path  : /root/irdb_to_tuya/IRDB/irdb/codes/Sanyo/Unknown_RB-SL22/60,196.csv
Function   : KEY_SETUP
Raw Timing : [9024, 4512, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 1692, 564, 564, 564, 1692, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 564, 1692, 564, 564, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 1692, 564, 40884]
===========================================================================
```
[Pressed Ctrl+D two times]
```
============================================================

Function: KEY_SETUP
Generated Tuya IR Code:
BUAjoBE0AuADAQGcBuABA+AfAeAHM+ATO+ADI8ADAVSx

Function: KEY_SETUP
Generated Tuya IR Code:
BUAjoBE0AsABAZwG4AUD4AcB4AcT4AMn4Asv4Ac34AdfwAMBtJ8=

============================================================

root@irdb-tuya:~# 
```

## ⚖️ Disclaimer
This was coded and tested in Proxmox LXC enviornment using Debian 12 Bookworm. I cannot make any guarantees that this will work in all Linux enviornments. Tested and functioning on Tuya UFO-11 (using Zigbee2MQTT).


## 🙏 Credits
- Built upon the Tuya compression script by mildsunrise [mildsunrise/1d576669b63a260d2cff35fda63ec0b5]
- Original encode an NEC IR command into code for Tuya ZS06/ZS08/TS1201 by andrewcchen [andrewcchen/tuya_ir_encode.js]
- IR protocol decoding logic sourced from kdschlosser [kdschlosser/pyIRDecoder]
- Contains/accesses irdb by Simon Peter and contributors, used under permission. For licensing details and for information on how to contribute to the database, see  https://github.com/probonopd/irdb


