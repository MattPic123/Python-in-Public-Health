import requests

Year = 2020
Dataset = "dec/pl"

URL = f"https://api.census.gov/data/{Year}/{Dataset}"

API_KEY = "e2bc9c4f1b45730bfa2cc897a2ebd1c0978723d0"


# Asking the user for the geography
state_fips = input(
    "Enter the State FIPS code(s) that you would like data for: "
)

# Asking the user for the variables
variables = input(
    "Enter the variable names that you would like data for: "
)

# Building the Census API parameters
params = {
    "get": f"NAME,{variables}",
    "for": f"state:{state_fips}",
    "key": API_KEY
}

# Request the data
response = requests.get(URL, params=params)
response.raise_for_status()


print("\nURL:", response.url)
print("Status Code:", response.status_code)

if response.status_code != 200:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
    raise SystemExit(1)

# Convert JSON response into a Python variable
data = response.json()


print(f"\nFound {len(data) - 1} Rows of Data.\n")

for row in data:
    print(row)

