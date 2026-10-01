"""Safety-first KH1 PC save parsing and read-only comparison helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
import struct
import tempfile
import time
import zlib

from kh1_reference import EQUIPMENT_BY_ID, WORLD_BY_ID

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SQEX = b"sqEX"
KHSQ = b"KHSQ"
STAT_BLOCK_DELTA = 0x16C3C

KHSQ_LEVEL = 0x08
KHSQ_MUNNY = 0x0C
KHSQ_EXP = 0x10
KHSQ_LOCATION = 0x14
KHSQ_DIFFICULTY = 0x38
KHSQ_WORLD = 0x3A

STAT_LEVEL = 0x00
STAT_HP_CURRENT = 0x01
STAT_HP = 0x02
STAT_MP_CURRENT = 0x03
STAT_MP = 0x04
STAT_AP = 0x05
STAT_STRENGTH = 0x06
STAT_DEFENSE = 0x07
STAT_WEAPON = 0x32
STAT_EXPERIENCE = 0x3C
STAT_ABILITIES = 0x40
ABILITY_COUNT = 0x30
CHARACTER_STRIDE = 0x74
CHARACTER_COUNT = 10
CHAR_ACCESSORY_COUNT = 0x18
CHAR_ACCESSORIES = 0x19
CHAR_ACCESSORY_CAPACITY = 8
CHAR_ITEM_COUNT = 0x21
CHAR_ITEMS = 0x22
CHAR_ITEM_CAPACITY = 12
INVENTORY_COUNT = 0x495
WORLD = 0x203C
ROOM = 0x2040
SPAWN = 0x2044
MUNNY = 0x16418
DIFFICULTY = 0x16428
RECORD_MAGIC_DELTA = 4
RECORD_LENGTH = 0x16C00


class SaveFormatError(ValueError):
    """Raised when a file is not a structurally valid supported save container."""


@dataclass(frozen=True)
class PngChunk:
    offset: int
    length: int
    chunk_type: bytes
    data_start: int
    data_end: int
    crc: int
    crc_ok: bool


@dataclass
class SaveContainer:
    raw: bytes
    sqex_chunk: PngChunk
    payload: bytearray
    slots: list[dict]


def parse_png_chunks(raw: bytes, *, verify_crc: bool = True) -> list[PngChunk]:
    if not raw.startswith(PNG_SIGNATURE):
        raise SaveFormatError("Not a PNG file (signature missing).")
    chunks: list[PngChunk] = []
    pos = len(PNG_SIGNATURE)
    saw_iend = False
    while pos < len(raw):
        if pos + 12 > len(raw):
            raise SaveFormatError(f"Truncated PNG chunk header at 0x{pos:X}.")
        length = struct.unpack_from(">I", raw, pos)[0]
        data_start = pos + 8
        data_end = data_start + length
        chunk_end = data_end + 4
        if chunk_end > len(raw):
            raise SaveFormatError(f"Truncated PNG chunk at 0x{pos:X}.")
        chunk_type = raw[pos + 4 : pos + 8]
        stored_crc = struct.unpack_from(">I", raw, data_end)[0]
        calculated_crc = zlib.crc32(chunk_type + raw[data_start:data_end]) & 0xFFFFFFFF
        crc_ok = stored_crc == calculated_crc
        if verify_crc and not crc_ok:
            name = chunk_type.decode("latin-1", errors="replace")
            raise SaveFormatError(f"Invalid CRC for {name} chunk at 0x{pos:X}.")
        chunks.append(
            PngChunk(pos, length, chunk_type, data_start, data_end, stored_crc, crc_ok)
        )
        pos = chunk_end
        if chunk_type == b"IEND":
            saw_iend = True
            break
    if not saw_iend:
        raise SaveFormatError("PNG has no IEND chunk.")
    if pos != len(raw):
        raise SaveFormatError(f"Unexpected {len(raw) - pos} bytes after IEND.")
    return chunks


def _read_u8(payload: bytes, address: int, label: str) -> int:
    if not 0 <= address < len(payload):
        raise SaveFormatError(f"{label} lies outside the sqEX payload.")
    return payload[address]


def _read_u16(payload: bytes, address: int, label: str) -> int:
    if not 0 <= address <= len(payload) - 2:
        raise SaveFormatError(f"{label} lies outside the sqEX payload.")
    return struct.unpack_from("<H", payload, address)[0]


def _read_u32(payload: bytes, address: int, label: str) -> int:
    if not 0 <= address <= len(payload) - 4:
        raise SaveFormatError(f"{label} lies outside the sqEX payload.")
    return struct.unpack_from("<I", payload, address)[0]


def enumerate_slots(payload: bytes) -> list[dict]:
    slots: list[dict] = []
    cursor = 0
    while True:
        khsq = payload.find(KHSQ, cursor)
        if khsq < 0:
            break
        cursor = khsq + len(KHSQ)
        stat_base = khsq - STAT_BLOCK_DELTA
        entry_base = stat_base - RECORD_MAGIC_DELTA
        # A bare KHSQ string elsewhere in the payload is not a valid slot.
        if (
            entry_base < 0
            or entry_base + RECORD_LENGTH > len(payload)
            or khsq + KHSQ_WORLD >= len(payload)
            or payload[entry_base : entry_base + 4] != b"\x05\x00\x00\x00"
        ):
            continue
        raw_location = payload[
            khsq + KHSQ_LOCATION : khsq + KHSQ_LOCATION + 32
        ].split(b"\0", 1)[0]
        location = raw_location.decode("shift_jis", errors="replace").strip()
        characters = []
        for character_index in range(CHARACTER_COUNT):
            character_base = stat_base + character_index * CHARACTER_STRIDE
            characters.append(
                {
                    "index": character_index,
                    "base": character_base,
                    "level": _read_u8(payload, character_base + STAT_LEVEL, "level"),
                    "hp_current": _read_u8(
                        payload, character_base + STAT_HP_CURRENT, "current HP"
                    ),
                    "hp": _read_u8(payload, character_base + STAT_HP, "base maximum HP"),
                    "mp_current": _read_u8(
                        payload, character_base + STAT_MP_CURRENT, "current MP"
                    ),
                    "mp": _read_u8(payload, character_base + STAT_MP, "base maximum MP"),
                    "ap": _read_u8(payload, character_base + STAT_AP, "AP"),
                    "strength": _read_u8(
                        payload, character_base + STAT_STRENGTH, "strength"
                    ),
                    "defense": _read_u8(
                        payload, character_base + STAT_DEFENSE, "defense"
                    ),
                    "accessory_count": _read_u8(
                        payload,
                        character_base + CHAR_ACCESSORY_COUNT,
                        "accessory count",
                    ),
                    "accessories": [
                        _read_u8(
                            payload,
                            character_base + CHAR_ACCESSORIES + item_index,
                            f"accessory slot {item_index + 1}",
                        )
                        for item_index in range(CHAR_ACCESSORY_CAPACITY)
                    ],
                    "item_count": _read_u8(
                        payload, character_base + CHAR_ITEM_COUNT, "item count"
                    ),
                    "items": [
                        _read_u8(
                            payload,
                            character_base + CHAR_ITEMS + item_index,
                            f"carried item slot {item_index + 1}",
                        )
                        for item_index in range(CHAR_ITEM_CAPACITY)
                    ],
                    "weapon": _read_u8(
                        payload, character_base + STAT_WEAPON, "equipped weapon"
                    ),
                    "exp": _read_u32(
                        payload, character_base + STAT_EXPERIENCE, "EXP"
                    ),
                    "abilities": [
                        _read_u8(
                            payload,
                            character_base + STAT_ABILITIES + ability_index,
                            f"ability slot {ability_index + 1}",
                        )
                        for ability_index in range(ABILITY_COUNT)
                    ],
                }
            )
        sora = characters[0]
        slots.append(
            {
                "index": len(slots),
                "khsq": khsq,
                "entry_base": entry_base,
                "stat_base": stat_base,
                "level": sora["level"],
                "munny": _read_u32(payload, stat_base + MUNNY, "munny"),
                "exp": sora["exp"],
                "difficulty": _read_u8(
                    payload, stat_base + DIFFICULTY, "difficulty"
                ),
                "world": _read_u32(payload, stat_base + WORLD, "world"),
                "room": _read_u32(payload, stat_base + ROOM, "room"),
                "spawn": _read_u32(payload, stat_base + SPAWN, "spawn"),
                "location": location,
                "hp_current": sora["hp_current"],
                "hp": sora["hp"],
                "mp_current": sora["mp_current"],
                "mp": sora["mp"],
                "ap": sora["ap"],
                "strength": sora["strength"],
                "defense": sora["defense"],
                "weapon": sora["weapon"],
                "abilities": sora["abilities"],
                "accessory_count": sora["accessory_count"],
                "accessories": sora["accessories"],
                "item_count": sora["item_count"],
                "items": sora["items"],
                "characters": characters,
                "inventory": [
                    _read_u8(
                        payload,
                        stat_base + INVENTORY_COUNT + item_id,
                        f"inventory item {item_id}",
                    )
                    for item_id in range(256)
                ],
            }
        )
    return slots


LEVEL_COMPANION_FIELDS = ("exp", "hp", "mp", "ap", "strength", "defense")


def update_slot(
    payload: bytearray,
    slot: dict,
    changes: dict,
    *,
    allow_raw_level: bool = False,
) -> None:
    """Apply validated authoritative fields to one extracted KH1FM record.

    A level change must arrive together with matching EXP and stat changes
    (as produced by kh1_leveling.simulate_leveling). A bare level edit leaves
    EXP, stats and abilities out of sync with the level, so it is refused
    unless allow_raw_level=True is passed explicitly.
    """
    stat_base = slot["stat_base"]

    if (
        "level" in changes
        and changes["level"] != slot.get("level")
        and not allow_raw_level
    ):
        missing = [name for name in LEVEL_COMPANION_FIELDS if name not in changes]
        if missing:
            raise ValueError(
                "Level-only edits are refused because EXP and stats would no "
                "longer match the level. Use simulate_leveling() to build the "
                "full change set. Missing: " + ", ".join(missing) + "."
            )

    def write_u8(relative: int, value: int, low: int, high: int, label: str):
        if not isinstance(value, int) or not low <= value <= high:
            raise ValueError(f"{label} must be between {low} and {high}.")
        payload[stat_base + relative] = value

    def write_u32(relative: int, value: int, low: int, high: int, label: str):
        if not isinstance(value, int) or not low <= value <= high:
            raise ValueError(f"{label} must be between {low} and {high}.")
        struct.pack_into("<I", payload, stat_base + relative, value)

    scalar_u8 = {
        "hp_current": (STAT_HP_CURRENT, 0, 255, "Current HP"),
        "hp": (STAT_HP, 0, 255, "Base maximum HP"),
        "mp_current": (STAT_MP_CURRENT, 0, 255, "Current MP"),
        "mp": (STAT_MP, 0, 255, "Base maximum MP"),
        "ap": (STAT_AP, 0, 255, "AP"),
        "strength": (STAT_STRENGTH, 0, 255, "Strength"),
        "defense": (STAT_DEFENSE, 0, 255, "Defense"),
        "difficulty": (DIFFICULTY, 0, 2, "Difficulty"),
    }
    for name, (relative, low, high, label) in scalar_u8.items():
        if name in changes:
            write_u8(relative, changes[name], low, high, label)

    if "level" in changes:
        level = changes["level"]
        write_u8(STAT_LEVEL, level, 1, 100, "Level")
        # KH1 mirrors Sora's level in the KHSQ record. Updating only the stat
        # block makes the menu display the new level while progression logic
        # continues using the old one.
        if not isinstance(level, int) or not 1 <= level <= 100:
            raise ValueError("Level must be between 1 and 100.")
        payload[slot["khsq"] + KHSQ_LEVEL] = level

    scalar_u32 = {
        "exp": (STAT_EXPERIENCE, 0, 0x7FFFFFFF, "EXP"),
        "munny": (MUNNY, 0, 0xFFFFFFFF, "Munny"),
        "room": (ROOM, 0, 0xFFFFFFFF, "Room"),
        "spawn": (SPAWN, 0, 0xFFFFFFFF, "Spawn"),
    }
    for name, (relative, low, high, label) in scalar_u32.items():
        if name in changes:
            write_u32(relative, changes[name], low, high, label)

    if "world" in changes:
        world = changes["world"]
        if world not in WORLD_BY_ID:
            raise ValueError(f"Unsupported world ID: {world}.")
        write_u32(WORLD, world, 0, 0xFFFFFFFF, "World")

    if "weapon" in changes:
        weapon = changes["weapon"]
        equipment = EQUIPMENT_BY_ID.get(weapon)
        if not equipment or equipment["category"] != "keyblade":
            raise ValueError("Sora's equipped weapon must be a known Keyblade.")
        write_u8(STAT_WEAPON, weapon, 0, 255, "Keyblade")

    if "inventory" in changes:
        inventory = changes["inventory"]
        if not isinstance(inventory, dict):
            raise ValueError("Inventory changes must map item IDs to quantities.")
        for item_id, amount in inventory.items():
            if not isinstance(item_id, int) or item_id not in EQUIPMENT_BY_ID:
                raise ValueError(f"Unknown inventory item ID: {item_id}.")
            write_u8(
                INVENTORY_COUNT + item_id,
                amount,
                0,
                99,
                EQUIPMENT_BY_ID[item_id]["name"],
            )

    if "abilities_append" in changes:
        abilities = changes["abilities_append"]
        if not isinstance(abilities, list):
            raise ValueError("Abilities to append must be a list.")
        empty_slots = [
            index
            for index in range(ABILITY_COUNT)
            if payload[stat_base + STAT_ABILITIES + index] & 0x7F == 0
        ]
        if len(abilities) > len(empty_slots):
            raise ValueError(
                f"Not enough empty ability slots: need {len(abilities)}, "
                f"found {len(empty_slots)}."
            )
        for index, ability in zip(empty_slots, abilities):
            if not isinstance(ability, int) or not 1 <= ability <= 0x41:
                raise ValueError(f"Unsupported ability ID: {ability!r}.")
            # In KH1 the high bit means equipped. Natural simulated abilities
            # start as plain owned entries so AP is never overspent.
            payload[stat_base + STAT_ABILITIES + index] = ability

    if "abilities_replace" in changes:
        abilities = changes["abilities_replace"]
        if not isinstance(abilities, list) or len(abilities) != ABILITY_COUNT:
            raise ValueError(
                f"Ability slots must be a list of exactly {ABILITY_COUNT} bytes."
            )
        for index, raw_value in enumerate(abilities):
            if not isinstance(raw_value, int) or not 0 <= raw_value <= 0xFF:
                raise ValueError(f"Invalid ability byte in slot {index + 1}.")
            ability = raw_value & 0x7F
            if ability > 0x41:
                raise ValueError(
                    f"Unsupported ability ID 0x{ability:02X} in slot {index + 1}."
                )
            if ability == 0 and raw_value & 0x80:
                raise ValueError(f"Empty ability slot {index + 1} cannot be equipped.")
            payload[stat_base + STAT_ABILITIES + index] = raw_value

    if "character_updates" in changes:
        updates = changes["character_updates"]
        if not isinstance(updates, dict):
            raise ValueError("Character updates must map character indices to fields.")
        weapon_categories = {0: "keyblade", 1: "staff", 2: "shield"}
        scalar_offsets = {
            "level": STAT_LEVEL,
            "hp_current": STAT_HP_CURRENT,
            "hp": STAT_HP,
            "mp_current": STAT_MP_CURRENT,
            "mp": STAT_MP,
            "ap": STAT_AP,
            "strength": STAT_STRENGTH,
            "defense": STAT_DEFENSE,
        }
        for character_index, fields in updates.items():
            if (
                not isinstance(character_index, int)
                or not 0 <= character_index < CHARACTER_COUNT
                or not isinstance(fields, dict)
            ):
                raise ValueError("Invalid character update entry.")
            base = stat_base + character_index * CHARACTER_STRIDE
            for name, relative in scalar_offsets.items():
                if name in fields:
                    value = fields[name]
                    low = 1 if name == "level" else 0
                    if not isinstance(value, int) or not low <= value <= 255:
                        raise ValueError(
                            f"Character {character_index} {name} must be "
                            f"between {low} and 255."
                        )
                    payload[base + relative] = value
            if "exp" in fields:
                value = fields["exp"]
                if not isinstance(value, int) or not 0 <= value <= 0x7FFFFFFF:
                    raise ValueError("Character EXP is outside the supported range.")
                struct.pack_into("<I", payload, base + STAT_EXPERIENCE, value)
            if "weapon" in fields:
                weapon = fields["weapon"]
                equipment = EQUIPMENT_BY_ID.get(weapon)
                required = weapon_categories.get(character_index)
                if required and (
                    not equipment or equipment["category"] != required
                ):
                    raise ValueError(
                        f"Character {character_index}'s weapon must be a {required}."
                    )
                payload[base + STAT_WEAPON] = weapon
            for field_name, relative, capacity, category in (
                (
                    "accessories",
                    CHAR_ACCESSORIES,
                    CHAR_ACCESSORY_CAPACITY,
                    "accessory",
                ),
                ("items", CHAR_ITEMS, CHAR_ITEM_CAPACITY, "consumable"),
            ):
                if field_name not in fields:
                    continue
                values = fields[field_name]
                if not isinstance(values, list) or len(values) != capacity:
                    raise ValueError(
                        f"{field_name.title()} must contain exactly {capacity} slots."
                    )
                for item_index, item_id in enumerate(values):
                    equipment = EQUIPMENT_BY_ID.get(item_id)
                    if item_id != 0 and (
                        not equipment or equipment["category"] != category
                    ):
                        raise ValueError(
                            f"Invalid {category} in character slot {item_index + 1}."
                        )
                    payload[base + relative + item_index] = item_id
            if "abilities" in fields:
                values = fields["abilities"]
                if not isinstance(values, list) or len(values) != ABILITY_COUNT:
                    raise ValueError(
                        f"Abilities must contain exactly {ABILITY_COUNT} slots."
                    )
                for ability_index, raw_value in enumerate(values):
                    if not isinstance(raw_value, int) or not 0 <= raw_value <= 0xFF:
                        raise ValueError("Invalid character ability byte.")
                    ability_id = raw_value & 0x7F
                    if ability_id > 0x41 or (ability_id == 0 and raw_value & 0x80):
                        raise ValueError(
                            f"Invalid ability in slot {ability_index + 1}."
                        )
                    payload[base + STAT_ABILITIES + ability_index] = raw_value


def load_save(path: str | os.PathLike[str]) -> SaveContainer:
    raw = Path(path).read_bytes()
    chunks = parse_png_chunks(raw)
    sqex_chunks = [chunk for chunk in chunks if chunk.chunk_type == SQEX]
    if not sqex_chunks:
        raise SaveFormatError(
            "No sqEX save-data chunk was found. If this was uploaded as an "
            "image, ZIP the original PNG first so its custom chunk is preserved."
        )
    if len(sqex_chunks) != 1:
        raise SaveFormatError(f"Expected one sqEX chunk, found {len(sqex_chunks)}.")
    chunk = sqex_chunks[0]
    payload = bytearray(raw[chunk.data_start : chunk.data_end])
    slots = enumerate_slots(payload)
    if not slots:
        raise SaveFormatError("The sqEX payload contains no structurally valid KHSQ slots.")
    return SaveContainer(raw, chunk, payload, slots)


def discover_save_files(
    home: str | os.PathLike[str] | None = None,
) -> list[Path]:
    """Find KHFM_WW.png in known Steam, Epic, Re:Fined, and Proton locations."""
    roots = []
    requested_home = Path(home).expanduser() if home else Path.home()
    roots.append(requested_home)
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        roots.append(Path(user_profile))

    proton_suffixes = (
        Path(
            ".local/share/Steam/steamapps/compatdata/2552430/pfx/drive_c/"
            "users/steamuser/Documents"
        ),
        Path(
            ".steam/steam/steamapps/compatdata/2552430/pfx/drive_c/"
            "users/steamuser/Documents"
        ),
    )
    document_roots = []
    for root in roots:
        document_roots.extend((root / "Documents", root / "OneDrive/Documents"))
        document_roots.extend(root / suffix for suffix in proton_suffixes)

    patterns = (
        "My Games/KINGDOM HEARTS HD 1.5+2.5 ReMIX/Steam/*/KHFM_WW.png",
        "KINGDOM HEARTS HD 1.5+2.5 ReMIX/Epic Games Store/*/KHFM_WW.png",
        "KINGDOM HEARTS HD 1.5+2.5 ReMIX/Epic Games Store/KHFM_WW.png",
        "Kingdom Hearts/KHFM_WW.png",
        "Kingdom Hearts/*/KHFM_WW.png",
    )
    found = {}
    for documents in document_roots:
        for pattern in patterns:
            for candidate in documents.glob(pattern):
                if not candidate.is_file():
                    continue
                try:
                    identity = candidate.resolve()
                except OSError:
                    identity = candidate.absolute()
                found[str(identity)] = candidate

    def modified(path: Path) -> float:
        try:
            return path.stat().st_mtime
        except OSError:
            return 0

    return sorted(found.values(), key=lambda path: (-modified(path), str(path)))


def rebuild_with_payload(container: SaveContainer, payload: bytes) -> bytes:
    chunk = container.sqex_chunk
    if len(payload) != chunk.length:
        raise SaveFormatError("Replacement sqEX payload length changed.")
    rebuilt = bytearray(container.raw)
    rebuilt[chunk.data_start : chunk.data_end] = payload
    crc = zlib.crc32(SQEX + payload) & 0xFFFFFFFF
    struct.pack_into(">I", rebuilt, chunk.data_end, crc)
    # Reparse before returning so malformed output never reaches disk.
    parse_png_chunks(bytes(rebuilt))
    return bytes(rebuilt)


def timestamped_backup_path(path: str | os.PathLike[str]) -> Path:
    source = Path(path)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup_dir = source.parent / "KH1_Save_Editor_Backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    candidate = backup_dir / f"{source.name}.{stamp}.bak"
    counter = 1
    while candidate.exists():
        candidate = backup_dir / f"{source.name}.{stamp}-{counter}.bak"
        counter += 1
    return candidate


def atomic_write_with_backup(
    path: str | os.PathLike[str], rebuilt: bytes
) -> Path:
    destination = Path(path)
    # Validate output and prove a supported save remains before any write.
    chunks = parse_png_chunks(rebuilt)
    if not any(chunk.chunk_type == SQEX for chunk in chunks):
        raise SaveFormatError("Refusing to write output without an sqEX chunk.")
    backup = timestamped_backup_path(destination)
    backup.write_bytes(destination.read_bytes())
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(rebuilt)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, destination)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
    return backup


def changed_ranges(before: bytes, after: bytes) -> list[dict]:
    if len(before) != len(after):
        raise SaveFormatError(
            f"sqEX payload sizes differ ({len(before)} vs {len(after)} bytes)."
        )
    ranges: list[dict] = []
    start = None
    for index, (old, new) in enumerate(zip(before, after)):
        if old != new and start is None:
            start = index
        if old == new and start is not None:
            ranges.append(_make_range(before, after, start, index))
            start = None
    if start is not None:
        ranges.append(_make_range(before, after, start, len(before)))
    return ranges


def _make_range(before: bytes, after: bytes, start: int, end: int) -> dict:
    return {
        "start": start,
        "end": end,
        "length": end - start,
        "before_hex": before[start:end].hex(" "),
        "after_hex": after[start:end].hex(" "),
    }


def compare_saves(
    before_path: str | os.PathLike[str], after_path: str | os.PathLike[str]
) -> dict:
    before = load_save(before_path)
    after = load_save(after_path)
    ranges = changed_ranges(before.payload, after.payload)
    report = {
        "before": str(Path(before_path)),
        "after": str(Path(after_path)),
        "payload_size": len(before.payload),
        "before_slots": before.slots,
        "after_slots": after.slots,
        "changed_byte_count": sum(item["length"] for item in ranges),
        "ranges": ranges,
    }
    for item in report["ranges"]:
        item["slot_relative"] = []
        for slot in before.slots:
            for basis_name, basis in (
                ("stat_base", slot["stat_base"]),
                ("khsq", slot["khsq"]),
            ):
                relative = item["start"] - basis
                item["slot_relative"].append(
                    {
                        "slot": slot["index"] + 1,
                        "basis": basis_name,
                        "offset": relative,
                        "offset_hex": (
                            f"+0x{relative:X}" if relative >= 0 else f"-0x{-relative:X}"
                        ),
                    }
                )
    return report


def format_diff_report(report: dict) -> str:
    lines = [
        "KH1 SAVE VALUES LAB — READ-ONLY DIFF",
        f"Before: {report['before']}",
        f"After:  {report['after']}",
        f"sqEX payload: {report['payload_size']} bytes",
        f"Changed bytes: {report['changed_byte_count']}",
        f"Changed ranges: {len(report['ranges'])}",
        "",
    ]
    if not report["ranges"]:
        lines.append("No sqEX payload differences found.")
    for number, item in enumerate(report["ranges"], 1):
        lines.extend(
            [
                f"[{number}] payload 0x{item['start']:X}..0x{item['end'] - 1:X} "
                f"({item['length']} byte(s))",
                f"    before: {item['before_hex']}",
                f"    after:  {item['after_hex']}",
            ]
        )
        for relative in item["slot_relative"]:
            lines.append(
                f"    slot {relative['slot']} {relative['basis']}: "
                f"{relative['offset_hex']}"
            )
        lines.append("")
    return "\n".join(lines)


def write_diff_reports(report: dict, text_path: Path, json_path: Path) -> None:
    text_path.write_text(format_diff_report(report), encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
