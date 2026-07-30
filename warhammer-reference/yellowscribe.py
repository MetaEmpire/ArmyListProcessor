import requests

BASE_URL = "https://yellowscribe.link/get_army_by_id"

def get_army_json(code):

    response = requests.get(
        BASE_URL,
        params={"id": code},
        timeout=10,
    )

    if response.status_code == 404:
        raise Exception("Invalid or expired code")
    return response.json()

def prompt_for_code():
    code = input("Please enter the code: ")
    # validate user input, should be X characters and only contain letters/numbers
    return code

def get_army_by_user_input():
    return get_army_json(prompt_for_code())

#print(r.status_code)
#print(r.headers["Content-Type"])
#print(r.json()['armyData'])
#print(r.json().keys())

def get_debug_json():
    return None