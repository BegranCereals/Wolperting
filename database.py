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
# 3. DIE HALBLINGE (Halflings)
# ==========================================
halfling = Race(name="Halfling", speed=25, size="Small")
halfling.ability_bonuses = {"Dex": 2}
halfling.languages = ["Common", "Halfling"]
halfling.traits = {
    "Lucky": "When you roll a 1 on the d20 for an attack roll, ability check, or saving throw, you can reroll the die and must use the new roll.",
    "Brave": "You have advantage on saving throws against being frightened."
}

lightfoot_halfling = Race(name="Lightfoot Halfling", speed=25, size="Small")
lightfoot_halfling.ability_bonuses = {"Cha": 1}
lightfoot_halfling.traits = {
    "Naturally Stealthy": "You can attempt to hide even when you are obscured only by a creature that is at least one size larger than you."
}

stout_halfling = Race(name="Stout Halfling", speed=25, size="Small")
stout_halfling.ability_bonuses = {"Con": 1}
stout_halfling.traits = {
    "Stout Resilience": "You have advantage on saving throws against poison, and resistance against poison damage."
}

halfling.add_subrace(lightfoot_halfling)
halfling.add_subrace(stout_halfling)


# ==========================================
# 4. DIE MENSCHEN (Humans)
# ==========================================
human = Race(name="Human", speed=30)
# Menschen bekommen +1 auf JEDES Attribut (Standard-Regel)
human.ability_bonuses = {"Str": 1, "Dex": 1, "Con": 1, "Int": 1, "Wis": 1, "Cha": 1}
human.languages = ["Common", "One extra language of your choice"]


# ==========================================
# 5. DIE DRACHENGEBORENEN (Dragonborn)
# ==========================================
dragonborn = Race(name="Dragonborn", speed=30)
dragonborn.ability_bonuses = {"Str": 2, "Cha": 1}
dragonborn.languages = ["Common", "Draconic"]
dragonborn.traits = {
    "Draconic Ancestry": "You choose one type of dragon, which determines your breath weapon and damage resistance.",
    "Breath Weapon": "You can use your action to exhale destructive energy determined by your draconic ancestry.",
    "Damage Resistance": "You have resistance to the damage type associated with your draconic ancestry."
}


# ==========================================
# 6. DIE GNOME (Gnomes)
# ==========================================
gnome = Race(name="Gnome", speed=25, size="Small")
gnome.ability_bonuses = {"Int": 2}
gnome.languages = ["Common", "Gnomish"]
gnome.traits = {
    "Gnome Cunning": "You have advantage on all Intelligence, Wisdom, and Charisma saving throws against magic."
}

rock_gnome = Race(name="Rock Gnome", speed=25, size="Small")
rock_gnome.ability_bonuses = {"Con": 1}
rock_gnome.traits = {
    "Artificer's Lore": "Whenever you make an Intelligence (History) check related to magic items, alchemical objects, or technological devices, you can add twice your proficiency bonus.",
    "Tinker": "You have proficiency with artisan's tools (tinker's tools). You can use them to construct tiny clockwork devices."
}

gnome.add_subrace(rock_gnome)


# ==========================================
# 7. DIE HALB-ELFEN (Half-Elves)
# ==========================================
half_elf = Race(name="Half-Elf", speed=30)
half_elf.ability_bonuses = {"Cha": 2, "Choice 1": 1, "Choice 2": 1} # Nutzer wählt später zwei weitere +1
half_elf.languages = ["Common", "Elvish", "One extra language of your choice"]
half_elf.traits = {
    "Fey Ancestry": "You have advantage on saving throws against being charmed, and magic can't put you to sleep.",
    "Skill Versatility": "You gain proficiency in two skills of your choice."
}


# ==========================================
# 8. DIE HALB-ORKS (Half-Orcs)
# ==========================================
half_orc = Race(name="Half-Orc", speed=30)
half_orc.ability_bonuses = {"Str": 2, "Con": 1}
half_orc.languages = ["Common", "Orc"]
half_orc.traits = {
    "Menacing": "You gain proficiency in the Intimidation skill.",
    "Relentless Endurance": "When you are reduced to 0 hit points but not killed outright, you can drop to 1 hit point instead (1/long rest).",
    "Savage Attacks": "When you score a critical hit, you can roll one of the weapon’s damage dice one additional time."
}


# ==========================================
# 9. DIE TIEFLINGE (Tieflings)
# ==========================================
tiefling = Race(name="Tiefling", speed=30)
tiefling.ability_bonuses = {"Cha": 2, "Int": 1}
tiefling.languages = ["Common", "Infernal"]
tiefling.traits = {
    "Darkvision": "You can see in dim light within 60 feet as if it were bright light.",
    "Hellish Resistance": "You have resistance to fire damage.",
    "Infernal Legacy": "You know the Thaumaturgy cantrip. (More spells unlocked at higher levels)."
}
# ==========================================
# CENTRAL DATABASE LIST
# ==========================================
# Diese Liste speichert alle Haupt-Rassen. Das ist perfekt für dein späteres GUI!
ALL_RACES = [dwarf, elf,halfling, human, dragonborn, gnome, half_elf, half_orc, tiefling]