#!/usr/bin/env python
###################################
#
# This file contains a list of all
# the defined asset structures
# within the Cyber Knight rom file
#
# This data is used within the
# extractAsset.py script to retrieve
# these data chunks from the ROM,
# and also in injectAsset.py to re-
# -insert them back in to a (possibly)
# expanded ROM file.
#
###################################

#########################################################################
# Asset Loading Tables
# --------------------
# The location of the table in the ROM file
# that specifies which asset bank to load
# e.g. load bank 0x0A, 0x0E, 0x14, then 0x0A again.
ASSET_LOAD_TABLE = 0x02939
# The number of entries in the asset load table
ASSET_LOAD_TABLE_SIZE = 33
# The location of the table in the ROM file
# that specifies which asset index pointer to
# load for which asset bank.
# e.g. load asset index 0x0D for asset bank 0x0C.
ASSET_OFFSET_TABLE = 0x0295A
# The number of entries in the asset offset table
ASSET_OFFSET_TABLE_SIZE = 33

##########################################################################
# Definition of all asset banks and asset index entries
# -----------------------------------------------------
# You can access the rom file address of an asset index item as follows; to access the asset chunk
# numbered as asset index 0x01, from bank 0x0A:
# data_location = ASSETS["asset_banks"][0x0A]["assets"][0x01][""asset_rom_pointer_address""]
# 
# To get a list of all the asset numbers from bank 0x14:
# asset_numbers = ASSETS["asset_banks"][0x14]["assets"].keys()

