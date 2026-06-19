from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CLEAN_DIR = Path("data/cleaned")
FIGURE_DIR = Path("outputs/figures")
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


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


def extract_code(value: str) -> str:
    value = str(value)
    if "[" in value and "]" in value:
        return value.split("[")[-1].split("]")[0]
    return value


def main() -> None:
    file_path = CLEAN_DIR / "provincial_gdp_selected.csv"

    if not file_path.exists():
        raise FileNotFoundError("Run src/clean_statcan.py first.")

    df = pd.read_csv(file_path)

    industry_col = find_industry_column(df)
    df["industry_code"] = df[industry_col].apply(extract_code)

    df["year"] = pd.to_numeric(df["REF_DATE"].astype(str).str[:4], errors="coerce")
    df["value"] = pd.to_numeric(df["VALUE"], errors="coerce")

    # Focus on the key direct channels.
    selected = df[
        (df["GEO"].isin(["Alberta", "British Columbia", "Saskatchewan", "Newfoundland and Labrador"]))
        & (df["industry_code"].isin(["211", "213", "486", "23"]))
    ]

    for code in ["211", "213", "486", "23"]:
        temp = selected[selected["industry_code"] == code]

        if temp.empty:
            continue

        plt.figure(figsize=(10, 6))

        for geo, group in temp.groupby("GEO"):
            group = group.sort_values("year")
            plt.plot(group["year"], group["value"], label=geo)

        plt.xlabel("Year")
        plt.ylabel("GDP at basic prices")
        plt.title(f"Provincial GDP Trend by Industry Code {code}")
        plt.legend()
        plt.tight_layout()

        output_path = FIGURE_DIR / f"provincial_gdp_trend_naics_{code}.png"
        plt.savefig(output_path, dpi=300)
        plt.close()

        print(f"Saved figure: {output_path}")


if __name__ == "__main__":
    main()