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

Tries to map untranslated strings from patches generated from 'extractAssets.py'
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

IN_DIR = "assets/split"
OUT_DIR = "assets/converted"
SNES_SCRIPT = "CyberKnightSNES.csv"

squashed_pce_strings = {}
squashed_snes_strings = {}

######################################################
############ < Code starts here > ####################
######################################################

def squashPCEPatchSegment(PCE_japanese):
	""" Squash a section of japanese PCE text by removing spaces, control codes etc """

	# Does a pre-squashed string already exist?
	#print("PCE Squashing :",PCE_japanese
	h = hashlib.md5(PCE_japanese.encode('utf-8')).hexdigest()
	if h in squashed_pce_strings.keys():
		t = squashed_pce_strings[h]
		#print("PCE Found     :", t
		return t
	else:
	 	# Remove control bytes
		text = re.sub('<..>','' , PCE_japanese)
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
			#print("PCE Squashed :", text
	return text

def squashSNESPatchSegment(snes_j_text):
	""" Squash a section of japanese SNES text by removing spaces, control codes etc """

	# Does a pre-squashed string already exist?
	#print("SNES Squashing:", snes_j_text
	h = hashlib.md5(snes_j_text).hexdigest()
        if h in squashed_snes_strings.keys():
		t = squashed_snes_strings[h]
		#print("SNES Found    :", t
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
			#print("SNES Squashed :", text
	return text



def selectMatch(patch_segment, possible_matches):
	""" Display a menu of possible matches """
	
	cnt = 0
	print("")
	for d in possible_matches:
		print("%s." % cnt)
		print("    Accuracy   : %.5f" % d["best"])
		
		######################################################
		# Print out the PCE raw text
		try:
			print("    PCE Raw    : %s" % unicode(patch_segment["PCE_japanese"], 'shift-jis').replace('\n', '\\n'))
		except:
			sys.stdout.write("    PCE Raw    : ")
			for c in patch_segment["PCE_japanese"].replace('\n', '\\n'):
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
			print("    SNES Raw   : %s" % d["snes-j"].replace('\n', '\\n'))
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
		print("")
		print("    PCE Squash : %s" % d["pce-squashed"])
		print("    SNES Squash: %s" % d["snes-squashed"])

		######################################################	
		# Print out the SNES translation
		print("")
		print("    SNES Trans : %s" % d["SNES_english"].replace('\n', '\\n'))
		print("")
		sys.stdout.flush()
		cnt += 1
	
	# Allow user to choose translation
	print("Select a choice: ")
	c = raw_input()
	try:
		ci = int(c)
	except:
		print("Skipped SNES translation")
		return False
	if ci in range(0, cnt):
		print("Selected SNES translation %s" % ci)
		patch_segment["SNES_english"] = possible_matches[ci]["SNES_english"]
		patch_segment["snes-j"] = possible_matches[ci]["snes-j"]
		patch_segment["accuracy"] = possible_matches[ci]["best"]
		patch_segment["snes_size"] = len(possible_matches[ci]["SNES_english"])
		patch_segment["snes_patched"] = 1
		return True
	else:
		print("Skipped SNES translation")
		return False

