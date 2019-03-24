# cyberknight-pce

Translation tools and resources for the PC-Engine game Cyber Knight.

Cyber Knight is a sci-fi twist on a traditional console RPG. There is a fair amount of dialogue between player and non-player characters, a top-down world map and (semi) random encounters on the map which trigger battle scenes.

There are a *lot* of battles.

The title was released on both the PC-Engine and the Super Famicom, both exclusively in Japanese. Later, the translation group [Aeon Genesis](http://agtp.romhack.net/project.php?id=ck1) translated it to English for the SNES. No attempts for the PC-Engine existed prior to now.

There are differences between SNES and PC-Engine version, in some respects the PC-Engine looks better (higher res menu screens and dialogue), in some the SNES is clearly superior (battle screens and higher colour use). Audio is very subjective - the PCE has really great, stereo PSG music in the best tradition of the console; the SNES has more *realistic* sounds, but I'm not sure if it's actually better.

### Status

The game menu and initial intro screens are all translated and playable in English. The first game world (FarWorld), all monster names and most NPC names are also translated. The battle screen is mostly in English and all the menus in the game (ship/battle/overworld map) are all translated. The game can be played quite easily, but the game story is only partially done.

This is a summary of the English language translation status:

| Aspect of game | Status        | Notes |
| -------------- |:-------------:| -----:|
| Font lookup tables | 99% | A very small number of control bytes and double height character codes unknown |
| Initial game menu | **COMPLETED** | This is the start/load/save/audio settings screen |
| Introductory cinematic | **COMPLETED** | Covers battle scene, scrolling intro and initial "lights out" crew chat |
| Shipboard menu navigation | **COMPLETED** | This is the menu system used to navigate around the ship |
| Weapon names and descriptions | **COMPLETED** | Weapon and item names are complete, but the display of this information is not fully sorted, i.e. the prefixes for weapon damage, damage type etc, are still in Japanese. |
| Mecha customisation screens | 99% | Text is translated, but a display bug currently barfs the screen when you access it. This is the screen accessed from the mech hangar on the ship. |
| Battle screen menu and text | 90% | Most text done, but there are a few alignment/text length bugs to iron out. |
| Party stats/experience screen | **COMPLETED** | Shown after battles |
| NPC names | 95% | 3 or 4 names have length issues to resolve |
| Enemy names | 99% | 1 or 2 questionable names |
| Doctor / Medbay dialogue | 50% | This includes the game save screen which has some display issues; likely a missing or additional control code somewhere. |
| Scientist / Lab dialogue | 25% | Haven't been far enough in game to trigger much of this dialogue tree - it relies on acquiring items called *items* (ha!) from enemies after battles. |
| Engineer / Hangar dialogue | 50% | Some screen corruption - possible stray or missing control codes in the auto translated text. |
| Planetary scan details | 20% | |
| Main, in-game story text | 15% | FarWorld: 85% some dialogue towards end of planet quest remains|

THe bulk of the gameplay dialogue that you come across in regular play is done, it's mostly text that is only triggered after progressing through the story, gaining sufficient XP or acquiring certain items that I can't test until I play it enough :)

----

## How it works

Luckily, the PC-Engine version of Cyber Knight uses uncompressed text and already has a full English character set in the font table, so a lot of what we need is already in place.

Cyber Knight also uses an asset bank system - the text is not in one location in the ROM. A full explanation is is the [Cyber Knight Asset Bank Scheme](documents/CyberKnight Asset Bank Scheme.md) file.

What we needed to do in order to get the Japanese text into data files that we could edit was:

  - Extract text regions from the PC-Engine Cyber Knight game rom to one or more patch files, mapping byte codes from the game data into the font table (see the font table screenshots in **documents** folder as well as the files **CyberKnightTranslation.csv** and **CyberKnightKanjiTranslation.csv** which map the byte codes to actual, printable Japanese and English characters) - I wrote **lib/extractAssets.py** to do this
  - Split test regions into individual strings and turn bytes back in to printable characters - This was the job of **lib/splitAssets.py**
  - Map those patch files to the existing JPN to ENG SNES translation using Python pattern matching tools (optional) - using **lib/mapScript.py**

At this point I have a directory full of data files, one per asset bank (the game keeps graphics and script data in asset banks that are swapped in and out from ROM as needed). Some of the strings will have the equivalent matching SNES English translation already embedded. Check the contents of the *assets/split* directory.

The next part is the hard part:

  - Manually translate remaining text strings in the patch files.
  - Inject patch files back into Cyber KNight rom file, creating a (partially/fully) English translation **and** expand the ROM from 512KB to 768KB at the same time in order to create enough new asset banks in ROM to fit the expanded English script - see **lib/expandRom.py**

It's at this point that the above two steps need to repeat over and over again, manually fixing text, re-injecting and testing the ROM, fixing things that haven't been translated, or don't quite work correctly (text control codes, etc), or typographical errors that mean the game barfs when I accidentaly remove a string delimeter or something similar.
  
All python scripts can be run with a **-h** parameter to display a list of options and help.

### Helping

If you want to help, you'll need (alongside a working installation of **Python 3**) to do the following:
  
Download the git archive, unpack and drop in "Cyber Knight (J).pce" in to the same directory. All being well, there should be no configuration to edit.

Assuming you're reasonably confident that I've already extracted all the game script already, you only need to run:

```
python lib/expandRom.py -s -f
```

 * -s *show progress*
 * -f *force overwrite of an existing ROM file*

This will use the data files I've translated so far in **assets/converted/**, inject them into your Japanese ROM file and build a new one for you. You then need to test the game!

Feel free to edit the patch data files in **assets/converted** if you feel like anything needs changing or fixing.

### Future Patch Release

Eventually, an IPS patch file will be released with all the modifications already patched in. Until then, feel free to use these scripts to edit the game yourself.

----

## Useful Links

Old sites with information on enemy names, descripions, weapons, levels etc. (Japanese, load in Google translator)

  * http://www.otv.ne.jp/~hidechus/pcesknight/data/enemi-neo.html
  * http://ifs.nog.cc/aracnizauls.hp.infoseek.co.jp/CyberKnight_Top.html
