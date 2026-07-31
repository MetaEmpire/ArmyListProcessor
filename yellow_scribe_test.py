import requests
from pprint import pprint
code = "71604f55"

r = requests.get(
    "https://yellowscribe.link/get_army_by_id",
    params={"id": code},
    timeout=10,
)

#print(r.status_code)
#print(r.headers["Content-Type"])
#print(r.json()['armyData'])
print(r.text)