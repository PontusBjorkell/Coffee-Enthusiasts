"""Run the portfolio SQL analysis and export every result to CSV."""

from pathlib import Path
import re
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "coffee_enthusiasts.db"
QUERY_PATH = PROJECT_ROOT / "sql" / "analysis_queries.sql"
OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis_results"


def split_queries(sql_text: str) -> list[tuple[str, str]]:
    """Split the SQL file into numbered queries.

    Each query must begin with a comment such as:
        -- 1. How many respondents are represented?
    """

    pattern = re.compile(
        r"--\s*(\d+)\.\s*(.+?)\n(.*?;)",
        flags=re.DOTALL,
    )

    queries = []

    for match in pattern.finditer(sql_text):
        query_number = int(match.group(1))
        title = match.group(2).strip()
        sql = match.group(3).strip()

        filename_title = re.sub(r"[^a-z0-9]+", "_", title.lower())
        filename_title = filename_title.strip("_")

        filename = f"{query_number:02d}_{filename_title}.csv"
        queries.append((filename, sql))

    return queries


def main() -> None:
    """Execute all numbered queries and export their results."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}\n"
            "Run scripts/prepare_data.py first."
        )

    if not QUERY_PATH.exists():
        raise FileNotFoundError(f"Query file not found: {QUERY_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sql_text = QUERY_PATH.read_text(encoding="utf-8")
    queries = split_queries(sql_text)

    if not queries:
        raise ValueError(
            "No numbered SQL queries were found in analysis_queries.sql."
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        for filename, query in queries:
            try:
                result = pd.read_sql_query(query, connection)
            except Exception as error:
                raise RuntimeError(
                    f"Query failed while creating {filename}:\n{error}"
                ) from error

            output_path = OUTPUT_DIR / filename
            result.to_csv(output_path, index=False)

            print(
                f"Exported {len(result):,} rows "
                f"to {output_path.relative_to(PROJECT_ROOT)}"
            )

    print(f"\nSuccessfully executed {len(queries)} queries.")


if __name__ == "__main__":
    main()