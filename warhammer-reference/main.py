import parser
import yellowscribe
import output
from models import Army

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

    # parse input to an army object
    my_army = parser.parse_army(input_data)
    #print(my_army)

    # export army to outputs
    #final_list = process_unit_list(units, gspreadsheet)
    output.print_to_terminal(my_army)


if __name__ == '__main__':
    main()