# Wir importieren den Bauplan aus der models.py
from models import Race, RPGClass, RPGBackground


# ==========================================
# D&D HINTERGRÜNDE (Backgrounds)
# ==========================================

# 1. DER AKOLITH (Acolyte) - Im Tempel aufgewachsen
acolyte = RPGBackground(
    name="Acolyte",
    feature_name="Shelter of the Faithful",
    feature_description="You and your companions can receive free healing and care at a temple of your faith."
)
acolyte.skill_proficiencies = ["Insight", "Religion"]
acolyte.languages = ["Two languages of your choice"]
acolyte.suggested_traits = [
    "I idolize a particular hero of my faith, and constantly refer to that person's deeds and example.",
    "I see omens in every event and action. The gods are trying to speak to us, we just need to listen."
]
acolyte.suggested_ideals = [
    "Faith. I trust that my deity will guide my actions. I have faith that if I work hard, things will go well.",
    "Charity. I always try to help those in need, no matter what the personal cost."
]
acolyte.suggested_bonds = [
    "I would die to recover an ancient relic of my faith that was lost long ago.",
    "I owe my life to the priest who took me in when my parents died."
]
acolyte.suggested_flaws = [
    "I judge others harshly, and myself even more harshly.",
    "I am suspicious of strangers and expect the worst of them."
]

# 2. DER KRIMINELLE (Criminal) - Diebe, Schmuggler, Halsabschneider
criminal = RPGBackground(
    name="Criminal",
    feature_name="Criminal Contact",
    feature_description="You have a reliable trustworthy contact who acts as your liaison to a network of other criminals."
)
criminal.skill_proficiencies = ["Deception", "Stealth"]
criminal.suggested_traits = [
    "I always have a plan for what to do when things go wrong.",
    "The best way to get me to do something is to tell me I can't do it."
]
criminal.suggested_ideals = [
    "Honor. I don't steal from others in the trade.",
    "Freedom. Chains are meant to be broken, as are those who would forge them."
]
criminal.suggested_bonds = [
    "I'm trying to pay off an old debt I owe to a generous benefactor.",
    "A share of my profits goes to support my family."
]
criminal.suggested_flaws = [
    "When I see something valuable, I can't think about anything but how to steal it.",
    "An innocent person is in prison for a crime that I committed. I'm okay with that."
]

# 3. DER VOLKSHELD (Folk Hero) - Aus dem einfachen Volk aufgestiegen
folk_hero = RPGBackground(
    name="Folk Hero",
    feature_name="Rustic Hospitality",
    feature_description="Since you come from the ranks of the common folk, you fit in among them with ease. You can find a place to hide or rest among commoners."
)
folk_hero.skill_proficiencies = ["Animal Handling", "Survival"]

# 4. DER ADLIGE (Noble) - Wohlhabend und einflussreich
noble = RPGBackground(
    name="Noble",
    feature_name="Position of Privilege",
    feature_description="Thanks to your noble birth, people are inclined to think the best of you. You are welcome in high society, and people assume you have the right to be where you are."
)
noble.skill_proficiencies = ["History", "Persuasion"]
noble.languages = ["One language of your choice"]

# 5. DER GELEHRTE (Sage) - Verbringt sein Leben in Bibliotheken
sage = RPGBackground(
    name="Sage",
    feature_name="Researcher",
    feature_description="When you attempt to learn or recall a piece of lore, if you do not know the info, you often know where and from whom you can obtain it."
)
sage.skill_proficiencies = ["Arcana", "History"]
sage.languages = ["Two languages of your choice"]


# ==========================================
# CENTRAL BACKGROUND LIST
# ==========================================
# Und auch hier: Eine zentrale Liste für unser späteres Web-Interface!
ALL_BACKGROUNDS = [acolyte, criminal, folk_hero, noble, sage]

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

# Wichtig: Wir müssen unseren neuen Bauplan oben aus den Models importieren!
# Ändere ganz oben in der Datei die Import-Zeile zu:
# from models import Race, RPGClass

# ==========================================
# D&D KLASSEN (Classes)
# ==========================================

