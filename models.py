class Race:
    def __init__(self, name, speed, size="Medium"):
        self.name = name
        self.speed = speed
        self.size = size

        # Dictionaries für veränderliche Werte
        self.ability_bonuses = {}  # z.B. {"Con": 2}

        # Listen und Wörterbücher für Eigenschaften und Spezialisierungen
        self.languages = []  # z.B. ["Common", "Dwarvish"]
        self.traits = {}  # z.B. {"Darkvision": "Beschreibung..."}
        self.proficiencies = {
            "weapons": [],
            "armor": [],
            "tools": []
        }

        # Hier speichern wir die Unterrassen direkt als Liste von weiteren Race-Objekten!
        self.subraces = []

    def add_subrace(self, subrace_object):
        """Fügt dieser Hauptrasse eine Unterrasse hinzu."""
        self.subraces.append(subrace_object)

    def get_final_stats(self, chosen_subrace=None):
        """Rechnet die Boni der Hauptrasse und der Unterrasse zusammen."""
        final_bonuses = self.ability_bonuses.copy()
        final_languages = list(self.languages)
        final_traits = self.traits.copy()

        if chosen_subrace:
            # Boni addieren
            for stat, value in chosen_subrace.ability_bonuses.items():
                final_bonuses[stat] = final_bonuses.get(stat, 0) + value
            # Sprachen erweitern
            for lang in chosen_subrace.languages:
                if lang not in final_languages:
                    final_languages.append(lang)
            # Traits (Eigenschaften) zusammenführen
            final_traits.update(chosen_subrace.traits)

        return {
            "bonuses": final_bonuses,
            "languages": final_languages,
            "traits": final_traits,
            "speed": chosen_subrace.speed if chosen_subrace and chosen_subrace.speed else self.speed
        }

class RPGClass:
        def __init__(self, name, hit_die):
            self.name = name
            self.hit_die = hit_die  # z.B. 10 für W10, 8 für W8

            # Start-Ressourcen und Kompetenzen
            self.proficiencies = {
                "armor": [],
                "weapons": [],
                "saving_throws": []  # z.B. ["Str", "Con"]
            }

            # Eine Liste für Klassen-Features auf Level 1
            self.features = {}  # z.B. {"Second Wind": "Beschreibung..."}

            # Startausrüstung (später nützlich)
            self.starting_equipment = []

        def get_starting_hp(self, con_modifier):
            """Berechnet die Start-HP auf Level 1 anhand des Konstitutions-Modifikators."""
            return self.hit_die + con_modifier
class RPGBackground:
    def __init__(self, name, feature_name, feature_description):
        self.name = name
        self.feature_name = feature_name
        self.feature_description = feature_description

        # Was der Hintergrund dem Charakter schenkt
        self.skill_proficiencies = []  # z.B. ["Insight", "Religion"]
        self.languages = []  # Zusätzliche Sprachen
        self.starting_equipment = []  # z.B. ["A pouch with 15gp"] #        }


class Character:
    def __init__(self, name):
        self.name = name

        # Die 6 Basis-Attribute (Standardmäßig alle auf 10)
        self.base_attributes = {
            "Str": 10, "Dex": 10, "Con": 10,
            "Int": 10, "Wis": 10, "Cha": 10
        }

        # Hier speichern wir die gewählten Bausteine (Objekte)
        self.race = None
        self.subrace = None
        self.rpg_class = None
        self.background = None

        self.level = 1

    def calculate_modifier(self, score):
        """Berechnet den D&D-Modifikator für einen Attributswert (z.B. 14 -> +2)."""
        return (score - 10) // 2

    def get_final_stats(self):
        """Führt alle Daten von Rasse, Klasse und Hintergrund zusammen."""
        # 1. Attribute berechnen (Basis + Rassenboni)
        final_attributes = self.base_attributes.copy()
        if self.race:
            # Hole die kombinierten Boni aus der Rassen-Logik
            race_stats = self.race.get_final_stats(self.subrace)
            for stat, bonus in race_stats["bonuses"].items():
                if stat in final_attributes:
                    final_attributes[stat] += bonus
                # Falls der Bonus ein variabler "Choice"-Bonus ist (z.B. beim Halb-Elf):
                else:
                    final_attributes[stat] = bonus

        # 2. Modifikatoren berechnen
        modifiers = {stat: self.calculate_modifier(val) for stat, val in final_attributes.items()}

        # 3. Lebenspunkte (HP) berechnen
        con_mod = modifiers["Con"]
        hit_points = 0
        if self.rpg_class:
            hit_points = self.rpg_class.get_starting_hp(con_mod)

        # 4. Sprachen, Traits und Proficiencies sammeln
        languages = []
        traits = {}
        proficiencies = {"armor": [], "weapons": [], "skills": []}

        if self.race:
            r_stats = self.race.get_final_stats(self.subrace)
            languages.extend(r_stats["languages"])
            traits.update(r_stats["traits"])
            proficiencies["weapons"].extend(self.race.proficiencies["weapons"])
            proficiencies["armor"].extend(self.race.proficiencies["armor"])

        if self.rpg_class:
            traits.update(self.rpg_class.features)
            proficiencies["weapons"].extend(self.rpg_class.proficiencies["weapons"])
            proficiencies["armor"].extend(self.rpg_class.proficiencies["armor"])

        if self.background:
            proficiencies["skills"].extend(self.background.skill_proficiencies)
            if hasattr(self.background, 'languages'):
                languages.extend(self.background.languages)

        return {
            "name": self.name,
            "level": self.level,
            "attributes": final_attributes,
            "modifiers": modifiers,
            "hp": hit_points,
            "languages": list(set(languages)),  # set() entfernt doppelte Einträge
            "traits": traits,
            "proficiencies": proficiencies
        }