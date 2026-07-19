"""Export analytical SQLite views for the Streamlit dashboard."""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "coffee_enthusiasts.db"
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "dashboard"

VIEWS = [
    "vw_respondent_profile",
    "vw_taste_test_analysis",
    "vw_coffee_performance",
    "vw_expertise_summary",
]


def main() -> None:
    """Export each analytical view as a CSV file."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}\n"
            "Run scripts/prepare_data.py and scripts/create_views.py first."
        )

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        for view_name in VIEWS:
            data = pd.read_sql_query(
                f"SELECT * FROM {view_name}",
                connection,
            )

            output_path = OUTPUT_DIRECTORY / f"{view_name}.csv"
            data.to_csv(output_path, index=False)

            print(
                f"Exported {len(data):,} rows to "
                f"{output_path.relative_to(PROJECT_ROOT)}"
            )

    print("\nDashboard export complete.")


if __name__ == "__main__":
    main()