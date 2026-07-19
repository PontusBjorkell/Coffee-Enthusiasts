"""Export analytical SQLite views for the Streamlit dashboard."""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "coffee_enthusiasts.db"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "dashboard"
)

DASHBOARD_VIEWS = (
    "vw_respondent_profile",
    "vw_taste_test_analysis",
    "vw_coffee_performance",
    "vw_expertise_summary",
    "vw_segment_coffee_performance",
)


def view_exists(
    connection: sqlite3.Connection,
    view_name: str,
) -> bool:
    """Return whether a named SQLite view exists."""

    result = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE
            type = 'view'
            AND name = ?
        """,
        (view_name,),
    ).fetchone()

    return result is not None


def main() -> None:
    """Export each dashboard view as a UTF-8 CSV file."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}\n"
            "Run scripts/prepare_data.py first."
        )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(
        DATABASE_PATH
    ) as connection:
        missing_views = [
            view_name
            for view_name in DASHBOARD_VIEWS
            if not view_exists(
                connection,
                view_name,
            )
        ]

        if missing_views:
            missing_list = ", ".join(
                missing_views
            )

            raise RuntimeError(
                "Dashboard views are missing: "
                f"{missing_list}\n"
                "Run scripts/create_views.py first."
            )

        for view_name in DASHBOARD_VIEWS:
            data = pd.read_sql_query(
                f"SELECT * FROM {view_name}",
                connection,
            )

            if data.empty:
                raise RuntimeError(
                    f"{view_name} returned no rows."
                )

            output_path = (
                OUTPUT_DIRECTORY
                / f"{view_name}.csv"
            )

            data.to_csv(
                output_path,
                index=False,
                encoding="utf-8",
            )

            relative_path = output_path.relative_to(
                PROJECT_ROOT
            )

            print(
                f"Exported {len(data):,} rows to "
                f"{relative_path}"
            )

    print("\nDashboard export complete.")


if __name__ == "__main__":
    main()