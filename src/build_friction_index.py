"""
Build project-level regulatory friction index.

This script:
1. Loads data/manual/project_dataset_validated.csv
2. Scores each project based on status, cause, and evidence strength
3. Outputs outputs/tables/project_friction_index.csv
4. Outputs outputs/tables/friction_summary_by_bucket.csv
"""

from pathlib import Path

import pandas as pd


INPUT_PATH = Path("data/manual/project_dataset_validated.csv")
OUTPUT_DIR = Path("outputs/tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROJECT_OUTPUT = OUTPUT_DIR / "project_friction_index.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "friction_summary_by_bucket.csv"


def status_score(status_3cat: str) -> int:
    """
    Score project outcome.

    3 = delayed/cancelled/rejected/withdrawn
    1 = operating/completed after some friction
    0 = starting/advancing normally
    """
    value = str(status_3cat).lower()

    if "delayed" in value or "cancelled" in value:
        return 3

    if "operating" in value or "completed" in value:
        return 1

    if "starting" in value or "advancing" in value:
        return 0

    return 0


def cause_score(cause_category: str) -> int:
    """
    Score cause of friction.

    3 = regulatory/legal/consultation/policy/environmental causes
    2 = mixed causes
    1 = market/cost/financing causes
    0 = proceeding/no major friction
    """
    value = str(cause_category).lower()

    high_friction_terms = [
        "regulatory",
        "legal",
        "consultation",
        "policy",
        "climate",
        "environmental",
        "permit",
        "assessment",
        "court",
    ]

    market_terms = [
        "market",
        "cost",
        "financing",
        "economic",
        "price",
    ]

    proceeding_terms = [
        "proceeding",
        "under construction",
        "fid",
        "final investment decision",
    ]

    if any(term in value for term in high_friction_terms):
        return 3

    if "mixed" in value:
        return 2

    if any(term in value for term in market_terms):
        return 1

    if any(term in value for term in proceeding_terms):
        return 0

    return 1


def regulatory_bucket(row: pd.Series) -> str:
    """
    Classify project into broad friction bucket.
    """
    cause = str(row["cause_category"]).lower()
    jurisdiction = str(row["blocking_jurisdiction"]).lower()

    if "united states" in jurisdiction or "u.s." in cause:
        return "Foreign/cross-border"

    if any(
        term in cause
        for term in [
            "regulatory",
            "legal",
            "consultation",
            "policy",
            "climate",
            "environmental",
            "assessment",
            "permit",
            "court",
        ]
    ):
        return "Canadian regulatory/legal"

    if any(
        term in cause
        for term in [
            "market",
            "cost",
            "financing",
            "economic",
            "price",
        ]
    ):
        return "Market/economic"

    if "mixed" in jurisdiction or "mixed" in cause:
        return "Mixed"

    return "Other/unclear"


def build_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build project-level friction index.
    """
    df = df.copy()

    df["capex_billion"] = pd.to_numeric(df["capex_billion"], errors="coerce")
    df["evidence_score"] = pd.to_numeric(df["evidence_score"], errors="coerce").fillna(0)

    df["status_score"] = df["status_3cat"].apply(status_score)
    df["cause_score"] = df["cause_category"].apply(cause_score)

    # Evidence score is 0 to 3, so divide by 3 to get 0 to 1.
    df["evidence_weight"] = df["evidence_score"] / 3

    # Raw score combines outcome and cause.
    # Outcome gets 50%, cause gets 50%.
    df["raw_friction_index_0_100"] = (
        (df["status_score"] / 3 * 0.50)
        + (df["cause_score"] / 3 * 0.50)
    ) * 100

    # Adjusted score discounts weak evidence.
    df["adjusted_friction_index_0_100"] = (
        df["raw_friction_index_0_100"] * df["evidence_weight"]
    )

    # Capital exposure weighted by friction score.
    df["friction_weighted_capex_billion"] = (
        df["capex_billion"] * df["adjusted_friction_index_0_100"] / 100
    )

    df["regulatory_bucket"] = df.apply(regulatory_bucket, axis=1)

    return df


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize friction results by broad bucket.
    """
    summary = (
        df.groupby("regulatory_bucket")
        .agg(
            projects=("project", "count"),
            total_capex_billion=("capex_billion", "sum"),
            average_raw_friction_index=("raw_friction_index_0_100", "mean"),
            average_adjusted_friction_index=("adjusted_friction_index_0_100", "mean"),
            friction_weighted_capex_billion=("friction_weighted_capex_billion", "sum"),
        )
        .reset_index()
    )

    return summary.round(2)


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing input file: {INPUT_PATH}. "
            "Run scripts/build_project_dataset.py first."
        )

    df = pd.read_csv(INPUT_PATH)

    index_df = build_index(df)
    summary_df = build_summary(index_df)

    index_df.to_csv(PROJECT_OUTPUT, index=False)
    summary_df.to_csv(SUMMARY_OUTPUT, index=False)

    print("Built project-level regulatory friction index.")
    print(f"Saved project index to: {PROJECT_OUTPUT}")
    print(f"Saved summary table to: {SUMMARY_OUTPUT}")
    print()
    print(summary_df)


if __name__ == "__main__":
    main()