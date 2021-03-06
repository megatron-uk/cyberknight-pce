#!/usr/bin/env python

#########################################################
#
# Configuration data for extractScript and injectScript
#
#########################################################
import os

try:
	REVISION = os.popen('git rev-list HEAD --count').readlines()[0]
except:
	REVISION = "Undef!"

# Defaults for input, translation and output file name
# Required for extractScript
ROM_NAME = "Cyber Knight (J).pce"
TABLE_NAME = "CyberKnightTranslation.csv"
TABLE_NAME_DOUBLE = "CyberKnightKanjiTranslation.csv"
OUT_NAME = "Script.json"
# Additional requirements for injectScript/mapScript
OUT_EXPANDED_NAME = "Cyber Knight (J) Expanded.pce"
OUT_ROM_NAME = "Cyber Knight (E).pce"
SNES_SCRIPT = "CyberKnightSNES.csv"
OUT_DIR_NAME = "./patches-processed/"
PATCH_DIR_NAME = "./patches/"
PATCH_EXTENSION = ".json"

# Rom checksum of the commonly available "Cyber Knight (J).pce" file
ROM_CHECKSUM = "dad257d4984635f70580b10f1ae1b75c"

# Size of the ROM in original state
ROM_SIZE = 524288
ROM_BANKS = 64
BANK_SIZE = 8192
# PC-Engine games cannot be any bigger than this, other we
# get in to trouble with needing hardware like the Streetfighter 2 
# mapper, Arcade Card and other doodads.
ROM_MAX_SIZE = 1048576

# Default pass level and fuzzy match trigger level
PASS_NUMBER = 1
FUZZY_LEVELS = {
	"1" : { 'FUZZY_LIMIT' : 0.70, 'FUZZY_BEST_LIMIT' : 0.79 },
	"2" : { 'FUZZY_LIMIT' : 0.69, 'FUZZY_BEST_LIMIT' : 0.75 },
	"3" : { 'FUZZY_LIMIT' : 0.60, 'FUZZY_BEST_LIMIT' : 0.65 },
	"4" : { 'FUZZY_LIMIT' : 0.55, 'FUZZY_BEST_LIMIT' : 0.60 },
	"5" : { 'FUZZY_LIMIT' : 0.50, 'FUZZY_BEST_LIMIT' : 0.55 },
	"6" : { 'FUZZY_LIMIT' : 0.45, 'FUZZY_BEST_LIMIT' : 0.50 },
	"7" : { 'FUZZY_LIMIT' : 0.40, 'FUZZY_BEST_LIMIT' : 0.45 },
	"8" : { 'FUZZY_LIMIT' : 0.35, 'FUZZY_BEST_LIMIT' : 0.40 }
}
# The limit at which best matches are auto selected
# At lower than this level, the user is prompted
FUZZY_AUTO_SELECT_LIMIT = 0.8

# Whether to overwrite existing files
OVERWRITE = False

# Additional, verbose output about the process
VERBOSE = False

# The byte which determines which translation table to use
SWITCH_MODE = '5C'

# The byte that tells us a double height char is next
KANJI_CODE = '1D'

# All possible dakuten bytes
DAKUTEN_ALL = ["DE", "DF"]

# The bytes which are mapped to composite chars
DAKUTEN = ["DE", "DF"]

# What "81" should be converted to
DAKUTEN_REPLACE = "DE"

# Start byte of a PC/NPC name string.. if a byte sequence cotnains these, then
# we look them up as a composite, rather than an individual btye.
PC_NAME = "10"
PC_NAMES = [
	"1E", "1F", 
	"28", "29", "2a", "2b", "2c", "2d", 
	"30", "34", "35", "36", "3b", "3c", "3d", "3e", "3f",
	"40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "4a", "4b", "4c", "4d", "4e", "4f",
	"50", "51", 
	"ff"
]

DIALOGUE_BOX = "1A"
DIALOGUE_CODES = [
	"1A", "1B", "1C", "1D", "1E", "1F", 
	"2A", "2B", "2C", "2D", "2E", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
	"3A",
	"48", "49", "4A", "4B", "4C", "4D", "4E", "4F", 
	"50", "51", "52", "53", "54", "55", "56", "57",
	"70", "71", "72", "73", "74"
]

####################################################################
#
# NOTE !!!!
#
# This following section was used by the original extraction/patching tools found in ./tools/,
# none of these variables are used by the new asset extractor, mapper or injector code.

