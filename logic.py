import json

class Character:
    def __init__(self, name="Neuer Held"):
        self.name = name
        # Grundwerte (können später per PDF erweitert werden)
        self.stats = {
            "Stärke": 10,
            "Geschick": 10,
            "Konstitution": 10,
            "Intelligenz": 10,
            "Weisheit": 10,
            "Charisma": 10
        }
        self.compendium_entries = [] # Hier landen später PDF-Extrakte

    def get_modifier(self, stat_name):
        value = self.stats.get(stat_name, 10)
        return (value - 10) // 2

    def to_dict(self):
        """Wandelt das Objekt in ein Dictionary für JSON um"""
        return {
            "name": self.name,
            "stats": self.stats,
            "entries": self.compendium_entries
        }

    @classmethod
    def from_dict(cls, data):
        """Erstellt ein Objekt aus einem Dictionary"""
        char = cls(data.get("name", "Unbekannt"))
        char.stats = data.get("stats", char.stats)
        char.compendium_entries = data.get("entries", [])
        return char

