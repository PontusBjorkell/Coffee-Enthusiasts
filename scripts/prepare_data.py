"""Prepare the Coffee Taste Test survey for SQL analysis.

This script:
1. Reads the untouched survey CSV.
2. Splits the flat dataset into five analytical tables.
3. Reshapes Coffee A-D ratings into a long-format taste-test table.
4. Writes processed CSV files.
5. Creates and populates a SQLite database.
"""

from pathlib import Path
import sqlite3

import pandas as pd


# Resolve paths relative to the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "coffee_taste_test.csv"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"
DATABASE_PATH = PROJECT_ROOT / "data" / "coffee_enthusiasts.db"


def validate_source_data(data: pd.DataFrame) -> None:
    """Check that the source dataset contains the required columns."""

    required_columns = {
        "submission_id",
        "age",
        "gender",
        "gender_specify",
        "education_level",
        "ethnicity_race",
        "ethnicity_race_specify",
        "employment_status",
        "number_children",
        "political_affiliation",
        "wfh",
        "cups",
        "where_drink",
        "brew",
        "brew_other",
        "purchase",
        "purchase_other",
        "favorite",
        "favorite_specify",
        "additions",
        "additions_other",
        "dairy",
        "sweetener",
        "style",
        "strength",
        "roast_level",
        "caffeine",
        "expertise",
        "why_drink",
        "why_drink_other",
        "taste",
        "know_source",
        "total_spend",
        "most_paid",
        "most_willing",
        "value_cafe",
        "spent_equipment",
        "value_equipment",
        "prefer_abc",
        "prefer_ad",
        "prefer_overall",
    }

    for coffee_code in ("a", "b", "c", "d"):
        required_columns.update(
            {
                f"coffee_{coffee_code}_bitterness",
                f"coffee_{coffee_code}_acidity",
                f"coffee_{coffee_code}_personal_preference",
                f"coffee_{coffee_code}_notes",
            }
        )

    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        missing_list = ", ".join(sorted(missing_columns))
        raise ValueError(f"Source data is missing columns: {missing_list}")

    if data["submission_id"].isna().any():
        raise ValueError("The source data contains missing submission IDs.")

    if data["submission_id"].duplicated().any():
        raise ValueError("The source data contains duplicate submission IDs.")


def build_participants(data: pd.DataFrame) -> pd.DataFrame:
    """Create one row per survey participant."""

    participants = data[
        [
            "submission_id",
            "age",
            "gender",
            "gender_specify",
            "education_level",
            "ethnicity_race",
            "ethnicity_race_specify",
            "employment_status",
            "number_children",
            "political_affiliation",
            "wfh",
        ]
    ].copy()

    return participants.rename(columns={"wfh": "work_from_home"})


def build_coffee_habits(data: pd.DataFrame) -> pd.DataFrame:
    """Create the respondent-level coffee habits table."""

    coffee_habits = data[
        [
            "submission_id",
            "cups",
            "where_drink",
            "brew",
            "brew_other",
            "purchase",
            "purchase_other",
            "favorite",
            "favorite_specify",
            "additions",
            "additions_other",
            "dairy",
            "sweetener",
            "style",
            "strength",
            "roast_level",
            "caffeine",
            "expertise",
            "why_drink",
            "why_drink_other",
            "taste",
            "know_source",
        ]
    ].copy()

    coffee_habits = coffee_habits.rename(
        columns={
            "cups": "cups_per_day",
            "brew": "brew_methods",
            "purchase": "purchase_locations",
            "favorite": "favorite_drink",
            "style": "preferred_style",
            "strength": "preferred_strength",
            "roast_level": "preferred_roast_level",
            "caffeine": "caffeine_preference",
            "why_drink": "reasons_for_drinking",
            "why_drink_other": "reasons_for_drinking_other",
            "taste": "likes_coffee_taste",
            "know_source": "knows_coffee_source",
        }
    )

    coffee_habits["expertise"] = pd.to_numeric(
        coffee_habits["expertise"],
        errors="coerce",
    ).astype("Int64")

    return coffee_habits


