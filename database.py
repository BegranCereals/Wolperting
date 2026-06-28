import json
import os
from models import Race, RPGClass, RPGBackground

ALL_RACES = []
ALL_CLASSES = []
ALL_BACKGROUNDS = []


def load_races_from_5etools():
    """Liest die races.json ein."""
    file_path = os.path.join("data", "races.json")
    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    race_dict = {}
    for r in raw_data.get("race", []):
        try:
            if "name" not in r or "speed" not in r:
                continue
            speed_val = r["speed"].get("walk", 30) if isinstance(r["speed"], dict) else r["speed"]
            size_map = {"M": "Medium", "S": "Small", "L": "Large"}
            size = size_map.get(r.get("size", ["M"])[0], "Medium") if isinstance(r.get("size"), list) else size_map.get(
                r.get("size", "M"), "Medium")

            new_race = Race(name=r["name"], speed=speed_val, size=size)

            if "ability" in r and r["ability"]:
                for ability_set in r["ability"]:
                    if isinstance(ability_set, dict):
                        for attr, val in ability_set.items():
                            if isinstance(val, int):
                                new_race.ability_bonuses[attr.capitalize()] = val

            ALL_RACES.append(new_race)
            race_dict[r["name"]] = new_race
        except Exception:
            continue

    for sub in raw_data.get("subrace", []):
        try:
            parent_race_name = sub.get("raceName")
            if parent_race_name in race_dict:
                parent_race = race_dict[parent_race_name]
                new_subrace = Race(name=sub["name"], speed=parent_race.speed, size=parent_race.size)
                if "ability" in sub and sub["ability"]:
                    for ability_set in sub["ability"]:
                        if isinstance(ability_set, dict):
                            for attr, val in ability_set.items():
                                if isinstance(val, int):
                                    new_subrace.ability_bonuses[attr.capitalize()] = val
                parent_race.add_subrace(new_subrace)
        except Exception:
            continue


def load_backgrounds_from_5etools():
    """Liest die backgrounds.json ein."""
    file_path = os.path.join("data", "backgrounds.json")
    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    for bg in raw_data.get("background", []):
        try:
            if "name" not in bg:
                continue
            entries = bg.get("entries", [])
            feature_name = "Background Feature"
            feature_desc = "No description available."
            for entry in entries:
                if isinstance(entry, dict) and entry.get("type") == "entries" and "Background Feature" in entry.get(
                        "name", ""):
                    feature_name = entry.get("name", "Feature")
                    feature_desc = " ".join([str(e) for e in entry.get("entries", []) if isinstance(e, str)])

            new_bg = RPGBackground(name=bg["name"], feature_name=feature_name, feature_description=feature_desc)

            if "skillProficiencies" in bg and bg["skillProficiencies"]:
                for prof_set in bg["skillProficiencies"]:
                    for skill in prof_set.keys():
                        new_bg.skill_proficiencies.append(skill.capitalize())

            if "data" in bg and isinstance(bg["data"], list):
                for table in bg["data"]:
                    if isinstance(table, dict) and table.get("type") == "table" and "caption" in table:
                        caption = table["caption"].lower()
                        rows = [r[1] for r in table.get("rows", []) if len(r) > 1 and isinstance(r[1], str)]
                        if "personality trait" in caption:
                            new_bg.suggested_traits = rows
                        elif "ideal" in caption:
                            new_bg.suggested_ideals = rows
                        elif "bond" in caption:
                            new_bg.suggested_bonds = rows
                        elif "flaw" in caption:
                            new_bg.suggested_flaws = rows

            ALL_BACKGROUNDS.append(new_bg)
        except Exception:
            continue


def load_classes_from_5etools():
    """Liest die classes.json ein und baut die Kernklassen."""
    file_path = os.path.join("data", "classes.json")
    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    for cl in raw_data.get("class", []):
        try:
            if "name" not in cl or "hd" not in cl:
                continue

            # Trefferwürfel auslesen (ist ein Dict bei 5etools, z.B. {"number": 1, "faces": 10})
            hd_dict = cl["hd"]
            hit_die = hd_dict.get("faces", 8) if isinstance(hd_dict, dict) else 8

            # Klasse erstellen
            new_class = RPGClass(name=cl["name"], hit_die=hit_die)

            # Rettungswürfe (Saving Throws) auslesen und in Proficiencies stopfen
            if "proficiency" in cl and isinstance(cl["proficiency"], list):
                clean_saves = [stat.capitalize() for stat in cl["proficiency"]]
                new_class.proficiencies["saving_throws"] = clean_saves

            ALL_CLASSES.append(new_class)
        except Exception:
            continue


# --- STARTEN ALLER AUTOMATISCHEN LOADER ---
load_races_from_5etools()
load_backgrounds_from_5etools()
load_classes_from_5etools()

# Absicherungs-Fallbacks falls doch mal eine Datei fehlt
if not ALL_RACES:
    ALL_RACES.append(Race(name="Human (Fallback)", speed=30, size="Medium"))
if not ALL_CLASSES:
    ALL_CLASSES.append(RPGClass("Fighter (Fallback)", 10))
if not ALL_BACKGROUNDS:
    ALL_BACKGROUNDS.append(RPGBackground("Acolyte (Fallback)", "Feature", "Desc"))