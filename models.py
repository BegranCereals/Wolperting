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

        self.skill_proficiencies = []
        self.languages = []
        self.starting_equipment = []

        # NEU: Listen für die offiziellen Vorschlagstabellen
        self.suggested_traits = []
        self.suggested_ideals = []
        self.suggested_bonds = []
        self.suggested_flaws = []


class Character:
    def __init__(self, name):
        self.name = name

        self.base_attributes = {
            "Str": 10, "Dex": 10, "Con": 10,
            "Int": 10, "Wis": 10, "Cha": 10
        }

        self.race = None
        self.subrace = None
        self.rpg_class = None
        self.background = None
        self.level = 1

        # NEU: Persönlichkeitsmerkmale für die Spielbarkeit
        self.personality_traits = ""
        self.ideals = ""
        self.bonds = ""
        self.flaws = ""

    # ... (get_final_stats bleibt genau so, wie es ist!) ...



    def calculate_modifier(self, score):
        """Berechnet den D&D-Modifikator für einen Attributswert (z.B. 14 -> +2)."""
        return (score - 10) // 2

    def get_final_stats(self):
        """Führt alle Daten zusammen und schlüsselt auf, woher sie kommen."""
        # Basis-Attribute kopieren
        final_attributes = self.base_attributes.copy()

        # Aufschlüsselung der Boni für farbliche Markierung
        bonus_sources = {
            "Race": {},
            "Class": {},
            "Background": {}
        }

        if self.race:
            race_stats = self.race.get_final_stats(self.subrace)
            for stat, bonus in race_stats["bonuses"].items():
                if stat in final_attributes:
                    final_attributes[stat] += bonus
                    bonus_sources["Race"][stat] = bonus

        # Modifikatoren berechnen
        modifiers = {stat: self.calculate_modifier(val) for stat, val in final_attributes.items()}

        # HP berechnen
        con_mod = modifiers["Con"]
        hit_points = self.rpg_class.get_starting_hp(con_mod) if self.rpg_class else 0

        # Eigenschaften nach Quelle sortiert sammeln
        languages = {"Race": [], "Background": []}
        traits = {"Race": {}, "Class": {}}
        proficiencies = {
            "Race": {"weapons": [], "armor": [], "skills": []},
            "Class": {"weapons": [], "armor": [], "skills": []},
            "Background": {"weapons": [], "armor": [], "skills": []}
        }

        # Daten einsaugen
        if self.race:
            r_stats = self.race.get_final_stats(self.subrace)
            languages["Race"].extend(r_stats["languages"])
            traits["Race"].update(r_stats["traits"])
            proficiencies["Race"]["weapons"].extend(self.race.proficiencies["weapons"])
            proficiencies["Race"]["armor"].extend(self.race.proficiencies["armor"])

        if self.rpg_class:
            traits["Class"].update(self.rpg_class.features)
            proficiencies["Class"]["weapons"].extend(self.rpg_class.proficiencies["weapons"])
            proficiencies["Class"]["armor"].extend(self.rpg_class.proficiencies["armor"])

        if self.background:
            proficiencies["Background"]["skills"].extend(self.background.skill_proficiencies)
            if hasattr(self.background, 'languages'):
                languages["Background"].extend(self.background.languages)

        return {
            "name": self.name,
            "level": self.level,
            "attributes": final_attributes,
            "modifiers": modifiers,
            "hp": hit_points,
            "languages": languages,
            "traits": traits,
            "proficiencies": proficiencies,
            "bonus_sources": bonus_sources
        }

    def to_json(self):
        """Wandelt den Charakter in ein einfaches Wörterbuch zum Speichern um."""
        return {
            "name": self.name,
            "base_attributes": self.base_attributes,
            "race": self.race.name if self.race else None,
            "subrace": self.subrace.name if self.subrace else None,
            "rpg_class": self.rpg_class.name if self.rpg_class else None,
            "background": self.background.name if self.background else None,
            # NEU: Auch die Persönlichkeit mitspeichern!
            "personality_traits": self.personality_traits,
            "ideals": self.ideals,
            "bonds": self.bonds,
            "flaws": self.flaws
        }