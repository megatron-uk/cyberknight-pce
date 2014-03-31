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
  * Weapon names and descriptions 99% (some 'hidden' weapons translated, but unviewed)
  * Mecha customisation screens 100%
  * Party stats/experience screen 100%
  * Enemy names 90%  
  * Doctor / Medbay dialogue 50%
  * Scientist / Lab dialogue 25%
  * Engineer / Hangar dialogue 50%
  * Planetary scan details 0%
  * Main, in-game story text 0%

How to use
==========

Add the text regions you want to extract into the configuration file 'config.py'.
Run extractScript.py on the rom file - you will need a headerless version of "Cyber Knight (J).pce". It should be 524288 bytes exactly in size, if you have a headered version simply remove it using a standard rom or hex editor.

The extract script will produce a patch file with a .json extension. You can then edit this file to add in the translations you want to make. Drop this file, or portions of it into the patches directory.

Running injectScript can use the patches directory to apply the translations you have made.

For example:

    python extractScript.py -i "Cyber Knight (J).pce" -o "Script.json" -t "CyberKnightTranslation.csv"

....edit Script.json to add in your translations and then copy in to the patches folder....

    python injectScript.py -i "Cyber Knight (J).pce" -o "Cyber Knight (E).pce" -d ./patches/

If you download this entire git archive and drop in a 'Cyber Knight (J).pce' rom file, the standard options defined in config.py should work just fine without any command line parameters:

    python extractScript.py

and...

    python injectScript.py
    
    
Useful Links
============

  * http://translate.google.co.uk/translate?hl=en&sl=ja&tl=en&u=http%3A%2F%2Fwww.otv.ne.jp%2F~hidechus%2Fpcesknight%2Fdata%2Fenemi-neo.html
  
