"""Run all numbered portfolio SQL queries and export the results."""

from pathlib import Path
import re
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "coffee_enthusiasts.db"
)

QUERY_PATH = (
    PROJECT_ROOT
    / "sql"
    / "analysis_queries.sql"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "analysis_results"
)

QUERY_HEADER_PATTERN = re.compile(
    r"^-- (\d+)\. (.+?)\s*$",
    flags=re.MULTILINE,
)


def create_safe_filename(
    query_number: int,
    title: str,
) -> str:
    """Create a consistent filename from a query title."""

    filename_title = re.sub(
        r"[^a-z0-9]+",
        "_",
        title.lower(),
    ).strip("_")

    return (
        f"{query_number:02d}_"
        f"{filename_title}.csv"
    )


def split_queries(
    sql_text: str,
) -> list[tuple[int, str, str]]:
    """Split SQL using numbered comment headings.

    Expected heading format:

        -- 1. How many respondents are represented?

    A query continues until the next numbered heading or the end
    of the SQL file.
    """

    matches = list(
        QUERY_HEADER_PATTERN.finditer(
            sql_text
        )
    )

    queries: list[
        tuple[int, str, str]
    ] = []

    for index, match in enumerate(matches):
        query_number = int(
            match.group(1)
        )

        title = match.group(2).strip()

        query_start = match.end()

        if index + 1 < len(matches):
            query_end = matches[
                index + 1
            ].start()
        else:
            query_end = len(sql_text)

        query_sql = sql_text[
            query_start:query_end
        ].strip()

        # Remove section-divider comments that may appear between
        # a completed query and the next numbered query.
        section_marker = re.search(
            r"\n--\s*=+",
            query_sql,
        )

        if section_marker:
            query_sql = query_sql[
                :section_marker.start()
            ].strip()

        query_sql = query_sql.rstrip(";").strip()

        if query_sql:
            queries.append(
                (
                    query_number,
                    title,
                    query_sql,
                )
            )

    return queries


def validate_query_numbers(
    queries: list[tuple[int, str, str]],
) -> None:
    """Confirm that query numbers are unique and sequential."""

    query_numbers = [
        query_number
        for query_number, _, _ in queries
    ]

    if len(query_numbers) != len(
        set(query_numbers)
    ):
        raise ValueError(
            "Duplicate query numbers were found."
        )

    expected_numbers = list(
        range(
            1,
            len(query_numbers) + 1,
        )
    )

    if query_numbers != expected_numbers:
        raise ValueError(
            "Query numbers must be sequential. "
            f"Found {query_numbers}; "
            f"expected {expected_numbers}."
        )


def main() -> None:
    """Execute every numbered query and export its result."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}\n"
            "Run scripts/prepare_data.py first."
        )

    if not QUERY_PATH.exists():
        raise FileNotFoundError(
            f"Query file not found: {QUERY_PATH}"
        )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    sql_text = QUERY_PATH.read_text(
        encoding="utf-8"
    )

    queries = split_queries(sql_text)

    if not queries:
        raise ValueError(
            "No numbered SQL queries were found."
        )

    validate_query_numbers(queries)

    with sqlite3.connect(
        DATABASE_PATH
    ) as connection:
        for (
            query_number,
            title,
            query,
        ) in queries:
            filename = create_safe_filename(
                query_number,
                title,
            )

            try:
                result = pd.read_sql_query(
                    query,
                    connection,
                )
            except Exception as error:
                raise RuntimeError(
                    "SQL analysis failed.\n"
                    f"Query {query_number}: {title}\n"
                    f"Error: {error}"
                ) from error

            output_path = (
                OUTPUT_DIRECTORY
                / filename
            )

            result.to_csv(
                output_path,
                index=False,
                encoding="utf-8",
            )

            relative_path = output_path.relative_to(
                PROJECT_ROOT
            )

            print(
                f"Query {query_number:02d}: "
                f"{len(result):,} rows -> "
                f"{relative_path}"
            )

    print(
        "\nSuccessfully executed "
        f"{len(queries)} SQL queries."
    )


if __name__ == "__main__":
    main()