cyberknight-pce
===============

Translation tools and resources for the PC-Engine game Cyber Knight

Status
======

English language translation status

  * Font lookup tables 99% (small number of control bytes and double height character codes unknown)
  * Initial game menus (start/load/save/audio settings) 100%
  * Introductory cinematics 100%
  * Shipboard menu navigation 100%
  * Weapon names and descriptions 100%
  * Mecha customisation screens 100%
  * Battle screen menu and text 60% (all menus done, MICA 'analysis' and weapon effects to-do)
  * Party stats/experience screen 100%
  * NPC names 100% 
  * Enemy names 99% (one or two questionable names)
  * Doctor / Medbay dialogue 50%
  * Scientist / Lab dialogue 25%
  * Engineer / Hangar dialogue 50%
  * Planetary scan details 0%
  * Main, in-game story text 5% (75% of the first planet, FarWorld, translated)

How to use
==========

## General Principles

  - Extract text regions from the PC-Engine Cyber Knight game rom to one or patch files - //extractScript.py//
  - Map those patch files to existing SNES translations (optional) - //mapScript.py//
  - Manually translate remaining text strings in the patch files.
  - Inject patch files back into Cyber KNight rom file, creating a (partially/fully) English translation - //injectScript.py//
  
All python scripts can be run with a //-h// parameter to display a list of options and help.
  
## Extracting Text Regions

Add the text regions you want to extract into the configuration file 'config.py'.
Run extractScript.py on the rom file - you will need a headerless version of "Cyber Knight (J).pce". It should be 524288 bytes exactly in size, if you have a headered version simply remove it using a standard rom or hex editor.

The extract script will produce a patch file with a .json extension. You can then edit this file to add in the translations you want to make. Drop this file, or portions of it into the patches directory.

Running injectScript can use the patches directory to apply the translations you have made.

For example:

    python extractScript.py -i "Cyber Knight (J).pce" -o "Script.json" -t "CyberKnightTranslation.csv"

....edit Script.json to add in your translations and then copy in to the patches folder.

## (Optionally) Mapping to Existing SNES Translations

You can use the optional Cyber Knight SNES translation file to match any existing text. Use the mapScript.py file to do this, any exact matches will be inserted as the translation text, any partial matches will be embedded in the patch file, but not used. Anytime more than one SNES string matches, the script will pause, print a list of choices and then prompt for one to use (or none).

You can specifiy pass levels 1, 2 and 3. Level 1 requires the closest match (+80%), Level 2 is a bit easier (and will hence prompt a lot more, and Level 3 is the sloppiest match.

To run a strict match:

   python mapScript.py -d ./patches/ -o ./patches-processed/ -p 1 -v

I reccomend running level 1 pass, then 2, then 3, so that the largest amount of automatic matches are made first. You should get a good >50% match rating on all of the dialogue strings from the game.

At this point you'll probably want to hand-edit the patch files to fix up the SNES translations, embed control codes etc, to make it fit the PC-Engine original text.


## Applying Patches / Injecting Text

Once you have some patch files with translations, you can then use injectScript to insert them back into the Japanese PC-Engine rom file:

    python injectScript.py -i "Cyber Knight (J).pce" -o "Cyber Knight (E).pce" -d ./patches/

If you download this entire git archive and drop in a 'Cyber Knight (J).pce' rom file, the standard options defined in config.py should work just fine without any command line parameters:

    python extractScript.py

and...

    python injectScript.py
    
    
Useful Links
============

Old sites with information on enemy names, descripions, weapons, levels etc. (Japanese, load in Google translator)

  * http://www.otv.ne.jp/~hidechus/pcesknight/data/enemi-neo.html
  * http://ifs.nog.cc/aracnizauls.hp.infoseek.co.jp/CyberKnight_Top.html
