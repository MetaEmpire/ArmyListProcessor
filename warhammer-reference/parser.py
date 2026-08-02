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

    for unit_name, unit_data in json_data["armyData"].items():
        #print(unit_name)
        #print(unit_data)

        #current_unit = Unit()

        models = []
        weapons = {}
        model_profiles = {}
        weapon_profiles = {}

        for weapon_profile_name, weapon_profile_data in unit_data['weapons'].items():
            #print(weapon_profile_name)
            #print(weapon_profile_data)
            weapon_profiles[weapon_profile_name] = parse_weapon_profile(weapon_profile_data)

        for model_profile_name, model_profile_data in unit_data['modelProfiles'].items():
            #print(model_profile_name)
            #print(model_profile_data)
            model_profiles[model_profile_name] = parse_model_profile(model_profile_data)

        #for each model, associate model profiles and build model object
        for model_name, model_data in unit_data['models']['models'].items():
            print(model_name)
            print(model_data)

            current_model = Model()

            current_model.name = model_data['name']
            current_model.count = model_data['number']

            # counting model profile matches, the only way to do that currently is by imperfectly using the name string
            current_model.profile = find_model_profile(model_data['name'], model_profiles)
            if not current_model.profile:
                continue # this most likely creates unusable output so we might as well exit,
                # but for troubleshooting it will be useful to identify any other problem models.

            for weapon in model_data['weapons']:
                current_model.weapons[weapon['name']] = weapon['number']

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
