# Wir importieren den Bauplan aus der models.py
from models import Race

# ==========================================
# 1. DIE ZWERGE (Dwarves)
# ==========================================
dwarf = Race(name="Dwarf", speed=25)
dwarf.ability_bonuses = {"Con": 2}
dwarf.languages = ["Common", "Dwarvish"]
dwarf.traits = {
    "Darkvision": "You can see in dim light within 60 feet as if it were bright light.",
    "Dwarven Resilience": "You have advantage on saving throws against poison, and resistance against poison damage."
}
dwarf.proficiencies["weapons"] = ["Battleaxe", "Handaxe", "Light Hammer", "Warhammer"]

# Unterrassen für den Zwerg
hill_dwarf = Race(name="Hill Dwarf", speed=25)
hill_dwarf.ability_bonuses = {"Wis": 1}
hill_dwarf.traits = {
    "Dwarven Toughness": "Your hit point maximum increases by 1, and it increases by 1 every time you gain a level."
}

mountain_dwarf = Race(name="Mountain Dwarf", speed=25)
mountain_dwarf.ability_bonuses = {"Str": 2}
mountain_dwarf.proficiencies["armor"] = ["Light Armor", "Medium Armor"]

# Unterrassen an die Hauptrasse koppeln
dwarf.add_subrace(hill_dwarf)
dwarf.add_subrace(mountain_dwarf)


# ==========================================
# 2. DIE ELFEN (Elves)
# ==========================================
elf = Race(name="Elf", speed=30)
elf.ability_bonuses = {"Dex": 2}
elf.languages = ["Common", "Elvish"]
elf.traits = {
    "Darkvision": "You can see in dim light within 60 feet as if it were bright light.",
    "Keen Senses": "You have proficiency in the Perception skill.",
    "Fey Ancestry": "You have advantage on saving throws against being charmed, and magic can't put you to sleep."
}

# Unterrassen für den Elfen
high_elf = Race(name="High Elf", speed=30)
high_elf.ability_bonuses = {"Int": 1}
high_elf.proficiencies["weapons"] = ["Longsword", "Shortsword", "Shortbow", "Longbow"]
high_elf.traits = {
    "Cantrip": "You know one cantrip of your choice from the wizard spell list."
}

wood_elf = Race(name="Wood Elf", speed=35) # Waldelfen sind schneller!
wood_elf.ability_bonuses = {"Wis": 1}
wood_elf.proficiencies["weapons"] = ["Longsword", "Shortsword", "Shortbow", "Longbow"]
wood_elf.traits = {
    "Mask of the Wild": "You can attempt to hide even when you are only lightly obscured by foliage, heavy rain, or mist."
}

# Unterrassen an die Hauptrasse koppeln
elf.add_subrace(high_elf)
elf.add_subrace(wood_elf)


# ==========================================
# CENTRAL DATABASE LIST
# ==========================================
# Diese Liste speichert alle Haupt-Rassen. Das ist perfekt für dein späteres GUI!
ALL_RACES = [dwarf, elf]