ASSETS = {
	# Assets are stored in asset banks
	"asset_banks" : {
		0x0A : {
			# Asset banks are accessible by bank ID
			"asset_bank" : 0x0A,
			# An asset bank has a physical start location in the ROM file
			"asset_bank_rom_start_address" : 0x14000,
			# An asset bank has a physical end location in the ROM file
			"asset_bank_rom_end_address" : 0x17FFF,
			# Each bank has a number of asset chunks, accessed by asset index number
			"assets" :{
				0x01 : {
					"asset_index" : 0x01,
					# An asset number points to an position in PCE memory of a particular asset chunk, be it text or graphics.
					"asset_rom_pointer_value" : 0x400B,
					# The PCE memory address is also linked to a physical location in the ROM file.
					"asset_rom_pointer_address" : 0x1400B,
					# An asset has a type
					"asset_type" : "text"
				},
				0x03 : {
					"asset_index" : 0x03,
					"asset_rom_pointer_value" : 0x54FD,
					"asset_rom_pointer_address" : 0x154FD,
					"asset_type" : "text"
				},
				0x05 : {
					"asset_index" : 0x05,
					"asset_rom_pointer_value" : 0x6A6F,
					"asset_rom_pointer_address" : 0x16A6F,
					"asset_type" : "text"
				},
				0x07 : {
					"asset_index" : 0x07,
					"asset_rom_pointer_value" : 0x6C29,
					"asset_rom_pointer_address" : 0x16C29,
					"asset_type" : "text"
				},
				0x09 : {
					"asset_index" : 0x09,
					"asset_rom_pointer_value" : 0x75C1,
					"asset_rom_pointer_address" : 0x175C1,
					"asset_type" : "text"
				},
			}
		},
		0x0C : {
			"asset_bank" : 0x0C,
			"asset_bank_rom_start_address" : 0x18000,
			"asset_bank_rom_end_address" : 0x1BFFF,
			"assets" : {
				0x01 : {
					"asset_index" : 0x01,
					"asset_rom_pointer_value" : 0x4019,
					"asset_rom_pointer_address" : 0x18019,
					"asset_type" : "text"
				},
				0x03 : {
					"asset_index" : 0x03,
					"asset_rom_pointer_value" : 0x4462,
					"asset_rom_pointer_address" : 0x18462,
					"asset_type" : "text"
				},
				0x05 : {
					"asset_index" : 0x05,
					"asset_rom_pointer_value" : 0x4C61,
					"asset_rom_pointer_address" : 0x18C61,
					"asset_type" : "text"
				},
				0x07 : {
					"asset_index" : 0x07,
					"asset_rom_pointer_value" : 0x5147,
					"asset_rom_pointer_address" : 0x19147,
					"asset_type" : "text"
				},
				0x09 : {
					"asset_index" : 0x09,
					"asset_rom_pointer_value" : 0x5927,
					"asset_rom_pointer_address" : 0x19927,
					"asset_type" : "text"
				},
				0x0B : {
					"asset_index" : 0x0B,
					"asset_rom_pointer_value" : 0x5C16,
					"asset_rom_pointer_address" : 0x19C16,
					"asset_type" : "text"
				},
				0x0D : {
					"asset_index" : 0x0D,
					"asset_rom_pointer_value" : 0x634B,
					"asset_rom_pointer_address" : 0x1A34B,
					"asset_type" : "text"
				},
				0x0F : {
					"asset_index" : 0x0F,
					"asset_rom_pointer_value" : 0x6E17,
					"asset_rom_pointer_address" : 0x1AE17,
					"asset_type" : "text"
				},
				0x11 : {
					"asset_index" : 0x11,
					"asset_rom_pointer_value" : 0x6EA2,
					"asset_rom_pointer_address" : 0x1AEA2,
					"asset_type" : "text"
				},
				0x13 : {
					"asset_index" : 0x13,
					"asset_rom_pointer_value" : 0x71D5,
					"asset_rom_pointer_address" : 0x1B1D5,
					"asset_type" : "text"
				},
				0x15 : {
					"asset_index" : 0x15,
					"asset_rom_pointer_value" : 0x75DB,
					"asset_rom_pointer_address" : 0x1B5D8,
					"asset_type" : "text"
				},
				0x17 : {
					"asset_index" : 0x17,
					"asset_rom_pointer_value" : 0x78CE,
					"asset_rom_pointer_address" : 0x1B8CE,
					"asset_type" : "text",
					"note" : "Scrolling intro text",
				},
			},
		},
		0x0E : {
			"asset_bank" : 0x0E,
			"asset_bank_rom_start_address" : 0x1C000,
			"asset_bank_rom_end_address" : 0x1FFFF,
			"assets" : {
				0x01 : {
					"asset_index" : 0x01,
					"asset_rom_pointer_value" : 0x4011,
					"asset_rom_pointer_address" : 0x1C011,
					"asset_type" : "text"
				},
				0x03 : {
					"asset_index" : 0x03,
					"asset_rom_pointer_value" : 0x4B4C,
					"asset_rom_pointer_address" : 0x1CB4C,
					"asset_type" : "text"
				},
				0x05 : {
					"asset_index" : 0x05,
					"asset_rom_pointer_value" : 0x4EED,
					"asset_rom_pointer_address" : 0x1CEED,
					"asset_type" : "text"
				},
				0x07 : {
					"asset_index" : 0x07,
					"asset_rom_pointer_value" : 0x5373,
					"asset_rom_pointer_address" : 0x1D373,
					"asset_type" : "text"
				},
				0x09 : {
					"asset_index" : 0x09,
					"asset_rom_pointer_value" : 0x55B2,
					"asset_rom_pointer_address" : 0x1D5B2,
					"asset_type" : "text"
				},
				0x0B : {
					"asset_index" : 0x0B,
					"asset_rom_pointer_value" : 0x5C86,
					"asset_rom_pointer_address" : 0x1DC86,
					"asset_type" : "text"
				},
				0x0D : {
					"asset_index" : 0x0D,
					"asset_rom_pointer_value" : 0x6BFF,
					"asset_rom_pointer_address" : 0x1EBFF,
					"asset_type" : "text"
				},
				0x0F : {
					"asset_index" : 0x0F,
					"asset_rom_pointer_value" : 0x70EC,
					"asset_rom_pointer_address" : 0x1F0EC,
					"asset_type" : "text"
				},
			},
		},
		0x14 : {
			"asset_bank" : 0x14,
			"asset_bank_rom_start_address" : 0x28000,
			"asset_bank_rom_end_address" : 0x2BFFF,
			"assets" : {
				0x01 : {
					"asset_index" : 0x01,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x03 : {
					"asset_index" : 0x03,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x05 : {
					"asset_index" : 0x05,
					"asset_rom_pointer_value" : 0x6DA4,
					"asset_rom_pointer_address" : 0x2ADA4,
					"asset_type" : ""
				},
				0x07 : {
					"asset_index" : 0x07,
					"asset_rom_pointer_value" : 0x6E36,
					"asset_rom_pointer_address" : 0x2AE36,
					"asset_type" : ""
				},
				0x09 : {
					"asset_index" : 0x09,
					"asset_rom_pointer_value" : 0x6E65,
					"asset_rom_pointer_address" : 0x2AE65,
					"asset_type" : ""
				},
				0x0B : {
					"asset_index" : 0x0B,
					"asset_rom_pointer_value" : 0x6EB7,
					"asset_rom_pointer_address" : 0x2AEB7,
					"asset_type" : ""
				},
				0x0D : {
					"asset_index" : 0x0D,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x0F : {
					"asset_index" : 0x0F,
					"asset_rom_pointer_value" : 0x6F0E,
					"asset_rom_pointer_address" : 0x2AF0E,
					"asset_type" : ""
				},
				0x11 : {
					"asset_index" : 0x11,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x13 : {
					"asset_index" : 0x13,
					"asset_rom_pointer_value" : 0x6F3D,
					"asset_rom_pointer_address" : 0x2AF3D,
					"asset_type" : ""
				},
				0x15 : {
					"asset_index" : 0x15,
					"asset_rom_pointer_value" : 0x705E,
					"asset_rom_pointer_address" : 0x2B05E,
					"asset_type" : ""
				},
				0x17 : {
					"asset_index" : 0x17,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x19 : {
					"asset_index" : 0x19,
					"asset_rom_pointer_value" : 0x7084,
					"asset_rom_pointer_address" : 0x2B084,
					"asset_type" : ""
				},
				0x1B : {
					"asset_index" : 0x1B,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x1D : {
					"asset_index" : 0x1D,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x1F : {
					"asset_index" : 0x1F,
					"asset_rom_pointer_value" : 0x7145,
					"asset_rom_pointer_address" : 0x2B145,
					"asset_type" : ""
				},
				0x21 : {
					"asset_index" : 0x21,
					"asset_rom_pointer_value" : 0x7171,
					"asset_rom_pointer_address" : 0x2B171,
					"asset_type" : ""
				},
				0x23 : {
					"asset_index" : 0x23,
					"asset_rom_pointer_value" : 0x7202,
					"asset_rom_pointer_address" : 0x2B202,
					"asset_type" : ""
				},
				0x25 : {
					"asset_index" : 0x25,
					"asset_rom_pointer_value" : 0x7237,
					"asset_rom_pointer_address" : 0x2B237,
					"asset_type" : ""
				},
				0x27 : {
					"asset_index" : 0x27,
					"asset_rom_pointer_value" : 0x72B2,
					"asset_rom_pointer_address" : 0x2B2B2,
					"asset_type" : ""
				},
				0x29 : {
					"asset_index" : 0x29,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x2B : {
					"asset_index" : 0x2B,
					"asset_rom_pointer_value" : 0x730E,
					"asset_rom_pointer_address" : 0x2B30E,
					"asset_type" : ""
				},
				0x2D : {
					"asset_index" : 0x2D,
					"asset_rom_pointer_value" : 0x73DF,
					"asset_rom_pointer_address" : 0x2B3DF,
					"asset_type" : ""
				},
				0x2F : {
					"asset_index" : 0x2F,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x31 : {
					"asset_index" : 0x31,
					"asset_rom_pointer_value" : 0x7420,
					"asset_rom_pointer_address" : 0x2B420,
					"asset_type" : ""
				},
				0x33 : {
					"asset_index" : 0x33,
					"asset_rom_pointer_value" : 0x7481,
					"asset_rom_pointer_address" : 0x2B481,
					"asset_type" : ""
				},
				0x35 : {
					"asset_index" : 0x35,
					"asset_rom_pointer_value" : 0x74AA,
					"asset_rom_pointer_address" : 0x2B4AA,
					"asset_type" : ""
				},
				0x37 : {
					"asset_index" : 0x37,
					"asset_rom_pointer_value" : 0x74BD,
					"asset_rom_pointer_address" : 0x2B4BD,
					"asset_type" : ""
				},
				0x39 : {
					"asset_index" : 0x39,
					"asset_rom_pointer_value" : 0x74D4,
					"asset_rom_pointer_address" : 0x2B4D4,
					"asset_type" : ""
				},
				0x3B : {
					"asset_index" : 0x3B,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x3D : {
					"asset_index" : 0x3D,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x3F : {
					"asset_index" : 0x3F,
					"asset_rom_pointer_value" : 0x7542,
					"asset_rom_pointer_address" : 0x2B542,
					"asset_type" : ""
				},
				0x41 : {
					"asset_index" : 0x41,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x43 : {
					"asset_index" : 0x43,
					"asset_rom_pointer_value" : 0x7574,
					"asset_rom_pointer_address" : 0x2B574,
					"asset_type" : ""
				},
				0x45 : {
					"asset_index" : 0x45,
					"asset_rom_pointer_value" : 0x75B4,
					"asset_rom_pointer_address" : 0x2B5B4,
					"asset_type" : ""
				},
				0x47 : {
					"asset_index" : 0x47,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x49 : {
					"asset_index" : 0x49,
					"asset_rom_pointer_value" : 0x75F7,
					"asset_rom_pointer_address" : 0x2B5F7,
					"asset_type" : ""
				},
				0x4B : {
					"asset_index" : 0x4B,
					"asset_rom_pointer_value" : 0x7649,
					"asset_rom_pointer_address" : 0x2B649,
					"asset_type" : ""
				},
				0x4D : {
					"asset_index" : 0x4D,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x4F : {
					"asset_index" : 0x4F,
					"asset_rom_pointer_value" : 0x766F,
					"asset_rom_pointer_address" : 0x2B66F,
					"asset_type" : ""
				},
				0x51 : {
					"asset_index" : 0x51,
					"asset_rom_pointer_value" : 0x76F4,
					"asset_rom_pointer_address" : 0x2B6F4,
					"asset_type" : ""
				},
				0x53 : {
					"asset_index" : 0x53,
					"asset_rom_pointer_value" : 0x77B4,
					"asset_rom_pointer_address" : 0x2B7B4,
					"asset_type" : ""
				},
				0x55 : {
					"asset_index" : 0x55,
					"asset_rom_pointer_value" : 0x77CF,
					"asset_rom_pointer_address" : 0x2B7CF,
					"asset_type" : ""
				},
				0x57 : {
					"asset_index" : 0x57,
					"asset_rom_pointer_value" : 0x77CF,
					"asset_rom_pointer_address" : 0x2B7CF,
					"asset_type" : ""
				},
				0x59 : {
					"asset_index" : 0x59,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x5B : {
					"asset_index" : 0x5B,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x5D : {
					"asset_index" : 0x5D,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x5F : {
					"asset_index" : 0x5F,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x61 : {
					"asset_index" : 0x61,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x63 : {
					"asset_index" : 0x63,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x65 : {
					"asset_index" : 0x65,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x67 : {
					"asset_index" : 0x67,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x69 : {
					"asset_index" : 0x69,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x6B : {
					"asset_index" : 0x6B,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x6D : {
					"asset_index" : 0x6D,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x6F : {
					"asset_index" : 0x6F,
					"asset_rom_pointer_value" : 0x77DA,
					"asset_rom_pointer_address" : 0x2B7DA,
					"asset_type" : ""
				},
				0x71 : {
					"asset_index" : 0x71,
					"asset_rom_pointer_value" : 0x6D95,
					"asset_rom_pointer_address" : 0x2AD95,
					"asset_type" : ""
				},
				0x73 : {
					"asset_index" : 0x73,
					"asset_rom_pointer_value" : 0x77FA,
					"asset_rom_pointer_address" : 0x2B7FA,
					"asset_type" : ""
				},
				0x75 : {
					"asset_index" : 0x75,
					"asset_rom_pointer_value" : 0x786C,
					"asset_rom_pointer_address" : 0x2B86C,
					"asset_type" : ""
				},
				0x77 : {
					"asset_index" : 0x77,
					"asset_rom_pointer_value" : 0x78C1,
					"asset_rom_pointer_address" : 0x2B8C1,
					"asset_type" : ""
				},
				0x77 : {
					"asset_index" : 0x77,
					"asset_rom_pointer_value" : 0x78C1,
					"asset_rom_pointer_address" : 0x2B8C1,
					"asset_type" : ""
				},
				0x79 : {
					"asset_index" : 0x79,
					"asset_rom_pointer_value" : 0x78E4,
					"asset_rom_pointer_address" : 0x2B8E4,
					"asset_type" : "text"
				},
				0x7B : {
					"asset_index" : 0x7B,
					"asset_rom_pointer_value" : 0x790C,
					"asset_rom_pointer_address" : 0x2B90C,
					"asset_type" : ""
				},
				0x7D : {
					"asset_index" : 0x7D,
					"asset_rom_pointer_value" : 0x6D93,
					"asset_rom_pointer_address" : 0x2AD93,
					"asset_type" : ""
				},
				0x7F : {
					"asset_index" : 0x7F,
					"asset_rom_pointer_value" : 0x793D,
					"asset_rom_pointer_address" : 0x2B93D,
					"asset_type" : ""
				},
				0x81 : {
					"asset_index" : 0x81,
					"asset_rom_pointer_value" : 0x6A15,
					"asset_rom_pointer_address" : 0x2AA15,
					"asset_type" : ""
				},
				0x83 : {
					"asset_index" : 0x83,
					"asset_rom_pointer_value" : 0x4085,
					"asset_rom_pointer_address" : 0x28085,
					"asset_type" : "text"
				},
			},
		}
	}
}