#!/usr/bin/env python

from config import TABLE_NAME

def load_table():
	"""
	load_table - load the translation table.
	The translation table is a tab delimited data file
	with the following columns:
	hex code, actual char pre-0x5c byte, char set type (A/K/H/S), post-0x5c byte, char set type, notes
	
	where A/S/H/K = ASCII, Symbol, Hiragana, Katakana
	pre-0x5c = the character shown if the byte come before a 0x5c control byte
	post-0x5c = the character shown if the byte comes after a 0x5c control byte
	"""
	trans_table = {}
	
	try:
		f = open(TABLE_NAME, "r")
		for line in f:
			columns = line.split('\t')
			byte_code = columns[0].replace('"', '')
			trans_table[byte_code] = {}
			trans_table[byte_code]["byte_code"] = byte_code
			trans_table[byte_code]["pre_shift"] = columns[1].replace('"', '')
			trans_table[byte_code]["pre_shift_type"] = columns[2].replace('"', '')
			trans_table[byte_code]["post_shift"] = columns[3].replace('"', '')
			trans_table[byte_code]["post_shift_type"] = columns[4].replace('"', '')
			if len(columns) > 5:
				trans_table[byte_code]["notes"] = columns[5].replace('"', '')
		f.close()
	except Exception as e:
		print traceback.format_exc()
		print line
		sys.exit(2)
	return trans_table
