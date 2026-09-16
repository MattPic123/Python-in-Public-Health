import requests

Year = 2020
Dataset = "dec/pl"

URL = f"https://api.census.gov/data/{Year}/{Dataset}"
API_KEY = "e2bc9c4f1b45730bfa2cc897a2ebd1c0978723d0"

params = {     #NAME= state name, BO1003_001E= total population
    "get": "NAME,P1_001N",
    "for": "state:*",
    "key": API_KEY
}

response = requests.get(URL, params=params)
response.raise_for_status()

print("URL:", response.url)
print("Status Code:", response.status_code)

if response.status_code != 200:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
    raise SystemExit(1)

data = response.json()



print(f"Got {len(data) - 1} rows back.")


for i in data:
    print(i)