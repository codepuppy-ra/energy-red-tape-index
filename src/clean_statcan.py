from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/cleaned")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)


SELECTED_GEOGRAPHIES = [
    "Canada",
    "Alberta",
    "British Columbia",
    "Saskatchewan",
    "Newfoundland and Labrador",
]


SELECTED_CODES = [
    "T001",
    "211",
    "21111",
    "213",
    "21311A",
    "23",
    "23B",
    "23X",
    "48-49",
    "486",
    "486A",
    "4862",
    "54",
    "5413",
    "31-33",
    "324",
    "331",
    "3311",
    "3312",
    "332",
    "333",
]


def find_industry_column(df: pd.DataFrame) -> str:
    candidates = [
        col for col in df.columns
        if "industry" in col.lower()
        or "naics" in col.lower()
        or "classification" in col.lower()
    ]

    if not candidates:
        raise ValueError(f"Could not identify industry/NAICS column. Columns are: {df.columns.tolist()}")

    return candidates[0]


def filter_years(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    df = df.copy()

    if "REF_DATE" in df.columns:
        df["year"] = pd.to_numeric(df["REF_DATE"].astype(str).str[:4], errors="coerce")
        df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

    return df


def clean_statcan_file(
    input_path: Path,
    output_name: str,
    start_year: int,
    end_year: int,
) -> Path:
    print(f"Cleaning {input_path.name}")

    df = pd.read_csv(input_path)

    if "GEO" in df.columns:
        df = df[df["GEO"].isin(SELECTED_GEOGRAPHIES)]

    df = filter_years(df, start_year, end_year)

    industry_col = find_industry_column(df)

    pattern = "|".join([rf"\[{code}\]" for code in SELECTED_CODES])

    df = df[
        df[industry_col]
        .astype(str)
        .str.contains(pattern, regex=True, na=False)
    ]

    output_path = CLEAN_DIR / f"{output_name}.csv"
    df.to_csv(output_path, index=False)

    print(f"Saved cleaned file: {output_path}")
    return output_path


def main() -> None:
    files = list(RAW_DIR.glob("*.csv"))

    if not files:
        raise FileNotFoundError("No raw CSV files found. Run src/download_statcan.py first.")

    for file in files:
        file_name = file.name.lower()

        if "provincial_gdp" in file_name:
            clean_statcan_file(file, "provincial_gdp_selected", 2005, 2025)

        elif "canada_gdp" in file_name:
            clean_statcan_file(file, "canada_gdp_annual_selected", 2005, 2026)

        elif "capital_expenditures" in file_name:
            clean_statcan_file(file, "capital_expenditures_selected", 2006, 2026)


if __name__ == "__main__":
    main()