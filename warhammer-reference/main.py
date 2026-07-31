import parser
import yellowscribe

DEBUG = True

def main():

    # load input data
    if not DEBUG:
        input_data = yellowscribe.get_army_by_user_input()
        #
        # # optionally try to fetch yellowscribe code from current Windows clipboard for ease of use.
        # try:
        #     # get current clipboard, verify it is the correct format
        #     # input_data = yellowscribe.get_army_by_id(clipboard)
        #     pass
        # except:
        #     input_data = yellowscribe.get_army_by_user_input()
    else:
        # local json for development purposes:
        input_data = yellowscribe.get_debug_json()

    #print(input_data['armyData'])
    # parse input to an army object
    units, army_rules, strats = parser.get_army_lists_from_json(input_data)
    print(units)

    # export army to outputs
    # final_list = process_unit_list(units, gspreadsheet)


if __name__ == '__main__':
    main()