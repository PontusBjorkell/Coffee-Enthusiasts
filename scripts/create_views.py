"""Create and verify the project's analytical SQLite views."""

from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "coffee_enthusiasts.db"
)

VIEWS_PATH = (
    PROJECT_ROOT
    / "sql"
    / "views.sql"
)

EXPECTED_VIEWS = (
    "vw_respondent_profile",
    "vw_taste_test_analysis",
    "vw_coffee_performance",
    "vw_expertise_summary",
    "vw_segment_coffee_performance",
)


def verify_view_exists(
    connection: sqlite3.Connection,
    view_name: str,
) -> None:
    """Raise an error when an expected view was not created."""

    result = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE
            type = 'view'
            AND name = ?
        """,
        (view_name,),
    ).fetchone()

    if result is None:
        raise RuntimeError(
            f"Expected view was not created: {view_name}"
        )


def main() -> None:
    """Create all analytical views and verify their row counts."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}\n"
            "Run scripts/prepare_data.py first."
        )

    if not VIEWS_PATH.exists():
        raise FileNotFoundError(
            f"Views file not found: {VIEWS_PATH}"
        )

    views_sql = VIEWS_PATH.read_text(
        encoding="utf-8"
    )

    with sqlite3.connect(
        DATABASE_PATH
    ) as connection:
        connection.execute(
            "PRAGMA foreign_keys = ON;"
        )

        connection.executescript(views_sql)
        connection.commit()

        print("Analytical view verification:")

        for view_name in EXPECTED_VIEWS:
            verify_view_exists(
                connection,
                view_name,
            )

            row_count = connection.execute(
                f"SELECT COUNT(*) FROM {view_name}"
            ).fetchone()[0]

            print(
                f"  {view_name}: "
                f"{row_count:,} rows"
            )

        respondent_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM participants
            """
        ).fetchone()[0]

        profile_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM vw_respondent_profile
            """
        ).fetchone()[0]

        if profile_count != respondent_count:
            raise RuntimeError(
                "vw_respondent_profile row count "
                "does not match participants."
            )

        duplicate_profile_ids = connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT submission_id
                FROM vw_respondent_profile
                GROUP BY submission_id
                HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]

        if duplicate_profile_ids:
            raise RuntimeError(
                "vw_respondent_profile contains "
                "duplicate submission IDs."
            )

    print("\nAnalytical views created successfully.")


if __name__ == "__main__":
    main()