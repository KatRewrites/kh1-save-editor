# KH1 Final Mix (PC) save offsets: what's confirmed and what isn't

Tested against one real Steam save (`KHFM_WW.png`, 18,788,509 bytes, 2 slots). **In-game check (Oct 1, 2026, Steam Deck):** Orichalcum in slot 2 changed 19 → 20 with the core library; the game loaded the save and showed 20. Other fields are still unchecked in game.

## Confirmed by structure (the file itself proves it)
| What | Where | How we know |
|---|---|---|
| Save container | PNG chunk `sqEX`, payload at file offset 0x60 | Chunk CRCs check out; one sqEX chunk |
| Archive directory | payload 0x10, 200 entries × 0x158, first 0xF0 bytes XOR'd with key at 0xE0 | Decodes into `BISLPS-25198-NN` and `-NN/system.bin` names |
| Slot data / summary pair | data entry 0x16C00 long + summary entry starting `KHSQ` | Both slots pair up |
| Rewrite safety | no-op save is byte-identical; a 1-item edit changes 1 byte + 4 CRC bytes | Tested on a copy |

## Confirmed by two sources agreeing
| Field | Offset | Evidence |
|---|---|---|
| Level | data +0x04 (u8), summary +0x08 | Both read 6 and 99 |
| Munny | data +0x1641C (u32), summary +0x0C (u16) | Both read 306 and 23,276 |
| Materials, Tent, Camping Set, Cottage, Thunder Arts | data +0x499 + item ID | Slot 2 values match the June version's separately found absolute offsets exactly |

## Plausible but not cross-checked (editable, use with backups)
| Field | Offset (from data entry) | Note |
|---|---|---|
| Current HP / base max HP | +0x05 / +0x06 | Current can exceed base max because equipment adds HP (slot 2: 93 current, 87 base). Order matches Xeeynamo's KingdomSaveEditor |
| Current MP / base max MP | +0x07 / +0x08 | Same pattern (13 / 10) |
| Max AP, base Strength, base Defense | +0x09, +0x0A, +0x0B | Values look sane (38, 50, 50 at slot 2) |
| Potion, Hi-Potion, Ether, Elixir, Mega-Potion, Mega-Ether, Megalixir | +0x499 + 0x01…0x08 | June version read Potion 21 vs 31 here; June's was marked "interpolated" |

## Read-only / protected
- EXP at +0x40 (u32): slot 2 shows 188,278 at level 99, far below a real level-99 total (931,815 on the Midday curve), so that slot was level-edited directly at some point. Direct level edits are blocked in the app; use Simulate Leveling.
- Difficulty at +0x1642C: both slots read 1 (Standard). Not writable.
- Hero License, Thunder Arts: readable, not writable. Hero License reads 1 here but 0 in the June version, so its offset is disputed.
- Abilities, party, quest items, Steam/Epic conversion: not mapped, disabled.

## Retired from older versions
- June 27 stat block at `KHSQ − 0x16C3C`: reads nonsense (HP 3, MP 100). Dropped.
- May 5 header-relative offsets (0x18 level, 0x22 munny, ...): unverified guesses. Dropped.

## Simulate Leveling (v0.7)
- Growth tables in `kh1_leveling.py`. Simulating slot 1 from level 6 to 99 (Staff) gives base HP 87 and MP 10, exactly what the real level-99 slot holds, which cross-checks the HP/MP tables.
- Writes both level records, EXP, stats, and adds missing abilities unequipped. Changed 41 bytes on a test copy; the other slot was untouched.

## Still to do
- In-game checks for stats, Simulate Leveling, abilities, and equipment.
- Enforce the no-level-only-edit rule in `kh1_save_core.py`, not just the UI.