# 1. DER KÄMPFER (Fighter)
fighter = RPGClass(name="Fighter", hit_die=10)
fighter.proficiencies["armor"] = ["All Armor", "Shields"]
fighter.proficiencies["weapons"] = ["Simple Weapons", "Martial Weapons"]
fighter.proficiencies["saving_throws"] = ["Str", "Con"]
fighter.features = {
    "Fighting Style": "You adopt a particular style of fighting as your specialty (e.g., Archery, Defense).",
    "Second Wind": "You have a limited well of stamina that you can draw on to protect yourself from harm. On your turn, you can use a bonus action to regain hit points equal to 1d10 + your fighter level."
}

# 2. DER MAGIER (Wizard)
wizard = RPGClass(name="Wizard", hit_die=6)
wizard.proficiencies["armor"] = ["None"]
wizard.proficiencies["weapons"] = ["Daggers", "Darts", "Slings", "Quarterstaffs", "Light Crossbows"]
wizard.proficiencies["saving_throws"] = ["Int", "Wis"]
wizard.features = {
    "Spellcasting": "You can cast arcane spells from the wizard spell list.",
    "Arcane Recovery": "Once per day when you finish a short rest, you can choose expended spell slots to recover."
}

# 3. DER SCHURKE (Rogue)
rogue = RPGClass(name="Rogue", hit_die=8)
rogue.proficiencies["armor"] = ["Light Armor"]
rogue.proficiencies["weapons"] = ["Simple Weapons", "Hand Crossbows", "Longswords", "Rapiers", "Shortswords"]
rogue.proficiencies["saving_throws"] = ["Dex", "Int"]
rogue.features = {
    "Expertise": "Your proficiency bonus is doubled for two of your skill proficiencies.",
    "Sneak Attack": "Once per turn, you can deal an extra 1d6 damage to one creature you hit with an attack if you have advantage on the attack roll."
}

# 4. DER KLERIKER (Cleric)
cleric = RPGClass(name="Cleric", hit_die=8)
cleric.proficiencies["armor"] = ["Light Armor", "Medium Armor", "Shields"]
cleric.proficiencies["weapons"] = ["Simple Weapons"]
cleric.proficiencies["saving_throws"] = ["Wis", "Cha"]
cleric.features = {
    "Spellcasting": "You can cast divine spells from the cleric spell list.",
    "Divine Domain": "You choose a domain related to your deity, which grants you domain spells and features."
}
# ==========================================
# WEITERE D&D KLASSEN (Classes)
# ==========================================

# 5. DER BARBAR (Barbarian)
barbarian = RPGClass(name="Barbarian", hit_die=12) # Höchste Hit Die im Spiel!
barbarian.proficiencies["armor"] = ["Light Armor", "Medium Armor", "Shields"]
barbarian.proficiencies["weapons"] = ["Simple Weapons", "Martial Weapons"]
barbarian.proficiencies["saving_throws"] = ["Str", "Con"]
barbarian.features = {
    "Rage": "On your turn, you can enter a rage as a bonus action, gaining advantages on Strength checks and resistance to bludgeoning, piercing, and slashing damage.",
    "Unarmored Defense": "While you are not wearing any armor, your Armor Class equals 10 + your Dexterity modifier + your Constitution modifier."
}

# 6. DER BARDE (Bard)
bard = RPGClass(name="Bard", hit_die=8)
bard.proficiencies["armor"] = ["Light Armor"]
bard.proficiencies["weapons"] = ["Simple Weapons", "Hand Crossbows", "Longswords", "Rapiers", "Shortswords"]
bard.proficiencies["saving_throws"] = ["Dex", "Cha"]
bard.features = {
    "Spellcasting": "You can cast arcane spells through your musical talent or artistic performance.",
    "Bardic Inspiration": "You can inspire others through stirring words or music. You can use a bonus action to give one creature a Bardic Inspiration die (1d6)."
}

