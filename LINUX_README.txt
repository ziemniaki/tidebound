TIDEBOUND - THE KEEPER'S LIGHT
Linux x86_64 player

Requires a graphical Linux desktop, x86_64 CPU, glibc 2.35 or newer, and an
OpenGL-capable graphics driver. Ubuntu 22.04 and 24.04 are the initial test
targets. ARM Linux, Steam Deck controls and other distributions are not verified.

1. Extract the complete ZIP into a normal folder you own.
2. On Ubuntu, install the runtime libraries if they are missing:
   sudo apt install libpulse0 libgomp1 zlib1g libffi8 libyaml-0-2 libcrypt1 libbsd0 libmd0 libgl1 libegl1
   Ubuntu 22.04 also needs libasound2; Ubuntu 24.04 uses libasound2t64.
   Use your distribution's normal graphics drivers and desktop audio service.
3. Run ./Tidebound.sh in the extracted folder. No Wine, Python or Ruby install
   is required. If your extractor discarded permissions, run:
   chmod +x Tidebound.sh mkxp-z.x86_64
4. Press Return, then Continue for an existing save or New Game to begin.

Controls: arrows to move; Return to confirm; Esc or X for menu/back.
F1 opens key bindings. Save through the in-game menu.

The game keeps the Tidebound_Opening_0_2 save identity. On Linux saves normally
live below ~/.local/share/ (or XDG_DATA_HOME), outside this player folder.
Replacing the player folder does not replace saves. Saves do not automatically
transfer between computers; back up an existing save before transferring one.

Native CI checks boot, game data, isolated save/load and a rendered frame using
Xvfb/Mesa and silent audio. It is not a complete playthrough or proof of working
hardware audio, controllers, Wayland or every GPU/desktop configuration.

The pinned engine is mkxp-z 826929e, built upstream on Ubuntu 22.04 with Ruby
3.1.3. Its bundled libraries, source archive, license and provenance are included.
BUILD.json lists the packaged file hashes. For a launch error, preserve the
terminal output, exact archive version and your Linux distribution/version.

Unofficial Pokemon fan project. See CREDITS.md for attribution.
