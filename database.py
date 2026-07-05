import json
import os
from models import Race, RPGClass, RPGBackground

ALL_RACES = []
ALL_CLASSES = []
ALL_BACKGROUNDS = []


def load_races_from_5etools():
    """Liest die races.json ein und speichert Rassen sowie deren Quellen (source) sauber ab."""
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

            # Buch-Kürzel herausholen (z.B. PHB, MPMM, DMG)
            source_val = r.get("source", "PHB")

            speed_val = r["speed"].get("walk", 30) if isinstance(r["speed"], dict) else r["speed"]
            if isinstance(speed_val, bool):
                speed_val = 30

            size_map = {"M": "Medium", "S": "Small", "L": "Large"}
            size = size_map.get(r.get("size", ["M"])[0], "Medium") if isinstance(r.get("size"), list) else size_map.get(
                r.get("size", "M"), "Medium")

            # Wir übergeben die Source direkt an das Objekt (vorausgesetzt dein Model unterstützt das jetzt)
            new_race = Race(name=r["name"], speed=speed_val, size=size, source=source_val)

            if "ability" in r and r["ability"]:
                for ability_set in r["ability"]:
                    if isinstance(ability_set, dict):
                        for attr, val in ability_set.items():
                            if isinstance(val, int):
                                new_race.ability_bonuses[attr.capitalize()] = val

            ALL_RACES.append(new_race)

            # Eindeutiger Key für die Zuordnung der Unterrassen (z.B. "Aasimar_DMG")
            unique_key = f"{r['name']}_{source_val}"
            race_dict[unique_key] = new_race
        except Exception:
            continue

    # Unterrassen sauber zuordnen
    for sub in raw_data.get("subrace", []):
        try:
            parent_race_name = sub.get("raceName")
            parent_source = sub.get("raceSource", "")
            unique_key = f"{parent_race_name}_{parent_source}"

            if unique_key in race_dict:
                parent_race = race_dict[unique_key]
                sub_source = sub.get("source", parent_source)

                new_subrace = Race(name=sub["name"], speed=parent_race.speed, size=parent_race.size, source=sub_source)
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
    """Liest die backgrounds.json ein und extrahiert Name, Source, Features und Tabellen."""
    file_path = os.path.join("data", "backgrounds.json")
    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    for bg in raw_data.get("background", []):
        try:
            if "name" not in bg:
                continue

            source_val = bg.get("source", "PHB")
            entries = bg.get("entries", [])
            feature_name = "Background Feature"
            feature_desc = "No description available."

            # Feature extrahieren
            for entry in entries:
                if isinstance(entry, dict) and entry.get("type") == "entries" and "Feature:" in entry.get("name", ""):
                    feature_name = entry.get("name", "Feature")
                    feature_desc = " ".join([str(e) for e in entry.get("entries", []) if isinstance(e, str)])

            new_bg = RPGBackground(name=bg["name"], feature_name=feature_name, feature_description=feature_desc,
                                   source=source_val)

            if "skillProficiencies" in bg and bg["skillProficiencies"]:
                for prof_set in bg["skillProficiencies"]:
                    for skill in prof_set.keys():
                        new_bg.skill_proficiencies.append(skill.capitalize())

            # --- NEU & KORRIGIERT: Tabellen rekursiv durchsuchen ---
            def scan_entries_for_tables(entry_list):
                for item in entry_list:
                    if not isinstance(item, dict):
                        continue

                    # Wenn es sich um eine Tabelle handelt
                    if item.get("type") == "table":
                        # Wir prüfen die Spaltenbeschriftungen (colLabels), da 'caption' oft fehlt
                        labels = [str(lbl).lower() for lbl in item.get("colLabels", [])]
                        rows = [r[1] for r in item.get("rows", []) if len(r) > 1 and isinstance(r[1], str)]

                        # Zuordnung basierend auf den Spaltennamen
                        if any("trait" in lbl for lbl in labels):
                            new_bg.suggested_traits = rows
                        elif any("ideal" in lbl for lbl in labels):
                            new_bg.suggested_ideals = rows
                        elif any("bond" in lbl for lbl in labels):
                            new_bg.suggested_bonds = rows
                        elif any("flaw" in lbl for lbl in labels):
                            new_bg.suggested_flaws = rows

                    # Wenn das Element verschachtelte Untereinträge hat, diese ebenfalls durchscannen
                    if "entries" in item and isinstance(item["entries"], list):
                        scan_entries_for_tables(item["entries"])

            # Starte die Suche in den Haupt-Entries
            scan_entries_for_tables(entries)

            ALL_BACKGROUNDS.append(new_bg)
        except Exception:
            continue

def load_classes_from_5etools():
    """Scannt den Ordner data/class/ nach allen Klassen-JSONs und liest sie dynamisch inklusive Source ein."""
    folder_path = os.path.join("data", "class")
    if not os.path.exists(folder_path):
        return

    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            for cl in raw_data.get("class", []):
                if "name" not in cl or "hd" not in cl:
                    continue

                source_val = cl.get("source", "PHB")
                hd_dict = cl["hd"]
                hit_die = hd_dict.get("faces", 8) if isinstance(hd_dict, dict) else 8

                new_class = RPGClass(name=cl["name"], hit_die=hit_die, source=source_val)

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

# Absicherungs-Fallbacks falls doch mal eine Datei fehlen sollte
if not ALL_RACES:
    ALL_RACES.append(Race(name="Human (Fallback)", speed=30, size="Medium", source="PHB"))
if not ALL_CLASSES:
    ALL_CLASSES.append(RPGClass("Fighter (Fallback)", 10, source="PHB"))
if not ALL_BACKGROUNDS:
    ALL_BACKGROUNDS.append(RPGBackground("Acolyte (Fallback)", "Feature", "Desc", source="PHB"))