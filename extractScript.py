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


extractScript.py
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
############ < User configuration > ##################
######################################################

# Holds all missing translation characters encountered
MISSING_BYTES = {}

# Translation table loader
from Table import load_table, load_table_double

# Default values
from config import ROM_NAME, TABLE_NAME, TABLE_NAME_DOUBLE, OUT_NAME
from config import OVERWRITE, VERBOSE
from config import SWITCH_MODE, KANJI_CODE
from config import DAKUTEN_ALL, DAKUTEN, DAKUTEN_REPLACE, PC_NAME, PC_NAMES

# Load the definitions of which ranges in the files to examine
from config import BYTES
from config import METHOD_1, METHOD_2, METHOD_3
from config import METHOD_1_OFFSET, METHOD_2_OFFSET, METHOD_3_OFFSET
from config import METHOD_1_TRAILING_BYTES, METHOD_2_TRAILING_BYTES, METHOD_3_TRAILING_BYTES

######################################################
############ < Code starts here > ####################
######################################################

def translate_double_string(bytes, trans_table_double, alt=False):
	"""
	translate_double_string - construct the actual text, using multi-byte, double height (aka Kanji ideograms)
	where appropriate.
	"""

	new_bytes = []
	# Can only work with even string lengths
	if (len(bytes)%2==0):
		if VERBOSE:
			print ""
		check_bytes = []
		b_pos_start = 0
		b_pos_end = 2
		while b_pos_end <= len(bytes):
			b = ""
			b_range = bytes[b_pos_start:b_pos_end]

			for ch in b_range:

				b += str(binascii.hexlify(ch))
			if VERBOSE:
				print "Searching for <%s>" % str(b.upper())
			# Double height strings are only ever an even number
			if b.upper() in trans_table_double.keys():
				
				bt = trans_table_double[b.upper()]["pre_shift"]
				if VERBOSE:
					print "Found %s" % bt
				new_bytes.append("%s" % bt)
				b_pos_start = b_pos_end
				b_pos_end = b_pos_start + 2
			else:
				#print "Not Found"
				# warning - byte sequence not in table
				b_pos_end += 2
				b_range = bytes[b_pos_start:b_pos_end]
				if b_pos_end > len(bytes):
					for ch in b_range:
						new_bytes.append("<" + str(binascii.hexlify(ch)) + ">")
		if len(new_bytes) == 0:
			new_bytes = bytes
		if VERBOSE:
			print "End <%s>" % new_bytes
		return new_bytes
	else:
		if VERBOSE:
			print "Not a valid double height string"
		return bytes

