# ArmyListProcessor.py
# a utility for processing wargaming profiles into a cleaner/shorter reference
#
# pseudocode:
# read each row, determine if it's a section header row. If it is, change the current state
# process each non-header row according to the current state
# process units to sort them, remove duplicates, and condense verbose abilities
# write each unit out in rows with some extra columns that makes the output easier to format in a spreadsheet

# example data from CSV input:
##['Unit', 'M', 'T', 'SV', 'W', 'LD', 'OC', '']
##['Cadre Fireblade', '6"', '3', '4+', '3', '7+', '1', '']
##['Ranged Weapons', 'Range', 'A', 'BS', 'S', 'AP', 'D', 'Keywords']
##['Fireblade pulse rifle', '30"', '1', '3+', '5', '0', '2', 'Rapid Fire 1']
##['Twin pulse carbine (x2)', '20"', '2', '5+', '5', '0', '1', 'Assault, Twin-linked']
##['Melee Weapons', 'Range', 'A', 'WS', 'S', 'AP', 'D', 'Keywords']
##['Close combat weapon', 'Melee', '3', '4+', '3', '0', '1', '-']

import re
import csv

INPUT_FILE_NAME = "gsheetexport.csv"
OUTPUT_FILE_NAME = "pyexport.csv"

# a unit represented by a collection of named lists, based on the rows from the input format
class Unit:
    def __init__(self):
        self.unit_model_stat_rows = []
        self.ranged_rows = []
        self.melee_rows = []
        self.ability_rows = []

    # return the name of the first model in the unit
    def __str__(self):
        return self.unit_model_stat_rows[0][0]

# Regex helper utility, prints information about the regex match
def print_regex_match(re_match, original_string):
    print(f"String: {original_string}")
    print(f"Match: {re_match.group()}")
    print(f"Span: {re_match.span()}")

def try_converting_to_ints(list_of_strings):
    return_me = []
    for string in list_of_strings:
        try:
            stripped_string = string.strip("+\"")
            new_value = int(stripped_string)
            return_me.append(new_value)
        except (ValueError, AttributeError): # if we can't cast, keep the original string
            return_me.append(string)
            #print(f"One of the expected errors occurred while trying to cast a string to an int: {string}")
    return return_me

def handle_garbage_row(unit, row):
    pass
def handle_name_row(unit, row):
    # cast everything that can be to an int
    new_row = try_converting_to_ints(row)
    unit.unit_model_stat_rows.append(new_row)
def handle_ranged_row(unit, row):
    # if row contains the pistol keyword move the weapon into the melee list
    new_row = try_converting_to_ints(row)
    if "pistol" in new_row[7].lower():
        handle_melee_row(unit, new_row)
    else:
        unit.ranged_rows.append(new_row)
def handle_melee_row(unit, row):
    new_row = try_converting_to_ints(row)
    unit.melee_rows.append(new_row)

ABILITY_FILTER = ["Fly", "Markerlight", "Stealth", "Scouts 7", "Deep Strike", "Deadly Demise D3"]

def handle_ability_row(unit, row):
    if row[0].lower() in ["rules", "categories"]:
        ability_re = re.compile(r'fly|Markerlight|Stealth|Deep Strike|Deadly Demise D?\d|Scouts \d+', re.IGNORECASE)
        matches = re.findall(ability_re, "".join(row))
        if len(matches) > 0:
            unit.ability_rows.append([", ".join(matches), row[1]])
    # if row has nothing in row 2, dump it
    elif row[1] == "":
        pass
    else:
        unit.ability_rows.append(row)


def parse_input_to_units(input_file):
    return_me = []

    # function map (dict?)
    SECTION_MAP = {
        "Move Up": handle_garbage_row,
        "Unit": handle_name_row,
        "Ranged Weapons": handle_ranged_row,
        "Melee Weapons": handle_melee_row,
        "Abilities": handle_ability_row,
    }

    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.reader(file)

        current_unit = Unit()
        handler = handle_garbage_row

        for row in csv_reader:

            # this signifies that the current unit is done, and we're on a new unit
            if handler != handle_garbage_row and row[0].lower() == "move up":
                return_me.append(current_unit)
                current_unit = Unit()
                handler = handle_garbage_row

            # if we detect a header row change the handler state
            if row[0] in SECTION_MAP:
                handler = SECTION_MAP[row[0]]
                continue

            # if we aren't in a "header" row, process the line according to the current handler.
            else:
                handler(current_unit,row)

    return return_me

