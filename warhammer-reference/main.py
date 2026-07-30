import parser
import yellowscribe

DEBUG = True

def main():

    # load input data
    if not DEBUG:
        # optionally try to fetch yellowscribe code from current Windows clipboard for ease of use.
        try:
            # get current clipboard, verify it is the correct format
            # input_data = yellowscribe.get_army_by_id(clipboard)
            pass
        except:
            input_data = yellowscribe.get_army_by_user_input()
    else:
        # local json for development purposes:
        input_data = yellowscribe.get_debug_json()


    # parse input to an army object
    army = parser.get_army_from_json(input_data)

    # export army to outputs
    # final_list = process_unit_list(units, gspreadsheet)

    # write_list_to_csv(final_list)
    # if CLOUD_OUTPUT_MODE:
    #     write_list_to_cloud_sheet(final_list, gspreadsheet)


if __name__ == '__main__':
    main()