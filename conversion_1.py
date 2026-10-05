# Lab 5: Dataset Conversion
# Name: Matt Picaroni
# Purpose: Converting dataset to JSON

from pathlib import Path
import csv

import pandas as pd

folder = Path(__file__).parent
csv_path = folder / "Maternal Health Risk Data Set.csv"
output_path = folder / "maternal_health_risk.json"

with csv_path.open("r", newline="",
encoding="utf-8-sig") as file:
    headers = next(csv.reader(file))

if len(headers) != len(set(headers)):
    raise ValueError("Duplicate headers in csv file")

df = pd.read_csv(csv_path)
df = df.loc[:,
df.columns.str.startswith("Unnamed")]

if not df.columns.is_unique:
    raise ValueError("Duplicate columns in csv file")

df.to_json(output_path, orient="records",
indent = 2)

print(f"Saved {output_path.name}")
