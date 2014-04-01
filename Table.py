#!/usr/bin/env python

import traceback
import sys
from config import TABLE_NAME, TABLE_NAME_DOUBLE

def load_snes_table(snes_name):
	"""
	load_snes_table - load the existing SNES script
	The SNES script is a simple, two-column CSV file;
	col 1 = Japanese text
	col 2 = English text
	"""

	trans_table = {}
	try:
		line = ""
		f = open(snes_name, "r")
		for line in f:
			columns = line.split(',')
			key = columns[0]
			value = columns[1]
			trans_table[key] = value
		f.close
	except Exception as e:
		print traceback.format_exc()
		print e
		print line
		sys.exit(2)
	return trans_table

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
		line = ""
		f = open(TABLE_NAME, "r")
		for line in f:
			columns = line.split('\t')
			byte_code = columns[0].replace('"', '')
			trans_table[byte_code] = {}
			trans_table[byte_code]["byte_code"] = byte_code.upper()
			trans_table[byte_code]["pre_shift"] = columns[1].replace('"', '')
			trans_table[byte_code]["pre_shift_type"] = columns[2].replace('"', '')
			trans_table[byte_code]["post_shift"] = columns[3].replace('"', '')
			trans_table[byte_code]["post_shift_type"] = columns[4].replace('"', '')
			if len(columns) > 5:
				trans_table[byte_code]["notes"] = columns[5].replace('"', '')

		f.close()
	except Exception as e:
		print traceback.format_exc()
		print e
		print line
		sys.exit(2)
	return trans_table

def load_table_double():
	"""
	load_double_table - load the double height (aka Kanji) translation table.
	The translation table is a tab delimited data file
	with the following columns:
	hex code, actual char char set type (A/K/H/S), notes
	
	where A/S/H/K/Kj = ASCII, Symbol, Hiragana, Katakana, Kanji
	"""
	trans_table = {}
	
	try:
		line = ""
		f = open(TABLE_NAME_DOUBLE, "r")
		for line in f:
			columns = line.split('\t')
			byte_code = columns[0].replace('"', '').upper()
			trans_table[byte_code] = {}
			trans_table[byte_code]["byte_code"] = byte_code.upper()
			trans_table[byte_code]["pre_shift"] = columns[1].replace('"', '')
			trans_table[byte_code]["pre_shift_type"] = columns[2].replace('"', '')
			trans_table[byte_code]["post_shift"] = columns[3].replace('"', '')
			trans_table[byte_code]["post_shift_type"] = columns[4].replace('"', '')
			
			if len(columns) > 3:
				trans_table[byte_code]["notes"] = columns[5].replace('"', '')

		f.close()
	except Exception as e:
		print traceback.format_exc()
		print e
		print line
		sys.exit(2)
	return trans_table