# Text extraction method
# Method 1 = 2 control bytes + string + 0x00 as terminator, defaults to switch mode = disabled
# Method 2 = text wrapped in 0x04 and 0x3c bytes, also defaults to switch mode = enabled
# Method 3 = no control bytes, + 0x00 as terminator, defaults to switch mode = disabled
METHOD_1 = 1
METHOD_2 = 2
METHOD_3 = 3

METHOD_1_OFFSET = 2
METHOD_2_OFFSET = 1
METHOD_3_OFFSET = 0
 
METHOD_1_TRAILING_BYTES = 0
METHOD_2_TRAILING_BYTES = 1
METHOD_3_TRAILING_BYTES = 0

# Insertion methods
# SIMPLE = exact string length insertion, padding with no-op (0x5c)
# bytes if the translated string is shorter.
# CONTIGUOUS = Treat the entire range (start/end) as one long string,
# as long as the last string does not exceed the end address, all strings
# between the start and end can be whatever legth desired (useful if the end
# address contains many empty null bytes so that a number of string can be
# extended if desired).
METHOD_SIMPLE = 1
METHOD_CONTIGUOUS = 2

# Define the areas of the ROM file we are wanting to extract
# text from.
# A list of tuples, each tuple identifying the type of dialogue
# extract that should be used, and the start/end region of the ROM
# in hexadecimal notation.
# Note: a headerless rom file is assumed.
#
# Syntax: (A, B, C, D, E)
#	A: extraction method (METHOD_1, METHOD_2, METHOD_3)
#	B: start address
#	C: end address
#	D: insertion type (SIMPLE, CONTIGUOUS)
#	E: textual description of what this block of text represents, if known
#	F: string end byte delimiter

BYTES = [

	# just use this one for looking at all strings - not a good way of translating
	# that are some sections use different delimiters, handy to scan through
	# looking for possible dialogue though...
	#
	#(METHOD_3, 0x00000, 0x40000, METHOD_SIMPLE, "Full game dump", "\x00"),
	
	# interesting sections of the rom...	
	#(METHOD_3, 0x1400c, 0x1b8cd, METHOD_SIMPLE, "Main game dialogue", "\x00"),
	#(METHOD_3, 0x1b8d6, 0x1bfdf, METHOD_CONTIGUOUS, "Scrolling intro text after cinematics.", "\x00"),
	#(METHOD_3, 0x1c01c, 0x1c90d, METHOD_SIMPLE, "Main menu text and configuration options.", "\x00"),
	#(METHOD_3, 0x1c952, 0x1ca2b, METHOD_SIMPLE, "Additional game menus.", "\x00"),	
	#(METHOD_3, 0x1cbad, 0x1ccac, METHOD_SIMPLE, "NPC character names.", "\x00"),
	#(METHOD_3, 0x1ccbf, 0x1d59f, METHOD_SIMPLE, "Names - possible battle text", "\x00"),
	#(METHOD_3, 0x1d59f, 0x1dc7a, METHOD_SIMPLE, "Weapon list", "\x00"),
	#(METHOD_3, 0x1dc87, 0x1defb, METHOD_SIMPLE, "Shipboard menus", "\x02"),
	#(METHOD_3, 0x1e71c, 0x1ea86, METHOD_SIMPLE, "Professor lab screen", "\x00"),
	#(METHOD_3, 0x1ea88, 0x1ec00, METHOD_SIMPLE, "Mecha overview screen", "\x20"),	
	#(METHOD_3, 0x1ec08, 0x1edfa, METHOD_SIMPLE, "CLosing credits", "\x20"),
	#(METHOD_3, 0x1ee0f, 0x1f0df, METHOD_SIMPLE, "Staff credits", "\x00"),
	#(METHOD_3, 0x1f0f4, 0x1fb3f, METHOD_CONTIGUOUS, "Unknown dialogue", "\x00"),
	#(METHOD_3, 0x28086, 0x29efe, METHOD_SIMPLE, "MICA, PLAYER, Planet scan text", "\x00"),
	#(METHOD_2, 0x29efe, 0x2a1af, METHOD_SIMPLE, "Introductory Cinematics"),	
	#(METHOD_3, 0x2a74c, 0x2a930, METHOD_SIMPLE, "Short scene after scrolling intro text.", "\x1c"),
	
	# Some text, but unknown start or end points
	#(METHOD_3, 0x2a934, ???????, METHOD_SIMPLE, "More text with MICA and PLAYER?", "\x00"),
	
]
