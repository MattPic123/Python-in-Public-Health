
# U.S. Census API - State Population Data
# Author: Matt Picaroni
# Purpose Retrieve state-level population data from the 2020/
#/ U.S. Census API using State FIPS codes and variables

import requests

# Set the Census API year and dataset
Year = 2020
Dataset = "dec/pl"

# Build the Census API URL
URL = f"https://api.census.gov/data/{Year}/{Dataset}"

# Census API Key
API_KEY = "e2bc9c4f1b45730bfa2cc897a2ebd1c0978723d0"

# Asking the user for a State FIPS code
state_fips = input(
      "Enter the State FIPS code(s) that you would like data for:"
)

# Asking the user for variables
variables = input(
      "Enter the variable(s) that you would like data for: "
)

# Building the Census API parameters
params = {
    "get": f"NAME,{variables}",
    "for": f"state:{state_fips}",
    "key": API_KEY
}

try:
# Send the request to the Census API
response = requests.get(URL, params=params, timeout=30)

# Check for an unsuccessful HTTP response
response.raise_for_status()

# Display the request information
print("\nURL:", response.url)
print("Status Code:", response.status_code)

#Convert the JSON response to a Python variable
data = response.json()

#Display the number of rows returned
print(f"\nFound {len(data) - 1} Rows of Data.\n")

# print each row of Census data
for row in data:
    print(row)

except requests.exceptions.Timeout:(
    print("\nThe Census API timed out."))
print("Check your internet connection and try again.")

except requests.exceptions.RequestException as error: (
    print("\nThe Census API request failed."))
print(error)
