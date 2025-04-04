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
	from io import StringIO
except:
	print("io not available")
	
######################################################
############ < User configuration > ##################
######################################################

# Default values
from config import VERBOSE, REVISION
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
	opts, args = getopt.getopt(sys.argv[1:], "hvsd:o:p:f")
except getopt.GetoptError as err:
	print(err)
	sys.exit(2)

print("")
print("expandRom.py - Expand the rom file of the Japanese PC-Engine CyberKnight with")
print("sufficient space to include the English script")
print("----------------")
print("")

SHOW_SUMMARY = False
SHOW_PROGRESS = False
IN_FILE = ROM_NAME
OUT_FILE = OUT_EXPANDED_NAME
ASSETS_DIR = "./assets/converted/"
OVERWRITE = False
DELIMETER_CHECK = True
for o, a in opts:
	if o == "-h":
		print("A tool which Expand the rom file of the Japanese PC-Engine CyberKnight with")
		print("sufficient space to include the English script.")
		print("")
		print("Options:")
		print("-h	Show help text")
		print("-v	Enable verbose output")
		print("-s   Show progress")
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

	if o == "-s":
		SHOW_PROGRESS = True
		
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
		
##########################################################
#
# Find out the size of the new english text and encode it
#
##########################################################
print("Encoding English script assets")
print("------------------------------")
TOTAL_PCE_BYTES_SIZE = 0
TOTAL_ASSET_BANKS = 0
all_assets = []
for bank_number in ASSETS["asset_banks"].keys():
	for asset_number in ASSETS["asset_banks"][bank_number]["assets"].keys():
		if ASSETS["asset_banks"][bank_number]["assets"][asset_number]["asset_type"] == "text":
			if os.path.isfile(ASSETS_DIR + "/" + hex(bank_number) + "." + hex(asset_number) + ".dat"):
				# Load asset structure from the file
				print("")
				print("#########################################################")
				print("Calculating asset data for %s.%s" % (hex(bank_number), hex(asset_number)))
				asset = json.loads(open(ASSETS_DIR + "/" + hex(bank_number) + "." + hex(asset_number) + ".dat", encoding='utf-8').read())
				PCE_translated_bytes = 0
				PCE_original_bytes = 0
				ttable = load_table()
				ttable2 = load_table_double()
				original_delimeters = 0
				translated_delimeters = 0
				for asset_chunk in asset["strings"]:
					translated_string_delimeters = 0
					original_string_delimeters = 0
					for b in asset_chunk["bytes"]:
						if "delimeter_skip" not in asset_chunk.keys():
							if b == "00":
								original_delimeters += 1
								original_string_delimeters += 1
				
					PCE_original_bytes += len(asset_chunk["bytes"])
					# Load english text if translated
					if len(asset_chunk["PCE_english"])>0:
						if SHOW_PROGRESS:
                                                    print("TRANSLATED - %s.%s.%s: %s" % (hex(bank_number), hex(asset_number), asset_chunk["string_number"], asset_chunk["PCE_english"].encode('utf-8')))
								
						
						if "<GIT_REVISION>" in asset_chunk["PCE_english"]:
							print("------ Found a Git revision control code - replacing with current Git version")
							print("------ Revision: r%s" % REVISION)
							asset_chunk["PCE_english"] = asset_chunk["PCE_english"].replace('<GIT_REVISION>', REVISION)
												
						# Step 1, encode the text
						new_bytes = encode_text(string = asset_chunk["PCE_english"], trans_table = ttable, string_number = asset_chunk["string_number"])
						
						# Step 2, decode the text back again
						asset_chunk["translated_bytes"] = new_bytes
						new_asset_chunk = asset_chunk
						# Swap the translated bytes with the original bytes field, as that is what 'translate_string' works on
						new_asset_chunk["original_bytes"] = new_asset_chunk["bytes"]
						new_asset_chunk["bytes"] = new_asset_chunk["translated_bytes"]
						new_asset_chunk["text"] = []
						new_asset_chunk = translate_string(byte_sequence = new_asset_chunk, trans_table = ttable, trans_table_double = ttable2, alt = False, old_assets = False, VERBOSE = VERBOSE)
						if "delimeter_skip" not in asset_chunk.keys():
							for b in asset_chunk["translated_bytes"]:
								if b == "00":
									translated_string_delimeters += 1
									translated_delimeters += 1

						s = ""
						for b in new_asset_chunk["text"]:
							s += b
						s = s.replace('\\n', '\n')
						# Step 3, compare the decoded string to the english text - do they match?
						# First test is for length:
						#matched_length = True
						#if len(s) != len(asset_chunk["PCE_english"]):
						#	matched_length = False
						#	print("------------------")
						#	print("WARNING!! String length does not match")
						#	print("Asset data: %s.%s, string number: %s" % (asset["bank"], asset["asset_index"], asset_chunk["string_number"]))
						#	print("-")
						#	print("Pre-encoded string:")
						#	print("@%s@" % asset_chunk["PCE_english"].encode('utf-8'))
						#	print("-")
						#	print("Decoded string:")
						#	print("@%s@" % s)
						#	print("-")
						#	print("Pre-encoded size: @%s@" % len(asset_chunk["PCE_english"]))
						#	print("Decoded size: @%s@" % len(s))
						#	idx = 0
						#	for c in s:
						#		sys.stdout.write("%s" % c)
							#	idx += 1	
						#	print("Please fix this error!")
						#	sys.exit(2)
						
						# Second test is for character match:
						#if matched_length == True:
						#	matched = True
						#	processed = ""
						#	mismatch_pre = ""
						#	mismatch_post = ""	
						#	if matched is False:
						#		print("WARNING!! Strings do not match")
						#		print("Asset data: %s.%s, string number: %s" % (asset["bank"], asset["asset_index"], asset_chunk["string_number"]))
						#		print("-")
						#		print("Pre-encoded string:")
						#		print("@%s@" % asset_chunk["PCE_english"])
						#		print("-")
						#		print("Decoded string:")
						#		print("@%s@" % s)
						#		print("-")
						#		print("Pre-encoded character: @%s@" % mismatch_pre)
						#		print("Decoded character: @%s@" % mismatch_post)
						#		print("String match extend: @%s@" % processed)
						#		print("Please fix this error!")
						#		sys.exit(2)
							
						#if SHOW_PROGRESS:
							#print("---- new_asset_chunk[text]: %s" % s)
							
						PCE_translated_bytes += len(new_bytes)
						
						# Have we got the same amount of <end> bytes?
						if DELIMETER_CHECK:
							if original_string_delimeters != translated_string_delimeters:
								print("")
								print("---- WARNING!! String delimeters do not match")
								print("---- Asset data: %s.%s.%s" % (asset["bank"], asset["asset_index"], asset_chunk["string_number"]))
								print("---- Original delimeters: %s" % original_string_delimeters)
								print("---- Translated delimeters: %s" % translated_string_delimeters)
								print("---- Please fix this error!")
								print("")
								#sys.exit(2)
						
					else:
						if SHOW_PROGRESS:
							print("UNTRANSLATED %s.%s.%s: %s" % (hex(bank_number), hex(asset_number), asset_chunk["string_number"], asset_chunk["PCE_japanese"].encode('utf-8')))
							
						# Otherwise load Japanese text
						for b in asset_chunk["bytes"]:
							if b == "00":
								translated_delimeters += 1
						asset_chunk["translated_bytes"] = asset_chunk["bytes"]
						PCE_translated_bytes += len(asset_chunk["bytes"])
					#if SHOW_PROGRESS:
					#	print("----------------------- End -----------------------")
					#	print("")

				all_assets.append(asset)

				asset_required_banks = int(math.ceil(PCE_translated_bytes / (BANK_SIZE * 1.0)))
				TOTAL_ASSET_BANKS += asset_required_banks
				TOTAL_PCE_BYTES_SIZE += PCE_translated_bytes
				asset["required_banks"] = asset_required_banks
				print("- %s.%s" %  (hex(bank_number), hex(asset_number)))
				print("-- Translated script == %s == %s bank(s) == %s bytes" % (PCE_translated_bytes, asset_required_banks, asset_required_banks * BANK_SIZE))
				print("-- Translated delimeters == %s" % translated_delimeters)
				print("-- Original script == %s == %s bank(s) == %s bytes" % (PCE_original_bytes, asset_required_banks, asset_required_banks * BANK_SIZE))
				print("-- Original delimeters == %s" % original_delimeters)
				if asset_required_banks > 2:
					print("")
					print("-- WARNING!")
					print("-- WARNING! This asset requires more than 2 banks!!")
					print("-- WARNING! This should not happen!!")
					print("-- WARNING!")
			else:
				print("Sorry, there isn't a matching asset in %s for bank %s, asset %s" % (ASSET_DIR, bank_number, asset_number))
				print("Did you forget to copy your asset files as generated by mapAssets.py?")
				sys.exit(2)
