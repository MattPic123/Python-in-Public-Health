#imports
import pandas as pd
import numpy as np

df = pd.read_csv('eye_health.csv')
print(df.shape,
      df.dtypes,
      df.isnull().sum(),
      df.nunique(),
      sep='\n')
print("Duplicates: ", df.duplicated().sum())

df = df.dropna(axis=1, how='all')
df = df.drop(columns=[c for c in df.columns if c.endswith('ID')])

df = df.dropna(subset=["Data_Value"])
df.drop(columns=["Geolocation", "Data_Value_Footnote_Symbol", "Data_Value_Footnote", "StateAbbr", "NonWeightedSample", "Geographic Level", "Numerator"])

df.columns = df.columns.str.lower().str.replace(" ", '_')
df["ci_width"] = (df["high_confidence_limit"]- df["low_confidence_limit"]) / 2
df["prevalence_level"] = np.select([df["data_value"] < 5, df["data_value"] <= 7], ["Low", "Medium"], "High")

df.to_csv('eye_health.csv', index=False)
print(pd.read_csv('eye_health.csv').shape == df.shape)
print(pd.read_csv("eye_Health.csv").shape)
print(pd.read_csv("eye_Health.csv").head)