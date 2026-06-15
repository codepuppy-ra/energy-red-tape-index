from pathlib import Path

import pandas as pd


PROJECT_DATA = Path("data/manual/project_dataset.csv")
OUTPUT_DIR = Path("outputs/tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def assign_status_score(status_3cat: str) -> int:
    """
    Higher score = more severe project outcome.
    """
    status = str(status_3cat).lower()

    if any(word in status for word in ["delayed", "cancelled", "withdrawn", "rejected", "suspended"]):
        return 3

    if any(word in status for word in ["operating", "completed"]):
        return 1

    if any(word in status for word in ["starting", "advancing", "approved", "construction"]):
        return 0

    return 2


def assign_cause_score(cause_category: str) -> int:
    """
    Higher score = stronger regulatory/legal/friction component.
    """
    cause = str(cause_category).lower()

    if any(word in cause for word in ["regulatory", "permit", "legal", "consultation", "policy", "climate"]):
        return 3

    if "mixed" in cause:
        return 2

    if any(word in cause for word in ["market", "cost", "financing"]):
        return 1

    return 0


def classify_regulatory_bucket(row: pd.Series) -> str:
    """
    Separates domestic Canadian regulatory cases from cross-border and market cases.
    """
    country = str(row.get("country", "")).lower()
    cause = str(row.get("cause_category", "")).lower()
    jurisdiction = str(row.get("blocking_jurisdiction", "")).lower()

    if "united states" in jurisdiction or "u.s." in cause or "us" in jurisdiction:
        return "Foreign / cross-border permit risk"

    if any(word in cause for word in ["market", "cost", "financing"]):
        return "Market / economic conditions"

    if country == "canada" and any(
        word in cause for word in ["regulatory", "legal", "consultation", "policy", "climate", "permit"]
    ):
        return "Canadian regulatory / legal friction"

    return "Mixed / unclear"


def build_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["status_score"] = df["status_3cat"].apply(assign_status_score)
    df["cause_score"] = df["cause_category"].apply(assign_cause_score)

    df["evidence_score"] = pd.to_numeric(df["evidence_score"], errors="coerce").fillna(0)
    df["capex_billion"] = pd.to_numeric(df["capex_billion"], errors="coerce").fillna(0)

    df["regulatory_bucket"] = df.apply(classify_regulatory_bucket, axis=1)

    # Simple preliminary score from 0 to 3.
    df["raw_friction_score"] = (
        0.40 * df["status_score"]
        + 0.40 * df["cause_score"]
        + 0.20 * df["evidence_score"]
    )

    # Normalize to 0-100.
    df["raw_friction_index_0_100"] = (df["raw_friction_score"] / 3) * 100

    # Evidence-adjusted index.
    df["evidence_weight"] = df["evidence_score"] / 3
    df["adjusted_friction_index_0_100"] = (
        df["raw_friction_index_0_100"] * df["evidence_weight"]
    )

    # Capex weighted by adjusted score.
    df["friction_weighted_capex_billion"] = (
        df["capex_billion"] * df["adjusted_friction_index_0_100"] / 100
    )

    return df


def main() -> None:
    if not PROJECT_DATA.exists():
        raise FileNotFoundError(
            f"{PROJECT_DATA} does not exist. Create data/manual/project_dataset.csv first."
        )

    df = pd.read_csv(PROJECT_DATA)
    results = build_index(df)

    output_path = OUTPUT_DIR / "project_red_tape_index_preliminary.csv"
    results.to_csv(output_path, index=False)

    summary_path = OUTPUT_DIR / "project_red_tape_summary_by_bucket.csv"
    summary = (
        results.groupby("regulatory_bucket", as_index=False)
        .agg(
            projects=("project", "count"),
            total_capex_billion=("capex_billion", "sum"),
            avg_adjusted_friction_index=("adjusted_friction_index_0_100", "mean"),
            friction_weighted_capex_billion=("friction_weighted_capex_billion", "sum"),
        )
        .sort_values("friction_weighted_capex_billion", ascending=False)
    )
    summary.to_csv(summary_path, index=False)

    # Strict estimate: only domestic Canadian regulatory/legal friction cases.
    strict_canadian_regulatory = results[
        results["regulatory_bucket"] == "Canadian regulatory / legal friction"
    ]

    strict_summary = pd.DataFrame(
        {
            "estimate_type": ["Strict Canadian regulatory/legal estimate"],
            "projects": [strict_canadian_regulatory["project"].count()],
            "total_capex_billion": [strict_canadian_regulatory["capex_billion"].sum()],
            "avg_adjusted_friction_index": [
                strict_canadian_regulatory["adjusted_friction_index_0_100"].mean()
            ],
            "friction_weighted_capex_billion": [
                strict_canadian_regulatory["friction_weighted_capex_billion"].sum()
            ],
        }
    )

    strict_path = OUTPUT_DIR / "strict_canadian_regulatory_estimate.csv"
    strict_summary.to_csv(strict_path, index=False)

    # Broader estimate: includes Canadian regulatory/legal friction,
    # foreign permit risk, and market/economic cases affecting Canadian energy projects.
    broader_energy_opportunity = results[
        results["regulatory_bucket"].isin(
            [
                "Canadian regulatory / legal friction",
                "Foreign / cross-border permit risk",
                "Market / economic conditions",
                "Mixed / unclear",
            ]
        )
    ]

    broader_summary = pd.DataFrame(
        {
            "estimate_type": ["Broader Canadian energy opportunity-cost estimate"],
            "projects": [broader_energy_opportunity["project"].count()],
            "total_capex_billion": [broader_energy_opportunity["capex_billion"].sum()],
            "avg_adjusted_friction_index": [
                broader_energy_opportunity["adjusted_friction_index_0_100"].mean()
            ],
            "friction_weighted_capex_billion": [
                broader_energy_opportunity["friction_weighted_capex_billion"].sum()
            ],
        }
    )

    broader_path = OUTPUT_DIR / "broader_energy_opportunity_cost_estimate.csv"
    broader_summary.to_csv(broader_path, index=False)

    print("Saved preliminary red tape index:")
    print(output_path)

    print("\nSaved summary by bucket:")
    print(summary_path)

    print("\nSaved strict Canadian regulatory estimate:")
    print(strict_path)

    print("\nSaved broader energy opportunity-cost estimate:")
    print(broader_path)

    print("\nTop projects by adjusted friction index:")
    print(
        results[
            [
                "project",
                "country",
                "project_type",
                "capex_billion",
                "cause_category",
                "regulatory_bucket",
                "evidence_score",
                "adjusted_friction_index_0_100",
                "friction_weighted_capex_billion",
            ]
        ]
        .sort_values("adjusted_friction_index_0_100", ascending=False)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()