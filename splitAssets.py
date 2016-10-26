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
INPUT_NAME = "assets/raw/0x14.0x83.dat"
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

for o, a in opts:
	if o == "-h":
		print("A simple tool for splitting text asset blocks from the data files")
		print("produced by the tool 'extractAssets.py'. Note this needs to be run for each asset chunk file.")
		print("")
		print("Options:")
		print("-h	Show help text")
		print("-v	Enable verbose output")
		print("-i	Input file name (e.g. 'assets/raw/0x14.0x83.dat')")
		print("-f	Force overwite of output file even if it already exists")
		print("")
		print("Example:")
		print("extractAssets.py -i 'assets/raw/0xC.0x9.dat'")
		print("")
		sys.exit(0)
		
	if o == "-v":
		VERBOSE = True
		
	if o == "-i":
		INPUT_NAME = a
		
	if o == "-f":
		OVERWRITE = True

print("Configuration")
print("=============")
print("Verbose: %s" % VERBOSE)
print("Over-write: %s" % OVERWRITE)
if os.path.isfile(INPUT_NAME):
	print("Input Asset File: %s <- OK" % INPUT_NAME)
else:
	print("Input Asset File: %s <- ERROR, input file not found!" % INPUT_NAME)
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

print("Loading asset file %s" % INPUT_NAME)
file_data = open(INPUT_NAME).read()
data = json.loads(file_data)
data["strings"] = []
print("Asset Bank: %s" % data["bank"])
print("Asset Index: %s" % data["asset_index"])
print("Asset Pointer: %s" % data["asset_rom_pointer_address"])
print("Asset ROM Address: %s-%s" % (data["asset_rom_pointer_address"], data["asset_rom_pointer_address_limit"]))
print("Asset Size: %s" % data["asset_size"])

# Rebuild the binary
print("")
print("Parsing text strings")

ttable = load_table()
ttable2 = load_table_double()
string_number = 0
byte_sequence = {
	"bytes" : [],
	"text" : "",
	"alt_text" : "",
	"start_pos" : int(data["asset_rom_pointer_address"],16)
}
byte_sequences = []
pos = int(data["asset_rom_pointer_address"],16)
for byte in data["asset_chunk"]:
	pos += 1
	byte = byte.upper()
	if byte != "00":
		# Not an end marker, so add it to the string and loop again
		byte_sequence["bytes"].append(byte)
	else:

		# Part 1, translate the string and add it to the list
		string_number += 1
		print("%3s: %s Found a %s length byte sequence" % (string_number, hex(pos - len(byte_sequence["bytes"])), len(byte_sequence["bytes"])))
		byte_sequence = translate_string(byte_sequence, ttable, ttable2, False, False)
		byte_sequence = translate_string(byte_sequence, ttable, ttable2, True, False)
		byte_sequences.append(byte_sequence)
		
		# Part 2, add the end byte
		byte_sequence = {
			"string_number" : string_number,
			"bytes" : [byte],
			"text" : "",
			"alt_text" : "",
			"start_pos" : (pos - len(byte_sequence["bytes"])),
		}
		string_number += 1
		print("%3s: Found a 1 byte end marker" % string_number)
		byte_sequences.append([byte_sequence])
		
		# Make a new, empty data structure for the next string
		byte_sequence = {
			"string_number" : string_number,
			"bytes" : [],
			"text" : "",
			"alt_text" : "",
			"start_pos" : pos,
		}
		
print(len(byte_sequences))
#byte = struct.unpack('c', f.read(1))[0]
#new_string
#f.close()