def mapScript(patchfile, patch, snes_table):
	""" Attempt to map to SNES translation """
	t = 0
	ut = 0
	mt = 0
	tiny = 0
	for patch_segment in patch["data"]["strings"]:
		if (len(patch_segment["SNES_english"]) != 0) or (len(patch_segment["bytes"]) == 0):
			t += 1
		else:
			ut += 1
		if len(patch_segment["PCE_japanese"]) < 2:
			tiny += 1
	print("Skipping %s tiny strings" % tiny)
	print("Attempting map of %s untranslated / unmatched strings" % (ut - tiny))
	if VERBOSE:
		print("---")
	for patch_segment in patch["data"]["strings"]:
		if (len(patch_segment["PCE_english"]) == 0) and (len(patch_segment["bytes"]) > 2) and (len(patch_segment["SNES_english"]) == 0):
			matched = False
			snes_text = None
				
			# Test for exact match
			for snes_text in snes_table.keys():
				if (snes_text == patch_segment["PCE_japanese"].encode('utf-8')):
					matched = True
					# Exact matches are autopatched
					patch_segment["SNES_english"] = snes_table[snes_text]
					patch_segment["SNES_accuracy"] = 1.0
					break
					
			if matched:
				if VERBOSE:
					print("%s - Successfully mapped" % patch_segment["start_pos"])
				patch_segment["SNES_english"] = snes_table[snes_text]
				patch_segment["SNES_accuracy"] = 1.0
				mt += 1
			else:	
				
				possible_matches = []
				best_matches = []
				# Attempt fuzzy match
				s1 = squashPCEPatchSegment(patch_segment["PCE_japanese"])
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
						d["SNES_english"] = snes_table[snes_text]
						d["snes-j"] = snes_text
						d["sm"] = sm
						d["ratio"] = r
						possible_matches.append(d)
				# Sort list of possibles
				if len(possible_matches) > 0:
					if VERBOSE:
						print("String Number %s" % (patch_segment["string_number"]))
						sys.stdout.write("%s - " % (patch_segment["start_pos"]))
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
							print("Warning! Best match not high enough to auto select - confirm below:")
							patch_number = selectMatch(patch_segment, best_matches)
							if patch_number:
								mt += 1
						else:
							patch_segment["SNES_english"] = best_matches[0]["SNES_english"]
							patch_segment["SNES_japanese"] = best_matches[0]["snes-j"]
							patch_segment["SNES_accuracy"] = best_matches[0]["best"]
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
						patch_segment["SNES_english"] = best_matches[patch_number]["SNES_english"]
						patch_segment["SNES_japanese"] = best_matches[patch_number]["snes-j"]
						patch_segment["SNES_accuracy"] = best_matches[patch_number]["best"]
						if patch_number:
							mt += 1
					
				# Get highest 3
				# Prompt for user action
	if VERBOSE:
		print("---")
	print("Mapping routine found %s matches" % mt)
	print("Mapping routine left %s untranslated" % (ut - mt - tiny))
	return patch
	
######################################################

def write_export(patch, filename):
	"""
	Writes the document used for translation.
	"""
	
	file_out = open(OUT_DIR + "/" + patch["data"]["bank"] + "." + patch["data"]["asset_index"] + ".dat", "w")
	file_out.write("{\n")
	file_out.write("	\"bank\" : \"%s\",\n" % patch["data"]["bank"])
	file_out.write("	\"asset_index\" : \"%s\",\n" % patch["data"]["asset_index"])
	file_out.write("	\"asset_rom_pointer_value\" : \"%s\",\n" % patch["data"]["asset_rom_pointer_value"])
	file_out.write("	\"asset_rom_pointer_address\" : \"%s\",\n" % patch["data"]["asset_rom_pointer_address"])
	file_out.write("	\"asset_rom_pointer_address_limit\" : \"%s\",\n" % patch["data"]["asset_rom_pointer_address_limit"])
	file_out.write("	\"asset_size\" : %s,\n" % (int(patch["data"]["asset_rom_pointer_address_limit"], 16) - int(patch["data"]["asset_rom_pointer_address"], 16)))
	file_out.write("	\"strings\" : [\n")
	for byte_sequence in patch["data"]["strings"]:
		file_out.write("		{\n")
		file_out.write("			\"string_number\" : %s,\n" % byte_sequence["string_number"])
		file_out.write("			\"string_size\" : %s,\n" % len(byte_sequence["bytes"]))
		file_out.write("			\"start_pos\" : \"%s\",\n" % byte_sequence["start_pos"])
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
		for c in byte_sequence["PCE_japanese"]:
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
				file_out.write(c)
			except:
				try:
					file_out.write(c.encode('utf-8'))
				except:
					file_out.write(c.encode('shift-jis'))
			#file_out.write(c)
		file_out.write("\",\n")
		
		# Space for SNES translation
		file_out.write("			\"SNES_japanese\" : \"")
		for c in byte_sequence["SNES_japanese"]:
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
				file_out.write(c)
			except:
				try:
					file_out.write(c.encode('utf-8'))
				except:
					file_out.write(c.encode('shift-jis'))
			#file_out.write(c)
		file_out.write("\",\n")
		file_out.write("			\"SNES_english\" : \"")
		for c in byte_sequence["SNES_english"]:
			if c == "\r\n":
				c == "\\n"
			if c == "\n":
				c = "\\n"
			file_out.write(c)
		file_out.write("\",\n")
		file_out.write("			\"SNES_accuracy\" : %s,\n" % byte_sequence["SNES_accuracy"])
		
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
	
