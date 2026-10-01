"""KH1 Final Mix PC Save Editor — safety-first cross-platform desktop UI.

KH1 data model ported from Xeeynamo/KingdomSaveEditor (GPL-3.0).
"""

from pathlib import Path
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from kh1_reference import EQUIPMENT, EQUIPMENT_BY_ID, KEYBLADES, WORLDS
from kh1_leveling import (
    ABILITY_NAMES,
    DREAM_POWERS,
    EXP_CURVES,
    detect_dream_power,
    simulate_leveling,
)
from kh1_save_core import (
    atomic_write_with_backup,
    compare_saves,
    discover_save_files,
    format_diff_report,
    load_save,
    rebuild_with_payload,
    update_slot,
    write_diff_reports,
)

BG = "#0d1b2a"
BG2 = "#152236"
BG3 = "#1c2e45"
ACCENT = "#f0a500"
ACCENT2 = "#4a90d9"
RED = "#e94560"
TEXT = "#e0f0ff"
DIM = "#7f9ab4"
ENTRY_BG = "#0a1628"

DIFFICULTIES = (
    "Final Mix: Beginner Mode",
    "Final Mix Mode",
    "Final Mix: Proud Mode",
)
WORLD_CHOICES = tuple(f"{world_id:02X} — {name}" for world_id, name in WORLDS)
KEYBLADE_CHOICES = tuple(
    f"{item['id']:02X} — {item['name']}" for item in KEYBLADES
)
STAFF_CHOICES = tuple(
    f"{item['id']:02X} — {item['name']}"
    for item in EQUIPMENT
    if item["category"] == "staff"
)
SHIELD_CHOICES = tuple(
    f"{item['id']:02X} — {item['name']}"
    for item in EQUIPMENT
    if item["category"] == "shield"
)
ACCESSORY_CHOICES = ("00 — Empty",) + tuple(
    f"{item['id']:02X} — {item['name']}"
    for item in EQUIPMENT
    if item["category"] == "accessory"
)
CONSUMABLE_CHOICES = ("00 — Empty",) + tuple(
    f"{item['id']:02X} — {item['name']}"
    for item in EQUIPMENT
    if item["category"] == "consumable"
)
ABILITY_CHOICES = ("00 — Empty",) + tuple(
    f"{ability_id:02X} — {name}"
    for ability_id, name in sorted(ABILITY_NAMES.items())
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KH1 Final Mix Save Editor")
        self.geometry("900x720")
        self.minsize(760, 560)
        self.configure(bg=BG)

        self.path = None
        self.container = None
        self.last_save_directory = None
        self.current_slot = 0
        self.slot_buttons = []
        self.scalar_vars = {}
        self.inventory_vars = {}
        self.keyblade_vars = {}
        self.ability_vars = []
        self.ability_equipped_vars = []
        self.sora_accessory_vars = []
        self.sora_item_vars = []
        self.party_vars = {}
        self.level_plans = {}

        self._configure_style()
        self._build_ui()

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure(
            "TLabelframe", background=BG2, foreground=ACCENT, relief="flat"
        )
        style.configure(
            "TLabelframe.Label",
            background=BG2,
            foreground=ACCENT,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure("TNotebook", background=BG)
        style.configure(
            "TNotebook.Tab", background=BG3, foreground=DIM, padding=(14, 7)
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", BG2)],
            foreground=[("selected", ACCENT)],
        )
        style.configure(
            "TCombobox",
            fieldbackground=ENTRY_BG,
            background=BG3,
            foreground=TEXT,
        )
        style.configure(
            "TSpinbox",
            fieldbackground=ENTRY_BG,
            background=BG3,
            foreground=TEXT,
            arrowcolor=ACCENT2,
        )
        style.configure(
            "Action.TButton",
            background=ACCENT2,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
        )
        style.map("Action.TButton", background=[("active", "#356fac")])
        style.configure(
            "Save.TButton",
            background=RED,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
        )
        style.map("Save.TButton", background=[("active", "#c93652")])
        style.configure("TCheckbutton", background=BG2, foreground=TEXT)

    def _build_ui(self):
        toolbar = tk.Frame(self, bg=BG, padx=12, pady=9)
        toolbar.pack(fill="x")
        tk.Label(
            toolbar,
            text="◆ KH1 Final Mix Save Editor",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")
        ttk.Button(
            toolbar, text="Save", style="Save.TButton", command=self._save
        ).pack(side="right", padx=(5, 0))
        ttk.Button(
            toolbar,
            text="Values Lab",
            style="Action.TButton",
            command=self._values_lab,
        ).pack(side="right", padx=(5, 0))
        ttk.Button(
            toolbar, text="Open Save", style="Action.TButton", command=self._open
        ).pack(side="right")
        ttk.Button(
            toolbar,
            text="Backups Folder",
            style="Action.TButton",
            command=self._open_backups_folder,
        ).pack(side="right", padx=(0, 5))
        ttk.Button(
            toolbar,
            text="Find My Saves",
            style="Action.TButton",
            command=self._find_saves,
        ).pack(side="right", padx=(0, 5))

        self.path_label = tk.Label(
            self,
            text="No file loaded",
            bg=BG2,
            fg=DIM,
            padx=12,
            pady=5,
            anchor="w",
        )
        self.path_label.pack(fill="x")

        self.slot_frame = tk.Frame(self, bg=BG, padx=8, pady=5)
        self.slot_frame.pack(fill="x")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=(0, 5))
        character = ttk.Frame(notebook)
        donald = ttk.Frame(notebook)
        goofy = ttk.Frame(notebook)
        equipment = ttk.Frame(notebook)
        inventory = ttk.Frame(notebook)
        keyblades = ttk.Frame(notebook)
        abilities = ttk.Frame(notebook)
        help_tab = ttk.Frame(notebook)
        notebook.add(character, text="Character & World")
        notebook.add(donald, text="Donald")
        notebook.add(goofy, text="Goofy")
        notebook.add(equipment, text="Equipment")
        notebook.add(inventory, text="Inventory")
        notebook.add(keyblades, text="Keyblades")
        notebook.add(abilities, text="Abilities")
        notebook.add(help_tab, text="Help")

        self._build_character_tab(character)
        self._build_party_tab(donald, 1, "Donald", STAFF_CHOICES)
        self._build_party_tab(goofy, 2, "Goofy", SHIELD_CHOICES)
        self._build_sora_equipment_tab(equipment)
        self._build_inventory_tab(inventory)
        self._build_keyblade_tab(keyblades)
        self._build_abilities_tab(abilities)
        self._build_help_tab(help_tab)

        self.status = tk.Label(
            self,
            text="Open a ZIP-preserved KHFM_WW.png to begin.",
            bg=BG2,
            fg=DIM,
            padx=9,
            pady=5,
            anchor="w",
        )
        self.status.pack(fill="x", side="bottom")

    def _scroll_frame(self, parent):
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = ttk.Frame(canvas)
        window = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>", lambda event: canvas.itemconfigure(window, width=event.width)
        )

        def wheel(event):
            amount = -1 if event.delta > 0 else 1
            canvas.yview_scroll(amount * 3, "units")

        canvas.bind("<Enter>", lambda _event: canvas.bind_all("<MouseWheel>", wheel))
        canvas.bind(
            "<Leave>", lambda _event: canvas.unbind_all("<MouseWheel>")
        )
        return inner

    def _spin(self, parent, label, key, row, column, low, high, width=11):
        tk.Label(parent, text=label, bg=BG2, fg=TEXT).grid(
            row=row, column=column * 2, padx=(8, 4), pady=4, sticky="e"
        )
        variable = tk.IntVar(value=0)
        self.scalar_vars[key] = variable
        ttk.Spinbox(
            parent, from_=low, to=high, textvariable=variable, width=width
        ).grid(row=row, column=column * 2 + 1, padx=(0, 10), pady=4, sticky="w")

    def _build_character_tab(self, parent):
        inner = self._scroll_frame(parent)
        stats = ttk.LabelFrame(inner, text="Sora — authoritative record fields")
        stats.pack(fill="x", padx=10, pady=(10, 5))
        fields = (
            ("Level", "level", 1, 100),
            ("Current HP", "hp_current", 0, 255),
            ("Base Max HP", "hp", 0, 255),
            ("Current MP", "mp_current", 0, 255),
            ("Base Max MP", "mp", 0, 255),
            ("AP", "ap", 0, 255),
            ("Strength", "strength", 0, 255),
            ("Defense", "defense", 0, 255),
            ("EXP", "exp", 0, 2147483647),
            ("Munny", "munny", 0, 99999999),
        )
        for index, (label, key, low, high) in enumerate(fields):
            self._spin(stats, label, key, index // 2, index % 2, low, high)
        ttk.Button(
            stats,
            text="Simulate Leveling…",
            style="Action.TButton",
            command=self._simulate_leveling_dialog,
        ).grid(row=5, column=0, columnspan=4, padx=8, pady=(8, 10))

        location = ttk.LabelFrame(inner, text="World position")
        location.pack(fill="x", padx=10, pady=5)
        tk.Label(location, text="World", bg=BG2, fg=TEXT).grid(
            row=0, column=0, padx=(8, 4), pady=5, sticky="e"
        )
        self.world_var = tk.StringVar()
        ttk.Combobox(
            location,
            textvariable=self.world_var,
            values=WORLD_CHOICES,
            state="readonly",
            width=30,
        ).grid(row=0, column=1, padx=(0, 12), pady=5, sticky="w")
        self._spin(location, "Room ID", "room", 1, 0, 0, 0xFFFFFFFF)
        self._spin(location, "Spawn ID", "spawn", 1, 1, 0, 0xFFFFFFFF)

        settings = ttk.LabelFrame(inner, text="Game settings")
        settings.pack(fill="x", padx=10, pady=5)
        tk.Label(settings, text="Difficulty", bg=BG2, fg=TEXT).grid(
            row=0, column=0, padx=(8, 4), pady=5, sticky="e"
        )
        self.difficulty_var = tk.StringVar()
        ttk.Combobox(
            settings,
            textvariable=self.difficulty_var,
            values=DIFFICULTIES,
            state="readonly",
            width=30,
        ).grid(row=0, column=1, padx=(0, 12), pady=5, sticky="w")
        tk.Label(
            inner,
            text=(
                "Current and base maximum HP/MP are separate in the save. "
                "Equipment bonuses can make the visible in-game maximum larger "
                "than the stored base maximum."
            ),
            bg=BG,
            fg=DIM,
            justify="left",
            wraplength=780,
        ).pack(fill="x", padx=14, pady=(5, 12))

    def _build_inventory_tab(self, parent):
        inner = self._scroll_frame(parent)
        categories = (
            "consumable",
            "boost",
            "synthesis",
            "accessory",
            "recipe",
            "report",
            "keyitem",
            "summon",
        )
        for category in categories:
            items = [item for item in EQUIPMENT if item["category"] == category]
            frame = ttk.LabelFrame(inner, text=category.replace("keyitem", "key item").title())
            frame.pack(fill="x", padx=10, pady=(10, 3))
            for index, item in enumerate(items):
                row, column = divmod(index, 2)
                tk.Label(
                    frame,
                    text=f"{item['name']}  [{item['id']:02X}]",
                    bg=BG2,
                    fg=TEXT,
                    width=24,
                    anchor="e",
                ).grid(
                    row=row,
                    column=column * 2,
                    padx=(5, 4),
                    pady=2,
                    sticky="e",
                )
                variable = tk.IntVar(value=0)
                self.inventory_vars[item["id"]] = variable
                ttk.Spinbox(
                    frame, from_=0, to=99, textvariable=variable, width=6
                ).grid(
                    row=row,
                    column=column * 2 + 1,
                    padx=(0, 12),
                    pady=2,
                    sticky="w",
                )

    def _build_equipped_slots(self, parent, title, choices, count, variables):
        frame = ttk.LabelFrame(parent, text=title)
        frame.pack(fill="x", padx=10, pady=5)
        for index in range(count):
            variable = tk.StringVar(value=choices[0])
            variables.append(variable)
            tk.Label(
                frame,
                text=f"{index + 1:02d}",
                bg=BG2,
                fg=ACCENT,
                width=3,
            ).grid(
                row=index // 2,
                column=(index % 2) * 2,
                padx=(8, 4),
                pady=3,
                sticky="e",
            )
            ttk.Combobox(
                frame,
                textvariable=variable,
                values=choices,
                state="readonly",
                width=27,
            ).grid(
                row=index // 2,
                column=(index % 2) * 2 + 1,
                padx=(0, 12),
                pady=3,
                sticky="w",
            )

    def _build_sora_equipment_tab(self, parent):
        inner = self._scroll_frame(parent)
        weapon = ttk.LabelFrame(inner, text="Sora Weapon")
        weapon.pack(fill="x", padx=10, pady=(10, 5))
        self.sora_equipment_weapon_var = tk.StringVar()
        ttk.Combobox(
            weapon,
            textvariable=self.sora_equipment_weapon_var,
            values=KEYBLADE_CHOICES,
            state="readonly",
            width=34,
        ).pack(anchor="w", padx=12, pady=9)
        self._build_equipped_slots(
            inner,
            "Equipped Accessories — save capacity controls active slots",
            ACCESSORY_CHOICES,
            8,
            self.sora_accessory_vars,
        )
        self._build_equipped_slots(
            inner,
            "Carried Battle Items — save capacity controls active slots",
            CONSUMABLE_CHOICES,
            12,
            self.sora_item_vars,
        )

    def _build_party_tab(self, parent, character_index, name, weapon_choices):
        inner = self._scroll_frame(parent)
        state = {
            "stats": {},
            "weapon": tk.StringVar(),
            "accessories": [],
            "items": [],
            "abilities": [],
            "equipped": [],
        }
        self.party_vars[character_index] = state

        stats = ttk.LabelFrame(inner, text=f"{name} Stats")
        stats.pack(fill="x", padx=10, pady=(10, 5))
        fields = (
            ("Level", "level", 1, 255),
            ("Current HP", "hp_current", 0, 255),
            ("Base Max HP", "hp", 0, 255),
            ("Current MP", "mp_current", 0, 255),
            ("Base Max MP", "mp", 0, 255),
            ("AP", "ap", 0, 255),
            ("Strength", "strength", 0, 255),
            ("Defense", "defense", 0, 255),
            ("EXP", "exp", 0, 2147483647),
        )
        for field_index, (label, key, low, high) in enumerate(fields):
            row, column = divmod(field_index, 2)
            tk.Label(stats, text=label, bg=BG2, fg=TEXT).grid(
                row=row,
                column=column * 2,
                padx=(8, 4),
                pady=4,
                sticky="e",
            )
            variable = tk.IntVar(value=0)
            state["stats"][key] = variable
            ttk.Spinbox(
                stats,
                from_=low,
                to=high,
                textvariable=variable,
                width=11,
            ).grid(
                row=row,
                column=column * 2 + 1,
                padx=(0, 10),
                pady=4,
                sticky="w",
            )

        weapon = ttk.LabelFrame(inner, text=f"{name} Weapon")
        weapon.pack(fill="x", padx=10, pady=5)
        ttk.Combobox(
            weapon,
            textvariable=state["weapon"],
            values=weapon_choices,
            state="readonly",
            width=34,
        ).pack(anchor="w", padx=12, pady=9)
        self._build_equipped_slots(
            inner,
            f"{name} Accessories",
            ACCESSORY_CHOICES,
            8,
            state["accessories"],
        )
        self._build_equipped_slots(
            inner,
            f"{name} Carried Battle Items",
            CONSUMABLE_CHOICES,
            12,
            state["items"],
        )

        abilities = ttk.LabelFrame(inner, text=f"{name} Ability Slots")
        abilities.pack(fill="x", padx=10, pady=5)
        for ability_index in range(48):
            group = ability_index % 2
            row = ability_index // 2
            ability_var = tk.StringVar(value=ABILITY_CHOICES[0])
            equipped_var = tk.BooleanVar(value=False)
            state["abilities"].append(ability_var)
            state["equipped"].append(equipped_var)
            tk.Label(
                abilities,
                text=f"{ability_index + 1:02d}",
                bg=BG2,
                fg=ACCENT,
                width=3,
            ).grid(
                row=row,
                column=group * 3,
                padx=(7, 4),
                pady=3,
                sticky="e",
            )
            ttk.Combobox(
                abilities,
                textvariable=ability_var,
                values=ABILITY_CHOICES,
                state="readonly",
                width=24,
            ).grid(
                row=row,
                column=group * 3 + 1,
                padx=(0, 4),
                pady=3,
                sticky="w",
            )
            ttk.Checkbutton(
                abilities,
                text="Equipped",
                variable=equipped_var,
            ).grid(
                row=row,
                column=group * 3 + 2,
                padx=(0, 10),
                pady=3,
                sticky="w",
            )

    def _build_keyblade_tab(self, parent):
        inner = self._scroll_frame(parent)
        equipped = ttk.LabelFrame(inner, text="Equipped Keyblade")
        equipped.pack(fill="x", padx=10, pady=(10, 5))
        self.weapon_var = tk.StringVar()
        ttk.Combobox(
            equipped,
            textvariable=self.weapon_var,
            values=KEYBLADE_CHOICES,
            state="readonly",
            width=34,
        ).pack(anchor="w", padx=12, pady=9)

        owned = ttk.LabelFrame(inner, text="Owned Keyblades")
        owned.pack(fill="x", padx=10, pady=5)
        for index, item in enumerate(KEYBLADES):
            variable = tk.BooleanVar(value=False)
            self.keyblade_vars[item["id"]] = variable
            ttk.Checkbutton(
                owned,
                text=f"{item['name']}  [{item['id']:02X}]",
                variable=variable,
            ).grid(
                row=index // 2,
                column=index % 2,
                padx=12,
                pady=4,
                sticky="w",
            )

    def _build_abilities_tab(self, parent):
        inner = self._scroll_frame(parent)
        tk.Label(
            inner,
            text=(
                "KH1 stores 48 ordered ability slots and permits duplicates. "
                "Equipped sets the save's 0x80 flag; make sure Sora has enough "
                "AP for every ability you equip."
            ),
            bg=BG,
            fg=DIM,
            justify="left",
            wraplength=790,
        ).pack(fill="x", padx=14, pady=(10, 5))
        frame = ttk.LabelFrame(inner, text="Sora Ability Slots")
        frame.pack(fill="x", padx=10, pady=(5, 12))
        for index in range(48):
            group = index % 2
            row = index // 2
            tk.Label(
                frame,
                text=f"{index + 1:02d}",
                bg=BG2,
                fg=ACCENT,
                width=3,
                anchor="e",
            ).grid(
                row=row,
                column=group * 3,
                padx=(7, 4),
                pady=3,
                sticky="e",
            )
            ability_var = tk.StringVar(value=ABILITY_CHOICES[0])
            equipped_var = tk.BooleanVar(value=False)
            self.ability_vars.append(ability_var)
            self.ability_equipped_vars.append(equipped_var)
            ttk.Combobox(
                frame,
                textvariable=ability_var,
                values=ABILITY_CHOICES,
                state="readonly",
                width=24,
            ).grid(
                row=row,
                column=group * 3 + 1,
                padx=(0, 4),
                pady=3,
                sticky="w",
            )
            ttk.Checkbutton(
                frame,
                text="Equipped",
                variable=equipped_var,
            ).grid(
                row=row,
                column=group * 3 + 2,
                padx=(0, 10),
                pady=3,
                sticky="w",
            )

    def _build_help_tab(self, parent):
        text = tk.Text(
            parent,
            bg=BG2,
            fg=TEXT,
            wrap="word",
            relief="flat",
            padx=16,
            pady=14,
        )
        text.pack(fill="both", expand=True, padx=8, pady=8)
        text.insert(
            "1.0",
            """KH1 FINAL MIX SAVE EDITOR

Open KHFM_WW.png from the Steam, Epic, or Re:Fined save folder. Always preserve
the original custom PNG chunk when transferring the file; ZIP it before upload.

SAFETY
• A timestamped backup is created before every write.
• Output is written atomically.
• Every PNG chunk CRC is validated before and after editing.
• The editor reparses the completed output before reporting success.
• Values Lab compares two files without modifying either one.
• Direct Level-only changes are refused. Use Simulate Leveling so stats, EXP,
  and learned abilities stay synchronized.

SIMULATED LEVELING
Choose Sora's original Dream Sword, Staff, or Shield path and the Dawn, Midday,
or Dusk EXP curve. The simulator adds only missed natural stat increases, so
stat boosts already used are preserved. Missed abilities are added as owned and
unequipped in the same 48-slot array shown on the Abilities tab.

CHARACTERS AND EQUIPMENT
The Equipment tab edits Sora's Keyblade, equipped accessories, and carried
battle items. Donald and Goofy have their own tabs with stats, EXP, weapons,
accessories, carried items, and abilities. Donald is restricted to staffs,
Goofy to shields, and Sora to Keyblades.

REFERENCE MODEL
The KH1 record layout and equipment/world tables are ported from
Xeeynamo/KingdomSaveEditor under GPL-3.0. Steam/Epic archive handling and the
safety checks in this application are implemented independently.

WORLD WARNING
Changing only the world may place Sora into an invalid room or spawn. Prefer
changing World, Room, and Spawn together using values from a real save made at
the destination.
""",
        )
        text.configure(state="disabled")

    def _open(self):
        discovered = discover_save_files()
        initial_directory = self.last_save_directory
        if not initial_directory and discovered:
            initial_directory = str(discovered[0].parent)
        if not initial_directory:
            initial_directory = str(Path.home())
        path = self._choose_save_file(
            "Open KH1 Final Mix save", initial_directory
        )
        if not path:
            return
        self._load_path(path)

    def _choose_save_file(self, title, initial_directory=None):
        """Use KDE's native picker on Steam Deck, with Tk as a fallback."""
        kdialog = shutil.which("kdialog")
        if os.name != "nt" and kdialog:
            start = str(Path(initial_directory or Path.home()) / "KHFM_WW.png")
            result = subprocess.run(
                [
                    kdialog,
                    "--title",
                    title,
                    "--getopenfilename",
                    start,
                    "*.png|Kingdom Hearts PNG saves",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return ""
        return filedialog.askopenfilename(
            title=title,
            initialdir=initial_directory or str(Path.home()),
            initialfile="KHFM_WW.png",
            filetypes=(("KH1 PNG saves", "*.png"), ("All files", "*.*")),
        )

    def _open_backups_folder(self):
        if not self.path:
            messagebox.showwarning(
                "No save loaded",
                "Open a save first so the editor knows which backup folder to use.",
            )
            return
        backup_folder = Path(self.path).parent / "KH1_Save_Editor_Backups"
        backup_folder.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(str(backup_folder))
            elif shutil.which("kioclient5"):
                subprocess.Popen(["kioclient5", "exec", str(backup_folder)])
            elif shutil.which("kioclient"):
                subprocess.Popen(["kioclient", "exec", str(backup_folder)])
            elif shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", str(backup_folder)])
            elif shutil.which("open"):
                subprocess.Popen(["open", str(backup_folder)])
            else:
                raise RuntimeError("No desktop folder opener was found.")
            self.status.configure(text=f"Opened backups: {backup_folder}")
        except Exception as error:
            messagebox.showerror(
                "Cannot open backups",
                f"{error}\n\nBackup folder:\n{backup_folder}",
            )

    def _load_path(self, path):
        try:
            container = load_save(path)
        except Exception as error:
            messagebox.showerror("Cannot open save", str(error))
            return
        self.path = path
        self.last_save_directory = str(Path(path).parent)
        self.container = container
        self.level_plans.clear()
        self.current_slot = 0
        self.path_label.configure(text=path)
        self._rebuild_slot_buttons()
        self._load_slot(0)
        self.status.configure(
            text=f"Loaded {len(container.slots)} KH1 save slot(s)."
        )

    def _find_saves(self):
        saves = discover_save_files()
        if not saves:
            messagebox.showinfo(
                "No saves found",
                "No KHFM_WW.png was found in the known Steam, Epic, Re:Fined, "
                "OneDrive, or Steam Deck Proton locations.\n\n"
                "You can still use Open Save to select it manually.",
            )
            return
        if len(saves) == 1:
            self._load_path(str(saves[0]))
            return

        chooser = tk.Toplevel(self)
        chooser.title("Choose KH1 save")
        chooser.geometry("760x340")
        chooser.configure(bg=BG)
        chooser.transient(self)
        chooser.grab_set()
        tk.Label(
            chooser,
            text="Found multiple KHFM_WW.png files. Newest files are listed first.",
            bg=BG,
            fg=TEXT,
            padx=12,
            pady=10,
            anchor="w",
        ).pack(fill="x")
        listbox = tk.Listbox(
            chooser,
            bg=ENTRY_BG,
            fg=TEXT,
            selectbackground=ACCENT2,
            font=("Consolas", 9),
        )
        listbox.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        for save in saves:
            listbox.insert("end", str(save))
        listbox.selection_set(0)

        def open_selected(_event=None):
            selection = listbox.curselection()
            if not selection:
                return
            path = saves[selection[0]]
            chooser.destroy()
            self._load_path(str(path))

        buttons = tk.Frame(chooser, bg=BG, padx=12, pady=(0, 10))
        buttons.pack(fill="x")
        ttk.Button(
            buttons, text="Open Selected", style="Action.TButton", command=open_selected
        ).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=chooser.destroy).pack(
            side="right", padx=(0, 6)
        )
        listbox.bind("<Double-Button-1>", open_selected)

    def _rebuild_slot_buttons(self):
        for button in self.slot_buttons:
            button.destroy()
        self.slot_buttons.clear()
        for index, slot in enumerate(self.container.slots):
            world = dict(WORLDS).get(slot["world"], f"World {slot['world']:X}")
            button = tk.Button(
                self.slot_frame,
                text=f"Slot {index + 1}: {world} (LV {slot['level']})",
                bg=BG3,
                fg=TEXT,
                relief="flat",
                padx=10,
                pady=5,
                command=lambda selected=index: self._load_slot(selected),
            )
            button.pack(side="left", padx=(0, 5))
            self.slot_buttons.append(button)

    def _load_slot(self, index):
        self.current_slot = index
        slot = self.container.slots[index]
        for button_index, button in enumerate(self.slot_buttons):
            button.configure(
                bg=ACCENT2 if button_index == index else BG3,
                fg="white" if button_index == index else TEXT,
            )
        for key in (
            "level",
            "hp_current",
            "hp",
            "mp_current",
            "mp",
            "ap",
            "strength",
            "defense",
            "exp",
            "munny",
            "room",
            "spawn",
        ):
            self.scalar_vars[key].set(slot[key])
        self.world_var.set(
            next(
                (choice for choice in WORLD_CHOICES if choice.startswith(f"{slot['world']:02X}")),
                "",
            )
        )
        difficulty = slot["difficulty"]
        self.difficulty_var.set(
            DIFFICULTIES[difficulty] if difficulty < len(DIFFICULTIES) else ""
        )
        weapon = slot["weapon"]
        self.weapon_var.set(
            next(
                (choice for choice in KEYBLADE_CHOICES if choice.startswith(f"{weapon:02X}")),
                "",
            )
        )
        self.sora_equipment_weapon_var.set(self.weapon_var.get())
        for item_id, variable in self.inventory_vars.items():
            variable.set(slot["inventory"][item_id])
        for item_id, variable in self.keyblade_vars.items():
            variable.set(slot["inventory"][item_id] > 0)
        for ability_index, raw_value in enumerate(slot["abilities"]):
            ability_id = raw_value & 0x7F
            name = ABILITY_NAMES.get(ability_id)
            choice = (
                f"{ability_id:02X} — {name}"
                if name is not None
                else ABILITY_CHOICES[0]
            )
            self.ability_vars[ability_index].set(choice)
            self.ability_equipped_vars[ability_index].set(
                bool(raw_value & 0x80) and ability_id != 0
            )
        sora = slot["characters"][0]
        for variable, item_id in zip(
            self.sora_accessory_vars, sora["accessories"]
        ):
            item = EQUIPMENT_BY_ID.get(item_id)
            variable.set(
                f"{item_id:02X} — {item['name']}"
                if item_id and item and item["category"] == "accessory"
                else ACCESSORY_CHOICES[0]
            )
        for variable, item_id in zip(self.sora_item_vars, sora["items"]):
            item = EQUIPMENT_BY_ID.get(item_id)
            variable.set(
                f"{item_id:02X} — {item['name']}"
                if item_id and item and item["category"] == "consumable"
                else CONSUMABLE_CHOICES[0]
            )
        for character_index in (1, 2):
            character = slot["characters"][character_index]
            state = self.party_vars[character_index]
            for key, variable in state["stats"].items():
                variable.set(character[key])
            weapon_id = character["weapon"]
            weapon_item = EQUIPMENT_BY_ID.get(weapon_id)
            state["weapon"].set(
                f"{weapon_id:02X} — {weapon_item['name']}"
                if weapon_item is not None
                else ""
            )
            for variable, item_id in zip(
                state["accessories"], character["accessories"]
            ):
                item = EQUIPMENT_BY_ID.get(item_id)
                variable.set(
                    f"{item_id:02X} — {item['name']}"
                    if item_id and item and item["category"] == "accessory"
                    else ACCESSORY_CHOICES[0]
                )
            for variable, item_id in zip(state["items"], character["items"]):
                item = EQUIPMENT_BY_ID.get(item_id)
                variable.set(
                    f"{item_id:02X} — {item['name']}"
                    if item_id and item and item["category"] == "consumable"
                    else CONSUMABLE_CHOICES[0]
                )
            for ability_index, raw_value in enumerate(character["abilities"]):
                ability_id = raw_value & 0x7F
                name = ABILITY_NAMES.get(ability_id)
                state["abilities"][ability_index].set(
                    f"{ability_id:02X} — {name}"
                    if name is not None
                    else ABILITY_CHOICES[0]
                )
                state["equipped"][ability_index].set(
                    bool(raw_value & 0x80) and ability_id != 0
                )
        plan = self.level_plans.get(index)
        if plan:
            for key, value in plan["changes"].items():
                if key in self.scalar_vars:
                    self.scalar_vars[key].set(value)
            empty_slots = [
                slot_index
                for slot_index, variable in enumerate(self.ability_vars)
                if int(variable.get().split(" ", 1)[0], 16) == 0
            ]
            if len(plan["abilities"]) <= len(empty_slots):
                for slot_index, ability_id in zip(empty_slots, plan["abilities"]):
                    self.ability_vars[slot_index].set(
                        f"{ability_id:02X} — {ABILITY_NAMES[ability_id]}"
                    )
                    self.ability_equipped_vars[slot_index].set(False)

    def _simulate_leveling_dialog(self):
        if not self.container:
            messagebox.showwarning("No save loaded", "Open your backup save first.")
            return
        slot = self.container.slots[self.current_slot]
        if slot["level"] >= 99:
            messagebox.showwarning(
                "Backup required",
                "This slot already says level 99 or 100. Load the unmodified "
                "backup containing your real level before simulating.",
            )
            return

        detected, diagnostics = detect_dream_power(
            slot["abilities"], slot["level"]
        )
        window = tk.Toplevel(self)
        window.title("Simulate KH1 Leveling")
        window.geometry("520x390")
        window.resizable(False, False)
        window.configure(bg=BG)
        window.transient(self)
        window.grab_set()

        tk.Label(
            window,
            text=f"Simulate Sora from level {slot['level']}",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", padx=18, pady=(16, 5))
        match = diagnostics[detected]
        tk.Label(
            window,
            text=(
                f"Ability-table detection: {detected} "
                f"({match['matched']}/{match['expected']} expected abilities found)"
            ),
            bg=BG,
            fg=DIM,
        ).pack(anchor="w", padx=18, pady=(0, 14))

        form = tk.Frame(window, bg=BG2, padx=14, pady=12)
        form.pack(fill="x", padx=18)
        power_var = tk.StringVar(value=detected)
        curve_var = tk.StringVar(value="Midday")
        target_var = tk.IntVar(value=99)
        for row, (label, variable, values) in enumerate(
            (
                ("Dream power", power_var, DREAM_POWERS),
                ("EXP curve", curve_var, EXP_CURVES),
                ("Target level", target_var, (99, 100)),
            )
        ):
            tk.Label(form, text=label, bg=BG2, fg=TEXT).grid(
                row=row, column=0, padx=(0, 10), pady=6, sticky="e"
            )
            ttk.Combobox(
                form,
                textvariable=variable,
                values=values,
                state="readonly",
                width=24,
            ).grid(row=row, column=1, pady=6, sticky="w")

        tk.Label(
            window,
            text=(
                "Choose the same Dream power and question-result curve used "
                "when this playthrough began. Every missing natural level-up "
                "ability through the target will be restored unequipped. Both "
                "internal level records and existing stat boosts are preserved."
            ),
            bg=BG,
            fg=TEXT,
            justify="left",
            wraplength=470,
        ).pack(fill="x", padx=18, pady=14)

        def apply_plan():
            try:
                plan = simulate_leveling(
                    slot,
                    int(target_var.get()),
                    power_var.get(),
                    curve_var.get(),
                )
            except Exception as error:
                messagebox.showerror("Cannot simulate", str(error), parent=window)
                return
            self.level_plans[self.current_slot] = plan
            self._load_slot(self.current_slot)
            window.destroy()
            self.status.configure(
                text=(
                    f"Level {plan['target_level']} simulation ready: "
                    f"{len(plan['abilities'])} missed abilities will be added. "
                    "Press Save to write it with a backup."
                )
            )
            messagebox.showinfo(
                "Simulation ready",
                f"Level {plan['source_level']} → {plan['target_level']}\n"
                f"Dream {plan['dream_power']} / {plan['exp_curve']}\n"
                f"Missing abilities restored: {len(plan['abilities'])}\n\n"
                "Review the displayed stats, then press Save.",
            )

        buttons = tk.Frame(window, bg=BG, padx=18, pady=12)
        buttons.pack(fill="x")
        ttk.Button(
            buttons,
            text="Prepare Simulation",
            style="Action.TButton",
            command=apply_plan,
        ).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=window.destroy).pack(
            side="right", padx=(0, 7)
        )

    def _collect_changes(self):
        slot = self.container.slots[self.current_slot]
        plan = self.level_plans.get(self.current_slot)
        displayed_level = self.scalar_vars["level"].get()
        if displayed_level != slot["level"] and not plan:
            raise ValueError(
                "Direct Level-only editing is unsafe. Restore the original "
                "level and use Simulate Leveling instead."
            )
        if plan and displayed_level != plan["target_level"]:
            raise ValueError(
                "The simulated target level was changed manually. Run "
                "Simulate Leveling again."
            )
        changes = {}
        for key, variable in self.scalar_vars.items():
            value = variable.get()
            if value != slot[key]:
                changes[key] = value

        world = int(self.world_var.get().split(" ", 1)[0], 16)
        if world != slot["world"]:
            changes["world"] = world
        difficulty = DIFFICULTIES.index(self.difficulty_var.get())
        if difficulty != slot["difficulty"]:
            changes["difficulty"] = difficulty
        keyblade_weapon = int(self.weapon_var.get().split(" ", 1)[0], 16)
        equipment_weapon = int(
            self.sora_equipment_weapon_var.get().split(" ", 1)[0], 16
        )
        if (
            keyblade_weapon != slot["weapon"]
            and equipment_weapon != slot["weapon"]
            and keyblade_weapon != equipment_weapon
        ):
            raise ValueError(
                "Sora's weapon differs between the Keyblades and Equipment tabs."
            )
        weapon = (
            equipment_weapon
            if equipment_weapon != slot["weapon"]
            else keyblade_weapon
        )
        if weapon != slot["weapon"]:
            changes["weapon"] = weapon

        inventory = {}
        for item_id, variable in self.inventory_vars.items():
            value = variable.get()
            if value != slot["inventory"][item_id]:
                inventory[item_id] = value
        for item_id, variable in self.keyblade_vars.items():
            value = 1 if variable.get() else 0
            if value != slot["inventory"][item_id]:
                inventory[item_id] = value
        if inventory:
            changes["inventory"] = inventory
        abilities = []
        for slot_index, (ability_var, equipped_var) in enumerate(
            zip(self.ability_vars, self.ability_equipped_vars)
        ):
            ability_id = int(ability_var.get().split(" ", 1)[0], 16)
            if equipped_var.get() and ability_id == 0:
                raise ValueError(
                    f"Ability slot {slot_index + 1} is empty but marked Equipped."
                )
            abilities.append(
                ability_id | (0x80 if equipped_var.get() and ability_id else 0)
            )
        if abilities != slot["abilities"]:
            changes["abilities_replace"] = abilities

        character_updates = {}
        sora = slot["characters"][0]
        sora_accessories = [
            int(variable.get().split(" ", 1)[0], 16)
            for variable in self.sora_accessory_vars
        ]
        sora_items = [
            int(variable.get().split(" ", 1)[0], 16)
            for variable in self.sora_item_vars
        ]
        sora_fields = {}
        if sora_accessories != sora["accessories"]:
            sora_fields["accessories"] = sora_accessories
        if sora_items != sora["items"]:
            sora_fields["items"] = sora_items
        if sora_fields:
            character_updates[0] = sora_fields

        for character_index in (1, 2):
            original = slot["characters"][character_index]
            state = self.party_vars[character_index]
            fields = {}
            for key, variable in state["stats"].items():
                value = variable.get()
                if value != original[key]:
                    fields[key] = value
            weapon_id = int(state["weapon"].get().split(" ", 1)[0], 16)
            if weapon_id != original["weapon"]:
                fields["weapon"] = weapon_id
            accessories = [
                int(variable.get().split(" ", 1)[0], 16)
                for variable in state["accessories"]
            ]
            if accessories != original["accessories"]:
                fields["accessories"] = accessories
            items = [
                int(variable.get().split(" ", 1)[0], 16)
                for variable in state["items"]
            ]
            if items != original["items"]:
                fields["items"] = items
            party_abilities = []
            for ability_index, (ability_var, equipped_var) in enumerate(
                zip(state["abilities"], state["equipped"])
            ):
                ability_id = int(ability_var.get().split(" ", 1)[0], 16)
                if ability_id == 0 and equipped_var.get():
                    raise ValueError(
                        f"Character {character_index} ability slot "
                        f"{ability_index + 1} is empty but equipped."
                    )
                party_abilities.append(
                    ability_id | (0x80 if equipped_var.get() and ability_id else 0)
                )
            if party_abilities != original["abilities"]:
                fields["abilities"] = party_abilities
            if fields:
                character_updates[character_index] = fields
        if character_updates:
            changes["character_updates"] = character_updates
        return changes

    def _save(self):
        if not self.path or not self.container:
            messagebox.showwarning("No save loaded", "Open a save first.")
            return
        try:
            changes = self._collect_changes()
            if not changes:
                messagebox.showinfo("No changes", "Nothing changed in this slot.")
                return
            payload = bytearray(self.container.payload)
            update_slot(payload, self.container.slots[self.current_slot], changes)
            rebuilt = rebuild_with_payload(self.container, payload)
            backup = atomic_write_with_backup(self.path, rebuilt)
            self.container = load_save(self.path)
            self.level_plans.pop(self.current_slot, None)
            self._rebuild_slot_buttons()
            self._load_slot(self.current_slot)
            self.status.configure(
                text=f"Saved and verified. Backup: {backup.name}"
            )
            messagebox.showinfo(
                "Saved safely",
                f"Changes written and reparsed successfully.\n\nBackup:\n{backup}",
            )
        except Exception as error:
            messagebox.showerror("Save refused", str(error))

    def _values_lab(self):
        before = self._choose_save_file(
            "Values Lab — select BEFORE save",
            self.last_save_directory,
        )
        if not before:
            return
        after = self._choose_save_file(
            "Values Lab — select AFTER save",
            str(Path(before).parent),
        )
        if not after:
            return
        try:
            report = compare_saves(before, after)
            default = Path(after).with_name(f"{Path(after).stem}_values_diff.txt")
            output = filedialog.asksaveasfilename(
                title="Save Values Lab report",
                initialfile=default.name,
                defaultextension=".txt",
                filetypes=(("Text report", "*.txt"),),
            )
            if not output:
                return
            text_path = Path(output)
            json_path = text_path.with_suffix(".json")
            write_diff_reports(report, text_path, json_path)
            preview = format_diff_report(report)
            self.status.configure(
                text=f"Values Lab found {report['changed_byte_count']} changed byte(s)."
            )
            messagebox.showinfo(
                "Values Lab complete",
                f"{preview[:800]}\n\nReports:\n{text_path}\n{json_path}",
            )
        except Exception as error:
            messagebox.showerror("Comparison failed", str(error))


if __name__ == "__main__":
    App().mainloop()