def translate_string(byte_sequence, trans_table, trans_table_double, alt=False):
	"""
	translate_string - construct the actual text, using multi-byte characters
	where appropriate, that represent the hex codes found in the rom.
	e.g. 0x1A 0x5F 0x76 0x61 0x62 0x63 0x64 0x65 0x00 = <control><control>vabcde<end>
	"""

	if VERBOSE:
		print hex(byte_sequence["start_pos"])
					
	# method1 has two leading control bytes and a null byte as terminator
	text_key = "text"
	previous_b = ""
	switch_mode = False
	# Record the start bytes
	# TO DO!
	if (byte_sequence["method"] == METHOD_1):
		offset = METHOD_1_OFFSET
		trailing_bytes = METHOD_1_TRAILING_BYTES
		switch_mode = False
	
	if (byte_sequence["method"] == METHOD_2):
		offset = METHOD_2_OFFSET
		trailing_bytes = METHOD_2_TRAILING_BYTES
		switch_mode = True
			
	if (byte_sequence["method"] == METHOD_3):
		switch_mode = False
		offset = METHOD_3_OFFSET
		trailing_bytes = METHOD_3_TRAILING_BYTES
	
	if alt:
		switch_mode = not switch_mode
		text_key = "alt_text"
	
	
	byte_sequence[text_key] = []
	already_i = 0
	if VERBOSE:
		print ""
		print "String @ %s (%s bytes)" % (hex(byte_sequence["start_pos"]), len(byte_sequence["bytes"]))
	for i in range(0, len(byte_sequence["bytes"]) - trailing_bytes):
		#print "Index %s" % i
		already_decoded = False
		decode_it = False
		b1 = str(binascii.hexlify(byte_sequence["bytes"][i-1])).upper()
		# Don't process dakuten/handakuten
		# Is the next byte a dakuten/handakuten?
		b2 = str(binascii.hexlify(byte_sequence["bytes"][i])).upper()
		if b2 in DAKUTEN:
			if i > already_i:
				if VERBOSE:
					print "Processing composite dakuten char at Index %s" % i
				# Use a composite byte instead
				b = b1 + b2
				already_i = i + 1
				decode_it = True
		elif (b1 == PC_NAME) and (b2.upper() in PC_NAMES):
			if i > already_i:
				if VERBOSE:
					print "Processing PC name at Index %s" % i
				b = b1 + b2
				already_i = i + 1
				decode_it = True
		elif (b1 == KANJI_CODE):
			if VERBOSE:
				print "Processing double height char at Index %s" % i
			if i > already_i:
				double_byte_pos = byte_sequence["start_pos"] + i
				
				try:
					if len(byte_sequence["bytes"][i+1:i+int(b2, 16)+1]) >= int(b2, 16):
						if VERBOSE:
							print "Processing Index %s" % i					
							print "Double height lookup @ %s (%s %s)" % (hex(double_byte_pos), b1, b2)
						
						
						br = byte_sequence["bytes"][i+1:i+int(b2, 16)+1]
						
						already_i = i + int(b2, 16) + 1
						translated_chars = translate_double_string(br, trans_table_double)
						for c in translated_chars:
							byte_sequence[text_key].append(c)
						already_decoded = True
						if VERBOSE:
							print "Jump to %s" % already_i
					else:
						if VERBOSE:
							print "Not a Kanji code @ %s (%s %s, but only %s bytes)" % (hex(double_byte_pos), b1, b2, len(byte_sequence["bytes"][i+1:i+int(b2, 16)+1]))
						decode_it = True
						b = b1
				except Exception as e:
					print traceback.format_exc()
					print e
					b = b1
		else:
			if i > already_i:
				#print "Processing Index %s" % i
				b = b1		
		bt = ""
		if ((i > already_i) and (already_decoded == False)) or (decode_it == True):
			if switch_mode:
				if b == SWITCH_MODE:
					switch_mode = False
				else:
					if b.upper() in trans_table.keys():
						bt = trans_table[b.upper()]["post_shift"]
						byte_sequence[text_key].append(bt)
					else:
						# warning - byte sequence not in table
						record_missing(b, MISSING_BYTES, byte_sequence["start_pos"] + i)
						byte_sequence[text_key].append("<%s>" % b)
					if VERBOSE:
						print "%6s %2s %6s %5s" % (b, i, bt, switch_mode)
			else:
				if b == SWITCH_MODE:
					switch_mode = True
				else:
					if b.upper() in trans_table.keys():
						bt = trans_table[b.upper()]["pre_shift"]
						byte_sequence[text_key].append(bt)
					else:
						# warning - byte sequence not in table
						record_missing(b, MISSING_BYTES, byte_sequence["start_pos"] + i)
						byte_sequence[text_key].append("<%s>" % b)
					if VERBOSE:
						print "%6s %2s %6s %5s" % (b, i, bt, switch_mode)
	return byte_sequence

######################################################

def record_missing(b, missing_bytes, pos):
	"""
	Record a missing byte translation.
	"""
	
	if b in missing_bytes.keys():
		missing_bytes[b].append({'byte': b, 'pos' : pos})
	else:
		missing_bytes[b] = []
		missing_bytes[b].append({'byte': b, 'pos' : pos})	

######################################################