# 7. DER DRUIDE (Druid)
druid = RPGClass(name="Druid", hit_die=8)
# Druiden tragen aus Prinzip keine Rüstung aus Metall
druid.proficiencies["armor"] = ["Light Armor", "Medium Armor", "Shields (non-metal)"]
druid.proficiencies["weapons"] = ["Clubs", "Daggers", "Darts", "Javelins", "Maces", "Quarterstaffs", "Scimitars", "Sickles", "Slings", "Spears"]
druid.proficiencies["saving_throws"] = ["Int", "Wis"]
druid.features = {
    "Spellcasting": "You can cast divine spells drawing from the power of nature.",
    "Druidic": "You know Druidic, the secret language of druids. You can speak the language and use it to leave hidden messages."
}

# 8. DER MÖNCH (Monk)
monk = RPGClass(name="Monk", hit_die=8)
monk.proficiencies["armor"] = ["None"]
monk.proficiencies["weapons"] = ["Simple Weapons", "Shortswords"]
monk.proficiencies["saving_throws"] = ["Str", "Dex"]
monk.features = {
    "Unarmored Defense": "While not wearing armor and not wielding a shield, your AC equals 10 + Dex modifier + Wis modifier.",
    "Martial Arts": "You can use Dexterity instead of Strength for the attack and damage rolls of your unarmed strikes and monk weapons."
}

# 9. DER PALADIN (Paladin)
paladin = RPGClass(name="Paladin", hit_die=10)
paladin.proficiencies["armor"] = ["All Armor", "Shields"]
paladin.proficiencies["weapons"] = ["Simple Weapons", "Martial Weapons"]
paladin.proficiencies["saving_throws"] = ["Wis", "Cha"]
paladin.features = {
    "Divine Sense": "The presence of strong evil registers on your senses like a noxious odor. As an action, you can detect celestial, fiend, or undead creatures.",
    "Lay on Hands": "Your blessed touch can heal wounds. You have a pool of healing power that replenishes when you take a long rest."
}

# 10. DER WALDLÄUFER (Ranger)
ranger = RPGClass(name="Ranger", hit_die=10)
ranger.proficiencies["armor"] = ["Light Armor", "Medium Armor", "Shields"]
ranger.proficiencies["weapons"] = ["Simple Weapons", "Martial Weapons"]
ranger.proficiencies["saving_throws"] = ["Str", "Dex"]
ranger.features = {
    "Favored Enemy": "You have significant experience studying, tracking, hunting, and even talking to a certain type of enemy.",
    "Natural Explorer": "You are particularly familiar with one type of natural environment and are adept at traveling and surviving in such regions."
}

# 11. DER ZAUBERER (Sorcerer)
sorcerer = RPGClass(name="Sorcerer", hit_die=6)
sorcerer.proficiencies["armor"] = ["None"]
sorcerer.proficiencies["weapons"] = ["Daggers", "Darts", "Slings", "Quarterstaffs", "Light Crossbows"]
sorcerer.proficiencies["saving_throws"] = ["Con", "Cha"]
sorcerer.features = {
    "Spellcasting": "An event in your past, or in the life of an ancestor, left an indelible mark on you, infusing you with arcane magic. You cast spells using Charisma.",
    "Sorcerous Origin": "Choose a sorcerous origin, which describes the source of your innate magical power (e.g., Draconic Bloodline)."
}

# 12. DER HEXENMEISTER (Warlock)
warlock = RPGClass(name="Warlock", hit_die=8)
warlock.proficiencies["armor"] = ["Light Armor"]
warlock.proficiencies["weapons"] = ["Simple Weapons"]
warlock.proficiencies["saving_throws"] = ["Wis", "Cha"]
warlock.features = {
    "Pact Magic": "Your arcane research and the magic bestowed upon you by your patron have given you facility with spells.",
    "Otherworldly Patron": "You have struck a bargain with an otherworldly being of your choice (e.g., The Fiend)."
}
# ==========================================
# CENTRAL CLASS LIST
# ==========================================
# Genau wie bei den Rassen, sammeln wir alle Klassen in einer zentralen Liste für das GUI!
ALL_CLASSES = [fighter, wizard, rogue, cleric,barbarian, bard, druid, monk, paladin, ranger, sorcerer, warlock]