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

import os
import re
import csv
from dotenv import load_dotenv
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

CLOUD_OUTPUT_MODE = True  # toggle this to stop outputting to cloud, for debugging
KEYWORDS_COLUMN = 9
ABILITIES_COLUMN = 11

ABILITY_FILTER = ["", "Support", "Leader", "Abilities (Leader)"]

HEADER_ROWS = ["Unit Header Flag", "Unit Name", "Move / Range", "T / A",
                                  "Save / BS", "W / S", "Lead / AP", "Dmg / OC", "Keywords / InvS",
                                  "Abilities", "Abilities Shortened"]

OUTPUT_FILE_NAME = "pyexport.csv"

# a unit represented by a collection of named lists, based on the rows from the input format
class Unit:
    def __init__(self):
        self.unit_model_stat_rows = []
        self.ranged_rows = []
        self.melee_rows = []
        self.ability_rows = []
        self.keyword_rows = []

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
    if "pistol" in new_row[7].lower() or "close-quarters" in new_row[7].lower():
        handle_melee_row(unit, new_row)
    else:
        unit.ranged_rows.append(new_row)

def handle_melee_row(unit, row):
    new_row = try_converting_to_ints(row)
    unit.melee_rows.append(new_row)

def handle_keyword_row(unit, row):
    pattern = r'fly|Markerlight|Infiltrators|Lone Operative|Stealth|Grenades|Deep Strike|Deadly Demise D?[0-9]?\+?[0-9]|Scouts \d+'
    keyword_re = re.compile(pattern, re.IGNORECASE)
    matches = re.findall(keyword_re, "".join(row))
    # if any matches were found, append a row containing the condensed line and the original line
    if len(matches) > 0:
        unit.keyword_rows.append([", ".join(matches), row[1]])


def handle_ability_row(unit, row):
    if row[0] in ABILITY_FILTER or row[1] in ABILITY_FILTER:  # todo this could be handled in the garbage handler instead?
        pass
    else:
        unit.ability_rows.append(row)


