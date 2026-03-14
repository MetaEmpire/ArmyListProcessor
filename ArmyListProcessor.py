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

def print_regex_match(re_match, original_string):
    print(f"String: {original_string}")
    print(f"Match: {re_match.group()}")
    print(f"Span: {re_match.span()}")

new_list = []

with open(INPUT_FILE_NAME, mode = "r", newline ="", encoding="utf-8") as file:
    csv_reader = csv.reader(file)

    discard_re = re.compile(r"^(unit|\d+ |(\d*)x|leader)|\b(?:{Move|don't|models|ranged weapons|melee weapons|abilities})\b|\A\Z", re.IGNORECASE)

    #options_re = re.compile(r"(\d*)x", re.IGNORECASE)

    #leader_re = re.compile(r"^leader", re.IGNORECASE)

    new_unit = False
    current_unit_name = "UnitFindingLogicBroken"
    current_unit_toughness = 0

    for row in csv_reader:

        match = discard_re.match(row[0])
        #match = options_re.match(row[0])
        # match = leader_re.match(row[0])

        # special cases:
        if row[0].startswith("Army Roster"): # this signifies we've reached the end of the interesting rows
            break

        if new_unit: # this is executed if the previous line was "Unit", which means the next line contains special information we want.
            new_unit = False
            current_unit_name = row[0]
            current_unit_toughness = row[2]
            print(current_unit_toughness)

        if row[0].startswith("Unit"):
            new_unit = True


        if row[1] == "" or match: # this is a row that contains units a leader can be attached to, and for now isn't interesting.
            continue

        else:
            new_list.append((row, current_unit_name, current_unit_toughness))

    print(new_list)



