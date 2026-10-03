# U.S. Census API - State Population Data
# Name: Matt Picaroni
# Purpose: Retrieve the total population for every U.S. state/
#/from the 2020 Decennial Census using the Census API.

import requests

# Set the Census API year and dataset
year = 2020
dataset = "dec/pl"

# Build the Census API URL
url = f"https://api.census.gov/data/{year}/{dataset}"

# Census API key
api_key = "e2bc9c4f1b45730bfa2cc897a2ebd1c0978723d0"

# Set the API parameters
# NAME = state name
# P1_001N = total population
# state:* = request data for every state
params = {
    "get": "NAME,P1_001N",
    "for": "state:*",
    "key": api_key
}

# Send the request to the Census API
response = requests.get(url, params=params)

# Check whether the request was successful
response.raise_for_status()

# Display the URL and HTTP status code
print("URL:", response.url)
print("Status Code:", response.status_code)

# Convert the API response from JSON into a Python list
data = response.json()

# Display the number of states returned
print(f"Got {len(data) - 1} rows back.")

# Print each row of Census data
for row in data:
    print(row)


print(f"Got {len(data) - 1} rows back.")


for i in data:
    print(i)
