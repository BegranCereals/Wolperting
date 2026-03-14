import json

class Character:
    def __init__(self):
        self.name = "Neuer Held"
        self.class_name = "Abenteurer"
        self.level = 1
        self.race = "Unbekannt"
        self.hp_max = 10
        self.hp_current = 10
        self.ac = 10
        self.initiative = 0
        self.stats = {
            "Stärke": 10, "Geschicklichkeit": 10, "Konstitution": 10,
            "Intelligenz": 10, "Weisheit": 10, "Charisma": 10
        }

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        char = cls()
        char.__dict__.update(data)
        return char
