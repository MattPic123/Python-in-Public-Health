# BRFSS Eye Health Data Cleaning
# Name: Matt Picaroni
# Purpose: Clean the BRFSS eye health dataset, remove unnecessary
# columns, create new variables, and save the cleaned dataset.

import pandas as pd
import numpy as np

# Load the eye health dataset
df = pd.read_csv('eye_health.csv')

# Display basic information about the original dataset
print(df.shape,
      df.dtypes,
      df.isnull().sum(),
      df.nunique(),
      sep='\n')

# Check for duplicate rows
print("Duplicates:", df.duplicated().sum())

# Remove columns that contain no data
df = df.dropna(axis=1, how='all')

# Remove ID columns
df = df.drop(columns=[c for c in df.columns if c.endswith('ID')])

# Remove rows where data_value is missing
df = df.dropna(subset=["data_value"])

# Remove unnecessary columns
df = df.drop(columns=[
    "geolocation",
    "data_value_footnote_symbol",
    "data_value_footnote",
    "stateabbr",
    "nonweightedsample",
    "geographic_level",
    "numerator"
], errors="ignore")

# Standardize column names
df.columns = df.columns.str.lower().str.replace(" ", '_')

# Calculate confidence interval width
df["ci_width"] = (
    df["high_confidence_limit"] - df["low_confidence_limit"]
) / 2

# Categorize prevalence into Low, Medium, and High
df["prevalence_level"] = np.select(
    [
        df["data_value"] < 5,
        df["data_value"] <= 7
    ],
    [
        "Low",
        "Medium"
    ],
    default="High"
)

# Save the cleaned dataset
df.to_csv('eye_health.csv', index=False)

# Verify the saved dataset
cleaned_df = pd.read_csv('eye_health.csv')

print("Saved dataset shape:", cleaned_df.shape)
print("Shape matches:", cleaned_df.shape == df.shape)

# Display the first five rows
print(cleaned_df.head())
