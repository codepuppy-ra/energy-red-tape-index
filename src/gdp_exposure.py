from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CLEAN_DIR = Path("data/cleaned")
OUTPUT_TABLE_DIR = Path("outputs/tables")
OUTPUT_FIGURE_DIR = Path("outputs/figures")

OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FIGURE_DIR.mkdir(parents=True, exist_ok=True)


GDP_FILE = CLEAN_DIR / "provincial_gdp_selected.csv"


NARROW_DIRECT_CODES = [
    "211",      # Oil and gas extraction
    "213",      # Support activities for mining and oil/gas extraction
    "486",      # Pipeline transportation
    "486A",     # Crude oil and other pipeline transportation
    "4862",     # Pipeline transportation of natural gas
]


BROAD_PROJECT_DEVELOPMENT_CODES = [
    "211",
    "21111",
    "213",
    "21311A",
    "23",
    "23B",
    "23X",
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


SELECTED_GEOGRAPHIES = [
    "Canada",
    "Alberta",
    "British Columbia",
    "Saskatchewan",
    "Newfoundland and Labrador",
]


def find_industry_column(df: pd.DataFrame) -> str:
    candidates = [
        col for col in df.columns
        if "industry" in col.lower()
        or "naics" in col.lower()
        or "classification" in col.lower()
    ]

    if not candidates:
        raise ValueError(f"No industry column found. Columns: {df.columns.tolist()}")

    return candidates[0]


def extract_code(value: str) -> str | None:
    value = str(value)

    if "[" not in value or "]" not in value:
        return None

    return value.split("[")[-1].split("]")[0]


def prepare_gdp_data() -> pd.DataFrame:
    if not GDP_FILE.exists():
        raise FileNotFoundError(
            f"{GDP_FILE} does not exist. Run src/clean_statcan.py first."
        )

    df = pd.read_csv(GDP_FILE)

    industry_col = find_industry_column(df)

    df["industry_code"] = df[industry_col].apply(extract_code)
    df["year"] = pd.to_numeric(
        df["REF_DATE"].astype(str).str[:4],
        errors="coerce",
    )
    df["value"] = pd.to_numeric(df["VALUE"], errors="coerce")

    df = df[df["GEO"].isin(SELECTED_GEOGRAPHIES)]
    df = df.dropna(subset=["year", "value", "industry_code"])

    df["year"] = df["year"].astype(int)

    return df


def calculate_exposure(
    df: pd.DataFrame,
    selected_codes: list[str],
    basket_name: str,
) -> pd.DataFrame:
    total_gdp = (
        df[df["industry_code"] == "T001"]
        .groupby(["GEO", "year"], as_index=False)
        .agg(total_gdp=("value", "sum"))
    )

    exposed_gdp = (
        df[df["industry_code"].isin(selected_codes)]
        .groupby(["GEO", "year"], as_index=False)
        .agg(exposed_gdp=("value", "sum"))
    )

    exposure = total_gdp.merge(exposed_gdp, on=["GEO", "year"], how="left")
    exposure["exposed_gdp"] = exposure["exposed_gdp"].fillna(0)
    exposure["exposure_share"] = exposure["exposed_gdp"] / exposure["total_gdp"]
    exposure["exposure_share_percent"] = exposure["exposure_share"] * 100
    exposure["basket"] = basket_name
    exposure["year"] = exposure["year"].astype(int)

    return exposure


def make_latest_year_chart(
    exposure: pd.DataFrame,
    basket_name: str,
    output_name: str,
) -> None:
    exposure = exposure.copy()
    exposure["year"] = exposure["year"].astype(int)

    latest_year = int(exposure["year"].max())

    latest = (
        exposure[exposure["year"] == latest_year]
        .sort_values("exposure_share_percent", ascending=True)
    )

    plt.figure(figsize=(10, 6))
    plt.barh(latest["GEO"], latest["exposure_share_percent"])
    plt.xlabel("Share of GDP in Energy-Project-Exposed Industries (%)")
    plt.ylabel("Geography")
    plt.title(f"{basket_name}: GDP Exposure Share, {latest_year}")

    max_value = latest["exposure_share_percent"].max()

    for i, value in enumerate(latest["exposure_share_percent"]):
        plt.text(
            value - max_value * 0.03,
            i,
            f"{value:.1f}%",
            va="center",
            ha="right",
            color="white",
            fontweight="bold",
        )

    plt.tight_layout()

    output_path = OUTPUT_FIGURE_DIR / output_name
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved figure: {output_path}")


def make_time_series_chart(
    exposure: pd.DataFrame,
    basket_name: str,
    output_name: str,
) -> None:
    exposure = exposure.copy()
    exposure["year"] = exposure["year"].astype(int)

    plt.figure(figsize=(10, 6))

    for geo, group in exposure.groupby("GEO"):
        group = group.sort_values("year")
        plt.plot(group["year"], group["exposure_share_percent"], label=geo)

    years = sorted(exposure["year"].unique())
    tick_years = years[::2]

    plt.xlabel("Year")
    plt.ylabel("Share of GDP in Energy-Project-Exposed Industries (%)")
    plt.title(f"{basket_name}: GDP Exposure Share Over Time")
    plt.legend()

    plt.xticks(tick_years, [str(year) for year in tick_years])

    plt.tight_layout()

    output_path = OUTPUT_FIGURE_DIR / output_name
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved figure: {output_path}")


def main() -> None:
    df = prepare_gdp_data()

    narrow = calculate_exposure(
        df,
        NARROW_DIRECT_CODES,
        "Narrow Direct Energy Exposure",
    )

    broad = calculate_exposure(
        df,
        BROAD_PROJECT_DEVELOPMENT_CODES,
        "Broad Project-Development Exposure",
    )

    combined = pd.concat([narrow, broad], ignore_index=True)

    output_path = OUTPUT_TABLE_DIR / "gdp_exposure_by_geography_year.csv"
    combined.to_csv(output_path, index=False)

    print(f"Saved GDP exposure table: {output_path}")

    make_latest_year_chart(
        narrow,
        "Narrow Direct Energy Exposure",
        "gdp_exposure_narrow_latest_year.png",
    )

    make_latest_year_chart(
        broad,
        "Broad Project-Development Exposure",
        "gdp_exposure_broad_latest_year.png",
    )

    make_time_series_chart(
        narrow,
        "Narrow Direct Energy Exposure",
        "gdp_exposure_narrow_over_time.png",
    )

    make_time_series_chart(
        broad,
        "Broad Project-Development Exposure",
        "gdp_exposure_broad_over_time.png",
    )


if __name__ == "__main__":
    main()