print("")
all_assets.sort()

if TOTAL_ASSET_BANKS > 0 and TOTAL_ASSET_BANKS < 8:
	print("Total needed asset banks is %s [8]" % TOTAL_ASSET_BANKS)
	TOTAL_ASSET_BANKS = 8
elif TOTAL_ASSET_BANKS > 8 and TOTAL_ASSET_BANKS < 16:
	print("Total needed asset banks is %s [16]" % TOTAL_ASSET_BANKS)
	TOTAL_ASSET_BANKS = 8
elif TOTAL_ASSET_BANKS > 16 and TOTAL_ASSET_BANKS < 32:
	print("Total needed asset banks is %s [32]" % TOTAL_ASSET_BANKS)
	TOTAL_ASSET_BANKS = 32
else:
	print("WARNING Total asset banks required exceeds 32!")
	

print("Total asset size %s bytes" % TOTAL_PCE_BYTES_SIZE)
print("Total bank size %s x %s = %s bytes" % (TOTAL_ASSET_BANKS, BANK_SIZE, (TOTAL_ASSET_BANKS * BANK_SIZE)))
print("Total wasted bytes %s - %s = %s bytes" % ((TOTAL_ASSET_BANKS * BANK_SIZE), TOTAL_PCE_BYTES_SIZE, ((TOTAL_ASSET_BANKS * BANK_SIZE) - TOTAL_PCE_BYTES_SIZE)))
	
