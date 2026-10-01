"""KH1 Final Mix reference tables ported from Xeeynamo/KingdomSaveEditor.

Upstream project: https://github.com/Xeeynamo/KingdomSaveEditor
License: GPL-3.0
"""

_EQUIPMENT_ROWS = """
Empty|info
Potion|consumable
Hi-Potion|consumable
Ether|consumable
Elixir|consumable
Unused 05|unused
Mega-Potion|consumable
Mega-Ether|consumable
Megalixir|consumable
Fury Stone|synthesis
Power Stone|synthesis
Energy Stone|synthesis
Blazing Stone|synthesis
Frost Stone|synthesis
Lightning Stone|synthesis
Dazzling Stone|synthesis
Stormy Stone|synthesis
Protect Chain|accessory
Protera Chain|accessory
Protega Chain|accessory
Fire Ring|accessory
Fira Ring|accessory
Firaga Ring|accessory
Blizzard Ring|accessory
Blizzara Ring|accessory
Blizzaga Ring|accessory
Thunder Ring|accessory
Thundara Ring|accessory
Thundaga Ring|accessory
Ability Stud|accessory
Guard Earring|accessory
Master Earring|accessory
Chaos Ring|accessory
Dark Ring|accessory
Element Ring|accessory
Three Stars|accessory
Power Chain|accessory
Golem Chain|accessory
Titan Chain|accessory
Energy Bangle|accessory
Angel Bangle|accessory
Gaia Bangle|accessory
Magic Armlet|accessory
Rune Armlet|accessory
Atlas Armlet|accessory
Heartguard|accessory
Ribbon|accessory
Crystal Crown|accessory
Brave Warrior|accessory
Ifrit's Horn|accessory
Inferno Band|accessory
White Fang|accessory
Ray of Light|accessory
Holy Circlet|accessory
Raven's Claw|accessory
Omega Arts|accessory
EXP Earring|accessory
Unused 39|unused
EXP Ring|accessory
EXP Bracelet|accessory
EXP Necklace|accessory
Firagun Band|accessory
Blizzagun Band|accessory
Thundagun Band|accessory
Ifrit Belt|accessory
Shiva Belt|accessory
Ramuh Belt|accessory
Moogle Badge|accessory
Cosmic Arts|accessory
Royal Crown|accessory
Prime Cap|accessory
Obsidian Ring|accessory
Unused 48|unused
Unused 49|unused
Unused 4A|unused
Unused 4B|unused
Unused 4C|unused
Unused 4D|unused
Unused 4E|unused
Unused 4F|unused
Unused 50|unused
Kingdom Key|keyblade
Dream Sword|keyblade
Dream Shield (Sora)|keyblade
Dream Rod (Sora)|keyblade
Wooden Sword|keyblade
Jungle King|keyblade
Three Wishes|keyblade
Fairy Harp|keyblade
Pumpkinhead|keyblade
Crabclaw|keyblade
Divine Rose|keyblade
Spellbinder|keyblade
Olympia|keyblade
Lionheart|keyblade
Metal Chocobo|keyblade
Oathkeeper|keyblade
Oblivion|keyblade
Lady Luck|keyblade
Wishing Star|keyblade
Ultima Weapon|keyblade
Diamond Dust|keyblade
One-Winged Angel|keyblade
Mage's Staff|staff
Morning Star|staff
Shooting Star|staff
Magus Staff|staff
Wisdom Staff|staff
Warhammer|staff
Silver Mallet|staff
Grand Mallet|staff
Lord Fortune|staff
Violetta|staff
Dream Rod (Donald)|staff
Save the Queen|staff
Wizard's Relic|staff
Meteor Strike|staff
Fantasista|staff
Unknown Donald Weapon|staff
Knight's Shield|shield
Mythril Shield|shield
Onyx Shield|shield
Stout Shield|shield
Golem Shield|shield
Adamant Shield|shield
Smasher|shield
Gigas Fist|shield
Genji Shield|shield
Herc's Shield|shield
Dream Shield (Goofy)|shield
Save the King|shield
Defender|shield
Mighty Shield|shield
Seven Elements|shield
Unknown Goofy Weapon|shield
Spear|weapon
No Weapon (Pooh)|weapon
Scimitar|weapon
No Weapon (Ariel)|weapon
No Weapon (Jack)|weapon
Dagger|weapon
Claws|weapon
Tent|boost
Camping Set|boost
Cottage|boost
Unused 91|unused
Unused 92|unused
Unused 93|unused
Unused 94|unused
Ansem's Report 11|report
Ansem's Report 12|report
Ansem's Report 13|report
Power Up|boost
Defense Up|boost
AP Up|boost
Serenity Power|synthesis
Dark Matter|synthesis
Mythril Stone|synthesis
Fire Arts|recipe
Blizzard Arts|recipe
Thunder Arts|recipe
Cure Arts|recipe
Gravity Arts|recipe
Stop Arts|recipe
Aero Arts|recipe
Shiitank Rank|recipe
Matsutake Rank|recipe
Mystery Mold|recipe
Ansem's Report 1|report
Ansem's Report 2|report
Ansem's Report 3|report
Ansem's Report 4|report
Ansem's Report 5|report
Ansem's Report 6|report
Ansem's Report 7|report
Ansem's Report 8|report
Ansem's Report 9|report
Ansem's Report 10|report
Khama Vol. 8|keyitem
Salegg Vol. 6|keyitem
Azal Vol. 3|keyitem
Mava Vol. 3|keyitem
Mava Vol. 6|keyitem
Theon Vol. 6|keyitem
Nahara Vol. 5|keyitem
Hafet Vol. 4|keyitem
Empty Bottle|keyitem
Old Book|keyitem
Emblem Piece|keyitem
Emblem Piece 2|keyitem
Emblem Piece 3|keyitem
Emblem Piece 4|keyitem
Log|keyitem
Cloth|keyitem
Rope|keyitem
Seagull Egg|keyitem
Fish|keyitem
Mushroom|keyitem
Coconut|keyitem
Drinking Water|keyitem
Navi-G Piece 1|keyitem
Navi-G Piece 2|keyitem
Navi-Gummi 1|keyitem
Navi-G Piece 3|keyitem
Navi-G Piece 4|keyitem
Navi-Gummi 2|keyitem
Watergleam|summon
Naturespark|summon
Fireglow|summon
Earthshine|summon
Crystal Trident|keyitem
Postcard|keyitem
Torn Page 1|keyitem
Torn Page 2|keyitem
Torn Page 3|keyitem
Torn Page 4|keyitem
Torn Page 5|keyitem
Slide 1|keyitem
Slide 2|keyitem
Slide 3|keyitem
Slide 4|keyitem
Slide 5|keyitem
Slide 6|keyitem
Footprints|keyitem
Claw Marks|keyitem
Stench|keyitem
Antenna|keyitem
Forget-Me-Not|keyitem
Jack-In-The-Box|keyitem
Entry Pass|keyitem
Hero License|keyitem
Pretty Stone|synthesis
Unused E8|unused
Lucid Shard|synthesis
Lucid Gem|synthesis
Lucid Crystal|synthesis
Spirit Shard|synthesis
Spirit Gem|synthesis
Power Shard|synthesis
Power Gem|synthesis
Power Crystal|synthesis
Blaze Shard|synthesis
Blaze Gem|synthesis
Frost Shard|synthesis
Frost Gem|synthesis
Thunder Shard|synthesis
Thunder Gem|synthesis
Shiny Crystal|synthesis
Bright Shard|synthesis
Bright Gem|synthesis
Bright Crystal|synthesis
Mystery Goo|synthesis
Gale|synthesis
Mythril Shard|synthesis
Mythril|synthesis
Orichalcum|synthesis
""".strip()

