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

    def __str__(self):
        return self.name

# model profile, see note below about weapon class being a weapon profile. consider renaming to include word "profile"
class ModelProfile:
    def __init__(self, name, move, toughness, save, wounds, leadership, objective_control, invulnerable_save, weapons, number):
        self.name = name
        self.move = move
        self.toughness = toughness
        self.save = save
        self.wounds = wounds
        self.leadership = leadership
        self.objective_control = objective_control
        self.invulnerable_save = invulnerable_save
        self.weapons = weapons
        self.number = number

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
