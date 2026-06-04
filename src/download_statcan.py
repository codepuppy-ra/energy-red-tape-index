import io
import zipfile
from pathlib import Path

import pandas as pd
import requests


RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


STATCAN_TABLES = {
    "canada_gdp_annual": "36-10-0434-06",
    "provincial_gdp_industry": "36-10-0711-01",
    "capital_expenditures": "34-10-0035-01",
}


def table_number_to_product_id(table_number: str) -> str:
    """
    Converts a Statistics Canada table number into the product ID used in CSV download URLs.

    StatCan download URLs drop the final table version suffix.

    Examples:
    36-10-0434-06 -> 36100434
    36-10-0711-01 -> 36100711
    34-10-0035-01 -> 34100035
    """
    parts = table_number.split("-")

    if len(parts) != 4:
        raise ValueError(f"Unexpected StatCan table format: {table_number}")

    return "".join(parts[:3])

def download_statcan_table(table_number: str, output_name: str) -> Path:
    product_id = table_number_to_product_id(table_number)
    url = f"https://www150.statcan.gc.ca/n1/tbl/csv/{product_id}-eng.zip"

    print(f"Downloading {table_number} from {url}")

    response = requests.get(url, timeout=120)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        csv_files = [name for name in z.namelist() if name.endswith(".csv")]

        if not csv_files:
            raise FileNotFoundError(f"No CSV files found for {table_number}")

        main_csv = csv_files[0]

        with z.open(main_csv) as file:
            df = pd.read_csv(file)

    output_path = RAW_DIR / f"{output_name}_{product_id}.csv"
    df.to_csv(output_path, index=False)

    print(f"Saved: {output_path}")
    return output_path


def main() -> None:
    for output_name, table_number in STATCAN_TABLES.items():
        download_statcan_table(table_number, output_name)


if __name__ == "__main__":
    main()