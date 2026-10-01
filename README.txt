KH1 FINAL MIX PC SAVE EDITOR
========================================

GUIDES
  Install Guide:  docs/INSTALL.md
  User Manual:    docs/USER_MANUAL.md

A safety-first, cross-platform editor for KHFM_WW.png from:
  - Steam
  - Epic Games Store
  - Re:Fined

SUPPORTED IN THIS RELEASE
-------------------------
  - Multiple KH1 save slots
  - Automatic save discovery on Steam Deck, Windows Steam, Epic, Re:Fined,
    and OneDrive
  - Native KDE file browser on Steam Deck instead of Tkinter's compact picker
  - Sora level, current/base HP and MP, AP, Strength, Defense, and EXP
  - Munny and Final Mix difficulty
  - Full 256-entry inventory count table
  - Owned Keyblades and equipped Keyblade
  - Safe level 99/100 simulation that updates both mirrored KH1 level records,
    sets total EXP, applies natural stat growth, and restores every missing
    Dream Sword/Staff/Shield level-up ability through the target
  - Full 48-slot Sora ability editor with duplicate abilities and separate
    owned/equipped state
  - Sora Equipment tab with Keyblade, 8 accessory entries, and 12 carried-item
    entries
  - Donald and Goofy tabs with stats, EXP, character-specific weapons,
    accessories, carried battle items, and 48 ability entries
  - Used AP/Power/Defense boosts preserved during simulated leveling
  - Unsafe Level-only changes refused
  - World, room, and spawn location
  - Read-only Values Lab before/after comparison
  - Synthesis tab: every Final Mix recipe with have/need counts, a made-item
    checklist toward Ultima Weapon, and a total materials calculator
  - Timestamped backup before every write
  - One-click Backups Folder button (Explorer on Windows, Dolphin on Steam Deck)
  - Atomic saving, PNG CRC repair, and post-write reparsing

NOT YET ENABLED
---------------
  - Platform/account conversion

Those layouts are now known from the reference source, but will be enabled only
after their UI and targeted tests are completed.

FILES
-----
  kh1_save_editor.py     Desktop interface
  kh1_save_core.py       PNG/archive parsing, validation, diff, and writing
  kh1_leveling.py        KH1FM level-growth and ability simulation tables
  kh1_reference.py       KH1 equipment and world reference tables
  kh1_synthesis.py       Final Mix synthesis recipes and checklist
  docs/                  Install Guide and User Manual
  install_steamdeck.sh   Steam Deck installer
  build_windows_exe.bat  Windows executable builder
  run_windows.bat        Run directly on Windows without building an .exe
  tests/                 Automated safety and format tests

STEAM DECK
----------
1. Extract the complete package.
2. Enter Desktop Mode.
3. Open Konsole in the extracted directory.
4. Run:

     bash install_steamdeck.sh

5. Launch "KH1 Final Mix Save Editor" from the application menu.

Typical Steam save location:

  /home/deck/.local/share/Steam/steamapps/compatdata/2552430/
  pfx/drive_c/users/steamuser/Documents/My Games/
  KINGDOM HEARTS HD 1.5+2.5 ReMIX/Steam/<Steam ID>/KHFM_WW.png

Press Ctrl+H in Dolphin to show the hidden .local directory.

WINDOWS
-------
Install Python 3.8 or newer from python.org with tkinter enabled.

To run it directly, double-click:

  run_windows.bat

To build a standalone executable instead, run:

  build_windows_exe.bat

The executable appears under dist/KH1_Save_Editor.exe.

CUSTOM BANNER (OPTIONAL)
------------------------
Put a banner.png (or banner.gif) next to kh1_save_editor.py, or next to the
built .exe, and it appears across the top of the window. About 1000x190
pixels works well. No artwork is included with the project.

IMPORTANT SAFETY NOTES
----------------------
  - Never test with your only copy of a save.
  - A timestamped backup is created in KH1_Save_Editor_Backups before writing.
  - Changing World without a compatible Room and Spawn can place Sora somewhere
    invalid. Prefer copying all three values from a real save at the destination.
  - Current HP/MP and base maximum HP/MP are distinct save fields. Equipment
    bonuses may make the in-game displayed maximum exceed the stored base value.
  - Do not change Level by itself. Use Simulate Leveling and select the original
    Dream power and Dawn/Midday/Dusk EXP curve used for that playthrough.
  - Simulated abilities are added owned and unequipped. Open Abilities in-game
    or use the editor's Abilities tab to equip the ones you want.
  - The ability high bit means Equipped. Equipping more AP than Sora owns can
    produce an invalid setup, so simulated abilities deliberately start off.

TESTED SO FAR
-------------
  - Steam Deck (Steam): an inventory edit was loaded in-game and confirmed.
  - Windows 11 (Steam, Python 3.14): tests pass, save is found and read, and
    the editor opens. In-game confirmation on Windows is still pending.
  - Epic and Re:Fined: save discovery is supported but not yet confirmed by a
    real user. Reports welcome.

REPORTING BUGS
--------------
Open an issue at:

  https://github.com/KatRewrites/kh1-save-editor/issues

Please include:
  - Platform (Windows, Steam Deck, or Linux) and store (Steam, Epic, Re:Fined)
  - Editor version or commit
  - What you changed, what you expected, and what happened in-game
  - Any error message, copied as text
  - If possible, your backup .bak file from KH1_Save_Editor_Backups

Always keep your own backup copy before editing.

LICENSE AND ATTRIBUTION
-----------------------
This project is distributed under GPL-3.0.

The KH1 record model and equipment/world reference tables are ported from:
  Xeeynamo/KingdomSaveEditor
  https://github.com/Xeeynamo/KingdomSaveEditor

Original project copyright remains with its contributors. See LICENSE.
