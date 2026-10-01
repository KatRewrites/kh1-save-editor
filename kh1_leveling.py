"""KH1 Final Mix Sora level-growth and ability simulation."""

from __future__ import annotations

from collections import Counter


DREAM_POWERS = ("Sword", "Staff", "Shield")
EXP_CURVES = ("Dusk", "Midday", "Dawn")

# Total EXP at the requested level. The final level always costs 18,000 EXP.
EXP_TOTALS = {
    99: {"Dusk": 860_291, "Midday": 931_815, "Dawn": 966_856},
    100: {"Dusk": 878_291, "Midday": 949_815, "Dawn": 984_856},
}

# Each listed level grants the corresponding fixed-size stat bonus.
STAT_LEVELS = {
    "hp": (
        6, 8, 10, 14, 16, 22, 26, 28, 34, 38, 40, 46, 50, 52, 54,
        58, 62, 64, 66, 70, 72, 74, 76,
    ),
    "ap": (
        11, 17, 20, 23, 29, 32, 35, 41, 44, 47, 53, 56, 59, 65,
        68, 71, 77, 80, 83, 86, 89, 92, 95, 98,
    ),
    "strength": (
        2, 4, 7, 13, 19, 25, 31, 37, 43, 49, 55, 61, 67, 73,
        78, 81, 84, 87, 90, 93, 96, 99,
    ),
    "defense": (
        3, 5, 9, 15, 21, 27, 33, 39, 45, 51, 57, 63, 69, 75,
        79, 82, 85, 88, 91, 94, 97, 100,
    ),
    "mp": (12, 24, 36, 48, 60),
}
STAT_AMOUNTS = {"hp": 3, "mp": 1, "ap": 2, "strength": 2, "defense": 2}
EXTRA_MP_LEVELS = {"Sword": (42,), "Staff": (42, 72), "Shield": (72,)}

# Ability IDs are from KHSave.Lib1.Types.AbilityType. Duplicate entries are
# intentional because KH1 allows multiple copies of some support abilities.
ABILITY_LEVELS = {
    "Sword": {
        6: 0x36, 9: 0x0A, 12: 0x35, 15: 0x13, 18: 0x3C,
        21: 0x06, 24: 0x15, 27: 0x37, 33: 0x14, 36: 0x05,
        39: 0x38, 45: 0x17, 48: 0x19, 50: 0x41, 51: 0x39,
        57: 0x11, 60: 0x12, 63: 0x18, 66: 0x06, 69: 0x3E,
        72: 0x07, 75: 0x05, 78: 0x1A, 81: 0x3C, 84: 0x08,
        87: 0x18, 90: 0x1C, 93: 0x06, 96: 0x07, 99: 0x08,
        100: 0x1B,
    },
    "Staff": {
        6: 0x39, 9: 0x05, 12: 0x38, 15: 0x0A, 18: 0x37,
        21: 0x17, 24: 0x07, 27: 0x3C, 33: 0x15, 36: 0x12,
        39: 0x3E, 42: 0x18, 45: 0x07, 48: 0x1C, 51: 0x36,
        55: 0x41, 57: 0x13, 60: 0x1A, 63: 0x1B, 69: 0x35,
        72: 0x05, 75: 0x18, 78: 0x14, 81: 0x3C, 84: 0x11,
        87: 0x06, 90: 0x19, 93: 0x06, 96: 0x08, 99: 0x06,
        100: 0x08,
    },
    "Shield": {
        6: 0x35, 9: 0x1A, 12: 0x3C, 15: 0x15, 18: 0x39,
        21: 0x0A, 24: 0x1C, 27: 0x3E, 30: 0x05, 36: 0x19,
        39: 0x36, 42: 0x1B, 45: 0x13, 48: 0x08, 51: 0x37,
        55: 0x41, 57: 0x05, 60: 0x14, 63: 0x06, 69: 0x38,
        72: 0x17, 75: 0x08, 78: 0x11, 81: 0x3C, 84: 0x12,
        87: 0x06, 90: 0x18, 93: 0x07, 96: 0x06, 99: 0x07,
        100: 0x18,
    },
}

