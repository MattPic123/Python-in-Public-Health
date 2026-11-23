"""Author: Matt Picaroni  Date: 2026-11-22
Purpose: Extract and clean Florida adult records from CDC BRFSS 2022 LLCP2022.XPT.
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from common import DATA

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def default_input() -> Path:
    """Locate CDC data from the project root, independent of working directory."""
    for folder in ("Data", "data"):
        candidate = PROJECT_ROOT / folder / "LLCP2022.XPT"
        if candidate.is_file():
            return candidate
    return PROJECT_ROOT / "Data" / "LLCP2022.XPT"

COLUMNS = ["_STATE", "_MICHD", "_SMOKER3", "_AGEG5YR", "SEXVAR", "_BMI5", "DIABETE4", "_LLCPWT", "_STSTR", "_PSU"]

def load_florida(path: str) -> pd.DataFrame:
    """Read only required variables in batches; retain Florida (_STATE=12)."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Dataset not found: {source.resolve()}")

    florida_chunks = []
    if source.suffix.lower() in (".xpt", ".v9xpt"):
        # pandas passes the encoding directly to its XPORT reader, including
        # during the initial metadata read. pyreadstat.read_file_in_chunks()
        # may otherwise fail decoding metadata before iteration starts.
        try:
            reader = ((chunk, None) for chunk in pd.read_sas(
                source,
                format="xport",
                encoding="latin1",
                chunksize=5000,
            ))
        except Exception as exc:
            raise RuntimeError(f"Unable to open CDC XPT file: {source}") from exc
    elif source.suffix.lower() == ".csv":
        reader = ((chunk, None) for chunk in pd.read_csv(
            source, usecols=lambda c: c.upper().strip() in COLUMNS,
            chunksize=5000, low_memory=False,
        ))
    else:
        raise ValueError("Use the CDC 2022 .XPT file or a CSV with BRFSS columns")

    total = 0
    for chunk, _ in reader:
        total += len(chunk)
        chunk.columns = [str(c).upper().strip() for c in chunk.columns]
        missing = set(COLUMNS) - set(chunk.columns)
        if missing:
            raise ValueError(f"Missing official BRFSS variables: {sorted(missing)}")
        state = pd.to_numeric(chunk["_STATE"], errors="coerce")
        florida = chunk.loc[state.eq(12), COLUMNS].copy()
        if not florida.empty:
            florida_chunks.append(florida)
        if total % 50000 < len(chunk):
            print(f"Read {total:,} national records; retained Florida records so far: "
                  f"{sum(len(c) for c in florida_chunks):,}", flush=True)

    if not florida_chunks:
        raise ValueError("No Florida records (_STATE = 12) were found")
    return pd.concat(florida_chunks, ignore_index=True)

def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Recode CDC variables, retaining valid responses for each analysis."""
    for col in COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    out = pd.DataFrame(index=df.index)
    out["heart_disease"] = df["_MICHD"].map({1: 1, 2: 0})
    out["smoking_status"] = df["_SMOKER3"].map({1:"Current",2:"Current",3:"Former",4:"Never"})
    out["ever_smoked"] = out["smoking_status"].map({"Current":1,"Former":1,"Never":0})
    out["age_group"] = df["_AGEG5YR"].where(df["_AGEG5YR"].between(1,13))
    out["sex"] = df["SEXVAR"].map({1:"Male",2:"Female"})
    out["bmi"] = (df["_BMI5"] / 100).where(df["_BMI5"].between(1200, 9900))
    # DIABETE4: 1=yes, 2=gestational only, 3=no, 4=prediabetes.
    # Gestational/prediabetes are not classified as diagnosed diabetes here.
    out["diabetes"] = df["DIABETE4"].map({1:1,2:0,3:0,4:0})
    out["weight"] = df["_LLCPWT"].where(df["_LLCPWT"] > 0)
    out["stratum"] = df["_STSTR"]
    out["psu"] = df["_PSU"]
    out = out.dropna(subset=["heart_disease","ever_smoked","age_group","sex","weight","stratum","psu"])
    out["age_group"] = out["age_group"].astype(int)
    if out.empty:
        raise ValueError("No complete records for required variables")
    return out.reset_index(drop=True)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input(),
        help="Optional path to CDC LLCP2022.XPT (automatically found in Data folder)",
    )
    args = parser.parse_args()
    raw = load_florida(args.input)
    cleaned = clean(raw)
    cleaned.to_csv(DATA / "florida_2022_cleaned.csv", index=False)
    print(f"Florida source records: {len(raw):,}; usable core records: {len(cleaned):,}")
    print(f"Saved: {DATA / 'florida_2022_cleaned.csv'}")
if __name__ == "__main__":
    main()