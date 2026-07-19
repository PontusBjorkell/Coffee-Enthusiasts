"""Prepare the Coffee Taste Test survey for SQL analysis.

The pipeline:

1. Reads the untouched source CSV.
2. Validates required fields, identifiers, and rating ranges.
3. Splits the flat survey into five normalized analytical tables.
4. Reshapes Coffee A-D ratings into a long-format taste-test table.
5. Adds documented analytical fields for categorical spending.
6. Writes processed CSV files.
7. Creates and populates a SQLite database.
8. Verifies row counts and relational integrity.
"""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "coffee_taste_test.csv"
)

PROCESSED_DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "coffee_enthusiasts.db"
)


COFFEE_CODES = ("A", "B", "C", "D")

RATING_COLUMNS = (
    "bitterness",
    "acidity",
    "personal_preference",
)

SPENDING_BAND_ORDER = {
    "<$20": 1,
    "$20-$40": 2,
    "$40-$60": 3,
    "$60-$80": 4,
    "$80-$100": 5,
    ">$100": 6,
}

# These values are analytical estimates, not exact respondent spending.
# Closed ranges use their midpoint. Open-ended ranges use a documented
# representative value.
SPENDING_BAND_MIDPOINTS = {
    "<$20": 10.0,
    "$20-$40": 30.0,
    "$40-$60": 50.0,
    "$60-$80": 70.0,
    "$80-$100": 90.0,
    ">$100": 110.0,
}


def validate_source_data(data: pd.DataFrame) -> None:
    """Validate the raw survey before performing transformations."""

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
                (
                    f"coffee_{coffee_code}_"
                    "personal_preference"
                ),
                f"coffee_{coffee_code}_notes",
            }
        )

    missing_columns = sorted(
        required_columns.difference(data.columns)
    )

    if missing_columns:
        missing_list = ", ".join(missing_columns)

        raise ValueError(
            "Source data is missing required columns: "
            f"{missing_list}"
        )

    if data.empty:
        raise ValueError("The source dataset contains no rows.")

    if data["submission_id"].isna().any():
        raise ValueError(
            "The source data contains missing submission IDs."
        )

    if data["submission_id"].duplicated().any():
        duplicate_count = int(
            data["submission_id"].duplicated().sum()
        )

        raise ValueError(
            "The source data contains "
            f"{duplicate_count:,} duplicate submission IDs."
        )


def validate_numeric_range(
    values: pd.Series,
    column_name: str,
    minimum: int,
    maximum: int,
) -> None:
    """Validate a numeric survey field while allowing missing values."""

    numeric_values = pd.to_numeric(
        values,
        errors="coerce",
    )

    invalid_mask = (
        numeric_values.notna()
        & ~numeric_values.between(
            minimum,
            maximum,
            inclusive="both",
        )
    )

    if invalid_mask.any():
        invalid_values = sorted(
            numeric_values.loc[invalid_mask]
            .dropna()
            .unique()
            .tolist()
        )

        raise ValueError(
            f"{column_name} contains values outside "
            f"{minimum}-{maximum}: {invalid_values}"
        )


def validate_rating_columns(data: pd.DataFrame) -> None:
    """Validate expertise and Coffee A-D sensory ratings."""

    validate_numeric_range(
        data["expertise"],
        column_name="expertise",
        minimum=1,
        maximum=10,
    )

    for coffee_code in ("a", "b", "c", "d"):
        for measure in (
            "bitterness",
            "acidity",
            "personal_preference",
        ):
            column_name = (
                f"coffee_{coffee_code}_{measure}"
            )

            validate_numeric_range(
                data[column_name],
                column_name=column_name,
                minimum=1,
                maximum=5,
            )


