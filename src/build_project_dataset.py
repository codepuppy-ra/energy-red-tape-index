"""
Validates the manual project-level dataset.

This script:
1. Loads data/manual/project_dataset.csv
2. Checks required columns
3. Saves a validated copy
"""

from pathlib import Path
import pandas as pd


MANUAL_DIR = Path("data/manual")
INPUT_PATH = MANUAL_DIR / "project_dataset.csv"
OUTPUT_PATH = MANUAL_DIR / "project_dataset_validated.csv"


REQUIRED_COLUMNS = [
    "project",
    "country",
    "province_state",
    "project_type",
    "primary_naics",
    "capex_billion",
    "status",
    "status_3cat",
    "cause_category",
    "blocking_jurisdiction",
    "evidence_score",
    "source_type",
    "source_link",
    "source_quote",
    "proposed_year",
    "expected_in_service_year",
    "actual_cancel_delay_year",
    "delay_years_by_2026",
]


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df.to_csv(OUTPUT_PATH, index=False)

    print("Dataset is valid.")
    print(f"Saved validated dataset to: {OUTPUT_PATH}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")


if __name__ == "__main__":
    main()