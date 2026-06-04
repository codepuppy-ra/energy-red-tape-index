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

    if "delayed" in status or "cancelled" in status or "withdrawn" in status:
        return 3
    if "operating" in status or "completed" in status:
        return 1
    if "starting" in status or "advancing" in status:
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


def build_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["status_score"] = df["status_3cat"].apply(assign_status_score)
    df["cause_score"] = df["cause_category"].apply(assign_cause_score)

    # Evidence score should already be 0-3.
    df["evidence_score"] = pd.to_numeric(df["evidence_score"], errors="coerce").fillna(0)

    # Simple preliminary raw score.
    df["raw_friction_score"] = (
        0.40 * df["status_score"] +
        0.40 * df["cause_score"] +
        0.20 * df["evidence_score"]
    )

    # Normalize to 0-100.
    df["raw_friction_index_0_100"] = (df["raw_friction_score"] / 3) * 100

    # Evidence-adjusted index.
    df["evidence_weight"] = df["evidence_score"] / 3
    df["adjusted_friction_index_0_100"] = (
        df["raw_friction_index_0_100"] * df["evidence_weight"]
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

    print("Saved preliminary red tape index:")
    print(output_path)

    print("\nTop projects by adjusted friction index:")
    print(
        results[
            [
                "project",
                "country",
                "project_type",
                "capex_billion",
                "cause_category",
                "evidence_score",
                "adjusted_friction_index_0_100",
            ]
        ]
        .sort_values("adjusted_friction_index_0_100", ascending=False)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()