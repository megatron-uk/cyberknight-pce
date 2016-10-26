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

def translate_string(byte_sequence, trans_table, trans_table_double, alt=False, old_assets = True):
	"""
	translate_string - construct the actual text, using multi-byte characters
	where appropriate, that represent the hex codes found in the rom.
	e.g. 0x1A 0x5F 0x76 0x61 0x62 0x63 0x64 0x65 0x00 = <control><control>vabcde<end>
	"""

	
					
	# method1 has two leading control bytes and a null byte as terminator
	text_key = "text"
	previous_b = ""
	switch_mode = False
	# Record the start bytes
	# TO DO!
	if old_assets:
		
		if VERBOSE:
			print hex(byte_sequence["start_pos"])
		
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
	
		if VERBOSE:
			print ""
			print "String @ %s (%s bytes)" % (hex(byte_sequence["start_pos"]), len(byte_sequence["bytes"]))
	else:
		trailing_bytes = 0
	
	byte_sequence[text_key] = []
	already_i = 0
	
	for i in range(0, len(byte_sequence["bytes"]) - trailing_bytes):
		#print "Index %s" % i
		already_decoded = False
		decode_it = False
		if old_assets:
			b1 = str(binascii.hexlify(byte_sequence["bytes"][i-1])).upper()
		# Don't process dakuten/handakuten
		# Is the next byte a dakuten/handakuten?
			b2 = str(binascii.hexlify(byte_sequence["bytes"][i])).upper()
		else:
			b1 = byte_sequence["bytes"][i-1].upper()
			b2 = byte_sequence["bytes"][i].upper()
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