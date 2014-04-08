#!/usr/bin/env python
# -*- coding: utf-8
from __future__ import unicode_literals
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


mapScript.py
================
A script mapper for the PC-Engine game 'Cyber Knight' using the old
SNES English translation.

Tries to map untranslated strings from patches generated from 'extractScript.py'
to matches found in the SNES translation.

John Snowdon <john@target-earth.net>
"""

import os
import sys
import traceback
import getopt
import struct
import binascii
import hashlib
import re
try:
	import simplejson as json
	#print "Loading simplejson"
except:
	print "Warning: Falling back to json"
	import json
import difflib

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

# Translation table loader
from Table import load_snes_table, load_table

# Default values
from config import ROM_NAME, PATCH_DIR_NAME, PATCH_EXTENSION, OUT_ROM_NAME, TABLE_NAME, SNES_SCRIPT, OUT_DIR_NAME
from config import OVERWRITE, VERBOSE
from config import SWITCH_MODE
from config import DAKUTEN_ALL, DAKUTEN, DAKUTEN_REPLACE, PASS_NUMBER, FUZZY_LEVELS, FUZZY_AUTO_SELECT_LIMIT

# Load the definitions of which ranges in the files to examine
from config import BYTES
from config import METHOD_SIMPLE, METHOD_CONTIGUOUS
from config import METHOD_1, METHOD_2, METHOD_3
from config import METHOD_1_OFFSET, METHOD_2_OFFSET, METHOD_3_OFFSET
from config import METHOD_1_TRAILING_BYTES, METHOD_2_TRAILING_BYTES, METHOD_3_TRAILING_BYTES

squashed_pce_strings = {}
squashed_snes_strings = {}

######################################################
############ < Code starts here > ####################
######################################################

def squashPCEPatchSegment(raw_text):
	""" Squash a section of japanese PCE text by removing spaces, control codes etc """

	# Does a pre-squashed string already exist?
	#print "PCE Squashing :",raw_text
	h = hashlib.md5(raw_text.encode('utf-8')).hexdigest()
	if h in squashed_pce_strings.keys():
		t = squashed_pce_strings[h]
		#print "PCE Found     :", t
		return t
	else:
	 	# Remove control bytes
		text = re.sub('<..>','' , raw_text)
		ttable = load_table()
		# For any control strings as found in the translation table, remove them
		for byte_code in ttable.keys():
			try:
				if ttable[byte_code]["pre_shift"].startswith("<") and ttable[byte_code]["pre_shift"].endswith(">"):
					text = re.sub(ttable[byte_code]["pre_shift"], '', text)
			except:
				pass
		
		# Remove linebreaks
		text = text.replace('\n', '')
		text = text.replace('\\n', '')
		
		# Remove spaces
		text = text.replace(' ', '')
		
		# Convert dashed-dash to japanese single japanese dash
		text = text.replace('‥', '・')
		
		# Remove first japanese quotation mark
		try:
			text = text.split('「')[1]
		except:
			pass
		try:
			text = text.split('『')[1]
		except:
			pass
			
		if len(text) > 1:
			squashed_pce_strings[h] = text
			#print "PCE Squashed :", text
	return text

def squashSNESPatchSegment(snes_j_text):
	""" Squash a section of japanese SNES text by removing spaces, control codes etc """

	# Does a pre-squashed string already exist?
	#print "SNES Squashing:", snes_j_text
	h = hashlib.md5(snes_j_text).hexdigest()
        if h in squashed_snes_strings.keys():
		t = squashed_snes_strings[h]
		#print "SNES Found    :", t
		return t
        else:
		# Remove control bytes
		text = re.sub('{..}', '', snes_j_text)
		text = re.sub('\n', '', text)

		# Remove non printable characters
		try:
			text = re.sub('\n', '', text)
		except:
			try:
				text = re.sub('\n', '', text.decode('utf-8'))
			except:
				try:
					text = re.sub('\n', '', text.decode('shift-jis'))
				except:
					pass
		try:
			text = re.sub('\\n', '', text)
		except:
			try:
				text = re.sub('\\n', '', text.decode('utf-8'))
			except:
				try:
					text = re.sub('\\n', '', text.decode('shift-jis'))
				except:
					pass
		try:
			text = re.sub('\x32', '', text.decode('utf-8'))
		except:
			try:
				text = re.sub('\x32', '', text.decode('shift-jis'))
			except:
				pass

		try:
			text = re.sub(' ', '', text)
		except:
			pass
		
		# Remove first Japanese text quote	
		try:
			text = text.split('「')[1]
		except:
			pass
		try:
			text = text.split('『')[1]
		except:
			pass
		
		try:
			text = re.sub('ー', '-', text)
		except:
			pass
		
		if len(text) > 1:
			squashed_snes_strings[h] = text
			#print "SNES Squashed :", text
	return text



def selectMatch(patch_segment, possible_matches):
	""" Display a menu of possible matches """
	
	cnt = 0
	print ""
	for d in possible_matches:
		print "%s." % cnt
		print "    Accuracy   : %.5f" % d["best"]
		
		######################################################
		# Print out the PCE raw text
		try:
			print "    PCE Raw    : %s" % unicode(patch_segment["raw_text"], 'shift-jis').replace('\n', '\\n')
		except:
			sys.stdout.write("    PCE Raw    : ")
			for c in patch_segment["raw_text"].replace('\n', '\\n'):
				try:
					sys.stdout.write(c.decode('utf-8'))
				except:
					try:
						sys.stdout.write(c.decode('shift-jis'))
					except:
						sys.stdout.write(c)
			sys.stdout.write("\n")
			sys.stdout.flush()
		# Print out the SNES raw text
		try:
			print "    SNES Raw   : %s" % d["snes-j"].replace('\n', '\\n')
			sys.stdout.flush()
		except:
			sys.stdout.write("    SNES Raw   : ")
			for c in d["snes-j"]:
				try:
					sys.stdout.write(c.encode('utf-8'))
				except:
					try:
						sys.stdout.write(c.encode('shift-jis'))
					except:
						if c == "\n":
							c = "\\n"
						sys.stdout.write(c)
			sys.stdout.write("\n")
			sys.stdout.flush()
				
		######################################################	
		print ""
		print "    PCE Squash : %s" % d["pce-squashed"]
		print "    SNES Squash: %s" % d["snes-squashed"]

		######################################################	
		# Print out the SNES translation
		print ""
		print "    SNES Trans : %s" % d["snes-e"].replace('\n', '\\n')
		print ""
		sys.stdout.flush()
		cnt += 1
	
	# Allow user to choose translation
	print "Select a choice: "
	c = raw_input()
	try:
		ci = int(c)
	except:
		print "Skipped SNES translation"
		return False
	if ci in range(0, cnt):
		print "Selected SNES translation %s" % ci
		patch_segment["snes-e"] = possible_matches[ci]["snes-e"]
		patch_segment["snes-j"] = possible_matches[ci]["snes-j"]
		patch_segment["accuracy"] = possible_matches[ci]["best"]
		patch_segment["snes_size"] = len(possible_matches[ci]["snes-e"])
		patch_segment["snes_patched"] = 1
		return True
	else:
		print "Skipped SNES translation"
		return False

def mapScript(patchfile, patch, snes_table):
	""" Attempt to map to SNES translation """
	t = 0
	ut = 0
	mt = 0
	for patch_segment in patch["data"]["data"]:
		if (len(patch_segment["trans_text"]) != 0) or (len(patch_segment["raw"]) == 0) or ("snes-e" in patch_segment.keys()):
			t += 1
		else:
			ut += 1
	print "Attempting map of %s untranslated or unmatched strings" % ut
	if VERBOSE:
		print "---"
	for patch_segment in patch["data"]["data"]:
		if (len(patch_segment["trans_text"]) == 0) and (len(patch_segment["raw"]) > 2) and ("snes-e" not in patch_segment.keys()):
			matched = False
			snes_text = None
			if "alt_text" in patch_segment.keys():
				has_alt_text = True
			else:
				has_alt_text = False
				
			# Test for exact match
			for snes_text in snes_table.keys():
				if (snes_text == patch_segment["raw_text"].encode('utf-8')):
					matched = True
					# Exact matches are autopatched
					patch_segment["trans_text"] = snes_table[snes_text]
					break
					
				if has_alt_text:
					if (snes_text == patch_segment["alt_text"].encode('utf-8')):
						matched = True
						# Exact matches are autopatched
						patch_segment["trans_text"] = snes_table[snes_text]
						break
			if matched:
				if VERBOSE:
					print "%s - Successfully mapped" % patch_segment["string_start"]
				patch_segment["snes"] = { 'snes-e' : snes_table[snes_text], 'snes-j' : snes_text, 'ratio' : 1.0 }
				patch_segment["snes_patched"] = 1
				mt += 1
			else:	
				possible_matches = []
				best_matches = []
				# Attempt fuzzy match
				s1 = squashPCEPatchSegment(patch_segment["raw_text"])
				for snes_text in snes_table.keys():
					s2 = squashSNESPatchSegment(snes_text)
					#try:
					#sm = difflib.SequenceMatcher(lambda x: x in " \t\n", s1, s2)
					#except:
					sm = difflib.SequenceMatcher(None, s1, s2)
					# Do a quick check
					r = sm.quick_ratio()
					if r >= FUZZY_LIMIT:
						d = {}
						d["pce-squashed"] = s1
						d["snes-squashed"] = s2
						d["snes-e"] = snes_table[snes_text]
						d["snes-j"] = snes_text
						d["sm"] = sm
						d["ratio"] = r
						possible_matches.append(d)
				# Sort list of possibles
				if len(possible_matches) > 0:
					if VERBOSE:
						sys.stdout.write("%s - " % (patch_segment["string_start"]))
						sys.stdout.write( "Possibles: %4s " % len(possible_matches))
						sys.stdout.flush()
					for d in possible_matches:
						r = d["sm"].ratio()
						if r >= FUZZY_BEST_LIMIT:
							d["best"] = r
							best_matches.append(d)
        	                        
        	                        # Store the single best translation
					if len(best_matches) == 1:
						if best_matches[0]["best"] < FUZZY_AUTO_SELECT_LIMIT:
							print "Warning! Best match not high enough to auto select - confirm below:"
							patch_number = selectMatch(patch_segment, best_matches)
							if patch_number:
								mt += 1
						else:
							patch_segment["snes-e"] = best_matches[0]["snes-e"]
							patch_segment["snes-j"] = best_matches[0]["snes-j"]
							patch_segment["accuracy"] = best_matches[0]["best"]
							patch_segment["snes_size"] = len(best_matches[0]["snes-e"])
							patch_segment["snes_patched"] = 1
							mt += 1
						
					if VERBOSE:
                	                        sys.stdout.write("Best: %2s " % len(best_matches))
						if len(best_matches) == 1:
							sys.stdout.write("Accuracy: %.5f\n" % best_matches[0]["best"])
						else:
							sys.stdout.write("\n")
						sys.stdout.flush()
							
					# We got more than one best translation
					if len(best_matches) > 1:
						sorted_best_matches = sorted(best_matches, key=lambda k: k["best"])
						sorted_best_matches.reverse()
						patch_number = selectMatch(patch_segment, sorted_best_matches)
						if patch_number:
							mt += 1
					
				# Get highest 3
				# Prompt for user action
	if VERBOSE:
		print "---"
	print "Mapping routine found %s matches" % mt
	print "Mapping routine left %s untranslated" % (ut - mt)
	return patch
	
######################################################

def write_export(patch, filename):
	"""
	Writes the document used for translation.
	"""
	
	stats = {}
	stats["filename"] = filename

	if os.path.isfile(OUT_DIR_NAME + "/" + filename):
		if OVERWRITE:
			f = open(OUT_DIR_NAME + "/" + filename, "w")
		else:
			print "Sorry, refusing to overwrite existing output file. Perhaps use the '-f' flag" 
			sys.exit(2)
	else:
		f = open(OUT_DIR_NAME + "/" + filename, "w")
				


	f.write("{\n")
	if "block_description" in patch["data"].keys():
		try:
			f.write("\"block_description\" : \"%s\",\n" % patch["data"]["block_description"])
		except:
			f.write("\"block_description\" : \"%s\",\n" % patch["data"]["block_description"].encode('utf-8', 'ignore'))
	else:
		f.write("\"block_description\" : \"\",\n")
	f.write("\"block_start\" : \"%s\",\n" % (patch["data"]["block_start"]))
	f.write("\"block_end\" : \"%s\",\n" % (patch["data"]["block_end"]))
	f.write("\"insert_method\" : %s,\n" % patch["data"]["insert_method"])
	f.write("\"data\" : [\n")
	for b in patch["data"]["data"]:
		f.write("    {\n")
		if "block_description" in patch["data"].keys():
			f.write("        \"string_description\" : \"%s\",\n" % patch["data"]["block_description"])
		else:
			f.write("        \"string_description\" : \"\",\n")
		f.write("        \"string_start\" : \"%s\",\n" % (b["string_start"]))
		f.write("        \"method\" : %s,\n" % b["method"])
		f.write("        \"start_bytes\" : [")
		for c in b["start_bytes"]:
			f.write("\"")
			f.write(c)
			f.write("\",")
		if len(b["start_bytes"]) > 0:
			f.seek(-1, 1)
		f.write("],\n")
		f.write("        \"end_bytes\" : [")
		for c in b["end_bytes"]:
			f.write("\"")
			f.write(c)
			f.write("\",")
		if len(b["end_bytes"]) > 0:
			f.seek(-1, 1)
		f.write("],\n")
		f.write("        \"raw_size\" : %s,\n" % b["raw_size"])	
		
		# Write raw byte sequence
		f.write("        \"raw\" : [")
		if len(b["raw"]) > 0:
			for c in b["raw"]:
				f.write("\"")
				f.write(c)
				f.write("\", ")
			f.seek(-2, 1)
			f.write("],\n")
		else:
			f.write("],\n")
		
		# Write japanese text
		f.write("        \"raw_text\" : \"")
		if len(b["raw_text"]) > 0:
			for c in b["raw_text"]:
				if c == "\n":
					c = "\\n"
				f.write(c.encode('utf-8'))
			f.write("\",\n")
		else:
			f.write("\",\n")
		
		# Write alternate japanese text
		if "alt_text" in b.keys():	
			f.write("        \"alt_text\" : \"")	
			if len(b["raw_text"]) > 0:
				for c in b["alt_text"]:
					if c == "\n":
						c = "\\n"
					f.write(c.encode('utf-8'))
				f.write("\",\n")
			else:
				f.write("\",\n")

		# Write snes translation, if found
		if "snes-e" in b.keys():
			f.write("        \"snes_size\" : %s,\n" % len(b["snes-e"]))
			f.write("        \"snes-j\" : \"")
			for c in b["snes-j"]:
				try:
					if c == '\n':
						c = '\\n'
				except:
					try:
						if c.encode('utf-8') == '\n':
							c = '\\n'
					except:
						pass
				try:
					f.write(c)
				except:
					try:
						f.write(c.encode('utf-8'))
					except:
						f.write(c.encode('shift-jis'))
			f.write("\",\n")
			f.write("        \"snes-e\" : \"%s\",\n" % b["snes-e"].replace('\r\n', '').replace('\n', '\\n'))
			f.write("        \"accuracy\" : %s,\n" % b["accuracy"])
			
		# Write translated text, either manual or automatically matched
		f.write("        \"trans_size\" : %s,\n" % len(b["trans_text"]))
		f.write("        \"trans_text\" : \"")
		for c in b["trans_text"]:
			if c == "\n":
				c = "\\n"
			f.write(c.encode('utf-8'))
		f.write("\"\n")
		f.write("    },\n\n")
	f.seek(-3, 1)
	f.write("\n]")
	f.write("}\n")
	f.close()

	print "Done"
	return stats
	
######################################################
########## < Run-time code start here > ##############
######################################################

try:
	opts, args = getopt.getopt(sys.argv[1:], "hvs:d:o:p:f")
except getopt.GetoptError as err:
	print err
	sys.exit(2)

print ""
print "mapScript.py - Map untranslated patches from the PC-Engine CyberKnight to the SNES script"
print "----------------"
print ""

for o, a in opts:
	if o == "-h":
		print "A tool which can map sections of untranslated patch files (output generated by extractScript.py)"
		print "to translated sections from the English SNES translation, writing those translated strings back"
		print "into the PC-Engine patch files for use in injectScript.py later."
		print "If translated sections are found, then they are used instead of the SNES translation."
		print ""
		print "Options:"
		print "-h	Show help text"
		print "-v	Enable verbose output"
		print "-s	SNES script file name (e.g. 'CyberKnightSNES.csv')"
		print "-d	Directory containing untranslated/partially translated patches (.json files) (e.g. './patches/')"
		print "-o	Directory to write the modified translation patches (.json files) (e.g. './patches-processed/')"
		print "-f	Overwrite existing files (otherwise dry-run)"
		print "-p	Pass number (1 == strictest matching, 3 == least strict matching)"
		print ""
		print "Example:"
		print "mapScript.py -s 'CyberKnightSNES.csv' -d './patches/' -o './patches-processed/' -p 1"
		print ""
		sys.exit(0)
		
	if o == "-v":
		VERBOSE = True
		
	if o == "-i":
		ROM_NAME = a

	if o == "-d":
		PATCH_DIR_NAME = a

	if o == "-o":
		OUT_DIR_NAME = a

	if o == "-s":
		SNES_SCRIPT = a
		
	if o == "-p":
		PASS_NUMBER = a
		
	if o == "-f":
		OVERWRITE = True
		
# Load match levels depending on pass number
FUZZY_LIMIT = FUZZY_LEVELS[str(PASS_NUMBER)]["FUZZY_LIMIT"]
FUZZY_BEST_LIMIT = FUZZY_LEVELS[str(PASS_NUMBER)]["FUZZY_BEST_LIMIT"]
		
#############################################
# Print configuration
#############################################

print "Configuration"
print "============="
print "Verbose: %s" % VERBOSE
print "Over-write: %s" % OVERWRITE
print "Pass Type: %s" % PASS_NUMBER
	
if os.path.isfile(SNES_SCRIPT):
	print "SNES Script File: %s <- OK" % SNES_SCRIPT
else:
	print "SNES Script File: %s <- ERROR, SNES script not found!" % SNES_SCRIPT
	sys.exit(2)
	
if os.path.isdir(OUT_DIR_NAME):
	print "Output Directory: %s <- OK" % OUT_DIR_NAME
else:
	print "Output Directory: %s <- ERROR, directory not found!" % OUT_DIR_NAME
	sys.exit(2)
	
if os.path.isdir(PATCH_DIR_NAME):
	print "Patch Directory: %s <- OK" % PATCH_DIR_NAME
	for d in os.listdir(PATCH_DIR_NAME):
		if os.path.isfile(PATCH_DIR_NAME + "/" + d) and (d.endswith("json")):
			PATCH_FILES[d] = {}
	if len(PATCH_FILES.keys()) < 1:
		print "Patches Found: 0 <- ERROR, no patches found!"
		sys.exit(2)
	else:
		print "Patches Found: %s <- OK" % len(PATCH_FILES) 
		print ""
		print "Patch Summary"
		print "============="
		keys = PATCH_FILES.keys()
		keys.sort()
		for d in keys:
			try:
				PATCH_FILES[d]["json"] = open(PATCH_DIR_NAME + "/" + d).read()
				PATCH_FILES[d]["data"] = json.loads(PATCH_FILES[d]["json"])
				t = 0
				sm = 0
				tiny = 0
				tot = len(PATCH_FILES[d]["data"]["data"])
				for b in PATCH_FILES[d]["data"]["data"]:
					if len(b["trans_text"]) > 0:
						t += 1
					if "snes-e" in b.keys():
						sm += 1
					if len(b["raw_text"]) < 2:
						tiny += 1
				print "- %4s Strings %4s Translations %4s SNES matches %3s Tiny %4s Missing | %s" % (tot, t, sm, tiny, (tot - t - sm - tiny), d)
			except Exception as e:
				print traceback.format_exc()
				print "- %s <- ERROR, not a valid JSON file" % d
				print e
		print ""
		print "Patch Summary Key"
		print "================="
		print "Strings      : Total number of text strings in the patch file"
		print "Translations : How many strings already have we added a full english translation for?"
		print "SNES Matches : How many strings have matching SNES english text that canbe used as a basis for an english translation?"
		print "Tiny         : How many strings are sub-2 characters (ie not text)?"
		print "Missing      : How many strings remain to be translated?"
else:
	print "Patch Directory: %s <- ERROR, directory not found!" % PATCH_DIR_NAME
	sys.exit(2)

print ""

#################################################
# Use each patch file in turn
#################################################
print "Mapping Untranslated Patches"
print "============================"
FILE = StringIO.StringIO()
keys = PATCH_FILES.keys()
keys.sort()
snes_table = load_snes_table(SNES_SCRIPT)
for f in keys:
	print ""
	print "================="
	print "Mapping %s" % f

	t = 0
	ut = 0
	for patch_segment in PATCH_FILES[f]["data"]["data"]:
		if (len(patch_segment["trans_text"]) != 0) or (len(patch_segment["raw"]) == 0) or ("snes-e" in patch_segment.keys()):
			t += 1
		else:
			ut += 1
	print "Ignoring %s existing translations or SNES matches" % t
	print "Mapping %s untranslated strings"	% ut
	if (os.path.isfile(OUT_DIR_NAME + "/" + f)) and (OVERWRITE == False):
		print "Skipped - an existing process file was found"
	else:
		patch = mapScript(f, PATCH_FILES[f], snes_table)
		write_export(patch, f)
	print "-----------------"
	print ""