def method1(rom_start_address, rom_end_address, insert_method, description):
	""" 
	method1 - extract text from a given byte range using
	the notation of 2 control bytes, a variable number of
	text bytes and then a single null closing byte.
	This is a common notation used throughout the game for
	interactive dialogue.
	e.g. 0x1A 0x2B 0x60 0x61 0x62 0x63 0x64 0x65 0x00
	"""
		
	ttable = load_table()
	ttable2 = load_table_double()
	
	f = open(ROM_NAME, "rb")
	f.seek(rom_start_address, 0)
	rom_addr = rom_start_address
	
	byte_strings = []
	byte_sequence = {}
	byte_sequence["start_pos"] = rom_addr
	byte_sequence["bytes"] = []
	byte_sequence["size"] = 0
	byte_sequence["method"] = METHOD_1
	byte_sequence["start_bytes"] = []
	byte_sequence["block_start"] = rom_start_address
	byte_sequence["block_end"] = rom_end_address
	byte_sequence["block_description"] = description
	byte_sequence["start_bytes"] = []
	byte_sequence["end_bytes"] = []
				
	while (rom_addr <= rom_end_address):
		# Read a byte from the file at the current position
		try:
			# Increment position ID
			rom_addr += 1
			byte = struct.unpack('c', f.read(1))[0]
			if byte != "\x00":
				# Add the byte
				byte_sequence["bytes"].append(byte)
			else:
				# Add the end byte and record the string
				byte_sequence["bytes"].append(byte)
				byte_sequence["size"] = len(byte_sequence["bytes"])
				
				# Generate the actual text string (which we will print for translation)s
				byte_sequence = translate_string(byte_sequence, ttable, ttable2)
				byte_sequence = translate_string(byte_sequence, ttable, ttable2, alt=True)
				
				# Record just the start bytes
				if len(byte_sequence["bytes"]) > 1:
					byte_sequence["start_bytes"].append(byte_sequence["bytes"][0])
					byte_sequence["start_bytes"].append(byte_sequence["bytes"][1])
					
				byte_sequence["end_bytes"].append(byte)
				
				# Record the data
				byte_strings.append(byte_sequence)
				
				# Start a new byte sequence
				byte_sequence = {}
				byte_sequence["start_pos"] = rom_addr
				byte_sequence["bytes"] = []
				byte_sequence["size"] = 0
				byte_sequence["method"] = METHOD_1
				byte_sequence["start_bytes"] = []
				byte_sequence["block_start"] = rom_start_address
				byte_sequence["block_end"] = rom_end_address
				byte_sequence["block_description"] = description
				byte_sequence["start_bytes"] = []
				byte_sequence["end_bytes"] = []
			
		except Exception as e:
			print e
	f.close()
	return byte_strings
	
######################################################
	
