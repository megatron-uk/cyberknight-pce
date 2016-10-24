# Cyber Knight Asset Bank Details

Many of these details are provided by *Elmer* from *PCEngineFX.com* following a discussion (http://www.pcenginefx.com/forums/index.php?topic=16222.165) relating to the issues of English text overflowing in to 'unused' space in the ROM, following insertion of longer script text.

The options were to then fall back to fixed-length strings (which would result in truncated English text) or look at expanding the ROM size to allocate more space at the end for expanded dialogue.

*Elmer* found that the game does use a text block pointer system. Two tables loaded in bank 0x01 which point to the asset bank to load, and an offset in to that bank. Each asset bank then has a small table at the front with pointers then in to the data structures that follow. Asset banks are 16KB in size.

Here follows a break down of the text/asset bank system:

## Master Bank

Master Bank 0x01, it is always loaded at PCE memory address 0xC000-0xDFFF.

**Table A**

Table A, ROM offset 0x02939, is a table of Asset Bank pointers
This is a table of which Text Bank to load at any point.

*Data*
```
0e 0e 0e 0e 0e 0e 0c 0e
0e 00 00 00 00 00 00 00
14 0a 0a 0a 0a 0a 0c 0c
0c 0c 0c 0c 0c 0c 0c 0c
0c
```

There are 33 bank load addresses, many of which, as shown, are duplicates.


**Table B**

Table B, ROM offset 0x0295a, type = Script Offset pointers.
This is a table of offsets into the pointer tables at the start of each asset bank.

*Data*
```
01 03 05 07 09 0b 17 0d
0f 00 00 00 00 00 00 00
83 01 03 05 07 09 01 03
05 07 09 0b 0d 0f 11 13
15
```

There are 33 asset chunk pointer offset addresses, one for each of the bank load entries in Table A.

## Asset Banks

The below text banks are always loaded at 0x4000-0x7FFF

### Bank 0x0A - 0x0B

Text Bank $0A/$0B, ROM offset $14000-$17FFF
First byte = Bank number = 0x0A
Second byte = 0x0B = 11 = 10/2 = 5x 2-byte pointers

*Pointer Data*
```
0A 0B 40 FD 54 6F 6A 29
6C C1 75 00
```

*Pointer Table*
```
0x00 = 0A = Bank ID
0x01 = 0B = Table size
0x02 = 40 FD - 0x4000 + 0x14000 = 0x140FD
0x03 = 54 6F - 0x4000 + 0x14000 = 0x1546F
0x04 = 6A 29 - 0x4000 + 0x14000 = 0x16A29
0x05 = 6C C1 - 0x4000 + 0x14000 = 0x16CC1
0x06 = 75 00 - 0x4000 + 0x14000 = 0x17500
```

### Bank 0x0C - 0x0D

Text Bank $0C/$0D, ROM offset $18000-$1BFFF
First byte = Bank number = 0x0C
Second byte = 0x19 = 25 = 24/2 = 12x 2-byte pointers

*Pointer Data*
```
0C 19 40 62 44 61 4C 47
51 27 59 16 5C 4B 63 17
6E A2 6E D5 71 DB 75 CE
78 00
```

*Pointer Table*
```
Position / Value
0x00 = 0C = Bank ID
0x01 = 19 = Table size
0x02 = 40 62 - 0x4000 + 0x18000 = 0x18062
0x03 = 44 61 - 0x4000 + 0x18000 = 0x18461
0x04 = 4C 47 - 0x4000 + 0x18000 = 0x18C47 
0x05 = 51 27 - 0x4000 + 0x18000 = 0x19127
0x06 = 59 16 - 0x4000 + 0x18000 = 0x19916
0x07 = 5C 4B - 0x4000 + 0x18000 = 0x19C4B
0x08 = 63 17 - 0x4000 + 0x18000 = 0x1A317
0x09 = 6E A2 - 0x4000 + 0x18000 = 0x1AEA2
0x0A = 6E D5 - 0x4000 + 0x18000 = 0x1AED5
0x0B = 71 DB - 0x4000 + 0x18000 = 0x1B1DB
0x0C = 75 CE - 0x4000 + 0x18000 = 0x1B5CE
0x0D = 78 00 - 0x4000 + 0x18000 = 0x1B800
```

### Bank 0x0E - 0x0F

Text Bank $0E/$0F, ROM offset $1C000-$1FFFF
First byte = Bank number = 0x0E
Second byte = 0x11 = 17 bytes = 16/2 = 8x 2-byte pointers

*Pointer Data*
```
0E 11 40 4C 4B ED 4E 73
53 B2 55 86 5C FF 6B EC
70 00
```

*Pointer Table*
```
Position / Value
0x01 = 0E = Bank ID
0x02 = 11 = Table size
0x03 = 40 4C - 0x4000 + 0x1C000 = 0x1C04C
0x04 = 4B ED - 0x4000 + 0x1C000 = 0x1CBED 
0x05 = 4E 73 - 0x4000 + 0x1C000 = 0x1CE73
0x06 = 53 B2 - 0x4000 + 0x1C000 = 0x1D3B2
0x07 = 55 86 - 0x4000 + 0x1C000 = 0x1D586
0x08 = 5C FF - 0x4000 + 0x1C000 = 0x1DCFF
0x09 = 6B EC - 0x4000 + 0x1C000 = 0x1EBEC
0x0A = 70 00 - 0x4000 + 0x1C000 = 0x1F000
```

### Bank 0x14 - 0x15

Text Bank $14/$15, ROM offset $28000-$2BFFF
First byte = Bank number = 0x14
Second byte = 0x93 = 147 bytes = 146/2 = 73x 2-byte pointers (*INCORRECT, only 66 pointers in this table.*)

*Pointer Data*
```
14 93 6D 95 6D A4 6D 36
6E 65 6E B7 6E 95 6D 0E
6F 95 6D 3D 6F 5E 70 95
6D 84 70 95 6D 93 6D 45
71 71 71 02 72 37 72 B2
72 95 6D 0E 73 DF 73 95
6D 20 74 81 74 AA 74 BD
74 D4 74 93 6D 93 6D 42
75 95 6D 74 75 B4 75 95
6D F7 75 49 76 95 6D 6F
76 F4 76 B4 77 CF 77 CF
77 95 6D 93 6D 93 6D 93
6D 93 6D 93 6D 93 6D 93
6D 93 6D 93 6D 93 6D DA
77 95 6D FA 77 6C 78 C1
78 E4 78 0C 79 93 6D 3D
79 15 6A 85 40 00
```

*Pointer Table*
```
Position / Value
0x01 = 14 = Bank ID
0x02 = 93 = Table size
```

*TODO: The table size byte (0x93 == 147) doesn't appear to correlate to the actual number of entries (133 - 1 / 2 = 66) in the table for bank 0x0E, as there are not 73 entries in the table.*
