"""Convert the source dataset to Parquet."""

from pathlib import Path

import pandas as pd

from dataset_utils import columns, source_file, load_records


def main():
    records = load_records(source_file)
    if len(columns) != len(set(columns)):
        raise ValueError("Duplicate column names are not allowed.")

    data = pd.DataFrame.from_records(records, columns=columns)
    output_path = Path(__file__).with_name("maternal_health_risk.parquet")
    try:
        data.to_parquet(output_path, index=False, engine="pyarrow")
    except ImportError as exc:
        raise SystemExit(
            "Parquet support is missing. Install dependencies with "
            "'python -m pip install -r requirements.txt'."
        ) from exc
    print(f"Created {output_path.name}: {len(data)} records, {len(data.columns)} unique columns.")


if __name__ == "__main__":
    main()