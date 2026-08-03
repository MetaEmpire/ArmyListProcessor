class Army:
    def __init__(self, units):
        self.units = units
        self.army_rules = []
        self.stratagems = []
        self.disposition = ""

    def __str__(self):
        return ", ".join(str(unit) for unit in self.units)


class Unit:
    def __init__(self, name, models, model_profiles, weapon_profiles, abilities, keywords):
        self.name = name
        self.models = models
        self.model_profiles = {}
        self.weapon_profiles = {}
        self.abilities = abilities
        self.keywords = keywords
        self.leadable_units = []

    def __str__(self):
        return self.name

class Model:
    def __init__(self, name, count, profile, weapons):
        self.name = name
        self.count = count
        self.profile = profile # this will be type ModelProfile
        self.weapons = {} # dictionary of weapon names as the key and their count as value
        self.abilities = {}

    def __str__(self):
        return self.name

# model profile, see note below about weapon class being a weapon profile. consider renaming to include word "profile"
class ModelProfile:
    def __init__(self, name, move, toughness, save, wounds, leadership, objective_control, invulnerable_save, number = 0):

        self.name = name
        self.move = move
        self.toughness = toughness
        self.save = save
        self.wounds = wounds
        self.leadership = leadership
        self.objective_control = objective_control
        self.invulnerable_save = invulnerable_save

    def __str__(self):
        return self.name

# conceptually this is a weapon profile, not an individual weapon that an individual model would have.
class WeaponProfile:
    def __init__(self, name, range, attacks, skill, strength, armor_piercing, damage, abilities):
        self.name = name
        self.range = range
        self.attacks = attacks
        self.skill = skill
        self.strength = strength
        self.armor_piercing = armor_piercing
        self.damage = damage
        self.abilities = abilities

    def __str__(self):
        return self.name
