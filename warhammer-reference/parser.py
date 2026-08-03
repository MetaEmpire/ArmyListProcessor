from typing import Any

from models import Army, Unit, Model, ModelProfile, WeaponProfile


def find_model_profile(name, profiles):
    if name in profiles:
        return profiles[name]
    else:
        truncated_name = name.split(' w')[0]  # dropping common name suffix of "w/ .... "
        try:
            return profiles[truncated_name]
        except KeyError:
            print(f"Cannot associate this model name with a known model profile: {name}")


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

        new_unit = Unit(
            unit_data['name'],
            models,
            model_profiles,
            weapon_profiles,
            {},
            []
        )

        units.append(new_unit)

    # end unit scope iteration

    return Army(units)


def parse_weapon_profiles(weapons_json):
    weapon_profiles = {}
    for weapon_profile_name, weapon_profile_data in weapons_json.items():
        weapon_profiles[weapon_profile_name] = parse_weapon_profile(weapon_profile_data)
    return weapon_profiles

def parse_model_profiles(model_profiles_json):
    model_profiles = {}
    for model_profile_name, model_profile_data in model_profiles_json.items():
        model_profiles[model_profile_name] = parse_model_profile(model_profile_data)
    return model_profiles


def parse_model(model_data, model_profiles):
    weapons = {}

    for weapon in model_data['weapons']:
        weapons[weapon['name']] = weapon['number']

    return Model(
        model_data['name'],
        model_data['number'],
        find_model_profile(model_data['name'], model_profiles),
        weapons
    )


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