######################################################
########## < Run-time code start here > ##############
######################################################

try:
	opts, args = getopt.getopt(sys.argv[1:], "hvSs:d:o:p:f")
except getopt.GetoptError as err:
	print(err)
	sys.exit(2)

print("")
print("mapAssets.py - Map untranslated patches from the PC-Engine CyberKnight to the SNES script")
print("----------------")
print("")

SHOW_SUMMARY = False
for o, a in opts:
	if o == "-h":
		print("A tool which can map sections of untranslated patch files (output generated by splitAssets.py)")
		print("to translated sections from the English SNES translation, writing those translated strings back")
		print("into the PC-Engine patch files for use in injectScript.py later.")
		print("If translated sections are found, then they are used instead of the SNES translation.")
		print("")
		print("Options:")
		print("-h	Show help text")
		print("-v	Enable verbose output")
		print("-S	Show summary of patch files only")
		print("-s	SNES script file name (e.g. 'CyberKnightSNES.csv')")
		print("-i	Directory containing split asset files as generated by splitAssets.py (e.g. 'assets/split')")
		print("-o	Directory to write the modified translation (e.g. 'assets/converted')")
		print("-f	Overwrite existing files (otherwise dry-run)")
		print("-p	Pass number (1 == strictest matching, 3 == least strict matching)")
		print("")
		print("Example:")
		print("mapScriptAssets.py -s 'CyberKnightSNES.csv' -i 'assets/split' -o 'assets/converted' -p 1")
		print("")
		sys.exit(0)
		
	if o == "-v":
		VERBOSE = True
		
	if o == "-i":
		IN_DIR = a

	if o == "-o":
		OUT_DIR = a

	if o == "-s":
		SNES_SCRIPT = a
		
	if o == "-p":
		PASS_NUMBER = a
		
	if o == "-f":
		OVERWRITE = True
		
	if o == "-S":
		SHOW_SUMMARY = True
		
# Load match levels depending on pass number
FUZZY_LIMIT = FUZZY_LEVELS[str(PASS_NUMBER)]["FUZZY_LIMIT"]
FUZZY_BEST_LIMIT = FUZZY_LEVELS[str(PASS_NUMBER)]["FUZZY_BEST_LIMIT"]
		
#############################################
# Print configuration
#############################################

print("Configuration")
print("=============")
print("Verbose: %s" % VERBOSE)
print("Over-write: %s" % OVERWRITE)
print("Pass Type: %s" % PASS_NUMBER)
	
if os.path.isfile(SNES_SCRIPT):
	print("SNES Script File: %s <- OK" % SNES_SCRIPT)
else:
	print("SNES Script File: %s <- ERROR, SNES script not found!" % SNES_SCRIPT)
	sys.exit(2)

if os.path.isdir(IN_DIR):
	print("Input Directory: %s <- OK" % IN_DIR)
else:
	print("Input Directory: %s <- ERROR, directory not found!" % IN_DIR)
	sys.exit(2)

if os.path.isdir(OUT_DIR):
	print("Output Directory: %s <- OK" % OUT_DIR)
else:
	print("Output Directory: %s <- ERROR, directory not found!" % OUT_DIR)
	sys.exit(2)
	
