#from typing import Any

from models import Army, Unit, Model, ModelProfile, WeaponProfile


def parse_army(json_data) -> Army:

    units = []
    #units = parse_units(json_data["armyData"]) # todo

    for unit_name, unit_data in json_data["armyData"].items():

        weapon_profiles = parse_weapon_profiles(unit_data['weapons'])

        model_profiles = parse_model_profiles(unit_data['modelProfiles'])

        models = []

        #for each model, associate model profiles and build model object
        for model_name, model_data in unit_data['models']['models'].items():
            current_model = parse_model(model_data, model_profiles)

            models.append(current_model)

        # end model scope iteration

        unit_abilities = parse_abilities(unit_data['abilities'])

        new_unit = Unit(
            unit_data['name'],
            models,
            model_profiles,
            weapon_profiles,
            unit_abilities,
            unit_data['keywords']
        )

        units.append(new_unit)

    # end unit scope iteration

    return Army(units)

# this helper function will return a profile based on a name match. If the name doesn't match it
# will try a truncated version of the original name. Example: "Guardsmen w/ Long Las" will be
# shortened to "Guardsmen" if the original name is not found.
def find_model_profile(name, profiles) -> ModelProfile:
    if name in profiles:
        return profiles[name]
    else:
        truncated_name = name.split(' w')[0]  # dropping common name suffix of "w/ .... "
        try:
            return profiles[truncated_name]
        except KeyError:
            raise ValueError(f"ModelProfile {truncated_name} not found")

def parse_weapon_profiles(weapons_json) -> dict[str, WeaponProfile]:
    weapon_profiles = {}
    for weapon_profile_name, weapon_profile_data in weapons_json.items():
        weapon_profiles[weapon_profile_name] = parse_weapon_profile(weapon_profile_data)
    return weapon_profiles

def parse_model_profiles(model_profiles_json) -> dict[str, ModelProfile]:
    model_profiles = {}
    for model_profile_name, model_profile_data in model_profiles_json.items():
        model_profiles[model_profile_name] = parse_model_profile(model_profile_data)
    return model_profiles

def parse_model(model_data, model_profiles) -> Model:
    weapons = {}

    for weapon in model_data['weapons']:
        weapons[weapon['name']] = weapon['number']

    return Model(
        model_data['name'],
        model_data['number'],
        find_model_profile(model_data['name'], model_profiles),
        weapons
    )


def parse_abilities(abilities_json) -> dict[str, str]:
    return_me = {}
    for ability_name, ability_data in abilities_json.items():
        #print(ability_name)
        #print(ability_data)
        return_me[ability_data['name']] = ability_data['desc']
    return return_me

def parse_model_profile(model_dict) -> ModelProfile:
    return_me = ModelProfile(
        model_dict['name'],
        model_dict['m'],
        model_dict['t'],
        model_dict['sv'],
        model_dict['w'],
        model_dict['ld'],
        model_dict['oc'],
        model_dict['insv'],
    )
    return return_me

def parse_weapon_profile(weapon_dict) -> WeaponProfile:
    #print(weapon_dict)
    return_me = WeaponProfile(
        weapon_dict['name'],
        weapon_dict['range'],
        weapon_dict['a'],
        weapon_dict['bsws'],
        weapon_dict['s'],
        weapon_dict['ap'],
        weapon_dict['d'],
        weapon_dict['shortAbilities']
    )
    #print(return_me)
    return return_me
