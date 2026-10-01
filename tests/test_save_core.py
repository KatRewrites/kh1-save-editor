from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from kh1_leveling import ABILITY_LEVELS, detect_dream_power, simulate_leveling
from kh1_save_core import (
    CHARACTER_STRIDE,
    CHAR_ACCESSORIES,
    CHAR_ITEMS,
    STAT_ABILITIES,
    KHSQ_DIFFICULTY,
    KHSQ_EXP,
    KHSQ_LEVEL,
    KHSQ_LOCATION,
    KHSQ_MUNNY,
    KHSQ_WORLD,
    DIFFICULTY,
    INVENTORY_COUNT,
    MUNNY,
    ROOM,
    SPAWN,
    STAT_BLOCK_DELTA,
    STAT_AP,
    STAT_DEFENSE,
    STAT_HP,
    STAT_HP_CURRENT,
    STAT_LEVEL,
    STAT_MP,
    STAT_STRENGTH,
    STAT_WEAPON,
    STAT_EXPERIENCE,
    WORLD,
    SaveFormatError,
    changed_ranges,
    compare_saves,
    discover_save_files,
    load_save,
    parse_png_chunks,
    rebuild_with_payload,
    update_slot,
)


def chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def fixture_png(*, hp: int = 54, potion_byte: int = 6) -> bytes:
    stat_base = 0x100
    khsq = stat_base + STAT_BLOCK_DELTA
    payload = bytearray(khsq + 0x100)
    payload[stat_base - 4 : stat_base] = b"\x05\x00\x00\x00"
    payload[khsq : khsq + 4] = b"KHSQ"
    payload[khsq + KHSQ_LEVEL] = 41
    struct.pack_into("<H", payload, khsq + KHSQ_MUNNY, 16178)
    struct.pack_into("<I", payload, khsq + KHSQ_EXP, 123456)
    payload[khsq + KHSQ_LOCATION : khsq + KHSQ_LOCATION + 13] = b"Traverse Town"
    payload[khsq + KHSQ_DIFFICULTY] = 1
    payload[khsq + KHSQ_WORLD] = 2
    payload[stat_base + STAT_LEVEL] = 41
    payload[stat_base + STAT_HP_CURRENT] = hp
    payload[stat_base + STAT_HP] = 51
    payload[stat_base + STAT_MP] = 8
    payload[stat_base + STAT_AP] = 25
    payload[stat_base + STAT_STRENGTH] = 22
    payload[stat_base + STAT_DEFENSE] = 26
    payload[stat_base + STAT_WEAPON] = 0x5D
    struct.pack_into("<I", payload, stat_base + STAT_EXPERIENCE, 41892)
    payload[stat_base + INVENTORY_COUNT + 1] = potion_byte
    struct.pack_into("<I", payload, stat_base + WORLD, 6)
    struct.pack_into("<I", payload, stat_base + ROOM, 2)
    struct.pack_into("<I", payload, stat_base + SPAWN, 3)
    struct.pack_into("<I", payload, stat_base + MUNNY, 16178)
    payload[stat_base + DIFFICULTY] = 1
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"sqEX", bytes(payload))
        + chunk(b"IEND", b"")
    )


