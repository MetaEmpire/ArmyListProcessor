class Army:
    def __init__(self):
        self.units = []
        self.army_rules = []
        self.stratagems = []
        self.disposition = ""


class Unit:
    def __init__(self):
        self.name = ""
        self.model_profiles = []
        self.weapon_profiles = []
        self.abilities = []
        self.keywords = []
        self.leadable_units = []

    # return the name of the first model in the unit
    def __str__(self):
        return self.name

class Model:
    def __init__(self):
        self.name = ""
        self.move = ""
        self.toughness = ""
        self.save = ""
        self.wounds = ""
        self.leadership = ""
        self.objective_control = ""
        self.invulnerable_save = ""
        self.weapons = []

class Weapon:
    def __init__(self):
        self.name = ""
        self.range = ""
        self.attacks = ""
        self.skill = ""
        self.strength = ""
        self.armor_piercing = ""
        self.damage = ""
        self.abilities = []
