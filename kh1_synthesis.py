"""KH1 Final Mix item synthesis recipes and checklist math.

Recipe data comes from the KH Wiki "Moogle Shop" article, Kingdom Hearts
Final Mix section (https://www.khwiki.com/Moogle_Shop). Item names match
kh1_reference so counts can be read straight from the save inventory.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# (item, synthesis list number, ((material, quantity), ...))
RECIPES = (
    ("Mega-Potion", 1, (("Spirit Shard", 1), ("Power Shard", 1), ("Mythril Shard", 4),)),
    ("Cottage", 1, (("Lucid Shard", 1), ("Bright Shard", 1),)),
    ("Energy Bangle", 1, (("Spirit Shard", 2), ("Bright Shard", 1),)),
    ("Power Chain", 1, (("Power Shard", 2), ("Lucid Shard", 1),)),
    ("Magic Armlet", 1, (("Blaze Shard", 3), ("Frost Shard", 3), ("Thunder Shard", 3),)),
    ("EXP Earring", 1, (("Fury Stone", 1), ("Power Stone", 1), ("Mythril Stone", 1), ("Serenity Power", 1), ("Dark Matter", 3),)),
    ("Mega-Ether", 2, (("Blaze Shard", 1), ("Frost Shard", 1), ("Thunder Shard", 1), ("Mythril", 2),)),
    ("Guard Earring", 2, (("Bright Shard", 3), ("Frost Shard", 1), ("Mythril Shard", 3),)),
    ("Angel Bangle", 2, (("Thunder Shard", 3), ("Bright Gem", 1),)),
    ("Golem Chain", 2, (("Blaze Shard", 3), ("Spirit Gem", 1),)),
    ("Rune Armlet", 2, (("Blaze Gem", 3), ("Frost Gem", 3), ("Thunder Gem", 3),)),
    ("Moogle Badge", 2, (("Blazing Stone", 1), ("Frost Stone", 1), ("Lightning Stone", 1), ("Mythril", 5), ("Orichalcum", 3),)),
    ("AP Up", 3, (("Blaze Gem", 2), ("Frost Gem", 2), ("Thunder Gem", 2), ("Mythril", 4),)),
    ("Dark Ring", 3, (("Lucid Gem", 2), ("Bright Gem", 2),)),
    ("Master Earring", 3, (("Spirit Shard", 5), ("Spirit Gem", 3), ("Fury Stone", 1),)),
    ("Gaia Bangle", 3, (("Lucid Shard", 5), ("Lucid Gem", 3), ("Lightning Stone", 1),)),
    ("Titan Chain", 3, (("Power Shard", 5), ("Power Gem", 3), ("Power Stone", 1),)),
    ("Mythril", 3, (("Mythril Shard", 5), ("Mythril Stone", 1), ("Mystery Goo", 1),)),
    ("Elixir", 4, (("Power Crystal", 1), ("Shiny Crystal", 1), ("Bright Crystal", 2), ("Orichalcum", 3),)),
    ("Defense Up", 4, (("Lucid Shard", 3), ("Bright Shard", 3), ("Bright Gem", 2), ("Power Crystal", 1), ("Orichalcum", 5),)),
    ("Heartguard", 4, (("Lucid Gem", 3), ("Lucid Crystal", 1), ("Bright Crystal", 1),)),
    ("Three Stars", 4, (("Power Gem", 5), ("Mystery Goo", 3), ("Shiny Crystal", 1),)),
    ("Atlas Armlet", 4, (("Blaze Shard", 5), ("Frost Shard", 5), ("Thunder Shard", 5), ("Mystery Goo", 1), ("Dark Matter", 3),)),
    ("Crystal Crown", 4, (("Lucid Crystal", 5), ("Power Crystal", 1), ("Shiny Crystal", 1), ("Blazing Stone", 3), ("Frost Stone", 3),)),
    ("Megalixir", 5, (("Lucid Gem", 5), ("Lucid Crystal", 3), ("Gale", 2), ("Dark Matter", 1),)),
    ("Power Up", 5, (("Spirit Shard", 5), ("Spirit Gem", 3), ("Power Shard", 5), ("Power Gem", 3), ("Dark Matter", 1),)),
    ("Cosmic Arts", 5, (("Bright Shard", 5), ("Bright Gem", 3), ("Bright Crystal", 1), ("Mythril Stone", 3),)),
    ("EXP Bracelet", 5, (("Energy Stone", 1), ("Dazzling Stone", 1), ("Stormy Stone", 1), ("Orichalcum", 8), ("Dark Matter", 3),)),
    ("Ribbon", 5, (("Blaze Gem", 5), ("Frost Gem", 5), ("Thunder Gem", 5), ("Gale", 1), ("Serenity Power", 3),)),
    ("Dark Matter", 5, (("Lucid Shard", 9), ("Gale", 1), ("Mythril", 2),)),
    ("Fantasista", 6, (("Fury Stone", 3), ("Power Stone", 3), ("Mythril Stone", 3), ("Energy Stone", 5),)),
    ("Seven Elements", 6, (("Blazing Stone", 3), ("Frost Stone", 3), ("Lightning Stone", 3), ("Dazzling Stone", 5),)),
    ("Ultima Weapon", 6, (("Thunder Gem", 5), ("Mystery Goo", 5), ("Serenity Power", 3), ("Stormy Stone", 3), ("Dark Matter", 3),)),
)

LIST_NAMES = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}

# Unique items that must already be synthesized before each list opens.
LIST_UNLOCKS = {1: 0, 2: 3, 3: 9, 4: 15, 5: 21, 6: 30}

ULTIMA = "Ultima Weapon"
ULTIMA_REQUIREMENT = 30  # every item on Lists I-V
ENCOUNTER_PLUS_AT = 15


def recipe_status(materials, owned: dict) -> dict:
    """Return have/need/short for one recipe given owned counts by name."""
    rows = []
    for name, need in materials:
        have = int(owned.get(name, 0))
        rows.append({"material": name, "need": need, "have": have,
                     "short": max(0, need - have)})
    return {"rows": rows, "ready": all(row["short"] == 0 for row in rows)}


def progress(made: set[str]) -> dict:
    """Checklist progress toward Ultima Weapon."""
    lists_one_to_five = {name for name, number, _ in RECIPES if number <= 5}
    count = len(made & lists_one_to_five)
    unlocked = max(n for n, need in LIST_UNLOCKS.items() if count >= need)
    next_list = next(
        (n for n in sorted(LIST_UNLOCKS) if LIST_UNLOCKS[n] > count), None
    )
    return {
        "made": count,
        "total": len(lists_one_to_five),
        "highest_list": unlocked,
        "next_list": next_list,
        "next_needs": LIST_UNLOCKS[next_list] - count if next_list else 0,
        "ultima_unlocked": count >= ULTIMA_REQUIREMENT,
        "ultima_made": ULTIMA in made,
        "encounter_plus": len(made) >= ENCOUNTER_PLUS_AT,
    }


def remaining_materials(made: set[str], owned: dict) -> list[dict]:
    """Total materials needed to make one of every unchecked item."""
    totals: dict[str, int] = {}
    for name, _number, materials in RECIPES:
        if name in made:
            continue
        for material, quantity in materials:
            totals[material] = totals.get(material, 0) + quantity
    rows = []
    for material, need in totals.items():
        have = int(owned.get(material, 0))
        rows.append({"material": material, "need": need, "have": have,
                     "short": max(0, need - have)})
    rows.sort(key=lambda row: (-row["short"], row["material"]))
    return rows


def checklist_path() -> Path:
    if os.name == "nt" and os.environ.get("APPDATA"):
        base = Path(os.environ["APPDATA"]) / "KH1_Save_Editor"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        base = base / "kh1_save_editor"
    return base / "synthesis_checklist.json"


def load_checklist(key: str, path: Path | None = None) -> set[str]:
    path = path or checklist_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    valid = {name for name, _n, _m in RECIPES}
    return {name for name in data.get(key, []) if name in valid}


def save_checklist(key: str, made: set[str], path: Path | None = None) -> None:
    path = path or checklist_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    data[key] = sorted(made)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(temp, path)
