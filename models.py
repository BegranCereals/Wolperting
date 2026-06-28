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