"""Convert the source dataset to Parquet."""

from pathlib import Path
import csv

import pandas as pd

folder = Path(__file__).parent
csv_path = folder / "Maternal Health Risk Data Set.csv"
output_path = folder / "Maternal_Health_Risk_Data_Set.parquet"

#Checking the original CSV header
with csv_path.open("r", newline="", encoding="utf-8-sig") as file:
    headers = next(csv.reader(file))

if len(headers) != len(set(headers)):
    raise ValueError("headers must be unique")

df = pd.read_csv(csv_path)

# removing leftover index columns
df = df.loc[:,df.columns.str.startswith("Unnamed")]

if not df.columns.is_unique:
    raise ValueError("column names must be unique")

df.to_parquet(output_path, engine="pyarrow",
index = False)

print("Parquet created")