class SaveCoreTests(unittest.TestCase):
    def test_parse_and_enumerate_slot(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            self.assertEqual(len(save.slots), 1)
            slot = save.slots[0]
            self.assertEqual(slot["level"], 41)
            self.assertEqual(slot["munny"], 16178)
            self.assertEqual(slot["hp_current"], 54)
            self.assertEqual(slot["hp"], 51)
            self.assertEqual(slot["mp"], 8)
            self.assertEqual(slot["ap"], 25)
            self.assertEqual(slot["strength"], 22)
            self.assertEqual(slot["defense"], 26)
            self.assertEqual(slot["weapon"], 0x5D)
            self.assertEqual(slot["inventory"][1], 6)
            self.assertEqual(slot["world"], 6)
            self.assertEqual(slot["munny"], 16178)
            self.assertEqual(slot["location"], "Traverse Town")
            self.assertEqual(len(slot["characters"]), 10)
            self.assertEqual(
                slot["characters"][1]["base"],
                slot["stat_base"] + CHARACTER_STRIDE,
            )

    def test_noop_round_trip_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            original = fixture_png()
            path.write_bytes(original)
            save = load_save(path)
            rebuilt = rebuild_with_payload(save, save.payload)
            self.assertEqual(rebuilt, original)

    def test_payload_change_recalculates_sqex_crc(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            changed = bytearray(save.payload)
            changed[save.slots[0]["stat_base"] + STAT_HP_CURRENT] = 55
            rebuilt = rebuild_with_payload(save, changed)
            self.assertNotEqual(rebuilt, save.raw)
            self.assertTrue(all(item.crc_ok for item in parse_png_chunks(rebuilt)))

    def test_values_lab_reports_absolute_and_relative_offsets(self):
        with tempfile.TemporaryDirectory() as folder:
            before = Path(folder) / "before.png"
            after = Path(folder) / "after.png"
            before.write_bytes(fixture_png(potion_byte=6))
            after.write_bytes(fixture_png(potion_byte=5))
            report = compare_saves(before, after)
            self.assertEqual(report["changed_byte_count"], 1)
            changed = report["ranges"][0]
            self.assertEqual(changed["before_hex"], "06")
            self.assertEqual(changed["after_hex"], "05")
            self.assertIn(
                {
                    "slot": 1,
                    "basis": "stat_base",
                    "offset": INVENTORY_COUNT + 1,
                    "offset_hex": f"+0x{INVENTORY_COUNT + 1:X}",
                },
                changed["slot_relative"],
            )

    def test_authoritative_update_changes_only_requested_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            changed = bytearray(save.payload)
            update_slot(
                changed,
                save.slots[0],
                {
                    "weapon": 0x5C,
                    "inventory": {1: 99, 3: 12},
                    "world": 0x0B,
                    "room": 7,
                },
            )
            slot = save.slots[0]
            base = slot["stat_base"]
            self.assertEqual(changed[base + STAT_WEAPON], 0x5C)
            self.assertEqual(changed[base + INVENTORY_COUNT + 1], 99)
            self.assertEqual(changed[base + INVENTORY_COUNT + 3], 12)
            self.assertEqual(struct.unpack_from("<I", changed, base + WORLD)[0], 0x0B)
            self.assertEqual(struct.unpack_from("<I", changed, base + ROOM)[0], 7)

    def test_detects_staff_path_from_level_41_abilities(self):
        abilities = [
            ability
            for level, ability in ABILITY_LEVELS["Staff"].items()
            if level <= 41
        ]
        abilities.extend((0x0B, 0x16, 0x06, 0x0D))
        detected, diagnostics = detect_dream_power(abilities, 41)
        self.assertEqual(detected, "Staff")
        self.assertEqual(
            diagnostics["Staff"]["matched"], diagnostics["Staff"]["expected"]
        )

    def test_level_simulation_preserves_boosts_and_adds_disabled_abilities(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png(hp=51))
            save = load_save(path)
            slot = save.slots[0]
            plan = simulate_leveling(slot, 99, "Staff", "Midday")
            self.assertEqual(plan["deltas"], {
                "hp": 36,
                "ap": 32,
                "strength": 28,
                "defense": 26,
                "mp": 4,
            })
            self.assertEqual(plan["changes"]["level"], 99)
            self.assertEqual(plan["changes"]["exp"], 931815)
            self.assertEqual(plan["changes"]["strength"], 50)
            self.assertEqual(plan["changes"]["defense"], 52)

            changed = bytearray(save.payload)
            update_slot(changed, slot, plan["changes"])
            base = slot["stat_base"]
            self.assertEqual(changed[base + STAT_LEVEL], 99)
            self.assertEqual(changed[slot["khsq"] + KHSQ_LEVEL], 99)
            self.assertEqual(
                struct.unpack_from("<I", changed, base + STAT_EXPERIENCE)[0],
                931815,
            )
            first_added = plan["abilities"][0]
            self.assertEqual(
                changed[base + STAT_ABILITIES],
                first_added,
            )

    def test_level_only_update_is_refused_without_exp_and_stats(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            changed = bytearray(save.payload)
            before = bytes(changed)
            with self.assertRaises(ValueError):
                update_slot(changed, save.slots[0], {"level": 100})
            self.assertEqual(bytes(changed), before)

    def test_level_update_changes_both_mirrored_records(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            changed = bytearray(save.payload)
            update_slot(
                changed, save.slots[0], {"level": 100}, allow_raw_level=True
            )
            self.assertEqual(
                changed[save.slots[0]["stat_base"] + STAT_LEVEL],
                100,
            )
            self.assertEqual(
                changed[save.slots[0]["khsq"] + KHSQ_LEVEL],
                100,
            )

    def test_level_simulation_recovers_previously_missed_ability(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            slot = save.slots[0]
            # Staff should already have Stun Impact from level 6. Leaving the
            # ability list empty models an earlier incomplete level edit.
            plan = simulate_leveling(slot, 99, "Staff", "Midday")
            self.assertEqual(plan["abilities"][0], ABILITY_LEVELS["Staff"][6])

    def test_ability_replacement_preserves_owned_and_equipped_encoding(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            changed = bytearray(save.payload)
            abilities = [0] * 0x30
            abilities[0] = 0x3E
            abilities[1] = 0x18 | 0x80
            update_slot(
                changed,
                save.slots[0],
                {"abilities_replace": abilities},
            )
            base = save.slots[0]["stat_base"] + STAT_ABILITIES
            self.assertEqual(changed[base], 0x3E)
            self.assertEqual(changed[base + 1], 0x98)

    def test_donald_and_goofy_equipment_updates_are_record_local(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            changed = bytearray(save.payload)
            original = bytes(changed)
            update_slot(
                changed,
                save.slots[0],
                {
                    "character_updates": {
                        1: {
                            "weapon": 0x67,
                            "accessories": [0x11] + [0] * 7,
                            "items": [0x01] + [0] * 11,
                        },
                        2: {"weapon": 0x77},
                    }
                },
            )
            base = save.slots[0]["stat_base"]
            donald = base + CHARACTER_STRIDE
            goofy = base + CHARACTER_STRIDE * 2
            self.assertEqual(changed[donald + STAT_WEAPON], 0x67)
            self.assertEqual(changed[donald + CHAR_ACCESSORIES], 0x11)
            self.assertEqual(changed[donald + CHAR_ITEMS], 0x01)
            self.assertEqual(changed[goofy + STAT_WEAPON], 0x77)
            self.assertEqual(changed[base + STAT_WEAPON], original[base + STAT_WEAPON])

    def test_rejects_wrong_party_weapon_category(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            with self.assertRaisesRegex(ValueError, "must be a staff"):
                update_slot(
                    bytearray(save.payload),
                    save.slots[0],
                    {"character_updates": {1: {"weapon": 0x77}}},
                )

    def test_rejects_non_keyblade_as_soras_weapon(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            with self.assertRaisesRegex(ValueError, "known Keyblade"):
                update_slot(bytearray(save.payload), save.slots[0], {"weapon": 1})

    def test_rejects_inventory_quantity_over_99(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "KHFM_WW.png"
            path.write_bytes(fixture_png())
            save = load_save(path)
            with self.assertRaisesRegex(ValueError, "between 0 and 99"):
                update_slot(
                    bytearray(save.payload),
                    save.slots[0],
                    {"inventory": {1: 100}},
                )

    def test_discovers_known_steam_deck_and_windows_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            deck_save = (
                home
                / ".local/share/Steam/steamapps/compatdata/2552430/pfx/drive_c"
                / "users/steamuser/Documents/My Games"
                / "KINGDOM HEARTS HD 1.5+2.5 ReMIX/Steam/123/KHFM_WW.png"
            )
            windows_save = (
                home
                / "Documents/My Games/KINGDOM HEARTS HD 1.5+2.5 ReMIX"
                / "Steam/456/KHFM_WW.png"
            )
            unrelated = home / "Downloads/KHFM_WW.png"
            for path in (deck_save, windows_save, unrelated):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fixture")
            found = {path.resolve() for path in discover_save_files(home)}
            self.assertEqual(found, {deck_save.resolve(), windows_save.resolve()})

    def test_rejects_plain_preview_png(self):
        plain = b"\x89PNG\r\n\x1a\n" + chunk(b"IEND", b"")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "preview.png"
            path.write_bytes(plain)
            with self.assertRaisesRegex(SaveFormatError, "No sqEX"):
                load_save(path)

    def test_changed_ranges_groups_contiguous_bytes(self):
        self.assertEqual(
            changed_ranges(b"\x00\x01\x02\x03", b"\x00\x09\x08\x03"),
            [
                {
                    "start": 1,
                    "end": 3,
                    "length": 2,
                    "before_hex": "01 02",
                    "after_hex": "09 08",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
