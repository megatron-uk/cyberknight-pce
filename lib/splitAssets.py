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


splitAssets.py
================
Loads script asset datafiles as produced by extractAssets.py

Splits the data into individual text strings and writes them back out.

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
try:
	import simplejson as json
except:
	print("Warning: Falling back to json")
	import json
import difflib

try:
	import cStringIO as StringIO
except:
	print("cStringIO not available")
	import StringIO

######################################################
########## < Config starts here > ####################
######################################################

VERBOSE = False
OVERWRITE = False
INPUT_DIR = "assets/raw"
OUT_DIR = "assets/split"

from CyberKnightAssetBanks import ASSETS, ASSET_LOAD_TABLE, ASSET_OFFSET_TABLE
from CyberKnightAssetBanks import ASSET_LOAD_TABLE_SIZE, ASSET_OFFSET_TABLE_SIZE

from translators import translate_string
from Table import load_table, load_table_double

ASSET_BANKS = ASSETS["asset_banks"].keys()

######################################################
########## < Run-time code start here > ##############
######################################################

try:
	opts, args = getopt.getopt(sys.argv[1:], "hvi:t:o:f")
except getopt.GetoptError as err:
	print(err)
	sys.exit(2)

print("")
print("splitAssets.py - Asset block extractor for Cyber Knight")
print("----------------")
print("")

OVERWRITE = False
VERBOSE = False
for o, a in opts:
	if o == "-h":
		print("A simple tool for splitting text asset blocks from the data files")
		print("produced by the tool 'extractAssets.py'. Note this needs to be run for each asset chunk file.")
		print("")
		print("Options:")
		print("-h	Show help text")
		print("-v	Enable verbose output")
		print("-i	Input dir name (e.g. 'assets/raw')")
		print("-o	Output dir name (e.g. 'assets/split')")
		print("-f	Force overwite of output file even if it already exists")
		print("")
		print("Example:")
		print("extractAssets.py -i 'assets/raw/0xC.0x9.dat'")
		print("")
		sys.exit(0)
		
	if o == "-v":
		VERBOSE = True
		
	if o == "-i":
		INPUT_DIR = a
		
	if o == "-o":
		OUT_DIR = a
		
	if o == "-f":
		OVERWRITE = True

print("Configuration")
print("=============")
print("Verbose: %s" % VERBOSE)
print("Over-write: %s" % OVERWRITE)
if os.path.isdir(INPUT_DIR):
	print("Input Dir: %s <- OK" % INPUT_DIR)
else:
	print("Input Dir: %s <- ERROR, input dir not found!" % INPUT_DIR )
	sys.exit(2)
	
if OVERWRITE is False:
	if os.path.isdir(OUT_DIR):
		print("Output Dir: %s <- OK" % OUT_DIR)
	else:
		print("Output Dir: %s <- ERROR, Path does not exist" % OUT_DIR)
		sys.exit(2)		
		
print("")

#########################################################
# This is the code that parses the binary data and splits
# the text strings.
#########################################################

f_list = os.listdir(INPUT_DIR)

