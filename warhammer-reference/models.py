class Army:
    def __init__(self):
        self.units = []
        self.army_rules = []
        self.stratagems = []


class Unit:
    def __init__(self):
        self.models = []
        self.weapon_profiles = []
        self.abilities = []
        self.keywords = []
        self.can_lead = []

class Model:
    def __init__(self):
        self.stats = []
        self.weapons = []
