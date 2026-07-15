🎵 LOOM2 -- Sonifiquation : Mac Setup Guide (step by step!)

Welcome Justin! This guide walks you through every single click
to get LOOM2 running on your Mac. No technical knowledge needed.


═══════════════════════════════════════════════════════════════
STEP 1 — DOWNLOAD THE GAME
═══════════════════════════════════════════════════════════════

  1. Open your web browser (Safari / Chrome / Firefox)

  2. Go to this URL (copy and paste it into the address bar):

       https://github.com/strulovitz/peaktogether-website

  3. Look for a GREEN button that says "<> Code" (near the top
     of the page, on the right side). Click it.

  4. In the little menu that appears, click "Download ZIP"
     at the bottom.

  5. Wait for the download to finish. It's about 10 MB.

  6. Open your Downloads folder in Finder. You will see a file
     called:

       peaktogether-website-master.zip

  7. Double-click it to unzip. A new folder appears next to it:

       peaktogether-website-master

  8. Move this folder somewhere convenient, like your Desktop.
     (Drag it there in Finder.)


═══════════════════════════════════════════════════════════════
STEP 2 — INSTALL PYTHON (if you don't have it already)
═══════════════════════════════════════════════════════════════

  1. Open your browser and go to:

       https://www.python.org/downloads/

  2. Click the big yellow button that says "Download Python
     3.x.x" (any version 3.10 or higher is fine).

  3. Once downloaded, double-click the .pkg file and follow
     the installer steps (just click Continue → Continue →
     Install → Close — all defaults are fine).

  4. To double-check it worked: open Terminal (see Step 3
     below for how), type this, and press Enter:

       python3 --version

     You should see something like "Python 3.12.4". If you do,
     you're all set!


═══════════════════════════════════════════════════════════════
STEP 3 — OPEN TERMINAL
═══════════════════════════════════════════════════════════════

  Terminal is a program that lets you type commands. It's
  already on your Mac.

  Method A (Spotlight — fastest):
    1. Press Command (⌘) + Spacebar
    2. Type: Terminal
    3. Press Enter

  Method B (Finder):
    1. Open Finder
    2. Go to Applications → Utilities → Terminal
    3. Double-click it

  A white or black window appears with a blinking cursor.
  That's where you type the commands below.


═══════════════════════════════════════════════════════════════
STEP 4 — GO TO THE GAME FOLDER
═══════════════════════════════════════════════════════════════

  In the Terminal window, type this and press Enter:

     cd ~/Desktop/peaktogether-website-master/loom2

  💡 TIP: If you put the folder somewhere other than Desktop,
  replace "Desktop" with wherever you put it. For example:

     cd ~/Downloads/peaktogether-website-master/loom2

  💡 TIP: You can type "cd " (with a space), then drag the
  loom2 folder from Finder directly into the Terminal window —
  it will type the full path for you!

  After pressing Enter, your Terminal prompt should now show
  the loom2 folder at the end of the line. If it does, you're
  in the right place!


═══════════════════════════════════════════════════════════════
STEP 5 — RUN THE LAUNCHER
═══════════════════════════════════════════════════════════════

  Type these TWO commands, one after the other:

  First, make the launcher executable (type and press Enter):

     chmod +x MAC/run_loom2.sh

  Then, run it (type and press Enter):

     ./MAC/run_loom2.sh

  🎉 The game will start!

  The FIRST time you run it, the launcher will ask if you want
  to install the needed Python packages. Type "Y" (or just press
  Enter) to say yes. This takes about 30 seconds. After that,
  every launch is instant.


═══════════════════════════════════════════════════════════════
STEP 6 — PLAY! 🎮
═══════════════════════════════════════════════════════════════

  Controls:
     Arrow keys   —  rotate the camera view
     W / A / S / D — move the Listening Totem around
     Mouse drag    —  look around
     Mouse scroll  —  zoom in / out
     Esc           —  quit the game

  🎧 HEADPHONES STRONGLY RECOMMENDED!
  The game turns mathematical surfaces into music — you need
  stereo headphones to experience the full sonification.


═══════════════════════════════════════════════════════════════
TO RUN IT AGAIN LATER
═══════════════════════════════════════════════════════════════

  1. Open Terminal
  2. Type: cd ~/Desktop/peaktogether-website-master/loom2
  3. Type: ./MAC/run_loom2.sh
  4. Play!

  (You don't need to do chmod again — only the first time.)


═══════════════════════════════════════════════════════════════
TROUBLESHOOTING
═══════════════════════════════════════════════════════════════

  "ModuleNotFoundError: No module named 'audioop'"
  → This happened on Python 3.13+ (Apple removed audioop).
    FIX: The launcher now handles this automatically. If you
    need to fix it manually, type:
       pip3 install audioop-lts
    (NOTE: as of July 2026 we replaced pydub with miniaudio,
     which doesn't need audioop or ffmpeg — this error should
     no longer appear.)

  "command not found: python3"
  → Python isn't installed yet. Go back to Step 2.

  "no usable system TTF font found"
  → This should NOT happen (we added Mac font support —
    Helvetica), but if it does, type this and press Enter:
       brew install font-liberation
    (If you don't have Homebrew, install it from https://brew.sh
     first — it's one command and takes 2 minutes.)

  Audio crackles or stutters
  → Close other apps that use audio (Spotify, YouTube, Zoom).
  → Plug in your charger (Mac sometimes throttles on battery).

  Game window is black / doesn't appear
  → Make sure you're in the loom2 folder (Step 4).
  → Type "pwd" in Terminal and press Enter — it should end
    with ".../loom2". If not, repeat Step 4.

  Any other problem?
  → Just ask Nir! He'll help or ask me (DeepSeek) to fix it. 🎵


═══════════════════════════════════════════════════════════════
QUESTIONS? Just reach out to Nir! 🎵✨
═══════════════════════════════════════════════════════════════