#####################################################################
#
# We now have a list of translated assets, so lets work out how
# to expand the rom and fit them in.
#
######################################################################
	
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
		if (len(rom_bytes)) != ROM_SIZE:
			print("WARNING! File size does not match expected: %s != %s" % (len(rom_bytes), ROM_SIZE))
			sys.exit(2)
		new_rom = open(OUT_FILE, "wb")
		print("Writing original file contents from 0x0-%s [%s bytes]" % (hex(ROM_SIZE), ROM_SIZE))
		new_rom.write(rom_bytes)
		bytes_written = 0
		b = "00"
		print("Filling with 0x%s from %s-%s [%s bytes]" % (b, hex(ROM_SIZE), hex(ROM_SIZE + (TOTAL_ASSET_BANKS * BANK_SIZE)), (TOTAL_ASSET_BANKS * BANK_SIZE)))
		new_rom.seek(ROM_SIZE, 0)
		while bytes_written < (TOTAL_ASSET_BANKS * BANK_SIZE):
			new_rom.write(binascii.unhexlify(b))
			bytes_written += 1
		new_rom.close()
		print("Expanded file %s written" % OUT_FILE)
	except Exception as e:
		print("ERROR - Error while expanding file")
		print(e)
		sys.exit(2)
		
print("")
print("Insert Assets")
print("-------------")
print("")
# Patch the table low in the rom file with the bank numbers of the patched and injected assets.
try:
	print("Reading asset load table at 0x%s-0x%s" % (hex(ASSET_LOAD_TABLE), hex(ASSET_LOAD_TABLE + ASSET_LOAD_TABLE_SIZE)))
	new_rom = open(OUT_FILE, "rb")
	new_rom.seek(ASSET_LOAD_TABLE, 0)
	asset_table_bytes = new_rom.read(ASSET_LOAD_TABLE_SIZE)
	asset_table = []
	for byte in asset_table_bytes:
		asset_table.append(byte)
	new_rom.close()
	
	print("Reading asset pointer table at 0x%s-0x%s" % (hex(ASSET_OFFSET_TABLE), hex(ASSET_OFFSET_TABLE + ASSET_OFFSET_TABLE_SIZE)))
	new_rom = open(OUT_FILE, "rb")
	new_rom.seek(ASSET_OFFSET_TABLE, 0)
	asset_pointer_bytes = new_rom.read(ASSET_OFFSET_TABLE_SIZE)
	asset_pointer = []
	for byte in asset_pointer_bytes:
		asset_pointer.append(byte)
	new_rom.close()
except Exception as e:
	print("ERROR - Error while reading asset tables")
	print(e)
	sys.exit(2)
	
c = 0
print("Remapping assets")
last_original_bank = ROM_SIZE / BANK_SIZE
next_bank = last_original_bank + 2
next_location = next_bank * BANK_SIZE

new_asset_table = []
new_asset_pointer_table = []

