from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


INDEX_FILE = Path("outputs/tables/project_red_tape_index_preliminary.csv")
SUMMARY_FILE = Path("outputs/tables/project_red_tape_summary_by_bucket.csv")
FIGURE_DIR = Path("outputs/figures")
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def add_bar_labels(values):
    """
    Adds clean dollar-value labels to horizontal bars.
    Places labels inside longer bars and outside shorter bars.
    """
    max_value = max(values)

    for i, value in enumerate(values):
        label = f"${value:.1f}B"

        if value > max_value * 0.25:
            plt.text(
                value - max_value * 0.03,
                i,
                label,
                va="center",
                ha="right",
                color="white",
                fontweight="bold",
            )
        else:
            plt.text(
                value + max_value * 0.02,
                i,
                label,
                va="center",
                ha="left",
            )


def make_project_friction_chart(df: pd.DataFrame) -> None:
    df_sorted = df.sort_values("adjusted_friction_index_0_100", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(df_sorted["project"], df_sorted["adjusted_friction_index_0_100"])
    plt.xlabel("Adjusted Friction Index, 0-100")
    plt.ylabel("Project")
    plt.title("Preliminary Evidence-Adjusted Regulatory Friction Index")
    plt.xlim(0, 110)

    for i, value in enumerate(df_sorted["adjusted_friction_index_0_100"]):
        if value > 30:
            plt.text(
                value - 3,
                i,
                f"{value:.1f}",
                va="center",
                ha="right",
                color="white",
                fontweight="bold",
            )
        else:
            plt.text(
                value + 2,
                i,
                f"{value:.1f}",
                va="center",
                ha="left",
            )

    plt.tight_layout()

    output_path = FIGURE_DIR / "preliminary_friction_index_by_project.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved figure: {output_path}")


def make_capex_by_bucket_chart(summary: pd.DataFrame) -> None:
    summary_sorted = summary.sort_values(
        "friction_weighted_capex_billion",
        ascending=True,
    )

    plt.figure(figsize=(11, 6))
    plt.barh(
        summary_sorted["regulatory_bucket"],
        summary_sorted["friction_weighted_capex_billion"],
    )
    plt.xlabel("Friction-Weighted Capex Exposure, $ billions")
    plt.ylabel("Project Category")
    plt.title("Preliminary Friction-Weighted Capex Exposure by Category")
    plt.xlim(0, summary_sorted["friction_weighted_capex_billion"].max() * 1.12)

    add_bar_labels(summary_sorted["friction_weighted_capex_billion"])

    plt.tight_layout()

    output_path = FIGURE_DIR / "friction_weighted_capex_by_bucket.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved figure: {output_path}")


def make_total_capex_by_bucket_chart(summary: pd.DataFrame) -> None:
    summary_sorted = summary.sort_values("total_capex_billion", ascending=True)

    plt.figure(figsize=(11, 6))
    plt.barh(
        summary_sorted["regulatory_bucket"],
        summary_sorted["total_capex_billion"],
    )
    plt.xlabel("Total Proposed Capex, $ billions")
    plt.ylabel("Project Category")
    plt.title("Preliminary Total Proposed Capex by Category")
    plt.xlim(0, summary_sorted["total_capex_billion"].max() * 1.12)

    add_bar_labels(summary_sorted["total_capex_billion"])

    plt.tight_layout()

    output_path = FIGURE_DIR / "total_capex_by_bucket.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved figure: {output_path}")


def make_projects_by_status_chart(df: pd.DataFrame) -> None:
    counts = df["status_3cat"].value_counts().sort_values()

    plt.figure(figsize=(10, 6))
    plt.barh(counts.index, counts.values)
    plt.xlabel("Number of Projects")
    plt.ylabel("Project Status Category")
    plt.title("Preliminary Project Count by Status")
    plt.tight_layout()

    output_path = FIGURE_DIR / "project_count_by_status.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved figure: {output_path}")


def make_capex_by_project_type_chart(df: pd.DataFrame) -> None:
    summary = (
        df.groupby("project_type", as_index=False)
        .agg(total_capex_billion=("capex_billion", "sum"))
        .sort_values("total_capex_billion", ascending=True)
    )

    plt.figure(figsize=(10, 6))
    plt.barh(summary["project_type"], summary["total_capex_billion"])
    plt.xlabel("Total Proposed Capex, $ billions")
    plt.ylabel("Project Type")
    plt.title("Preliminary Total Proposed Capex by Project Type")
    plt.tight_layout()

    output_path = FIGURE_DIR / "total_capex_by_project_type.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved figure: {output_path}")


def make_avg_friction_by_project_type_chart(df: pd.DataFrame) -> None:
    summary = (
        df.groupby("project_type", as_index=False)
        .agg(avg_friction_index=("adjusted_friction_index_0_100", "mean"))
        .sort_values("avg_friction_index", ascending=True)
    )

    plt.figure(figsize=(10, 6))
    plt.barh(summary["project_type"], summary["avg_friction_index"])
    plt.xlabel("Average Adjusted Friction Index, 0-100")
    plt.ylabel("Project Type")
    plt.title("Preliminary Average Friction Index by Project Type")
    plt.tight_layout()

    output_path = FIGURE_DIR / "avg_friction_by_project_type.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved figure: {output_path}")


def make_projects_by_blocking_jurisdiction_chart(df: pd.DataFrame) -> None:
    counts = df["blocking_jurisdiction"].value_counts().sort_values()

    plt.figure(figsize=(10, 6))
    plt.barh(counts.index, counts.values)
    plt.xlabel("Number of Projects")
    plt.ylabel("Blocking Jurisdiction / Main Constraint")
    plt.title("Preliminary Project Count by Blocking Jurisdiction")
    plt.tight_layout()

    output_path = FIGURE_DIR / "project_count_by_blocking_jurisdiction.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved figure: {output_path}")


def main() -> None:
    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            "Index file not found. Run src/red_tape_index.py first."
        )

    if not SUMMARY_FILE.exists():
        raise FileNotFoundError(
            "Summary file not found. Run src/red_tape_index.py first."
        )

    df = pd.read_csv(INDEX_FILE)
    summary = pd.read_csv(SUMMARY_FILE)

    make_project_friction_chart(df)
    make_capex_by_bucket_chart(summary)
    make_total_capex_by_bucket_chart(summary)
    make_projects_by_status_chart(df)
    make_capex_by_project_type_chart(df)
    make_avg_friction_by_project_type_chart(df)
    make_projects_by_blocking_jurisdiction_chart(df)


if __name__ == "__main__":
    main()
    