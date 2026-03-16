# ArmyListProcessor.py
# a utility for processing wargaming profiles into a cleaner/shorter reference

# pseudocode:
#         # if line matches 'discard' regex, discard row
#         # if line matches "rules/categories/leader", process for relevant keywords and store
#         # else, if we can tell this line belongs to the current unit, add it to a new list of lists.
#         #       so each unit will have its own list of csv rows.

# example data from CSV read: 
##['Unit', 'M', 'T', 'SV', 'W', 'LD', 'OC', '']
##['Cadre Fireblade', '6"', '3', '4+', '3', '7+', '1', '']
##['Ranged Weapons', 'Range', 'A', 'BS', 'S', 'AP', 'D', 'Keywords']
##['Fireblade pulse rifle', '30"', '1', '3+', '5', '0', '2', 'Rapid Fire 1']
##['Twin pulse carbine (x2)', '20"', '2', '5+', '5', '0', '1', 'Assault, Twin-linked']
##['Melee Weapons', 'Range', 'A', 'WS', 'S', 'AP', 'D', 'Keywords']
##['Close combat weapon', 'Melee', '3', '4+', '3', '0', '1', '-']

import re
import csv
from enum import Enum, auto
from typing import Any

INPUT_FILE_NAME = "gsheetexport.csv"
OUTPUT_FILE_NAME = "pyexport.csv"

# a unit represented by a block of contiguous rows in the input file
class Unit:
    def __init__(self):
        self.unit_model_stat_rows = []
        self.ranged_rows = []
        self.melee_rows = []
        self.ability_rows = []

    def __str__(self):
        return self.unit_model_stat_rows[0][0]

def print_regex_match(re_match, original_string):
    print(f"String: {original_string}")
    print(f"Match: {re_match.group()}")
    print(f"Span: {re_match.span()}")

# takes a list of tuples containing unit data. If the stat block is exactly the same as the above, skip it.
def remove_duplicate_statlines(list_of_tuples):
    list_without_duplicates = []
    for index, tupl in enumerate(list_of_tuples):
        if tupl[2][2:] != list_of_tuples[index - 1][2][2:]: # lines of code like this make me want to step back and refactor a lot.
            list_without_duplicates.append(tupl)
        else:
            #print(f"duplicate detected {tupl[2]}")
            continue
    return list_without_duplicates

def shift_abilities_rows(list_with_abilities_rows):
    pass

class Section(Enum):
    NONE = auto()
    NAME = auto()
    RANGED = auto()
    MELEE = auto()
    ABILITY = auto()

def handle_garbage_row(unit, row):
    pass
def handle_name_row(unit, row):
    unit.unit_model_stat_rows.append(row)
def handle_ranged_row(unit, row):
    # if row contains the pistol keyword move the weapon into the melee list
    if "pistol" in row[7].lower():
        handle_melee_row(unit, row)
    else:
        unit.ranged_rows.append(row)
def handle_melee_row(unit, row):
    unit.melee_rows.append(row)
def handle_ability_row(unit, row):
    # process for common keywords like Fly, Deepstrike, grenades
    # if row has nothing in row 2, dump it
    if row[1] == "":
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
                continue

            # detect what section we are in and set the handler
            if row[0] in SECTION_MAP:
                handler = SECTION_MAP[row[0]]
                continue

            # if we aren't in a "header" row, process the line according to the current handler.
            else:
                handler(current_unit,row)

    return return_me


def parse_input_to_tuples(input_file):
    return_me = []
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.reader(file)

        # TODO: consider splitting up regex into "Header rows" and "Noise rows" patterns
        discard_re = re.compile(
            r"^(unit|\d+ |(\d*)x|leader|categories|rules)|\b(?:move|don't|models|ranged weapons|melee weapons)\b|\A\Z",
            re.IGNORECASE)

        # options_re = re.compile(r"(\d*)x", re.IGNORECASE)

        # leader_re = re.compile(r"^leader", re.IGNORECASE)

        new_unit = False
        abilities_section = False
        current_unit_name = "UnitFindingLogicBroken"
        current_unit_toughness = 0
        current_unit_starting_index = 0

        for row in csv_reader:

            match = discard_re.match(row[0])
            # match = options_re.match(row[0])
            # match = leader_re.match(row[0])

            # special cases:
            if row[0].startswith("Army Roster"):  # this signifies we've reached the end of the unit related rows
                break

            # check if this row is the beginning of a new units series of rows
            if row[0].startswith("Unit"):
                new_unit = True
                continue  # this is redundant, the regex filter would catch "unit" below and discard. TODO: remove redundancy
            elif new_unit:  # save certain information to be stamped on each row until a new unit begins
                current_unit_name = row[0]
                current_unit_toughness = int(row[2])  # this assumes every model inside the unit has the same toughness. Which is not always true for some factions. TODO: Fix unit toughness sameness assumption

            # discard unwanted rows
            if match or row[1] == "":  # row[1] being blank means it's a leadership block, and we discard it for now.
                continue
            # add desired rows to output list
            else:
                row.insert(0, str(new_unit))  # add a column to the list for formatting in spreadsheet editor
                return_me.append((current_unit_toughness, current_unit_name, row))
                new_unit = False

    return return_me

def write_output(output_list):
    # output final list back into a .csv
    with open(OUTPUT_FILE_NAME, mode="w", newline="", encoding="utf-8") as out_file:
        out_writer = csv.writer(out_file)
        for tup in output_list:
            out_writer.writerow(tup[2])

def main():
    # parse input file to a list of tuples, removing blank rows
    csv_to_tuples = parse_input_to_tuples(INPUT_FILE_NAME)
    csv_to_units = parse_input_to_units(INPUT_FILE_NAME)

    for unit in csv_to_units:
        print(unit)

    # sort list by toughness / range column.
    sorted_list = sorted(csv_to_tuples, key = lambda x: (x[0], x[1])) # sort the tuples first by toughness/range of the unit, then by unit name

    # remove duplicate stat unit rows (infantry squads and their sargent who have the exact same stats)
    no_duplicates_list = remove_duplicate_statlines(sorted_list)

    #TODO: Move the abilities rows to the right of the stat block with a column of space ( at index len(row)+1 )
    abilities_shifted_list = shift_abilities_rows(no_duplicates_list)
    # make sure to change the lists below to use the shifted list.

    # add header row
    sorted_list.insert(0, (0, 0, ["Unit Header Flag", "Unit Name", "Move / Range", "Tough / Attacks",
                                  "Save / BS", "Wounds / Strength", "Lead / AP", "Dmg", "Keywords",
                                  "Abilities Shortened"]))
    # output to a .csv
    write_output(no_duplicates_list)


if __name__ == '__main__':
    main()

