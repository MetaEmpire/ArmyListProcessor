from models import Army, Unit, ModelProfile, WeaponProfile

def parse_army(json_data) -> Army:

    for unit_name, unit_data in json_data["armyData"].items():
        #print(unit_name)
        #print(unit_data)

        models = {}
        model_profiles = {}
        weapon_profiles = {}

        for model_profile_name, model_profile_data in unit_data['modelProfiles'].items():
            print(model_profile_name)
            print(model_profile_data)

            model_profiles[model_profile_name] = parse_model_profile(model_profile_data)

        # for each of the model profiles, look up their sub section of weapon names+counts. add that to the profile.
        # ideally i wouldnt do two separate for loops for this... if i go up 1 level in scope i can probably see everything
        # to make the model_profile with all the fields i need. I need the above weapons and the model count.
        # note: still try to handle the parser ONLY the section it needs. even if i back the for loop scope up 1 level

        for weapon_profile_name, weapon_profile_data in unit_data['weapons'].items():
            #print(weapon_profile_name)
            #print(weapon_profile_data)
            weapon_profiles[weapon_profile_name] = parse_weapon(weapon_profile_data)


    # todo, return Army object.

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
        {},
        1
    )
    return return_me

def parse_weapon(weapon_dict) -> WeaponProfile:
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
