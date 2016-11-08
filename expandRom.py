#!/usr/bin/env python
# -*- coding: utf-8
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


expandRom.py
================
Expands and pads a copy of the Japanese Cyber Knight PC-Engine rom
file to include sufficient extra rom banks for English text.

John Snowdon <john@target-earth.net>
"""

import os
import sys
import traceback
import getopt
import hashlib
import binascii
import math

try:
	import simplejson as json
except:
	print("Warning: Falling back to json")
	import json
try:
	import cStringIO as StringIO
except:
	print("cStringIO not available")
	import StringIO
	
######################################################
############ < User configuration > ##################
######################################################

# Default values
from config import VERBOSE
from config import ROM_NAME, OUT_EXPANDED_NAME
from config import ROM_CHECKSUM, ROM_SIZE, ROM_BANKS, BANK_SIZE, ROM_MAX_SIZE

# Translation table loader
from Table import load_table, load_table_double

from CyberKnightAssetBanks import ASSETS, ASSET_LOAD_TABLE, ASSET_OFFSET_TABLE
from CyberKnightAssetBanks import ASSET_LOAD_TABLE_SIZE, ASSET_OFFSET_TABLE_SIZE

from translators import encode_text, translate_string

######################################################
########## < Run-time code start here > ##############
######################################################

try:
	opts, args = getopt.getopt(sys.argv[1:], "hvSs:d:o:p:f")
except getopt.GetoptError as err:
	print(err)
	sys.exit(2)

print("")
print("expandRom.py - Expand the rom file of the Japanese PC-Engine CyberKnight with")
print("sufficient space to include the English script")
print("----------------")
print("")

SHOW_SUMMARY = False
IN_FILE = ROM_NAME
OUT_FILE = OUT_EXPANDED_NAME
ASSETS_DIR = "./assets/converted/"
OVERWRITE = False
for o, a in opts:
	if o == "-h":
		print("A tool which Expand the rom file of the Japanese PC-Engine CyberKnight with")
		print("sufficient space to include the English script.")
		print("")
		print("Options:")
		print("-h	Show help text")
		print("-v	Enable verbose output")
		print("-d   Directory containing English script assets, as generated by mapAssets.py (e.g. ./assets/converted/")
		print("-i	Name of the original Japanese rom file (e.g. 'Cyber Knight (J).pce')")
		print("-o	Name of the expanded rom file to write (e.g. ''Cyber Knight (J) Expanded.pce')")
		print("-f	Overwrite existing files (otherwise dry-run)")
		print("")
		print("Example:")
		print("expandRom.py -i 'Cyber Knight (J).pce' -o 'Cyber Knight (J) Expanded.pce'")
		print("")
		sys.exit(0)
		
	if o == "-v":
		VERBOSE = True
		
	if o == "-i":
		IN_FILE = a

	if o == "-d":
		ASSETS_DIR = a

	if o == "-o":
		OUT_FILE = a
		
	if o == "-f":
		OVERWRITE = True
		
#############################################
# Print configuration
#############################################

print("Configuration")
print("=============")
print("Verbose: %s" % VERBOSE)
print("Over-write: %s" % OVERWRITE)

if os.path.isdir(ASSETS_DIR):
	print("Assets Dir: %s <- OK" % ASSETS_DIR)
else:
	print("Assets Dir: %s <- ERROR, directory not found!" % ASSETS_DIR)
	sys.exit(2)

if os.path.isfile(IN_FILE):
	print("Input File: %s <- OK" % IN_FILE)
else:
	print("Input File: %s <- ERROR, file not found!" % IN_FILE)
	sys.exit(2)

if OVERWRITE is False:
	if os.path.isfile(OUT_FILE):
		print("Output File: %s <- ERROR, file already exists!" % OUT_FILE)
		sys.exit(2)
	else:
		print("Output File: %s <- OK" % OUT_FILE)
		
else:
	print("Output File: %s <- OK" % OUT_FILE)
	
# Check that we have the correct file
print("")
print("Checking ROM file")
print("=================")
print("Correct checksum: %s" % ROM_CHECKSUM)
new_rom_checksum = hashlib.md5(open(IN_FILE, 'rb').read()).hexdigest()
print("Calculated checksum: %s" % new_rom_checksum)
if ROM_CHECKSUM != new_rom_checksum:
	print("")
	print("Sorry, cannot continue. Your ROM is different to what is expected.")
	sys.exit(2)
else:
	print("OK")
	print("")
		
# Find out the size of the new english text
print("Calculating English script size")
print("-------------------------------")
TOTAL_PCE_BYTES_SIZE = 0
for bank_number in ASSETS["asset_banks"].keys():
	for asset_number in ASSETS["asset_banks"][bank_number]["assets"].keys():
		if ASSETS["asset_banks"][bank_number]["assets"][asset_number]["asset_type"] == "text":
			if os.path.isfile(ASSETS_DIR + "/" + hex(bank_number) + "." + hex(asset_number) + ".dat"):
				# Load asset structure from the file
				print("")
				print("Calculating asset data for %s.%s" % (hex(bank_number), hex(asset_number)))
				asset = json.loads(open(ASSETS_DIR + "/" + hex(bank_number) + "." + hex(asset_number) + ".dat").read())
				PCE_bytes = []
				PCE_japanese_bytes = 0
				ttable = load_table()
				ttable2 = load_table_double()
				for asset_chunk in asset["strings"]:
					
					# Load english text if translated
					if len(asset_chunk["PCE_english"])>0:
						print("------------- Translated string (E) ---------------")
						print("asset_chunk[PCE_english]: %s" % asset_chunk["PCE_english"])
						print("")
						
						# Step 1, encode the text
						new_bytes = encode_text(string = asset_chunk["PCE_english"], trans_table = ttable)
						
						# Step 2, decode the text back again
						new_asset_chunk = asset_chunk
						new_asset_chunk["bytes"] = new_bytes
						new_asset_chunk = translate_string(byte_sequence = new_asset_chunk, trans_table = ttable, trans_table_double = ttable2, alt = False, old_assets = False, VERBOSE = VERBOSE)
						
						# Step 3, compare the decoded string to the english text - do they match?
						s = ""
						for b in new_asset_chunk["text"]:
							s += b
						print("new_asset_chunk[text]: %s" % s)
						
						PCE_bytes += new_bytes
						PCE_japanese_bytes += len(asset_chunk["bytes"])
						print("----------------------- End -----------------------")
					else:
						print("------------- Translated string (J) ---------------")
						print("asset_chunk[PCE_japanese]: %s" % asset_chunk["PCE_japanese"])
						print("")
						# Otherwise load Japanese text
						new_bytes = asset_chunk["bytes"]
						PCE_bytes += new_bytes
						PCE_japanese_bytes += len(asset_chunk["bytes"])
						print("----------------------- End -----------------------")
				          
					print("")
				#print("-- Japanese bytes length: %s" % PCE_japanese_bytes)
				#print("-- Converted bytes length: %s" % len(PCE_bytes))
				asset_required_banks = int(math.ceil(len(PCE_bytes) / (BANK_SIZE * 1.0)))
				TOTAL_PCE_BYTES_SIZE += (asset_required_banks * BANK_SIZE)
				print("- %s.%s script == %s == %s bank(s) == %s bytes" % (hex(bank_number), hex(asset_number), len(PCE_bytes), asset_required_banks, asset_required_banks * BANK_SIZE))
				if asset_required_banks > 2:
					print("-- WARNING! This asset requires more than 2 banks!!")
			else:
				print("Sorry, there isn't a matching asset in %s for bank %s, asset %s" % (ASSET_DIR, bank_number, asset_number))
				print("Did you forget to copy your asset files as generated by mapAssets.py?")
				sys.exit(2)
print("")
print("Total needed asset size %s bytes" % TOTAL_PCE_BYTES_SIZE)
	
c = False
if os.path.isfile(OUT_FILE):
	if OVERWRITE:
		c = True
else:
	c = True
if c is False:
	print("Unable to continue")
	sys.exit(2)
else:
	try:
		print("")
		print("Proceeding to expand file")
		print("-------------------------")
		print("Reading original file")
		rom_bytes = open(IN_FILE, "rb").read()
		new_rom = open(OUT_FILE, "wb")
		print("Writing original file contents from 0x0-%s" % hex(ROM_SIZE))
		new_rom.write(rom_bytes)
		bytes_written = 0
		b = "FF"
		print("Filling with 0xff from %s-%s" % (hex(ROM_SIZE), hex(ROM_SIZE + TOTAL_PCE_BYTES_SIZE)))
		while bytes_written < TOTAL_PCE_BYTES_SIZE:
			new_rom.write(binascii.unhexlify(b))
			bytes_written += 1
		new_rom.close()
		print("Expanded file %s written" % OUT_FILE)
	except Exception as e:
		print("Error while expanding file")
		print(e)
		sys.exit(2)