# U.S. Census API Data Retrieval
# Name: Matt Picaroni
# Purpose: Retrieve state-level population data from the 2020/
# /U.S. Census API using a State FIPS code and variable.

import requests

# Set the Census API year and dataset
year = 2020
dataset = "dec/pl"

# Build the Census API URL
URL = f"https://api.census.gov/data/{year}/{dataset}"

# Census API key
api_key = "e2bc9c4f1b45730bfa2cc897a2ebd1c0978723d0"

# Ask the user for a State FIPS code
state_fips = input(
    "Enter the State FIPS code(s) that you would like data for: "
)

# Ask the user for Census variable names
variables = input(
    "Enter the variable names that you would like data for: "
)

# Build the API request parameters
params = {
    "get": f"NAME,{variables}",
    "for": f"state:{state_fips}",
    "key": api_key
}

try:
    # Send the request to the Census API
    response = requests.get(URL, params=params, timeout=30)

    # Check for an unsuccessful HTTP response
    response.raise_for_status()

    # Display the request information
    print("\nURL:", response.url)
    print("Status Code:", response.status_code)

    # Convert the JSON response to a Python variable
    data = response.json()

    # Display the number of rows returned
    print(f"\nFound {len(data) - 1} Rows of Data.\n")

    # Print each row of Census data
    for row in data:
        print(row)

except requests.exceptions.Timeout:
    print("\nThe Census API request timed out.")
    print("Check your internet connection and try again.")

except requests.exceptions.RequestException as error:
    print("\nThe Census API request failed.")
    print(error)