def remove_duplicate_models(units_with_duplicates):
    return_me = []

    for unit in units_with_duplicates:
        previous_stats = list(range(6))
        removed_model_names = ""

        # check to see if this unit even has duplicates to consider
        if len(unit.unit_model_stat_rows) > 1:
            new_model_list = []

            # iterate through each model row to see if it's different from the last
            for model in unit.unit_model_stat_rows:

                # if the stats are exactly as the previous model, skip this model row and remember the name
                if model[1:] == previous_stats:
                    removed_model_names += f" + {model[0]} "
                    continue
                else:
                    previous_stats = model[1:]
                    new_model_list.append(model)

            unit.unit_model_stat_rows = new_model_list
            unit.unit_model_stat_rows[0][0] += removed_model_names

        # end duplicate checking if block
        return_me.append(unit)

    return return_me


def write_list_to_csv(final_list):
    with open(OUTPUT_FILE_NAME, mode="w", newline="", encoding="utf-8") as out_file:
        out_writer = csv.writer(out_file)
        for row in final_list:
            out_writer.writerow(row)

def shift_abilities_rows(list_with_abilities_rows):
    pass


def add_symbols_to_rows(list_to_change):

    symbol_column_map = {
        2:'"',
        4:'+',
    }

    for row in list_to_change:
        # add " to range column
        try:
            test = int(row[2])
            row[2] = str(row[2]) + '"'
        except ValueError:  # if we can't cast, keep the original value
            pass

        # add + to save column
        try:
            test = int(row[4])
            row[4] = str(row[4]) + '+'
        except ValueError:  # if we can't cast, keep the original value
            pass




# TODO, refactor some of the shifting logic out of the "to rows" function, it is doing multiple different tasks
def unit_list_to_rows(unit_list):
    return_me = []

    # iterate through every row of every unit, padding with a new column to help flag the start of new units
    i = 0
    start_of_unit_index = 0
    for unit in unit_list:
        for model_row in unit.unit_model_stat_rows:
            model_row.insert(0, 1)
            #model_row += [0,0,0,0]
            return_me.append(model_row)
            i += 1

        start_of_unit_index = i

        for row in unit.ranged_rows + unit.melee_rows:
            row.insert(0, 0)
            row += ["", "", ""]
            return_me.append(row)
            i += 1

        # logic for padding the units overall rows so the abilities will all fit to the right of the stat block.
        padding_rows_needed = len(unit.ability_rows) - (len(unit.ranged_rows) + len(unit.melee_rows))
        if padding_rows_needed > 0:
            for y in range(padding_rows_needed):
                return_me.append(["" for i in range(12)])
                i += 1

        for ability in unit.ability_rows:
            return_me[start_of_unit_index][10] = ability[0]
            return_me[start_of_unit_index][11] = ability[1]
            start_of_unit_index += 1

    # add header row
    return_me.insert(0, ["Unit Header Flag", "Unit Name", "Move / Range", "Tough / Attacks",
                                  "Save / BS", "Wounds / Strength", "Lead / AP", "Dmg", "Keywords",
                                  "Abilities Shortened", "Abilities", "Description"])

    add_symbols_to_rows(return_me)


    return return_me

def conflict_factory(fire):
    return fire / 3


def main():
    # parse input file to a list of unit objects
    csv_to_units = parse_input_to_units(INPUT_FILE_NAME)

    # sort units by toughness and then sort ranged weapons by range.
    csv_to_units.sort(key = lambda unit: unit.unit_model_stat_rows[0][2])

    for unit in csv_to_units:
        unit.ranged_rows.sort(key = lambda row: row[1], reverse = True)

    # remove duplicate stat unit rows (infantry squads and their sargent who have the exact same stats)
    no_duplicate_models = remove_duplicate_models(csv_to_units)
    # TODO: Expand this function to remove duplicate units (not only models) that just happen to have 1-2 weapon differences.
    # example, 2 hammerhead tanks with the same everything except the main gun, shouldn't duplicate every row in the final output

    # flatten units into simple rows
    final_list = unit_list_to_rows(no_duplicate_models)

    # output to a .csv
    write_list_to_csv(final_list)


if __name__ == '__main__':
    main()

