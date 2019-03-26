# Assets

These are the game script assets as dumped from the *Cyber Knight (J).pce* rom file. They go through 3 stages:

 * Raw - data as extracted from each asset bank, unterminated and unsplit. aka one big binary blob.
 * Split - data from *raw*, split on null bytes in to (what we hope) are individual strings.
 * Converted - data taken from *split* and mapped (where possible) to SNES translation strings and we add (by hand) additional English text and clean things up.

Patch files in **converted** are the actual patches that get injected in to the game.
