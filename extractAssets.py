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
ASSET_TABLE = "CyberKnight Asset Banks.csv"
OUT_NAME = "CyberKnight Assets.json"

ASSETS = []
ASSET_BANKS = []

######################################################
########## < Run-time code start here > ##############
######################################################

try:
	opts, args = getopt.getopt(sys.argv[1:], "hvi:t:o:f")
except getopt.GetoptError as err:
	print(err)
	sys.exit(2)

print ""
print "extractAssets.py - Asset block extractor for Cyber Knight"
print "----------------"
print ""

for o, a in opts:
	if o == "-h":
		print "A simple tool for extracting asset blockse from the game 'Cyber Knight' for the PC-Engine."
		print "The tool scans the asset blocks as described within 'CyberKnight Asset Banks.csv]"
		print ""
		print "Options:"
		print "-h	Show help text"
		print "-v	Enable verbose output"
		print "-i	Input file name (e.g. 'Cyber Knight (J).pce')"
		print "-o	Output file name (e.g. 'Cyber Knight.json')"
		print "-f	Force overwite of output file even if it already exists"
		print ""
		print "Example:"
		print "extractAssets.py -i 'Cyber Knight (J).pce' -o 'CyberKnight Assets.json'"
		print ""
		sys.exit(0)
		
	if o == "-v":
		VERBOSE = True
		
	if o == "-i":
		ROM_NAME = a

	if o == "-t":
		ASSET_TABLE = a

	if o == "-o":
		OUT_NAME = a
		
	if o == "-f":
		OVERWRITE = True
		
######################################################
########## < Run-time code start here > ##############
######################################################

print("Configuration")
print("=============")
print("Verbose: %s" % VERBOSE)
print("Over-write: %s" % OVERWRITE)
if os.path.isfile(ROM_NAME):
	print("Input ROM File: %s <- OK" % ROM_NAME)
else:
	print("Input ROM File: %s <- ERROR, input file not found!" % ROM_NAME)
	sys.exit(2)
if os.path.isfile(ASSET_TABLE):
	print("Asset Table File: %s <- OK" % ASSET_TABLE)
else:
	print("Asset Table File: %s <- ERROR, Asset Table file not found!" % ASSET_TABLE)
	sys.exit(2)	
	
print("Output File: %s" % OUT_NAME)
print("")

try:
	file_rom = open(ROM_NAME, "ro")
	file_table = open(ASSET_TABLE, "ro")
	
	# First get a unique list of asset bank id's
	for l in file_table:
		asset_bank = l.split(',')[0]
		ASSET_BANKS.append(asset_bank)
		
	asset_ids = list(set(ASSET_BANKS))
	asset_ids.sort()
	print(asset_ids)
	
	# Find all the asset pointers for each asset bank
	for asset_id in asset_ids:
		for l in file_table:
			asset_bank_id = l.split(',')[0]
			if asset_bank_id == asset_id:
				pass
				
		#asset_index = l.split(',')[1]
		#asset_pointer = l.split(',')[2]
		#asset_block_start = l.split(',')[3]
		#asset_block_end = l.split(',')[4]
		#asset_rom_location = l.rstrip().split(',')[5]
		#print(asset_rom_location)
except Exception as e:
	print(e)