print("Last original bank [%s] located at %s" % (hex(last_original_bank), hex(ROM_SIZE - BANK_SIZE)))
while c < ASSET_LOAD_TABLE_SIZE:
	assets_written = False
	tmp_bank = str(binascii.hexlify(asset_table[c])).lower()
	if tmp_bank[0] == "0":
		bank = "0x" + tmp_bank[1]
	else:
		bank = "0x" + tmp_bank

	tmp = str(binascii.hexlify(asset_pointer[c])).lower()
	if tmp[0] == "0":
		asset_number = "0x" + tmp[1]
	else:
		asset_number = "0x" + tmp
	
	#print("- %s.%s" % (bank, asset_number))
	
	# Find the matching asset chunk
	for asset in all_assets:
		if (asset["bank"] == bank) and (asset["asset_index"] == asset_number):
			this_bank = next_bank
			this_location = next_location
			this_index = 0x01
			
			#print("-- %s.%s" % (asset_chunk["bank"], asset_chunk["asset_index"]))
			byte_size = 0
			translated_bytes = []
			for string in asset["strings"]:
				translated_bytes += string["translated_bytes"]
			byte_size = len(translated_bytes)
			
			print("- %s.%s - relocating to bank %s as asset %s at %s [%s bytes]" % (bank, asset_number, hex(this_bank), hex(this_index), hex(this_location), byte_size))
			#print("--- Asset size = %s bytes" % byte_size)
			
			
			# The header table for an asset is much simpler than the original one.
			# The relative address is always 0x4000
			# byte position 0 = ID of bank (for example, 0x5f)
			# byte position 1 + 2 = address (in little endian) of the asset block to follow (always 0x4003, as it starts at the 4th byte)
			# byte position 4 = 0x00
			# SO, beyond the first byte (which changes per bank number) it will always look like:
			# 0x5f, 0x03, 0x40, 0x00, data_bytes_start_here
			# The reference to the asset in the asset pointer table will therefore always be 0x01, as it is the 
			# first address pair in the asset table.
			print("--- Seeking to 0x%s" % hex(this_location))
			new_rom = open(OUT_FILE, "rb+")
			new_rom.seek(this_location, 0)
			new_table = [hex(this_bank)[2:4], '03', '40']
			print("--- Writing new asset table %s" % (new_table))
			
			for table_byte in new_table:
				new_rom.write(binascii.unhexlify(table_byte))
			
			# Now write the text asset data
			print("--- Seeking to 0x%s" % hex(this_location + len(new_table)))
			new_rom.seek(this_location + len(new_table), 0)
			print("--- Writing asset data")
			for text_byte in translated_bytes:
				new_rom.write(binascii.unhexlify(text_byte))
			
			new_rom.close()
			
			new_asset_table.append(hex(this_bank))
			new_asset_pointer_table.append(hex(this_index))
			
			# Increment to next bank for the next asset to be inserted
			next_bank = next_bank + asset["required_banks"]
			next_location = (next_bank * BANK_SIZE)
		
			assets_written = True
	c += 1
	
	if assets_written:
		#print("-- Asset relocated")
		pass
	else:
		#print("-- Reusing existing asset location")
		new_asset_table.append(bank)
		new_asset_pointer_table.append(asset_number)
	#print("- Done")
	#print("")
	
#########################################################
#
# Patch the asset tables to load content from the new
# locations.
#
#########################################################
print("")
print("Patch Asset Tables")
print("------------------")
print("Original asset table: %s" % asset_table)
print("")
print("New asset table: %s" % new_asset_table)
if (len(asset_table) != len(new_asset_table)) and (len(new_asset_table) != ASSET_LOAD_TABLE_SIZE):
	print("ERROR! - Asset table sizes do not match!")
	sys.exit(2)
else:
	new_rom = open(OUT_FILE, "rb+")
	print("Seeking to 0x%s" % hex(ASSET_LOAD_TABLE))
	new_rom.seek(ASSET_LOAD_TABLE, 0)
	print("Writing new table")
	for byte in new_asset_table:
		new_byte = byte[2:4]
		if len(new_byte) == 1:
			new_byte = "0" + new_byte
		new_rom.write(binascii.unhexlify(new_byte))
	new_rom.close()
	print("Done")
	
print("")
print("Original asset pointer table: %s" % asset_pointer)
print("")
print("New asset pointer table: %s" % new_asset_pointer_table)
if (len(asset_pointer) != len(new_asset_pointer_table)) and (len(new_asset_pointer_table) != ASSET_OFFSET_TABLE_SIZE):
	print("ERROR! - Asset table sizes do not match!")
	sys.exit(2)
else:
	new_rom = open(OUT_FILE, "rb+")
	print("Seeking to 0x%s" % hex(ASSET_OFFSET_TABLE))
	new_rom.seek(ASSET_OFFSET_TABLE, 0)
	print("Writing new table")
	for byte in new_asset_pointer_table:
		new_byte = byte[2:4]
		if len(new_byte) == 1:
			new_byte = "0" + new_byte
		new_rom.write(binascii.unhexlify(new_byte))
	new_rom.close()
	print("Done")
