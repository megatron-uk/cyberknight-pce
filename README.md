cyberknight-pce
===============

Translation tools and resources for the PC-Engine game Cyber Knight

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