def csv_to_list(input_file):
    with open(input_file, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        return list(csv_reader)

def parse_input_to_units(input_list):
    return_me = []

    # function map (dict?)
    SECTION_MAP = {
        "move up": handle_garbage_row,
        "unit": handle_name_row,
        "ranged weapons": handle_ranged_row,
        "melee weapons": handle_melee_row,
        "abilities": handle_ability_row,
        "rules": handle_keyword_row,
        "categories": handle_keyword_row,
    }

    headers_to_keep = ["rules", "categories"]

    # initialize handler state
    handler = handle_garbage_row

    current_unit = Unit()

    # loop through list creating units, checking special header row keywords
    for row in input_list:
        check_me = row[0].lower()

        # this signifies that the current unit is done. Save the current unit and start a new one.
        if handler != handle_garbage_row and check_me == "move up":
            return_me.append(current_unit)
            current_unit = Unit()
            handler = handle_garbage_row

        # if we detect a header row change the handler state and check for header rows that need processing.
        elif check_me in SECTION_MAP:
            handler = SECTION_MAP[check_me]
            if check_me in headers_to_keep:
                handler(current_unit,row)

        # if we aren't in a header row, process the line according to the current handler.
        else:
            handler(current_unit,row)

    return return_me

#TODO: Verify if this will work with units made up of more than 2 stat profiles.
def remove_duplicate_models(units_with_duplicates):
    return_me = []

    for unit in units_with_duplicates:
        previous_stats = list(range(6)) # initial dummy data to compare to
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


def add_symbols_to_rows(list_to_change):

    symbol_column_map = { # not used, but could be used to reduce the near-duplicate lines below
        2:'"',
        4:'+',
        8:'++',
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

        # add ++ to Invulnerable Save column and consolidate into regular Save column.
        try:
            test = int(row[8])
            row[4] = row[4] + " / " + str(row[8]) + '++'
            row[8] = ""
        except ValueError:  # if we can't cast, keep the original value
            pass

def shift_abilities_rows(list_with_abilities_rows): # future home of logic to shift abilities to the right of unit stats
    pass

def unit_list_to_rows(unit_list, ability_shorthand_dict):
    return_me = [HEADER_ROWS]

    # iterate through every row of every unit, adding a new column to help flag the start of new units. Used in formatting later in the workflow.
    i = 1 # skip 1 row for header row
    for unit in unit_list:

        # insert stat block rows for unit models
        for model_row in unit.unit_model_stat_rows:
            model_row.insert(0, 1)
            return_me.append(model_row)
            i += 1

        # note the starting row of the unit, for use later when inserting abilities to the right of their stat block starting with this row
        start_of_unit_row = i

        # insert weapon stat blocks
        for row in unit.ranged_rows + unit.melee_rows:
            row.insert(0, 0)
            row += ["", ""]
            return_me.append(row)
            i += 1

        # insert the units abilities to the right of the stats, padding rows if needed to prevent spilling into next unit
        padding_rows_needed = len(unit.ability_rows) - (len(unit.ranged_rows) + len(unit.melee_rows)) + 1  # +1 is for the keywords rows which will always be a single row

        if padding_rows_needed > 0:
            for y in range(padding_rows_needed):
                return_me.append(["" for i in range(ABILITIES_COLUMN)])
                i += 1

        for ability in unit.ability_rows:
            return_me[start_of_unit_row][KEYWORDS_COLUMN] = ability[0]

            # insert ability short summaries, using input dict
            try:
                return_me[start_of_unit_row][KEYWORDS_COLUMN + 1] = ability_shorthand_dict[ability[1]]
            except KeyError: # if we don't find the ability, just leave this space blank and move on
                pass

            start_of_unit_row += 1

        # add keywords, condensing the two rows into a single row to save space
        if len(unit.keyword_rows) > 0:
            return_me[start_of_unit_row][KEYWORDS_COLUMN] = unit.keyword_rows[0][0]
        if len(unit.keyword_rows) > 1:
            return_me[start_of_unit_row][KEYWORDS_COLUMN + 1] = unit.keyword_rows[1][0]


    # add symbols for readability, like inches and plus signs.
    add_symbols_to_rows(return_me)

    return return_me

def get_cloud_spreadsheet(spreadsheet_key):
    # Connecting to google service account, to operate on spreadsheets in cloud
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )
    try:
        client = gspread.authorize(creds)
        return client.open_by_key(spreadsheet_key)
    except:
        print("Error while getting google spreadsheet. Check credentials JSON and dotenv. Spreadsheet key I tried to use: {}".format(spreadsheet_key))

def get_or_create_sheet(spreadsheet, name, rows=300, cols=ABILITIES_COLUMN):
    try:
        return spreadsheet.worksheet(name)
    except gspread.exceptions.WorksheetNotFound:
        return spreadsheet.add_worksheet(name, rows=rows, cols=cols)

def write_list_to_cloud_sheet(final_list, spreadsheet):
    # create new cloud sheet, name is date
    today = datetime.now()
    date_formatted = today.strftime("%m/%d/%y %H:%M:%S")
    new_sheet = get_or_create_sheet(spreadsheet, date_formatted)
    # write list to sheet.
    new_sheet.update(final_list)

    # Sorts units and their stats. Removes duplicate stat rows. Reorganizes ability cells to save space.
def process_unit_list(units, gspreadsheet):
    # sort units by toughness
    units.sort(key=lambda unit: (unit.unit_model_stat_rows[0][2], unit.unit_model_stat_rows[0][1]))

    # TODO: Remove blank rows, either here or in an earlier function

    # Within each unit sort ranged weapons by range
    for unit in units:
        try:
            unit.ranged_rows.sort(key=lambda row: -row[1])  # negative to reverse sort order
        except:
            print(unit) #breaks on blank rows, like if i manually delete a row in the g sheet that  i want to ignore (support turrets for example).


    # TODO: Sort units by units they could lead, or units they are leading. This currently happens naturally as many leaders have matching toughness to the units they lead.

    # remove duplicate stat unit rows (infantry squads and their sargent who have the exact same stats)
    no_duplicate_models = remove_duplicate_models(units)
    # TODO: Expand this function to remove duplicate units (not only models) that just happen to have 1-2 weapon differences.
    # example, 2 hammerhead tanks with the same everything except the main gun, shouldn't duplicate every row in the final output

    # reference a cloud sheet for a list of ability shorthands
    ability_shorthand_list = get_or_create_sheet(gspreadsheet, os.getenv("ABILITY_LOOKUP_SHEET_NAME")).get_all_values()
    ability_shorthand_dict = {row[2]: row[1] for row in ability_shorthand_list}

    # TODO: Refactor ability logic to its own function. "unit_list_to_rows()" is too complex right now
    # flatten units into simple rows, move ability text cells to save rows
    final_list = unit_list_to_rows(no_duplicate_models, ability_shorthand_dict)

    # TODO: add detachment/strategems to bottom of list

    return final_list

def main():
    # pull spreadsheet and get a list from it
    load_dotenv()  # exercise in hiding key in dotenv file, low risk but worth practicing.
    gspreadsheet = get_cloud_spreadsheet(os.getenv("SPREADSHEET_KEY"))
    input_data = get_or_create_sheet(gspreadsheet, os.getenv("RAW_DATA_SHEET_NAME")).get_all_values()

    # parse input file to a list of unit objects
    units = parse_input_to_units(input_data)

    final_list = process_unit_list(units, gspreadsheet)

    # output
    write_list_to_csv(final_list)
    if CLOUD_OUTPUT_MODE:
        write_list_to_cloud_sheet(final_list, gspreadsheet)

    # run formatting macro in cloud sheet
    #gspreadsheet.run macro on sheet # This macro functionality does not appear to be available easily.





if __name__ == '__main__':
    main()

