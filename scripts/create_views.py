"""Create analytical SQLite views used by Power BI."""

from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = PROJECT_ROOT / "data" / "coffee_enthusiasts.db"
VIEWS_PATH = PROJECT_ROOT / "sql" / "views.sql"


def main() -> None:
    """Create the analytical views and verify their row counts."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}\n"
            "Run scripts/prepare_data.py first."
        )

    if not VIEWS_PATH.exists():
        raise FileNotFoundError(
            f"Views file not found: {VIEWS_PATH}"
        )

    views_sql = VIEWS_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(views_sql)
        connection.commit()

        views = [
            "vw_respondent_profile",
            "vw_taste_test_analysis",
            "vw_coffee_performance",
            "vw_expertise_summary",
        ]

        print("View verification:")

        for view_name in views:
            row_count = connection.execute(
                f"SELECT COUNT(*) FROM {view_name}"
            ).fetchone()[0]

            print(f"  {view_name}: {row_count:,} rows")


if __name__ == "__main__":
    main()