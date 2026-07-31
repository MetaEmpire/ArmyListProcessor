
def get_army_lists_from_json(json_data):

    units = []

    for unit in json_data['order']:
        units.append(json_data['armyData'][unit])

    return units, [], []

