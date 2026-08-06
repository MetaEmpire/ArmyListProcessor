import os
import re
import csv
from dotenv import load_dotenv
from datetime import datetime
from models import Army, Unit, Model

import gspread
from google.oauth2.service_account import Credentials

CLOUD_OUTPUT_MODE = False  # toggle this to stop outputting to cloud, for debugging
KEYWORDS_COLUMN = 9
ABILITIES_COLUMN = 11

ABILITY_FILTER = ["", "Support", "Leader", "Abilities (Leader)", "Transport"]

HEADER_ROWS = ["Unit Header Flag", "Unit Name", "Move / Range", "T / A",
                                  "Save / BS", "W / S", "Lead / AP", "Dmg / OC", "Keywords / InvS",
                                  "Abilities", "Abilities Shortened"]

OUTPUT_FILE_NAME = "pyexport.csv"

def output_to_csv(final_list):
    with open(OUTPUT_FILE_NAME, mode="w", newline="", encoding="utf-8") as out_file:
        out_writer = csv.writer(out_file)
        for row in final_list:
            out_writer.writerow(row)

def output_to_gsheets():
    pass

def army_to_csv():
    pass


def print_to_terminal(input_army):
    for unit in input_army.units:
        # helper functions: count weapons profiles, count model profiles
        print(unit)
        print(unit.get_weapons_list())
        for model in unit.models:
            print(f"\t{model.name} x{model.count}")
            # for weapon in model.weapons:
            #     print(f"\t\t{model.weapons[weapon]}x {weapon}")
            #     print(f"\t\t\t{unit.weapon_profiles[weapon].range}")

        print(unit.abilities)
        print(unit.keywords)