def method2(rom_start_address, rom_end_address, insert_method, description):
	"""
	method2 - extract text from a given byte range using
	the notation of each string being delimited by (0x04 0x3c).
	This format is used during the introductory cinematics.
	e.g. 0x60 0x61 0x62 0x63 0x64 0x65 0x04 0x3C 
	"""
	
	ttable = load_table()
	ttable2 = load_table_double()
		
	f = open(ROM_NAME, "rb")
	f.seek(rom_start_address, 0)
	rom_addr = rom_start_address
	
	byte_strings = []
	byte_sequence = {}
	byte_sequence["block_start"] = rom_start_address
	byte_sequence["block_end"] = rom_end_address
	byte_sequence["block_description"] = description
	byte_sequence["start_pos"] = rom_addr
	byte_sequence["bytes"] = []
	byte_sequence["size"] = 0
	byte_sequence["method"] = METHOD_2
	byte_sequence["start_bytes"] = []
	byte_sequence["end_bytes"] = []
	
	end_byte1 = False
	end_byte2 = False
	
	while (rom_addr <= rom_end_address):
		# Read a byte from the file at the current position
		try:
			# Increment position ID
			rom_addr += 1
			byte = struct.unpack('c', f.read(1))[0]
			
			# Add the end byte and record the string
			if byte == "\x04":
				end_byte1 = True
				
			if byte == "\x3c":
				end_byte2 = True
			
			# Have both end byte1 and 2 been seen?
			if end_byte1 and end_byte2:
			
				byte_sequence["bytes"].append(byte)
				byte_sequence["size"] = len(byte_sequence["bytes"])
				
				# Record just the start bytes
				if len(byte_sequence["bytes"]) > 1:
					byte_sequence["end_bytes"].append(byte_sequence["bytes"][-2])
					byte_sequence["end_bytes"].append(byte_sequence["bytes"][-1])
				
				# Generate the actual text string (which we will print for translation)s
				byte_sequence = translate_string(byte_sequence, ttable, ttable2)
				byte_sequence = translate_string(byte_sequence, ttable, ttable2, alt=True)
				
				# Record the data
				byte_strings.append(byte_sequence)
				
				# Start a new byte sequence
				byte_sequence = {}
				byte_sequence["start_pos"] = rom_addr
				byte_sequence["bytes"] = []
				byte_sequence["size"] = 0
				byte_sequence["method"] = METHOD_2
				byte_sequence["block_start"] = rom_start_address
				byte_sequence["block_end"] = rom_end_address
				byte_sequence["block_description"] = description
				byte_sequence["start_bytes"] = []
				byte_sequence["end_bytes"] = []
				end_byte1 = False
				end_byte2 = False
			else:
				byte_sequence["bytes"].append(byte)
				
		except Exception as e:
			print e
	f.close()
	return byte_strings

######################################################
	
def method3(rom_start_address, rom_end_address, insert_method, description, end_byte = "\x00"):
	"""
	method3 - extract text from a given byte range using
	the notation of each string has no start control bytes
	and is only delimited by a single control byte to end (0x00).
	Main menus, title screen etc.
	e.g. 0x60 0x61 0x62 0x63 0x64 0x65 0x00
	"""
	ttable = load_table()
	ttable2 = load_table_double()
	
	f = open(ROM_NAME, "rb")
	f.seek(rom_start_address, 0)
	rom_addr = rom_start_address
	
	byte_strings = []
	byte_sequence = {}
	byte_sequence["block_start"] = rom_start_address
	byte_sequence["block_end"] = rom_end_address
	byte_sequence["block_description"] = description
	byte_sequence["start_pos"] = rom_addr
	byte_sequence["bytes"] = []
	byte_sequence["size"] = 0
	byte_sequence["method"] = METHOD_3
	byte_sequence["start_bytes"] = []
	byte_sequence["end_bytes"] = []
	
	while (rom_addr <= rom_end_address):
		# Read a byte from the file at the current position
		try:
			# Increment position ID
			rom_addr += 1
			byte = struct.unpack('c', f.read(1))[0]
			if byte != end_byte:
				# Add the byte
				byte_sequence["bytes"].append(byte)
			else:
				# Add the end byte and record the string
				byte_sequence["bytes"].append(byte)
				byte_sequence["size"] = len(byte_sequence["bytes"])
				
				# Generate the actual text string (which we will print for translation)s
				byte_sequence = translate_string(byte_sequence, ttable, ttable2)
				byte_sequence = translate_string(byte_sequence, ttable, ttable2, alt=True)
				
				byte_sequence["end_bytes"].append(byte)
				
				# Record the data
				byte_strings.append(byte_sequence)
				
				# Start a new byte sequence
				byte_sequence = {}
				byte_sequence["start_pos"] = rom_addr
				byte_sequence["bytes"] = []
				byte_sequence["size"] = 0
				byte_sequence["method"] = METHOD_3
				byte_sequence["block_start"] = rom_start_address
				byte_sequence["block_end"] = rom_end_address
				byte_sequence["block_description"] = description
				byte_sequence["start_bytes"] = []
				byte_sequence["end_bytes"] = []
				
		except Exception as e:
			print e
	f.close()
	return byte_strings