ABILITY_NAMES = {
    0x01: "High Jump", 0x02: "Mermaid Kick", 0x03: "Glide",
    0x04: "Superglide", 0x05: "Treasure Magnet", 0x06: "Combo Plus",
    0x07: "Air Combo Plus", 0x08: "Critical Plus",
    0x09: "Second Wind", 0x0A: "Scan", 0x0B: "Sonic Blade",
    0x0C: "Ars Arcanum", 0x0D: "Strike Raid", 0x0E: "Ragnarok",
    0x0F: "Trinity Limit", 0x10: "Cheer",
    0x11: "Vortex", 0x12: "Aerial Sweep", 0x13: "Counterattack",
    0x14: "Blitz", 0x15: "Guard", 0x16: "Dodge Roll",
    0x17: "MP Haste", 0x18: "MP Rage",
    0x19: "Second Chance", 0x1A: "Berserk", 0x1B: "Jackpot",
    0x1C: "Lucky Strike", 0x1D: "Charge", 0x1E: "Rocket",
    0x1F: "Tornado", 0x20: "MP Gift", 0x21: "Raging Boar",
    0x22: "Asp's Bite", 0x23: "Healing Herb", 0x24: "Wind Armor",
    0x25: "Crescent", 0x26: "Sandstorm", 0x27: "Applause!",
    0x28: "Blazing Fury", 0x29: "Icy Terror",
    0x2A: "Bolts of Sorrow", 0x2B: "Ghostly Scream",
    0x2C: "Hummingbird", 0x2D: "Time-Out", 0x2E: "Storm's Eye",
    0x2F: "Ferocious Lunge", 0x30: "Furious Bellow",
    0x31: "Spiral Wave", 0x32: "Thunder Potion",
    0x33: "Cure Potion", 0x34: "Aero Potion",
    0x35: "Slapshot", 0x36: "Sliding Dash",
    0x37: "Hurricane Blast", 0x38: "Ripple Drive", 0x39: "Stun Impact",
    0x3A: "Gravity Break", 0x3B: "Zantetsuken",
    0x3C: "Tech Boost", 0x3D: "Encounter Plus",
    0x3E: "Leaf Bracer", 0x3F: "Evolution", 0x40: "EXP Zero",
    0x41: "Combo Master",
}


def detect_dream_power(raw_abilities: list[int], level: int) -> tuple[str, dict]:
    """Return the best ability-table match and diagnostic match counts."""
    observed = Counter(value & 0x7F for value in raw_abilities if value & 0x7F)
    diagnostics = {}
    for power in DREAM_POWERS:
        expected = Counter(
            ability
            for ability_level, ability in ABILITY_LEVELS[power].items()
            if ability_level <= level
        )
        matched = sum(min(count, observed[ability]) for ability, count in expected.items())
        diagnostics[power] = {"matched": matched, "expected": sum(expected.values())}
    best = max(
        DREAM_POWERS,
        key=lambda power: (
            diagnostics[power]["matched"],
            -diagnostics[power]["expected"],
        ),
    )
    return best, diagnostics


def simulate_leveling(
    slot: dict, target_level: int, dream_power: str, exp_curve: str
) -> dict:
    """Build additive, stat-boost-preserving changes for level 99 or 100."""
    current_level = slot["level"]
    if target_level not in EXP_TOTALS:
        raise ValueError("The safe simulator currently supports level 99 or 100.")
    if not 1 <= current_level < target_level:
        raise ValueError(
            f"Load the unmodified backup first: its level must be below {target_level}."
        )
    if dream_power not in DREAM_POWERS:
        raise ValueError("Dream power must be Sword, Staff, or Shield.")
    if exp_curve not in EXP_CURVES:
        raise ValueError("EXP curve must be Dusk, Midday, or Dawn.")

    passed_levels = range(current_level + 1, target_level + 1)
    deltas = {}
    for stat, levels in STAT_LEVELS.items():
        deltas[stat] = sum(
            STAT_AMOUNTS[stat] for level in passed_levels if level in levels
        )
    deltas["mp"] += sum(
        1 for level in passed_levels if level in EXTRA_MP_LEVELS[dream_power]
    )

    # Recover the complete natural level-up set through the target. This is
    # intentionally count-aware because KH1 grants duplicate copies of several
    # support abilities. Comparing against the whole existing list also repairs
    # an ability missed before the source level (for example, after an earlier
    # incomplete level edit) without duplicating abilities already present.
    observed = Counter(
        value & 0x7F for value in slot["abilities"] if value & 0x7F
    )
    abilities = []
    for level, ability in ABILITY_LEVELS[dream_power].items():
        if level > target_level:
            continue
        if observed[ability]:
            observed[ability] -= 1
        else:
            abilities.append(ability)
    changes = {
        "level": target_level,
        "exp": EXP_TOTALS[target_level][exp_curve],
        "hp": slot["hp"] + deltas["hp"],
        "hp_current": min(255, slot["hp_current"] + deltas["hp"]),
        "mp": slot["mp"] + deltas["mp"],
        "mp_current": min(255, slot["mp_current"] + deltas["mp"]),
        "ap": slot["ap"] + deltas["ap"],
        "strength": slot["strength"] + deltas["strength"],
        "defense": slot["defense"] + deltas["defense"],
        "abilities_append": abilities,
    }
    for name in ("hp", "mp", "ap", "strength", "defense"):
        if changes[name] > 255:
            raise ValueError(f"{name.title()} would exceed the save field limit.")

    return {
        "source_level": current_level,
        "target_level": target_level,
        "dream_power": dream_power,
        "exp_curve": exp_curve,
        "deltas": deltas,
        "abilities": abilities,
        "ability_names": [ABILITY_NAMES[value] for value in abilities],
        "changes": changes,
    }
