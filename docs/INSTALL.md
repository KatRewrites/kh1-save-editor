# Install Guide: KH1 Final Mix Save Editor

The editor is a small Python desktop app. It works on **Windows 10/11**, the **Steam Deck**, and other **Linux** PCs. It edits `KHFM_WW.png`, the save file from Kingdom Hearts HD 1.5+2.5 ReMIX (Steam, Epic Games Store, or Re:Fined).

> **Before you start:** close the game, and copy your save file somewhere safe. The editor makes its own backup every time it saves, but keeping a copy of your own is the best protection.

---

## 1. Download the editor

1. Open the [GitHub repository](https://github.com/KatRewrites/kh1-save-editor).
2. Click the green **Code** button, then **Download ZIP**.
3. Extract (unzip) the whole folder. Keep all the files together, because the editor needs every `kh1_*.py` file.

If you use git, you can clone it instead:

```
git clone https://github.com/KatRewrites/kh1-save-editor.git
```

---

## 2. Windows

### Install Python (one time)

1. Download Python 3.8 or newer from [python.org](https://www.python.org/downloads/windows/).
2. Run the installer and tick **Add python.exe to PATH** on the first screen.
3. Leave **tcl/tk and IDLE** ticked (this is on by default). The editor's window needs it.

### Run the editor

Double-click **`run_windows.bat`** in the extracted folder. The editor window opens.

If Windows SmartScreen warns you, choose **More info**, then **Run anyway**. The `.bat` file only starts Python with `kh1_save_editor.py`.

### Optional: build a standalone `.exe`

Double-click **`build_windows_exe.bat`**. It will:

1. Check your Python version and tkinter.
2. Install or update PyInstaller.
3. Run the automated tests, and stop if any test fails.
4. Build `dist\KH1_Save_Editor.exe`.

You can then copy `KH1_Save_Editor.exe` anywhere and run it without opening the folder.

### Where Windows saves live

The editor finds these on its own. For reference:

- **Steam:** `Documents\My Games\KINGDOM HEARTS HD 1.5+2.5 ReMIX\Steam\<Steam ID>\KHFM_WW.png`
- **Epic:** `Documents\KINGDOM HEARTS HD 1.5+2.5 ReMIX\Epic Games Store\...\KHFM_WW.png`
- **Re:Fined:** `Documents\Kingdom Hearts\...\KHFM_WW.png`
- If your Documents folder is synced by **OneDrive**, the same paths under `OneDrive\Documents` are checked too.

---

## 3. Steam Deck

1. Hold the power button and choose **Switch to Desktop**.
2. Download and extract the ZIP (see step 1) in the Deck's browser, for example into `Downloads`.
3. Open the extracted folder in **Dolphin** (the file manager).
4. Right-click an empty spot and choose **Open Terminal Here** (this opens Konsole).
5. Run:

   ```
   bash install_steamdeck.sh
   ```

6. Open the application menu, then **Utilities**, and launch **KH1 Save Editor**.

The installer copies the editor to `~/.local/share/kh1-save-editor` and adds a menu shortcut. To update later, download the new version and run the installer again.

You can also run it without installing:

```
python3 kh1_save_editor.py
```

### Where Steam Deck saves live

```
/home/deck/.local/share/Steam/steamapps/compatdata/2552430/pfx/drive_c/users/steamuser/Documents/My Games/KINGDOM HEARTS HD 1.5+2.5 ReMIX/Steam/<Steam ID>/KHFM_WW.png
```

`.local` is a hidden folder. Press **Ctrl+H** in Dolphin to show it.

---

## 4. Other Linux PCs

Install Python 3 with tkinter (for example, `sudo apt install python3-tk` on Ubuntu or Debian), then run:

```
python3 kh1_save_editor.py
```

or use `bash install_steamdeck.sh` to add a menu shortcut.

---

## 5. Check that it works (optional)

From the editor folder, run the automated tests:

```
python -m unittest discover -s tests
```

(On the Steam Deck or Linux, use `python3`.) You should see `OK` at the end.

---

## 6. Optional: add your own banner

Put a picture named `banner.png` or `banner.gif` next to `kh1_save_editor.py`, or next to `KH1_Save_Editor.exe`. It shows across the top of the window. About **1000 x 190** pixels looks best. No artwork comes with the project.

On the Steam Deck, put the banner in the folder before you run the installer, or copy it into `~/.local/share/kh1-save-editor`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Python 3 was not found" | Install Python from python.org with **Add python.exe to PATH** ticked, then reopen `run_windows.bat`. |
| `No module named tkinter` | On Windows, reinstall Python with **tcl/tk** ticked. On Linux, install `python3-tk`. |
| "No saves found" | Start the game once and save, or use **Open Save** to pick `KHFM_WW.png` yourself. |
| The window opens and closes right away | Run `python kh1_save_editor.py` from a terminal in the folder to see the error, then [open an issue](https://github.com/KatRewrites/kh1-save-editor/issues). |
| Changes don't show in-game | Make sure the game was fully closed while you saved. On Steam, Cloud Sync may restore an older save, so check Steam's conflict prompt. |

Next: read the [User Manual](USER_MANUAL.md).
