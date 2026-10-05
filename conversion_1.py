"""Convert the source dataset to JSON records."""

import json
from pathlib import Path

from dataset_utils import columns, source_file, load_records


def main():
    records = load_records(source_file)
    if len(columns) != len(set(columns)):
        raise ValueError("Duplicate column names are not allowed.")

    output_path = Path(__file__).with_name("maternal_health_risk.json")
    output_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Created {output_path.name}: {len(records)} records, {len(columns)} unique columns.")


if __name__ == "__main__":
    main()
