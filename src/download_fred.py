import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/cleaned")

RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()

FRED_API_KEY = "07d9bc170311eb76272645ed0a506683"

if not FRED_API_KEY:
    print("⚠️  WARNING: FRED_API_KEY not found.")
    print("To use FRED data, create a .env file in your project root with:")
    print("  FRED_API_KEY=your_api_key_here")
    print("\nGet a free API key at: https://fred.stlouisfed.org/docs/api/")
    print("\nSkipping FRED download. You can run this later if needed.")
    print()
    exit(0)  # Exit gracefully instead of crashing


FRED_SERIES = {
    # GDP / recession context
    "us_real_gdp": "GDPC1",
    "us_industrial_production": "INDPRO",

    # Energy prices
    "wti_crude_oil_price": "DCOILWTICO",
    "henry_hub_natural_gas_price": "DHHNGSP",

    # Interest rates / macro controls
    "federal_funds_rate": "FEDFUNDS",
    "us_10_year_treasury_rate": "DGS10",

    # Exchange rate
    "cad_usd_exchange_rate": "DEXCAUS",
}


def download_fred_series(series_name: str, series_id: str) -> pd.DataFrame:
    """Download a FRED series with error handling."""
    url = "https://api.stlouisfed.org/fred/series/observations"

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": "2005-01-01",
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading {series_name} ({series_id}): {e}")
        return None

    try:
        data = response.json()["observations"]
    except (KeyError, ValueError) as e:
        print(f"❌ Error parsing {series_name}: {e}")
        print(f"Response: {response.text[:200]}")
        return None

    if not data:
        print(f"⚠️  No data returned for {series_name}")
        return None

    df = pd.DataFrame(data)

    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Drop rows where value is NaN (missing data)
    df = df.dropna(subset=["value"])

    df["series_name"] = series_name
    df["series_id"] = series_id

    print(f"✅ Downloaded {series_name}: {len(df)} observations")
    return df[["date", "series_name", "series_id", "value"]]


def main() -> None:
    all_series = []

    for series_name, series_id in FRED_SERIES.items():
        print(f"Downloading {series_name}: {series_id}")
        df = download_fred_series(series_name, series_id)

        if df is None:
            print(f"⚠️  Skipping {series_name}")
            continue

        raw_path = RAW_DIR / f"fred_{series_name}_{series_id}.csv"
        df.to_csv(raw_path, index=False)
        print(f"   Saved to {raw_path}")

        all_series.append(df)

    if not all_series:
        print("❌ No FRED data downloaded. Check your API key and internet connection.")
        return

    combined = pd.concat(all_series, ignore_index=True)

    combined_path = CLEAN_DIR / "fred_energy_macro_series.csv"
    combined.to_csv(combined_path, index=False)

    print(f"\n✅ Saved combined FRED dataset: {combined_path}")
    print(f"   Total records: {len(combined)}")


if __name__ == "__main__":
    main()
