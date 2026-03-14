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

    discard_re = re.compile(r"^(unit|\d+ )|\b(?:{Move|don't|models|ranged weapons|melee weapons|abilities})\b|\A\Z", re.IGNORECASE)
    #discard_re = r"^(unit|\d+)|\b(?:{Move|don't|models|ranged weapons|melee weapons|abilities})\b"

    options_re = re.compile(r"(\d*)x", re.IGNORECASE)

    leader_re = re.compile(r"^leader", re.IGNORECASE)



    for row in csv_reader:
        #match = leader_re.match(row[0])
        match = discard_re.match(row[0])
        #match = options_re.match(row[0])

        if row[0].startswith("Army Roster"): # this signifies we've reached the end of the interesting rows
            break

        if match:
            print_regex_match(match, row[0])
            #print(match.group())
            #new_list.append(row)
        else:
            print(f"Did not find match for {row[0]}")

    print(new_list)