def build_participants(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Create one row per survey respondent."""

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

    participants = participants.rename(
        columns={
            "wfh": "work_from_home",
        }
    )

    return participants


def build_coffee_habits(
    data: pd.DataFrame,
) -> pd.DataFrame:
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
            (
                "why_drink_other"
            ): "reasons_for_drinking_other",
            "taste": "likes_coffee_taste",
            "know_source": "knows_coffee_source",
        }
    )

    coffee_habits["expertise"] = pd.to_numeric(
        coffee_habits["expertise"],
        errors="coerce",
    ).astype("Int64")

    return coffee_habits


def build_spending(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Create spending fields, including documented band estimates."""

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

    spending = spending.rename(
        columns={
            "total_spend": "monthly_coffee_spend",
            "most_paid": "most_paid_for_coffee",
            "most_willing": "most_willing_to_pay",
            "value_cafe": "cafe_coffee_good_value",
            "spent_equipment": "equipment_spend",
            "value_equipment": "equipment_good_value",
        }
    )

    spending["monthly_coffee_spend"] = (
        spending["monthly_coffee_spend"]
        .astype("string")
        .str.strip()
    )

    spending["monthly_spend_band_order"] = (
        spending["monthly_coffee_spend"]
        .map(SPENDING_BAND_ORDER)
        .astype("Int64")
    )

    spending["estimated_monthly_spend"] = (
        spending["monthly_coffee_spend"]
        .map(SPENDING_BAND_MIDPOINTS)
        .astype("Float64")
    )

    return spending


def build_taste_tests(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Reshape Coffee A-D results from wide to long format."""

    taste_test_frames: list[pd.DataFrame] = []

    for coffee_code in COFFEE_CODES:
        source_prefix = (
            f"coffee_{coffee_code.lower()}"
        )

        coffee_results = data[
            [
                "submission_id",
                f"{source_prefix}_bitterness",
                f"{source_prefix}_acidity",
                (
                    f"{source_prefix}_"
                    "personal_preference"
                ),
                f"{source_prefix}_notes",
            ]
        ].copy()

        coffee_results = coffee_results.rename(
            columns={
                (
                    f"{source_prefix}_bitterness"
                ): "bitterness",
                (
                    f"{source_prefix}_acidity"
                ): "acidity",
                (
                    f"{source_prefix}_"
                    "personal_preference"
                ): "personal_preference",
                (
                    f"{source_prefix}_notes"
                ): "tasting_notes",
            }
        )

        coffee_results.insert(
            loc=1,
            column="coffee_code",
            value=coffee_code,
        )

        taste_test_frames.append(coffee_results)

    taste_tests = pd.concat(
        taste_test_frames,
        ignore_index=True,
    )

    for column in RATING_COLUMNS:
        taste_tests[column] = pd.to_numeric(
            taste_tests[column],
            errors="coerce",
        ).astype("Int64")

    return taste_tests


def build_overall_preferences(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Create respondent-level overall coffee choices."""

    overall_preferences = data[
        [
            "submission_id",
            "prefer_abc",
            "prefer_ad",
            "prefer_overall",
        ]
    ].copy()

    overall_preferences = overall_preferences.rename(
        columns={
            "prefer_abc": "preferred_abc",
            "prefer_ad": "preferred_a_or_d",
            "prefer_overall": "preferred_overall",
        }
    )

    return overall_preferences


def validate_transformed_tables(
    tables: dict[str, pd.DataFrame],
    source_row_count: int,
) -> None:
    """Check transformed row counts and key uniqueness."""

    one_row_tables = (
        "participants",
        "coffee_habits",
        "spending",
        "overall_preferences",
    )

    for table_name in one_row_tables:
        table = tables[table_name]

        if len(table) != source_row_count:
            raise ValueError(
                f"{table_name} contains {len(table):,} rows; "
                f"expected {source_row_count:,}."
            )

        if table["submission_id"].duplicated().any():
            raise ValueError(
                f"{table_name} contains duplicate "
                "submission IDs."
            )

    expected_taste_rows = (
        source_row_count * len(COFFEE_CODES)
    )

    taste_tests = tables["taste_tests"]

    if len(taste_tests) != expected_taste_rows:
        raise ValueError(
            "taste_tests contains "
            f"{len(taste_tests):,} rows; "
            f"expected {expected_taste_rows:,}."
        )

    duplicate_taste_keys = taste_tests.duplicated(
        subset=[
            "submission_id",
            "coffee_code",
        ]
    )

    if duplicate_taste_keys.any():
        raise ValueError(
            "taste_tests contains duplicate "
            "submission_id and coffee_code combinations."
        )

    observed_codes = set(
        taste_tests["coffee_code"]
        .dropna()
        .unique()
    )

    if observed_codes != set(COFFEE_CODES):
        raise ValueError(
            "Unexpected coffee codes found: "
            f"{sorted(observed_codes)}"
        )


def write_processed_csvs(
    tables: dict[str, pd.DataFrame],
) -> None:
    """Write each normalized table to a processed CSV."""

    PROCESSED_DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    for table_name, table in tables.items():
        output_path = (
            PROCESSED_DATA_DIRECTORY
            / f"{table_name}.csv"
        )

        table.to_csv(
            output_path,
            index=False,
        )

        relative_path = output_path.relative_to(
            PROJECT_ROOT
        )

        print(
            f"Wrote {len(table):,} rows to "
            f"{relative_path}"
        )


def create_database(
    tables: dict[str, pd.DataFrame],
) -> None:
    """Rebuild and populate the SQLite database."""

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema file not found: {SCHEMA_PATH}"
        )

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    schema_sql = SCHEMA_PATH.read_text(
        encoding="utf-8"
    )

    insertion_order = [
        "participants",
        "coffee_habits",
        "spending",
        "taste_tests",
        "overall_preferences",
    ]

    with sqlite3.connect(
        DATABASE_PATH
    ) as connection:
        connection.execute(
            "PRAGMA foreign_keys = ON;"
        )

        connection.executescript(schema_sql)

        for table_name in insertion_order:
            tables[table_name].to_sql(
                table_name,
                connection,
                if_exists="append",
                index=False,
            )

        connection.commit()

    print(
        "Created SQLite database at "
        f"{DATABASE_PATH.relative_to(PROJECT_ROOT)}"
    )


def verify_database(
    expected_respondents: int,
) -> None:
    """Verify row counts, foreign keys, and database integrity."""

    expected_counts = {
        "participants": expected_respondents,
        "coffee_habits": expected_respondents,
        "spending": expected_respondents,
        "taste_tests": (
            expected_respondents
            * len(COFFEE_CODES)
        ),
        "overall_preferences": expected_respondents,
    }

    print("\nDatabase verification:")

    with sqlite3.connect(
        DATABASE_PATH
    ) as connection:
        connection.execute(
            "PRAGMA foreign_keys = ON;"
        )

        for table_name, expected_count in (
            expected_counts.items()
        ):
            row_count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]

            if row_count != expected_count:
                raise ValueError(
                    f"{table_name} contains "
                    f"{row_count:,} rows; expected "
                    f"{expected_count:,}."
                )

            print(
                f"  {table_name}: "
                f"{row_count:,} rows"
            )

        foreign_key_issues = connection.execute(
            "PRAGMA foreign_key_check;"
        ).fetchall()

        if foreign_key_issues:
            raise ValueError(
                "Foreign-key validation failed: "
                f"{foreign_key_issues}"
            )

        integrity_result = connection.execute(
            "PRAGMA integrity_check;"
        ).fetchone()[0]

        if integrity_result != "ok":
            raise ValueError(
                "SQLite integrity check failed: "
                f"{integrity_result}"
            )

    print("  Foreign keys: valid")
    print("  SQLite integrity check: ok")


def main() -> None:
    """Run the complete data-preparation pipeline."""

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            "Raw dataset not found. Expected:\n"
            f"{RAW_DATA_PATH}"
        )

    source_data = pd.read_csv(
        RAW_DATA_PATH
    )

    validate_source_data(source_data)
    validate_rating_columns(source_data)

    tables = {
        "participants": build_participants(
            source_data
        ),
        "coffee_habits": build_coffee_habits(
            source_data
        ),
        "spending": build_spending(
            source_data
        ),
        "taste_tests": build_taste_tests(
            source_data
        ),
        "overall_preferences": (
            build_overall_preferences(
                source_data
            )
        ),
    }

    validate_transformed_tables(
        tables=tables,
        source_row_count=len(source_data),
    )

    write_processed_csvs(tables)
    create_database(tables)

    verify_database(
        expected_respondents=len(source_data)
    )

    print("\nData preparation complete.")


if __name__ == "__main__":
    main()