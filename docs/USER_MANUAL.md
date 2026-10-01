# User Manual: KH1 Final Mix Save Editor

This manual explains every part of the editor. If you haven't installed it yet, start with the [Install Guide](INSTALL.md).

> **Golden rules**
> 1. Close the game before you save in the editor.
> 2. Keep your own copy of the save. The editor also makes a backup each time it saves.
> 3. Don't change Sora's Level by itself. Use **Simulate Leveling** (see below).

---

## Contents

1. [Opening a save](#1-opening-a-save)
2. [The main window](#2-the-main-window)
3. [Character & World tab](#3-character--world-tab)
4. [Simulate Leveling](#4-simulate-leveling)
5. [Donald and Goofy tabs](#5-donald-and-goofy-tabs)
6. [Equipment tab](#6-equipment-tab)
7. [Inventory tab](#7-inventory-tab)
8. [Keyblades tab](#8-keyblades-tab)
9. [Abilities tab](#9-abilities-tab)
10. [Synthesis tab](#10-synthesis-tab)
11. [Saving your changes](#11-saving-your-changes)
12. [Backups and restoring](#12-backups-and-restoring)
13. [Values Lab](#13-values-lab)
14. [Safety features](#14-safety-features)
15. [FAQ](#15-faq)

---

## 1. Opening a save

- **Find My Saves** searches the usual Steam, Epic, Re:Fined, OneDrive, and Steam Deck folders. If it finds one save, it opens it. If it finds several, you pick one.
- **Open Save** lets you browse to any `KHFM_WW.png` yourself. On the Steam Deck it uses the normal KDE file browser.

The file path appears under the buttons once a save is loaded.

## 2. The main window

- **Top buttons:** Find My Saves, Backups Folder, Open Save, Values Lab, and **Save**.
- **Slot buttons:** one button for each save slot in the file, showing its world and level, for example `Slot 1: Traverse Town (LV 6)`. Click one to edit that slot. Each slot is edited and saved separately.
- **Tabs:** Character & World, Donald, Goofy, Equipment, Inventory, Keyblades, Abilities, Synthesis, and Help.
- **Status line:** the bottom of the window tells you what just happened, such as a finished save or a simulation that's ready.

Nothing is written to your save until you press **Save**.

## 3. Character & World tab

**Sora's stats**

| Field | What it does |
|---|---|
| Level | Sora's level. Changing only this is refused. Use Simulate Leveling. |
| Current HP / HP | Current HP and base max HP. Equipment can make the in-game max higher than the stored base value. |
| Current MP / MP | Same idea as HP. |
| AP | Base AP for equipping abilities. |
| Strength, Defense | Base stats. |
| EXP | Total experience points. |

**Game info**

- **Munny:** your money.
- **Difficulty:** the Final Mix difficulty mode.

**Location**

- **World, Room, and Spawn** set where Sora loads in.
- ⚠️ Changing only the World can drop Sora into a room that doesn't exist and soft-lock the save. Change all three together, using values copied from a real save made at that spot.

## 4. Simulate Leveling

This is the safe way to raise Sora's level (to 99 or 100). It's on the Character & World tab under **Simulate Leveling…**.

1. Load the slot. It must be your **real, unedited** level. Slots that already show level 99 or 100 are refused.
2. Choose:
   - **Dream power:** Sword, Staff, or Shield, whichever you picked at the start of the game. The editor guesses this from your abilities.
   - **EXP curve:** Dawn, Midday, or Dusk, from your answers to the opening questions.
   - **Target level:** 99 or 100.
3. Click **Prepare Simulation**. The editor:
   - updates both internal level records,
   - sets the matching total EXP,
   - adds only the natural stat growth you missed, so boosts you already used (Power, Defense, AP Ups) are kept,
   - restores every level-up ability you would have learned, added as **owned but not equipped**.
4. Look over the new numbers, then press **Save**.

Equip the new abilities in-game or on the Abilities tab. They start unequipped because equipping more AP than Sora has can make an invalid setup.

## 5. Donald and Goofy tabs

Each one has:

- Stats and EXP
- Weapon (Donald can only use staffs and Goofy can only use shields)
- Accessories
- Carried battle items
- 48 ability slots, each with an **Equipped** checkbox

## 6. Equipment tab

Sora's gear:

- Equipped **Keyblade** (the same setting as on the Keyblades tab)
- **8 accessory** slots
- **12 carried-item** slots (battle items)

Only items of the right type are listed in each dropdown.

## 7. Inventory tab

This lists every item count in the game, grouped into Consumables, Boosts, Synthesis materials, Accessories, Recipes, Reports, Key Items, and Summons. Each count can be 0 to 99. The hex number in brackets is the item's internal ID.

Tip: changing key items or reports can affect story progress, so only change them if you know what they do.

## 8. Keyblades tab

Pick Sora's **Equipped Keyblade** and tick the Keyblades he **owns**. The Equipment tab can also change the equipped Keyblade. Change it in one place: if the two tabs are set to different Keyblades, saving is refused until they match.

## 9. Abilities tab

Sora has 48 ability slots. Each slot has an ability and an **Equipped** checkbox. The same ability can appear in more than one slot. Keep the total AP of equipped abilities within Sora's AP.

## 10. Synthesis tab

This is a checklist and calculator for every Final Mix Moogle synthesis recipe, all the way to the Ultima Weapon.

**Recipe list**

| Column | Meaning |
|---|---|
| Made | ☑ means you've ticked it off as already made. |
| Item | What the Moogles make. |
| List | Which synthesis list (I to VI) the recipe is on. |
| Materials | Each material as *have / need*, read from your inventory. |
| Status | **Ready to make**, **Short N material(s)**, **Locked (make N more)**, or **Made**. |

- **Double-click** an item, or select it and press **Space**, to tick it off or untick it.
- Ticks are saved on your computer for each save file and slot. They are **never written into the game save**, because the save doesn't seem to record which items you've made.
- The line at the top shows your progress, for example *"Made 12 of 30 items on Lists I–V… List IV opens after 3 more."*

**Unlock rules (Final Mix)**

| List | Opens after making |
|---|---|
| I | Available from the start |
| II | 3 different items |
| III | 9 different items |
| IV | 15 different items (this also unlocks Encounter Plus) |
| V | 21 different items |
| VI (Ultima Weapon, Fantasista, Seven Elements) | All 30 items on Lists I–V |

The Ultima Weapon can only be made once.

**Calculator**

The bottom table adds up the materials needed to make **every unticked item once**, then compares that with what you have. Red rows are what you still need to farm, sorted by how many you're short. ✓ means you have enough.

The tab updates when you open it, switch slots, or tick an item. If you change counts on the Inventory tab, the Synthesis tab uses those new numbers right away.

Notes: Mythril and Dark Matter can also be synthesized, and Orichalcum can be bought. Recipe data comes from the [KH Wiki's Moogle Shop page](https://www.khwiki.com/Moogle_Shop) (Final Mix).

Where the ticks are stored:
- Windows: `%APPDATA%\KH1_Save_Editor\synthesis_checklist.json`
- Steam Deck and Linux: `~/.config/kh1_save_editor/synthesis_checklist.json`

## 11. Saving your changes

1. Close the game completely.
2. Press **Save**.
3. The editor then:
   - writes a timestamped backup into `KH1_Save_Editor_Backups` next to your save,
   - writes the new file safely, so a crash can't leave a half-written save,
   - repairs the PNG checksums,
   - re-reads the finished file to confirm it's valid.
4. You'll see **"Saved and verified"** with the backup's name.

If nothing changed in the slot, the editor tells you and doesn't write anything.

**Steam Cloud:** if Steam asks which save to keep the next time you launch the game, choose the **local** one (the one you just edited).

## 12. Backups and restoring

- **Backups Folder** opens `KH1_Save_Editor_Backups` (File Explorer on Windows, Dolphin on the Steam Deck).
- Each backup is named with the date and time it was made.

**To restore a backup:**

1. Close the game.
2. Copy the backup you want into the save folder.
3. Rename it to exactly `KHFM_WW.png`, replacing the current file. Make a copy of the current file first if you might want it.

## 13. Values Lab

Values Lab is a read-only tool for comparing two saves. Use it to find out what changed between them, for example before and after buying an item in-game.

1. Click **Values Lab**.
2. Pick the **BEFORE** save, then the **AFTER** save.
3. Choose where to save the report.

You'll get a `.txt` report and a `.json` report listing every changed value. Neither save is modified. These reports are very helpful when you report a bug.

## 14. Safety features

- Timestamped backup before every write
- Safe (atomic) writing
- PNG checksum checks before and after editing
- The finished file is re-read before success is reported
- Level-only changes are refused unless EXP, HP, MP, AP, Strength, and Defense change with them
- Simulated abilities start unequipped

## 15. FAQ

**Does this work with Epic or Re:Fined?**
Save discovery supports both, but they haven't been confirmed in-game by a user yet. Please report how it goes.

**Can I move a save between Steam and Epic?**
Not yet. Platform and account conversion is planned but not enabled.

**My edit didn't show up in-game.**
Make sure the game was closed while you saved, and pick the local save if Steam Cloud asks.

**Something broke. What do I do?**
Restore your backup (section 12), then [open an issue](https://github.com/KatRewrites/kh1-save-editor/issues). Include your platform, store, version, what you changed, what happened, any error text, and a Values Lab report if you can.