######################################################

def write_export(byte_strings):
	"""
	Writes the document used for translation.
	"""
	
	stats = {}
	stats["filename"] = OUT_NAME

	if os.path.isfile(OUT_NAME):
		if OVERWRITE:
			f = open(OUT_NAME, "w")
		else:
			print "Sorry, refusing to overwrite existing output file. Perhaps use the '-f' flag" 
			sys.exit(2)
	else:
		f = open(OUT_NAME, "w")
				

	for byte_range in byte_strings:
		f.write("{\n")
		f.write("\"block_description\" : \"%s\",\n" % byte_range["block_description"])
		f.write("\"block_start\" : \"%s\",\n" % hex(byte_range["block_start"]))
		f.write("\"block_end\" : \"%s\",\n" % hex(byte_range["block_end"]))
		f.write("\"insert_method\" : %s,\n" % byte_range["insert_method"])
		f.write("\"data\" : [\n")
		for b in byte_range["data"]:
			f.write("    {\n")
			f.write("        \"string_description\" : \"%s\",\n" % b["block_description"])
			f.write("        \"string_start\" : \"%s\",\n" % hex(b["start_pos"]))
			f.write("        \"method\" : %s,\n" % b["method"])
			f.write("        \"start_bytes\" : [")
			for c in b["start_bytes"]:
				f.write("\"")
				f.write(str(binascii.hexlify(c)))
				f.write("\",")
			if len(b["start_bytes"]) > 0:
				f.seek(-1, 1)
			f.write("],\n")
			f.write("        \"end_bytes\" : [")
			for c in b["end_bytes"]:
				f.write("\"")
				f.write(str(binascii.hexlify(c)))
				f.write("\",")
			if len(b["end_bytes"]) > 0:
				f.seek(-1, 1)
			f.write("],\n")
			f.write("        \"raw_size\" : %s,\n" % b["size"])	
			f.write("        \"raw\" : [")
			for c in b["bytes"]:
				f.write("\"")
				f.write(str(binascii.hexlify(c)))
				f.write("\", ")
			f.seek(-2, 1)
			f.write("],\n")
			f.write("        \"raw_text\" : \"")
			for c in b["text"]:
				f.write(c)
			f.write("\",\n")
			
			f.write("        \"alt_text\" : \"")	
			for c in b["alt_text"]:
				f.write(c)
			f.write("\",\n")
					
			f.write("        \"trans_size\" : 0,\n")
			f.write("        \"trans_text\" : \"\"\n")
			f.write("    },\n\n")
		f.seek(-3, 1)
		f.write("\n]")
		f.write("},\n")
	f.seek(-3, 1)
	f.write("  ")
	f.close()

	stats["filesize"] = os.path.getsize(OUT_NAME)
	print "Done"
	return stats

######################################################

def missing_stats():
	"""
	Print details about missing translation bytes.
	"""

	print "Missing character translations: %s" % len(MISSING_BYTES)
	if VERBOSE:
		print "Character | Occurences"
		for b in MISSING_BYTES.keys():
			print "%9s | %4s " % (b, len(MISSING_BYTES[b]))
	print "Done"
	

######################################################

def document_stats(report_stats):
	"""
	Print details about the exported document.
	"""
	
	print "Export filename: %s" % report_stats["filename"]
	print "Export filesize: %s bytes" % report_stats["filesize"]
	print "Done"

######################################################
########## < Run-time code start here > ##############
######################################################

try:
	opts, args = getopt.getopt(sys.argv[1:], "hvi:t:o:f")
except getopt.GetoptError as err:
	print err
	sys.exit(2)

print ""
print "extractScript.py - Script extractor for Cyber Knight"
print "----------------"
print ""

