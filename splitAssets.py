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
import json

######################################################
########## < Config starts here > ####################
######################################################

VERBOSE = False
OVERWRITE = False
INPUT_NAME = "assets/raw/0xa.0x1.dat"
OUT_DIR = "assets/split"

from CyberKnightAssetBanks import ASSETS, ASSET_LOAD_TABLE, ASSET_OFFSET_TABLE
from CyberKnightAssetBanks import ASSET_LOAD_TABLE_SIZE, ASSET_OFFSET_TABLE_SIZE

from extractScript import translate_string
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
		
try:
	f = open(INPUT_NAME, "ro")
	if os.path.isdir(INPUT_NAME + ".split"):
		pass
	else:
		os.mkdir(INPUT_NAME + ".split")
except Exception as e:
	print(e)
	sys.exit(2)
	
bytes = f.read()
byte_sequences = []
byte_sequence = {
	"bytes" : [],
	"encoded_bytes" : [],
	"text" : "",
	"alt_text" : "",
	"start_pos" : 0,
}
ttable = load_table()
ttable2 = load_table_double()
string_number = 1
for b in bytes:
	byte = struct.unpack('c', b)[0]
	if byte != "\x00":
		byte_sequence["bytes"].append(byte)
		byte_sequence["encoded_bytes"].append(str(binascii.hexlify(byte)))
	else:
		print("Found a %s length byte sequence" % len(byte_sequence["encoded_bytes"]))
		
		byte_sequence = translate_string(byte_sequence, ttable, ttable2, False, False)
		byte_sequence = translate_string(byte_sequence, ttable, ttable2, True, False)
		print(byte_sequence["text"])
		
		split_file = open(INPUT_NAME + ".split/" + str(string_number), "w")
		for c in byte_sequence["text"]:
			split_file.write(c)
		split_file.close()
		byte_sequences.append(byte_sequence)
		string_number += 1
		# Add the end byte
		byte_sequence = {
			"bytes" : [byte],
			"encoded_bytes" : [str(binascii.hexlify(byte))],
			"text" : "",
			"alt_text" : "",
			"start_pos" : 0,
		}
		print("Found a 0 length byte sequence")
		byte_sequences.append([byte_sequence])
		split_file = open(INPUT_NAME + ".split/" + str(string_number), "w")
		for c in byte_sequence["text"]:
			split_file.write(c)
		split_file.close()
		# Create anew byte sequence
		byte_sequence = {
			"bytes" : [],
			"encoded_bytes" : [],
			"text" : "",
			"alt_text" : "",
			"start_pos" : 0,
		}
		
print(len(byte_sequences))
#byte = struct.unpack('c', f.read(1))[0]
#new_string
f.close()