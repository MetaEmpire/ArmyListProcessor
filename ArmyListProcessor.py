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

INPUT_FILE_NAME = "gsheetexport.csv"
OUTPUT_FILE_NAME = "pyexport.csv"

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
    list_with_abilities_shifted = []

    # iterate through every item in the list. Whenever we encounter the new unit flag, remember that index.
    # whenever we find the "Ability" row, shift row content up to the unit index + 1.
    index_of_last_unit_start = 0
    index = 0
    while index < len(list_with_abilities_rows):
        if list_with_abilities_rows[2][0] == True:
            index_of_last_unit_start = index
            list_with_abilities_shifted.append(list_with_abilities_rows[index])

        elif list_with_abilities_rows[2][1] == "Abilities":
            # shift each line over until we hit a new unit flag.
            while list_with_abilities_rows[index][0] == False:
                print(f"Ability row found at index {index}: {list_with_abilities_rows[index][2][0]}")
                index += 1

        index += 1




    """
    for index, tupl in enumerate(list_with_abilities_rows):
        if tupl[2][0] == "True":
            index_of_last_unit_start = index
        if tupl[2][1] == "Abilities":
            print(f"Found an ability row, and the last unit start index was {index_of_last_unit_start}")
    """


    return list_with_abilities_shifted

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
            if row[0].startswith("Army Roster"):  # this signifies we've reached the end of the interesting rows
                break

            # check if this row is the beginning of a new units series of rows
            if row[0].startswith("Unit"):
                new_unit = True
                continue  # this is redundant, the regex filter would catch "unit" currently. TODO: remove redundancy
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


def main():
    # parse input file to a list of tuples, removing blank rows
    csv_to_tuples = parse_input_to_tuples(INPUT_FILE_NAME)

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

    # output final list back into a .csv
    with open(OUTPUT_FILE_NAME, mode="w", newline="", encoding="utf-8") as out_file:
        out_writer = csv.writer(out_file)
        for tup in no_duplicates_list:
            out_writer.writerow(tup[2])

if __name__ == '__main__':
    main()