if os.path.isdir(IN_DIR):
	for d in os.listdir(IN_DIR):
		if os.path.isfile(IN_DIR + "/" + d) and (d.endswith("dat")):
			PATCH_FILES[d] = {}
	if len(PATCH_FILES.keys()) < 1:
		print("Patches Found: 0 <- ERROR, no patches found!")
		sys.exit(2)
	else:
		
		
		print("Patches Found: %s <- OK" % len(PATCH_FILES)) 
		print("")
		print("Patch Summary")
		print("=============")
		keys = PATCH_FILES.keys()
		keys.sort()
		total_tot = 0
		total_t = 0
		total_sm = 0
		total_tiny = 0
		print("|--------|------------|------------|----------|----------|---------|--------|---------------")
		print("| Strings|Translations|SNES matches|SNES best |SNES worst|SNES avg.| Tiny   | Patch Name")
		print("|--------|------------|------------|----------|----------|---------|--------|---------------")
		total_snes_avg = 0
		total_snes_best = 0
		total_snes_worst = 1
		for d in keys:
			try:
				PATCH_FILES[d]["json"] = open(IN_DIR + "/" + d).read()
				PATCH_FILES[d]["data"] = json.loads(PATCH_FILES[d]["json"])
				t = 0
				sm = 0
				tiny = 0
				tot = len(PATCH_FILES[d]["data"]["strings"])
				total_tot += tot
				snes_best = 0
				snes_worst = 1
				snes_avg = 0
				
				for b in PATCH_FILES[d]["data"]["strings"]:
					if len(b["PCE_english"]) > 0:
						t += 1
						total_t += 1
					if len(b["SNES_english"]) > 0:
						if b["SNES_accuracy"] >= snes_best:
							snes_best = b["SNES_accuracy"]
						if b["SNES_accuracy"] <= snes_worst:
							snes_worst = b["SNES_accuracy"]
						sm += 1
						total_sm += 1
						#snes_avg = snes_avg / sm
						snes_avg = snes_avg + b["SNES_accuracy"]
					if len(b["PCE_japanese"]) < 2:
						tiny += 1
						total_tiny += 1
					if snes_worst < total_snes_worst:
						total_snes_worst = snes_worst
					if snes_best > total_snes_best:
						total_snes_best = snes_best
				if sm:
					snes_avg = snes_avg / sm
				if total_sm > 0:
					total_snes_avg += snes_avg
				print("| %4s   |%4s /%4s  | %4s /%4s |      %3.0f |      %3.0f |     %3.0f |   %3s  | %s" % (tot, t, tot, sm, tot, snes_best * 100, snes_worst * 100, snes_avg * 100, tiny, d))
			except Exception as e:
				print traceback.format_exc()
				print("| %s <- ERROR, not a valid JSON file" % d)
				print e
		print("|--------|------------|------------|----------|----------|---------|--------|---------------")
		print("| Strings|Translations|SNES matches|SNES best |SNES worst|SNES avg.| Tiny   | Patch Name")
		print("|--------|------------|------------|----------|----------|---------|--------|---------------")
		print("| %4s   |%4s / %4s |%4s / %3s |      %3.0f |      %3.0f |     %3.0f |   %3s  |" % (total_tot, total_t, total_tot, total_sm, total_tot, total_snes_best * 100.0, total_snes_worst * 100.0, total_snes_avg, total_tiny))
			
		print("")
		print("Patch Summary Key")
		print("=================")
		print("Strings      : Total number of text strings in the patch file")
		print("Translations : How many strings already have we added a full english translation for?")
		print("SNES Matches : How many strings have matching SNES english text that canbe used as a basis for an english translation?")
		print("SNES Best    : The most accurate SNES match in this patch file.")
		print("SNES Worst   : The least accurate SNES match in this patch file.")
		print("SNES average : The average accuracy of SNES matches in this patch file.")
		print("Tiny         : How many strings are sub-2 characters (ie not text)?")
		
		if SHOW_SUMMARY:
			sys.exit(0)
else:
	print("Patch Directory: %s <- ERROR, directory not found!" % IN_DIR)
	sys.exit(2)

print("")

#################################################
# Use each patch file in turn
#################################################
print("Mapping Untranslated Patches")
print("============================")
FILE = StringIO.StringIO()
keys = PATCH_FILES.keys()
keys.sort()
snes_table = load_snes_table(SNES_SCRIPT)
for f in keys:
	print("")
	print("=================")
	print("Mapping %s" % f)

	t = 0
	ut = 0
	tiny = 0
	tot = len(PATCH_FILES[f]["data"]["strings"])
	for patch_segment in PATCH_FILES[f]["data"]["strings"]:
		patch_segment["bank"] = PATCH_FILES[f]["data"]["bank"]
		if (len(patch_segment["PCE_english"]) != 0) or (len(patch_segment["bytes"]) == 0) or (len(patch_segment["SNES_english"]) != 0):
			t += 1
		else:
			ut += 1
		if len(patch_segment["PCE_japanese"]) < 2:
			tiny += 1
	print("Total of %s strings" % tot)
	print("Ignoring %s existing translations or SNES matches" % t)
	if (os.path.isfile(OUT_DIR + "/" + f)) and (OVERWRITE == False):
		print("Skipped - an existing process file was found")
	else:
		patch = mapScript(f, PATCH_FILES[f], snes_table)
		write_export(patch, f)
	print("-----------------")
	print("")
