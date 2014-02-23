#!/usr/bin/env python

#########################################################
#
# Configuration data for extractScript and injectScript
#
#########################################################

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

METHOD_1_TRAILING_BYTES = 1
METHOD_2_TRAILING_BYTES = 2
METHOD_3_TRAILING_BYTES = 1

# Define the areas of the ROM file we are wanting to extract
# text from.
# A list of tuples, each tuple identifying the type of dialogue
# extract that should be used, and the start/end region of the ROM
# in hexadecimal notation.
# Note: a headerless rom file is assumed.
#
# Syntax: (X, Y, Z, A)
#	X: extraction method (METHOD_1, METHOD_2, METHOD_3)
#	Y: start address
#	Z: end address
#	A: textual description of what this block of text represents, if known

BYTES = [
	#(METHOD_3, 0x1c87e, 0x1c90d, "Main menu text and configuration options."),
	#(METHOD_3, 0x28086, 0x28949, "Unknown."),
	#(METHOD_2, 0x1b8d6, 0x1bca6, "Scrolling intro text after cinematics."),
	#(METHOD_1, 0x1defc, 0x1e0a5, "Possible ship dialogue for first world."),
	(METHOD_2, 0x29eff, 0x2a1ad, "Introductory cinematics."),
]
