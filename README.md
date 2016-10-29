cyberknight-pce
===============

Translation tools and resources for the PC-Engine game Cyber Knight

Status
======

The game menu and initial intro screens are all translated and playable in English. The first game world (FarWorld), all monster names and most NPC names are also translated. The battle screen is mostly in English and all the menus in the game (ship/battle/overworld map) are all translated. The game can be played quite easily, but the game story is only partially done.

English language translation status

  * Font lookup tables 99% (small number of control bytes and double height character codes unknown)
  * Initial game menus (start/load/save/audio settings) 100%
  * Introductory cinematics 90% (scrolling intro translated, but broken by expanded main game dialogue)
  * Shipboard menu navigation 100%
  * Weapon names and descriptions 100%
  * Mecha customisation screens 100%
  * Battle screen menu and text 90% (alignment/text length bugs to iron out)
  * Party stats/experience screen 100%
  * NPC names 95% (3 or 4 names have length issues to resolve)
  * Enemy names 99% (one or two questionable names)
  * Doctor / Medbay dialogue 50%
  * Scientist / Lab dialogue 25%
  * Engineer / Hangar dialogue 50%
  * Planetary scan details 20%
  * Main, in-game story text 15% (85% of the first planet, FarWorld, translated)

How to use
==========

## General Principles

  - Extract text regions from the PC-Engine Cyber Knight game rom to one or patch files - //extractAssets.py//
  - Split test regions into individual strings and turn bytes back in to printable characters - //splitAssets.py//
  - Map those patch files to existing SNES translations (optional) - //mapScript.py//
  - Manually translate remaining text strings in the patch files.
  - Inject patch files back into Cyber KNight rom file, creating a (partially/fully) English translation - //injectScript.py//
  
All python scripts can be run with a //-h// parameter to display a list of options and help.
  
Download the git archive, unpack and drop in "Cyber Knight (J).pce" in to the same directory. All being well, there should be no configuration to edit.

Run the scripts in sequence: first //extractAssets.py//, then //splitAssets.py//, then //mapScript.py//, now edit the assets by hand before finally running //injectScript.py//.
    
Eventually, an IPS patch file will be released with all the modifications already patched in. Until then, feel free to use these scripts to edit the game yourself.

Useful Links
============

Old sites with information on enemy names, descripions, weapons, levels etc. (Japanese, load in Google translator)

  * http://www.otv.ne.jp/~hidechus/pcesknight/data/enemi-neo.html
  * http://ifs.nog.cc/aracnizauls.hp.infoseek.co.jp/CyberKnight_Top.html