EQUIPMENT = tuple(
    {"id": item_id, "name": row.split("|", 1)[0], "category": row.split("|", 1)[1]}
    for item_id, row in enumerate(_EQUIPMENT_ROWS.splitlines())
)

if len(EQUIPMENT) != 256:
    raise RuntimeError(f"KH1 equipment table must contain 256 entries, got {len(EQUIPMENT)}")

EQUIPMENT_BY_ID = {item["id"]: item for item in EQUIPMENT}
KEYBLADES = tuple(item for item in EQUIPMENT if item["category"] == "keyblade")

WORLDS = (
    (0x00, "Dive into the Heart"),
    (0x01, "Destiny Islands"),
    (0x02, "Disney Castle"),
    (0x03, "Traverse Town"),
    (0x04, "Wonderland"),
    (0x05, "Deep Jungle"),
    (0x06, "100 Acre Wood"),
    (0x07, "Unused/Crash 07"),
    (0x08, "Agrabah"),
    (0x09, "Atlantica"),
    (0x0A, "Halloween Town"),
    (0x0B, "Olympus Coliseum"),
    (0x0C, "Monstro"),
    (0x0D, "Neverland"),
    (0x0E, "Unused/Crash 0E"),
    (0x0F, "Hollow Bastion"),
    (0x10, "End of the World"),
)

WORLD_BY_ID = dict(WORLDS)
