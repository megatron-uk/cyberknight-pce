#!/usr/bin/env python

#########################################################
#
# Configuration data for extractScript and injectScript
#
#########################################################

# Defaults for input, translation and output file name
# Required for extractScript
ROM_NAME = "Cyber Knight (J).pce"
TABLE_NAME = "CyberKnightTranslation.csv"
TABLE_NAME_DOUBLE = "CyberKnightKanjiTranslation.csv"
OUT_NAME = "Script.json"
# Additional requirements for injectScript
OUT_ROM_NAME = "Cyber Knight (E).pce"
PATCH_DIR_NAME = "./patches/"
PATCH_EXTENSION = ".json"

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

# Start byte of a PC/NPC name string
PC_NAME = "10"
PC_NAMES = ["28", "29", "2a", "2b", "2c", "30", "34"]


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

<<<<<<< HEAD
	# just use this one for looking at all strings
	#(METHOD_3, 0x00000, 0x40000, METHOD_SIMPLE, "Full game dump", "\x00"),
	
	# interesting sections of the rom...
	#(METHOD_3, 0x1b8d6, 0x1bfdf, METHOD_CONTIGUOUS, "Scrolling intro text after cinematics.", "\x00"),
	#(METHOD_3, 0x1c01c, 0x1c90d, METHOD_SIMPLE, "Main menu text and configuration options.", "\x00"),
	#(METHOD_3, 0x1c952, 0x1ca2b, METHOD_SIMPLE, "Additional game menus.", "\x00"),
	#(METHOD_3, 0x1cbad, 0x1ccac, METHOD_SIMPLE, "NPC character names.", "\x00"),
	#(METHOD_3, 0x1d59f, 0x1dc7a, METHOD_SIMPLE, "Weapon list", "\x00"),
	#(METHOD_3, 0x1dc87, 0x1dee3, METHOD_SIMPLE, "Shipboard menus", "\x02"),
	#(METHOD_3, 0x1e71c, 0x1ea86, METHOD_SIMPLE, "Professor lab screen", "\x00"),
	#(METHOD_3, 0x1ea88, 0x1ec00, METHOD_SIMPLE, "Mecha overview screen", "\x20"),	
	#(METHOD_3, 0x1ec08, 0x1edfa, METHOD_SIMPLE, "CLosing credits", "\x20"),
	#(METHOD_3, 0x1ee0f, 0x1f0df, METHOD_SIMPLE, "Staff credits", "\x00"),
	(METHOD_3, 0x1f0f4, 0x1ffe0, METHOD_CONTIGUOUS, "???", "\x00"),

	#(METHOD_3, 0x28086, 0x28949, METHOD_SIMPLE, "Unknown.", "\x00"),
	#(METHOD_2, 0x29efe, 0x2a1af, METHOD_SIMPLE, "Introductory Cinematics"),	
=======
	#(METHOD_3, 0x00000, 0x40000, METHOD_SIMPLE, "Everything!", "\x00"),

	#(METHOD_2, 0x29efe, 0x2a1af, METHOD_SIMPLE, "Introductory Cinematics"),
	
	#(METHOD_3, 0x1c040, 0x1c87d, METHOD_SIMPLE, "Main menu, Player name entry screen, load game screen, in-game stats screen.", "\x00"),
	#(METHOD_3, 0x1cbad, 0x1ccac, METHOD_SIMPLE, "NPC character names.", "\x00"),
	#(METHOD_3, 0x1b8d6, 0x1bca6, METHOD_CONTIGUOUS, "Scrolling intro text after cinematics.", "\x00"),
	#(METHOD_2, 0x29eff, 0x2a1ad, METHOD_SIMPLE, "Introductory cinematics."),
>>>>>>> 3471bc066f194dcb05f1a97028bf27dbdb7fce37
	#(METHOD_3, 0x2a74c, 0x2a930, METHOD_SIMPLE, "Short scene after scrolling intro text.", "\x1c"),
	
]