def build_spending(data: pd.DataFrame) -> pd.DataFrame:
    """Create the respondent-level spending table."""

    spending = data[
        [
            "submission_id",
            "total_spend",
            "most_paid",
            "most_willing",
            "value_cafe",
            "spent_equipment",
            "value_equipment",
        ]
    ].copy()

    return spending.rename(
        columns={
            "total_spend": "monthly_coffee_spend",
            "most_paid": "most_paid_for_coffee",
            "most_willing": "most_willing_to_pay",
            "value_cafe": "cafe_coffee_good_value",
            "spent_equipment": "equipment_spend",
            "value_equipment": "equipment_good_value",
        }
    )


def build_taste_tests(data: pd.DataFrame) -> pd.DataFrame:
    """Reshape Coffee A-D results from wide format into long format."""

    taste_test_frames: list[pd.DataFrame] = []

    for coffee_code in ("A", "B", "C", "D"):
        source_prefix = f"coffee_{coffee_code.lower()}"

        coffee_results = data[
            [
                "submission_id",
                f"{source_prefix}_bitterness",
                f"{source_prefix}_acidity",
                f"{source_prefix}_personal_preference",
                f"{source_prefix}_notes",
            ]
        ].copy()

        coffee_results = coffee_results.rename(
            columns={
                f"{source_prefix}_bitterness": "bitterness",
                f"{source_prefix}_acidity": "acidity",
                f"{source_prefix}_personal_preference": (
                    "personal_preference"
                ),
                f"{source_prefix}_notes": "tasting_notes",
            }
        )

        coffee_results.insert(1, "coffee_code", coffee_code)
        taste_test_frames.append(coffee_results)

    taste_tests = pd.concat(taste_test_frames, ignore_index=True)

    rating_columns = [
        "bitterness",
        "acidity",
        "personal_preference",
    ]

    for column in rating_columns:
        taste_tests[column] = pd.to_numeric(
            taste_tests[column],
            errors="coerce",
        ).astype("Int64")

    return taste_tests


def build_overall_preferences(data: pd.DataFrame) -> pd.DataFrame:
    """Create respondent-level overall coffee choices."""

    overall_preferences = data[
        [
            "submission_id",
            "prefer_abc",
            "prefer_ad",
            "prefer_overall",
        ]
    ].copy()

    return overall_preferences.rename(
        columns={
            "prefer_abc": "preferred_abc",
            "prefer_ad": "preferred_a_or_d",
            "prefer_overall": "preferred_overall",
        }
    )


def write_processed_csvs(tables: dict[str, pd.DataFrame]) -> None:
    """Write each processed table to a separate CSV file."""

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for table_name, table in tables.items():
        output_path = PROCESSED_DATA_DIR / f"{table_name}.csv"
        table.to_csv(output_path, index=False)
        print(f"Wrote {len(table):,} rows to {output_path}")


def create_database(tables: dict[str, pd.DataFrame]) -> None:
    """Create the SQLite database and insert the processed data."""

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    # Rebuild the database so rerunning the script produces predictable results.
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.executescript(schema_sql)

        # Parent table must be inserted before tables with foreign keys.
        insertion_order = [
            "participants",
            "coffee_habits",
            "spending",
            "taste_tests",
            "overall_preferences",
        ]

        for table_name in insertion_order:
            tables[table_name].to_sql(
                table_name,
                connection,
                if_exists="append",
                index=False,
            )

        connection.commit()

    print(f"Created SQLite database at {DATABASE_PATH}")


def verify_database() -> None:
    """Print row counts from the finished SQLite database."""

    table_names = [
        "participants",
        "coffee_habits",
        "spending",
        "taste_tests",
        "overall_preferences",
    ]

    print("\nDatabase verification:")

    with sqlite3.connect(DATABASE_PATH) as connection:
        for table_name in table_names:
            row_count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]

            print(f"  {table_name}: {row_count:,} rows")


def main() -> None:
    """Run the complete data-preparation workflow."""

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            "Raw dataset not found. Expected it at:\n"
            f"{RAW_DATA_PATH}"
        )

    source_data = pd.read_csv(RAW_DATA_PATH)
    validate_source_data(source_data)

    tables = {
        "participants": build_participants(source_data),
        "coffee_habits": build_coffee_habits(source_data),
        "spending": build_spending(source_data),
        "taste_tests": build_taste_tests(source_data),
        "overall_preferences": build_overall_preferences(source_data),
    }

    write_processed_csvs(tables)
    create_database(tables)
    verify_database()


if __name__ == "__main__":
    main()