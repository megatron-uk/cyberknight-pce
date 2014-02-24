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


injectScript.py
================
A script inserter for the PC-Engine game 'Cyber Knight'.

In order to run, it requires a headerless copy of the Cyber Knight ROM file
and a directory of 'patch' JSON files, as generated by extractScript.py

John Snowdon <john@target-earth.net>
"""

import os
import sys
import traceback
import getopt
import struct
import binascii
import json

try:
	import cStringIO as StringIO
except:
	print "cStringIO not available"
	import StringIO

######################################################
############ < User configuration > ##################
######################################################

# Holds all patch files
PATCH_FILES = {}

MISMATCH_OK = False

# Default values
from config import ROM_NAME, PATCH_DIR_NAME, PATCH_EXTENSION, OUT_ROM_NAME
from config import OVERWRITE, VERBOSE
from config import SWITCH_MODE
from config import DAKUTEN_ALL, DAKUTEN, DAKUTEN_REPLACE

# Load the definitions of which ranges in the files to examine
from config import BYTES
from config import METHOD_1, METHOD_2, METHOD_3
from config import METHOD_1_OFFSET, METHOD_2_OFFSET, METHOD_3_OFFSET
from config import METHOD_1_TRAILING_BYTES, METHOD_2_TRAILING_BYTES, METHOD_3_TRAILING_BYTES

######################################################
############ < Code starts here > ####################
######################################################

def patch_file(patchfile, patch, romfile):
	"""
	Load, encode and apply a translation patch segment to a file.
	"""
	for patch_segment in patch["data"]:
		apply_patch = True
		patch_segment["trans_size"] = len(patch_segment["trans_text"]) + len(patch_segment["start_bytes"]) + len(patch_segment["end_bytes"])
		if len(patch_segment["trans_text"]) == 0:
			print "%s - Skipping zero-length translation" % patch_segment["position"]
		else:
			if patch_segment["trans_size"] != patch_segment["raw_size"]:
				if MISMATCH_OK:
					print "%s - INFO! Applying, but string sizes are mismatched! (%s != %s)" % (patch_segment["position"], patch_segment["trans_size"], patch_segment["raw_size"])
				else:
					print "%s - WARNING! Not applying, string size mismatch! (%s != %s)" % (patch_segment["position"], patch_segment["trans_size"], patch_segment["raw_size"])
					apply_patch = False
			else:
				"%s - Applying" % patch_segment["position"]
			if apply_patch:
				# add start bytes
				# encode main text
				# if string + end bytes < raw text
				# 	pad with 0x5c bytes
				# add end bytes
				pass
			
	return True

######################################################
########## < Run-time code start here > ##############
######################################################

try:
	opts, args = getopt.getopt(sys.argv[1:], "hvi:d:o:fm")
except getopt.GetoptError as err:
	print err
	sys.exit(2)

print ""
print "injectScript.py - Script injector for Cyber Knight"
print "----------------"
print ""

for o, a in opts:
	if o == "-h":
		print "A tool which can inject translated patches (output generated by extractScript.py)"
		print "back in to the Cyber Knight rom file for the PC-Engine."
		print ""
		print "Options:"
		print "-h	Show help text"
		print "-v	Enable verbose output"
		print "-i	Input file name (e.g. 'Cyber Knight (J).pce')"
		print "-d	Directory containing translation patches (.json files) (e.g. './patches/')"
		print "-o	Output file name (e.g. 'Cyber Knight (E).pce')"
		print "-f	Force overwite of output file even if it already exists"
		print "-m	Attempt to patch file, even if translation string sizes are mismatched to originals."
		print ""
		sys.exit(0)
		
	if o == "-v":
		VERBOSE = True
		
	if o == "-i":
		ROM_NAME = a

	if o == "-d":
		PATCH_DIR_NAME = a

	if o == "-o":
		OUT_ROM_NAME = a
		
	if o == "-f":
		OVERWRITE = True
		
	if o == "-m":
		MISMATCH_OK = True
		
#############################################
# Print configuration
#############################################

print "Configuration"
print "============="
print "Verbose: %s" % VERBOSE
print "Over-write: %s" % OVERWRITE
if os.path.isfile(ROM_NAME):
	print "Input ROM File: %s <- OK" % ROM_NAME
else:
	print "Input ROM File: %s <- ERROR, input file not found!" % ROM_NAME
	sys.exit(2)
	
if os.path.isdir(PATCH_DIR_NAME):
	print "Patch Directory: %s <- OK" % PATCH_DIR_NAME
	for d in os.listdir(PATCH_DIR_NAME):
		if os.path.isfile(PATCH_DIR_NAME + "/" + d):
			PATCH_FILES[d] = {}
	if len(PATCH_FILES.keys()) < 1:
		print "Patches Found: 0 <- ERROR, no patches found!"
		sys.exit(2)
	else:
		print "Patches Found: %s <- OK" % len(PATCH_FILES) 
		for d in PATCH_FILES.keys():
			try:
				PATCH_FILES[d]["json"] = open(PATCH_DIR_NAME + "/" + d).read()
				PATCH_FILES[d]["data"] = json.loads(PATCH_FILES[d]["json"])
				t = 0
				for b in PATCH_FILES[d]["data"]:
					if len(b["trans_text"]) > 0:
						t += 1
				print "- %16s : %4s strings : %4s translations" % (d, len(PATCH_FILES[d]["data"]), t)
			except Exception as e:
				print "- %s <- ERROR, not a valid JSON file" % d
				print e
else:
	print "Patch Directory: %s <- ERROR, directory not found!" % PATCH_DIR_NAME
	sys.exit(2)

print "Output File: %s" % OUT_ROM_NAME
print ""

#################################################
# Use each patch file in turn
#################################################
print "Applying Translation Patches"
print "============================"
FILE = StringIO.StringIO(open(ROM_NAME).read())
for f in PATCH_FILES.keys():
	print "Applying %s" % f
	patch_file(f, PATCH_FILES[f], FILE) 