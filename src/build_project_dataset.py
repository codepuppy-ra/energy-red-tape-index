"""
Builds or validates the manual project-level dataset.

This file will later be used to create a structured dataset of Canadian
oil and gas projects, including project status, NAICS category, capex,
evidence score, and stated reason for delay or cancellation.
"""

from pathlib import Path

import pandas as pd


MANUAL_DIR = Path("data/manual")
MANUAL_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print("Project dataset builder placeholder.")
    print("Next step: create data/manual/project_dataset.csv")


if __name__ == "__main__":
    main()