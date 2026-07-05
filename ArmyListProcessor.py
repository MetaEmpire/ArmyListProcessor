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
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import date

ABILITIES_COLUMN = 11

KEYWORDS_COLUMN = 9

ABILITY_FILTER = ["", "Leader", "Abilities (Leader)"]

INPUT_FILE_NAME = "gsheetexport.csv"
OUTPUT_FILE_NAME = "pyexport.csv"

# This formula is used in the final google sheet to look up abilities and their shorthand summaries. Todo pull this list from the cloud
LOOKUP_FORMULA = r"=IF(NOT(ISBLANK(L3)), XLOOKUP(L3,'Tau abilities'!C:C,'Tau abilities'!B:B,""), "")"
#LOOKUP_FORMULA = "=IF(NOT(ISBLANK(L3)), XLOOKUP(L3,'Soraritas Abilities lookup'!C:C,'Soraritas Abilities lookup'!B:B,""), "")"


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



def handle_ability_row(unit, row):
    # if row contains keywords, sort out the relevant keywords in a regex.
    if row[0].lower() in ["rules", "categories"]:
        ability_re = re.compile(r'fly|Markerlight|Infiltrators|Lone Operative|Stealth|Grenades|Deep Strike|Deadly Demise D?\d|Scouts \d+', re.IGNORECASE)
        matches = re.findall(ability_re, "".join(row))
        # if any matches were found, append a row containing the condensed line and the original line
        if len(matches) > 0:
            unit.ability_rows.append([", ".join(matches), row[1]])
    # if row contains certain unneeded strings, pass
    elif row[0] in ABILITY_FILTER or row[1] in ABILITY_FILTER:
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
        "rules": handle_ability_row,
        "abilities": handle_ability_row,
    }

    headers_to_keep = ["rules"]


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
            return_me[start_of_unit_index][KEYWORDS_COLUMN] = ability[0]
            return_me[start_of_unit_index][KEYWORDS_COLUMN + 1] = LOOKUP_FORMULA
            return_me[start_of_unit_index][ABILITIES_COLUMN] = ability[1]
            start_of_unit_index += 1

    # add header row
    return_me.insert(0, ["Unit Header Flag", "Unit Name", "Move / Range", "Tough / Attacks",
                                  "Save / BS", "Wounds / Strength", "Lead / AP", "Dmg / OC", "Keywords",
                                  "Abilities", "Abilities Shortened", "Description"])

    add_symbols_to_rows(return_me)


    return return_me


def cloud_sheet_to_list(spreadsheet_key):
    # Connecting to google service account, to operate on spreadsheets in cloud
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    # Import data from Google sheet, and return the spreadsheet for future use

    spreadsheet = client.open_by_key(spreadsheet_key)
    sheet = spreadsheet.worksheet(os.getenv("SHEET_NAME"))
    return sheet.get_all_values(), spreadsheet

def get_or_create_sheet(spreadsheet, name, rows=999, cols=13):
    try:
        return spreadsheet.worksheet(name)
    except gspread.exceptions.WorksheetNotFound:
        return spreadsheet.add_worksheet(name, rows=rows, cols=cols)

def write_list_to_cloud_sheet(final_list, spreadsheet):

    # create new cloud sheet, name is date
    today = date.today()
    date_formatted = today.strftime("%d/%m/%y")
    new_sheet = get_or_create_sheet(spreadsheet, date_formatted)
    # write list to sheet.
    new_sheet.update(final_list, value_input_option='USER_ENTERED')


def main():
    # load input data

    #input_data = csv_to_list(INPUT_FILE_NAME)
    load_dotenv()  # exercise in hiding key in dotenv file, low risk but worth practicing.
    input_data, gspreadsheet = cloud_sheet_to_list(os.getenv("SPREADSHEET_KEY"))

    # parse input file to a list of unit objects
    units = parse_input_to_units(input_data)

    # sort units by toughness and then sort ranged weapons by range.
    units.sort(key = lambda unit: (unit.unit_model_stat_rows[0][2], unit.unit_model_stat_rows[0][1]))  # subsorting by toughness then movement

    for unit in units:
        unit.ranged_rows.sort(key = lambda row: -row[1])  # negative to reverse sort order

    # TODO: Sort units by units they could lead, or units they are leading

    # remove duplicate stat unit rows (infantry squads and their sargent who have the exact same stats)
    no_duplicate_models = remove_duplicate_models(units)
    # TODO: Expand this function to remove duplicate units (not only models) that just happen to have 1-2 weapon differences.
    # example, 2 hammerhead tanks with the same everything except the main gun, shouldn't duplicate every row in the final output

    # flatten units into simple rows, reorganize ability text to save rows
    final_list = unit_list_to_rows(no_duplicate_models)

    # add detachment/strategems to bottom of list

    # output to a .csv
    write_list_to_csv(final_list)
    # output to cloud sheet
    write_list_to_cloud_sheet(final_list, gspreadsheet)

    # run formatting macro in cloud sheet
    #gclient.run macro on sheet # This macro functionality does not appear to be available easily.

if __name__ == '__main__':
    main()