for o, a in opts:
	if o == "-h":
		print "A simple tool for extracting text dialogue from the game 'Cyber Knight' for the PC-Engine."
		print "The tool scans a number of locations within the input ROM file and extracts dialogue strings"
		print "in one of several known formats."
		print "The output is then written to a well-formatted JSON file for translation and later insertion."
		print ""
		print "Options:"
		print "-h	Show help text"
		print "-v	Enable verbose output"
		print "-i	Input file name (e.g. 'Cyber Knight (J).pce')"
		print "-t	Translation file name (e.g. 'CyberKnightTranslation.csv')"
		print "-o	Output file name (e.g. 'Cyber Knight.json')"
		print "-f	Force overwite of output file even if it already exists"
		print ""
		print "Edit config.py to your needs (rom hex locations, string type, etc) and then run the script."
		print ""
		print "Example:"
		print "extractScript.py -i 'Cyber Knight (J).pce' -t 'table.csv' -o 'patches/script.json'"
		print ""
		sys.exit(0)
		
	if o == "-v":
		VERBOSE = True
		
	if o == "-i":
		ROM_NAME = a

	if o == "-t":
		TABLE_NAME = a

	if o == "-o":
		OUT_NAME = a
		
	if o == "-f":
		OVERWRITE = True

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
	
if os.path.isfile(TABLE_NAME):
	print "Translation Table File: %s <- OK" % TABLE_NAME
else:
	print "Translation Table File: %s <- ERROR, translation table not found!" % TABLE_NAME
	sys.exit(2)

print "Output File: %s" % OUT_NAME
print ""

#############################################
# Loop over defined ranges and extract text
#############################################

print "Extracting dialogue"
print "==================="
print ""
found_byte_strings = []
# Sort dialogue ranges by starting address
SORTED_BYTES = sorted(BYTES, key=lambda t: t[1])
for byte_range in SORTED_BYTES:
	data = []
	cnt = 0
	print "================="
	print "Extracting %s-%s" % (hex(byte_range[1]), hex(byte_range[2]))
	print "-----------------"
	if byte_range[0] == METHOD_1:
		print "Extract Method 1 : Insert Method %s" % (byte_range[3])
		data = {}
		data["block_description"] = byte_range[4]
		data["block_start"] = byte_range[1]
		data["block_end"] = byte_range[2]
		data["insert_method"] = byte_range[3]
		data["data"] = method1(data["block_start"], data["block_end"], data["insert_method"], data["block_description"])
		found_byte_strings.append(data)
	if byte_range[0] == METHOD_2:
		print "Extract Method 2 : Insert Method %s" % (byte_range[3])
		data = {}
		data["block_description"] = byte_range[4]
		data["block_start"] = byte_range[1]
		data["block_end"] = byte_range[2]
		data["insert_method"] = byte_range[3]
		data["data"] = method2(data["block_start"], data["block_end"], data["insert_method"], data["block_description"])
		found_byte_strings.append(data)
	if byte_range[0] == METHOD_3:
		print "Extract Method 3 : Insert Method %s " % (byte_range[3])
		data = {}
		data["block_description"] = byte_range[4]
		data["block_start"] = byte_range[1]
		data["block_end"] = byte_range[2]
		data["insert_method"] = byte_range[3]
		data["end_byte"] = byte_range[5]
		data["data"] = method3(data["block_start"], data["block_end"], data["insert_method"], data["block_description"], data["end_byte"])
		found_byte_strings.append(data)
	print "Total Strings: %s" % len(data["data"])
	for d in data["data"]:
		cnt = cnt + d["size"]
	print "Total Bytes: %s" % cnt
	print ""
print "Done"
if len(SORTED_BYTES) > 0:
	#############################################
	# Write strings to document
	#############################################
	
	print "\nWriting Document"
	print "=================="
	report_stats = write_export(found_byte_strings)
	
	#############################################
	# Show what we found
	#############################################
	
	print "\nDocument stats"
	print "================"
	document_stats(report_stats)
	
	#############################################
	# Show any missing characters
	#############################################
	
	print "\nMissing data stats"
	print "===================="
	missing_stats()