for INPUT_NAME in f_list:
	print("===============================")
	print("")
	print("Loading asset file %s" % INPUT_NAME)
	file_data = open(INPUT_DIR + "/" + INPUT_NAME).read()
	data = json.loads(file_data)
	data["strings"] = []
	print("Asset Bank: %s" % data["bank"])
	print("Asset Index: %s" % data["asset_index"])
	print("Asset Pointer: %s" % data["asset_rom_pointer_address"])
	print("Asset ROM Address: %s-%s" % (data["asset_rom_pointer_address"], data["asset_rom_pointer_address_limit"]))
	print("Asset Size: %s" % data["asset_size"])
	
	# Rebuild the binary
	print("")
	print("---")
	print("")
	print("Parsing text strings")
	
	ttable = load_table()
	ttable2 = load_table_double()
	string_number = 0
	byte_sequence = {
		"bytes" : [],
		"text" : "",
		"alt_text" : "",
		"start_pos" : int(data["asset_rom_pointer_address"],16),
		"string_number" : 0
	}
	byte_sequences = []
	pos = int(data["asset_rom_pointer_address"],16)
	for byte in data["asset_chunk"]:
		
		byte = byte.upper()
		if byte != "00":
			# Not an end marker, so add it to the string and loop again
			byte_sequence["bytes"].append(byte)
			pos += 1
		else:
			# We read a "0x00" - so this marks end of string
			
			# Part 1, translate the string and add it to the list
			if len(byte_sequence["bytes"]) > 0:
				string_number += 1
				byte_sequence["string_number"] = string_number
				if VERBOSE:
					print("%3s: %s Found a %s length byte sequence" % (string_number, hex(pos - len(byte_sequence["bytes"])), len(byte_sequence["bytes"])))
				byte_sequence = translate_string(byte_sequence = byte_sequence, trans_table = ttable, trans_table_double = ttable2, alt = False, old_assets = False, VERBOSE = VERBOSE)
				byte_sequences.append(byte_sequence)
			
			# Part 2, add the end byte
			string_number += 1
			if VERBOSE:
				print("%3s: %s End marker" % (string_number, hex(pos)))
			
			byte_sequence = {
				"string_number" : string_number,
				"bytes" : [byte],
				"text" : "<end>",
				"alt_text" : "<end>",
				"start_pos" : pos,
			}
			pos += 1
			byte_sequences.append(byte_sequence)
			
			# Make a new, empty data structure for the next string
			#string_number += 1
			byte_sequence = {
				"string_number" : string_number,
				"bytes" : [],
				"text" : "",
				"alt_text" : "",
				"start_pos" : pos,
			}
				
	print("")
	print("Found a total of %s strings" % len(byte_sequences))
	print("")
	print("---")
	print("")
	print("Writing strings to data file: %s" % (OUT_DIR + "/" + INPUT_NAME))
	if OVERWRITE is False:
		if os.path.isfile(OUT_DIR + "/" + INPUT_NAME):
			print("Output File: %s <- ERROR, Output file already exists" % (OUT_DIR + "/" + INPUT_NAME))
			sys.exit(2)
			
	file_out = open(OUT_DIR + "/" + INPUT_NAME, "w")
	file_out.write("{\n")
	file_out.write("	\"bank\" : \"%s\",\n" % data["bank"])
	file_out.write("	\"asset_index\" : \"%s\",\n" % data["asset_index"])
	file_out.write("	\"asset_rom_pointer_value\" : \"%s\",\n" % data["asset_rom_pointer_value"])
	file_out.write("	\"asset_rom_pointer_address\" : \"%s\",\n" % data["asset_rom_pointer_address"])
	file_out.write("	\"asset_rom_pointer_address_limit\" : \"%s\",\n" % data["asset_rom_pointer_address_limit"])
	file_out.write("	\"asset_size\" : %s,\n" % (int(data["asset_rom_pointer_address_limit"], 16) - int(data["asset_rom_pointer_address"], 16)))
	file_out.write("	\"strings\" : [\n")
	for byte_sequence in byte_sequences:
		file_out.write("		{\n")
		file_out.write("			\"string_number\" : %s,\n" % byte_sequence["string_number"])
		file_out.write("			\"string_size\" : %s,\n" % len(byte_sequence["bytes"]))
		file_out.write("			\"start_pos\" : \"%s\",\n" % hex(byte_sequence["start_pos"]))
		# Write out the raw byte sequence
		file_out.write("			\"bytes\" : [")
		for c in byte_sequence["bytes"]:
			file_out.write("\"")
			file_out.write(c.lower())
			file_out.write("\", ")
		file_out.seek(-2, 1)
		file_out.write("],\n")
		
		# Write out the first pass translation
		file_out.write("			\"PCE_japanese\" : \"")
		for c in byte_sequence["text"]:
			file_out.write(c)
		file_out.write("\",\n")
		
		# Space for SNES translation
		file_out.write("			\"SNES_japanese\" : \"\",\n")
		file_out.write("			\"SNES_english\" : \"\",\n")
		file_out.write("			\"SNES_accuracy\" : 0.0,\n")
		
		# Space for English translation
		file_out.write("			\"PCE_english\" : \"\",\n")
		
		# Notes
		file_out.write("			\"notes\" : \"\"\n")
		
		file_out.write("		},\n")
	file_out.seek(-2, 1)
	file_out.write("\n	]\n")
	file_out.write("}")
	file_out.close()
	print("")
	print("Done")