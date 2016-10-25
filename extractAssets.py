#!/usr/bin/env python

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


extractAssets.py
================
A (basic, initial) script extractor for the PC-Engine game 'Cyber Knight'.

In order to run, it requires a headerless copy of the Cyber Knight ROM file
and a complete translation table (distributed with this programe).

John Snowdon <john@target-earth.net>
"""

import os
import time
import codecs
import sys
import traceback
import getopt
import struct
import binascii
import json

######################################################
########## < Config starts here > ####################
######################################################

VERBOSE = False
OVERWRITE = False
ROM_NAME = "Cyber Knight (J).pce"
OUT_NAME = "CyberKnight Assets.json"

from CyberKnightAssetBanks import ASSETS, ASSET_LOAD_TABLE, ASSET_OFFSET_TABLE
from CyberKnightAssetBanks import ASSET_LOAD_TABLE_SIZE, ASSET_OFFSET_TABLE_SIZE

ASSET_BANKS = ASSETS["asset_banks"].keys()

######################################################

def find_next_address(upper_address = None, current_asset = None, assets = []):
	""" Return the upper address for a given asset """

	# Next address defaults to the upper region for this asset bank
	next_address = upper_address
	lowest_asset_address = upper_address
	for asset in assets:
			
			## Skip anything with a lower starting address than our current asset
			if asset["asset_rom_pointer_address"] <= current_asset["asset_rom_pointer_address"]:
				pass
			else:
				# If this asset has a lower address than the end address of this asset bank
				# then it could be the next in sequence, we'll know once we've looped through
				# all remaining assets
				if (asset["asset_rom_pointer_address"] <= lowest_asset_address) and (asset["asset_index"] != current_asset["asset_index"]):
					lowest_asset_address = asset["asset_rom_pointer_address"]
					next_address = lowest_asset_address
				else:
					pass

	print("-----> %s: %s - %s [%s bytes]" % (hex(current_asset["asset_index"]), hex(current_asset["asset_rom_pointer_address"]), hex(next_address), (next_address - current_asset["asset_rom_pointer_address"])))
	return next_address

######################################################
########## < Run-time code start here > ##############
######################################################

try:
	opts, args = getopt.getopt(sys.argv[1:], "hvi:t:o:f")
except getopt.GetoptError as err:
	print(err)
	sys.exit(2)

print("")
print("extractAssets.py - Asset block extractor for Cyber Knight")
print("----------------")
print("")

for o, a in opts:
	if o == "-h":
		print("A simple tool for extracting asset blockse from the game 'Cyber Knight' for the PC-Engine.")
		print("The tool scans the asset blocks as described within 'CyberKnightAssets.py")
		print("")
		print("Options:")
		print("-h	Show help text")
		print("-v	Enable verbose output")
		print("-i	Input file name (e.g. 'Cyber Knight (J).pce')")
		print("-o	Output file name (e.g. 'Cyber Knight.json')")
		print("-f	Force overwite of output file even if it already exists")
		print("")
		print("Example:")
		print("extractAssets.py -i 'Cyber Knight (J).pce' -o 'CyberKnight Assets.json'")
		print("")
		sys.exit(0)
		
	if o == "-v":
		VERBOSE = True
		
	if o == "-i":
		ROM_NAME = a

	if o == "-o":
		OUT_NAME = a
		
	if o == "-f":
		OVERWRITE = True

print("Configuration")
print("=============")
print("Verbose: %s" % VERBOSE)
print("Over-write: %s" % OVERWRITE)
if os.path.isfile(ROM_NAME):
	print("Input ROM File: %s <- OK" % ROM_NAME)
else:
	print("Input ROM File: %s <- ERROR, input file not found!" % ROM_NAME)
	sys.exit(2)
	
print("Output File: %s" % OUT_NAME)
print("")

try:
	file_rom = open(ROM_NAME, "ro")
except Exception as e:
	print(e)

print("There are %s asset banks defined" % len(ASSET_BANKS))
for ab in ASSET_BANKS:
	print("Bank: %s" % hex(ab))
	print("---> Contains %s asset pointers" % len(ASSETS["asset_banks"][ab]["assets"].keys()))
	print("---> Region %s - %s" % (hex(ASSETS["asset_banks"][ab]["asset_bank_rom_start_address"]), hex(ASSETS["asset_banks"][ab]["asset_bank_rom_end_address"])))
	# In order to know where to start we need to know the lowest asset chunk, 
	# and its not always the first asset number.
	lowest_asset_address = ASSETS["asset_banks"][ab]["asset_bank_rom_end_address"]
	lowest_asset_number = 0x0
	
	asset_sequence = []
	
	for asset_index in ASSETS["asset_banks"][ab]["assets"].keys():		
		# Is this the lowest asset start address for this bank?
		if ASSETS["asset_banks"][ab]["assets"][asset_index]["asset_rom_pointer_address"] < lowest_asset_address:
			lowest_asset_address = ASSETS["asset_banks"][ab]["assets"][asset_index]["asset_rom_pointer_address"]
			lowest_asset_number = asset_index
			
	lowest_asset = ASSETS["asset_banks"][ab]["assets"][lowest_asset_number]
	asset_sequence.append(lowest_asset)
	print("---> Starting asset chunk (%s) located at: %s" % (hex(lowest_asset_number), hex(lowest_asset_address)))
	print("---> Finding next asset sequence")
			
	# For each asset, find the upper limit of the region it can be assumed to use
	# by finding the start address of the next highest asset in the bank.
	processed_assets = []
	for asset in ASSETS["asset_banks"][ab]["assets"].values():	
		next_address = find_next_address(upper_address = ASSETS["asset_banks"][ab]["asset_bank_rom_end_address"], current_asset = asset, assets = ASSETS["asset_banks"][ab]["assets"].values())
		asset_sequence.append(next_address)			
		asset["asset_rom_pointer_address_limit"] = next_address
		processed_assets.append(asset)

	# Processed assets now contains a list of assets for this bank that have the 
	# upper limit address embedded, so we know how big each of them are!
	#print processed_assets
	print("")
	time.sleep(2)
	
