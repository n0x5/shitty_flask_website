#!/usr/bin/env python3

"""
Download the public IMDb non-commercial datasets and import them into SQLite.

Creates:

    imdb.db

Tables:

    title_akas
    title_basics
    title_crew
    title_episode
    title_principals
    title_ratings
    name_basics

And a convenience view:

    imdb_all

The IMDb TSV files are downloaded from:
    https://datasets.imdbws.com/

Requirements:
    Python 3.10+

No third-party Python packages are required.
"""

from __future__ import annotations

import csv
import gzip
import os
import shutil
import sqlite3
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen


BASE_URL = "https://datasets.imdbws.com"

DATA_DIR = Path("imdb_data")
DB_PATH = Path("imdb.db")

BATCH_SIZE = 10_000

DATASETS = {
    "title_akas": {
        "filename": "title.akas.tsv.gz",
        "columns": [
            ("titleId", "TEXT"),
            ("ordering", "INTEGER"),
            ("title", "TEXT"),
            ("region", "TEXT"),
            ("language", "TEXT"),
            ("types", "TEXT"),
            ("attributes", "TEXT"),
            ("isOriginalTitle", "INTEGER"),
        ],
    },

    "title_basics": {
        "filename": "title.basics.tsv.gz",
        "columns": [
            ("tconst", "TEXT"),
            ("titleType", "TEXT"),
            ("primaryTitle", "TEXT"),
            ("originalTitle", "TEXT"),
            ("isAdult", "INTEGER"),
            ("startYear", "INTEGER"),
            ("endYear", "INTEGER"),
            ("runtimeMinutes", "INTEGER"),
            ("genres", "TEXT"),
        ],
    },

    "title_crew": {
        "filename": "title.crew.tsv.gz",
        "columns": [
            ("tconst", "TEXT"),
            ("directors", "TEXT"),
            ("writers", "TEXT"),
        ],
    },

    "title_episode": {
        "filename": "title.episode.tsv.gz",
        "columns": [
            ("tconst", "TEXT"),
            ("parentTconst", "TEXT"),
            ("seasonNumber", "INTEGER"),
            ("episodeNumber", "INTEGER"),
        ],
    },

    "title_principals": {
        "filename": "title.principals.tsv.gz",
        "columns": [
            ("tconst", "TEXT"),
            ("ordering", "INTEGER"),
            ("nconst", "TEXT"),
            ("category", "TEXT"),
            ("job", "TEXT"),
            ("characters", "TEXT"),
        ],
    },

    "title_ratings": {
        "filename": "title.ratings.tsv.gz",
        "columns": [
            ("tconst", "TEXT"),
            ("averageRating", "REAL"),
            ("numVotes", "INTEGER"),
        ],
    },

    "name_basics": {
        "filename": "name.basics.tsv.gz",
        "columns": [
            ("nconst", "TEXT"),
            ("primaryName", "TEXT"),
            ("birthYear", "INTEGER"),
            ("deathYear", "INTEGER"),
            ("primaryProfession", "TEXT"),
            ("knownForTitles", "TEXT"),
        ],
    },
}


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def download_file(url: str, destination: Path) -> None:
    """Download a URL to destination with a progress indicator."""

    print(f"\nDownloading:")
    print(f"  {url}")
    print(f"  -> {destination}")

    temp_file = destination.with_suffix(destination.suffix + ".part")

    request = Request(
        url,
        headers={
            "User-Agent": "IMDb SQLite importer/1.0"
        },
    )

    with urlopen(request) as response, open(temp_file, "wb") as output:
        total = response.headers.get("Content-Length")
        total_bytes = int(total) if total else None

        downloaded = 0
        last_report = time.monotonic()

        while True:
            chunk = response.read(1024 * 1024)

            if not chunk:
                break

            output.write(chunk)
            downloaded += len(chunk)

            now = time.monotonic()

            if now - last_report >= 1:
                if total_bytes:
                    percent = downloaded / total_bytes * 100
                    print(
                        f"\r  {downloaded / 1024**3:.2f} GB "
                        f"/ {total_bytes / 1024**3:.2f} GB "
                        f"({percent:.1f}%)",
                        end="",
                        flush=True,
                    )
                else:
                    print(
                        f"\r  {downloaded / 1024**3:.2f} GB",
                        end="",
                        flush=True,
                    )

                last_report = now

    print()

    temp_file.replace(destination)


def download_datasets() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for dataset in DATASETS.values():
        filename = dataset["filename"]
        destination = DATA_DIR / filename

        if destination.exists():
            print(f"\nAlready downloaded: {filename}")
            continue

        url = f"{BASE_URL}/{filename}"
        download_file(url, destination)


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------

def sqlite_value(value: str, sqlite_type: str):
    """
    Convert IMDb's \\N representation and basic numeric fields into
    appropriate SQLite values.
    """

    if value == r"\N":
        return None

    if sqlite_type == "INTEGER":
        try:
            return int(value)
        except ValueError:
            return None

    if sqlite_type == "REAL":
        try:
            return float(value)
        except ValueError:
            return None

    return value


def create_table(
    connection: sqlite3.Connection,
    table_name: str,
    columns: list[tuple[str, str]],
) -> None:

    column_sql = ",\n        ".join(
        f'"{name}" {sqlite_type}'
        for name, sqlite_type in columns
    )

    sql = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            {column_sql}
        )
    """

    connection.execute(sql)


def create_indexes(connection: sqlite3.Connection) -> None:
    """Create indexes useful for joining the IMDb tables."""

    indexes = [
        (
            "idx_title_basics_tconst",
            "title_basics",
            "tconst",
        ),
        (
            "idx_title_akas_titleId",
            "title_akas",
            "titleId",
        ),
        (
            "idx_title_crew_tconst",
            "title_crew",
            "tconst",
        ),
        (
            "idx_title_episode_tconst",
            "title_episode",
            "tconst",
        ),
        (
            "idx_title_episode_parentTconst",
            "title_episode",
            "parentTconst",
        ),
        (
            "idx_title_principals_tconst",
            "title_principals",
            "tconst",
        ),
        (
            "idx_title_principals_nconst",
            "title_principals",
            "nconst",
        ),
        (
            "idx_title_ratings_tconst",
            "title_ratings",
            "tconst",
        ),
        (
            "idx_name_basics_nconst",
            "name_basics",
            "nconst",
        ),
    ]

    print("\nCreating indexes...")

    for index_name, table_name, column_name in indexes:
        connection.execute(
            f"""
            CREATE INDEX IF NOT EXISTS "{index_name}"
            ON "{table_name}" ("{column_name}")
            """
        )

    connection.commit()


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def import_dataset(
    connection: sqlite3.Connection,
    table_name: str,
    dataset: dict,
) -> None:

    filepath = DATA_DIR / dataset["filename"]
    columns = dataset["columns"]

    print(f"\nImporting {dataset['filename']}")
    print(f"  Table: {table_name}")
    print(f"  File:  {filepath}")

    create_table(connection, table_name, columns)

    column_names = [name for name, _ in columns]

    quoted_columns = ", ".join(
        f'"{name}"' for name in column_names
    )

    placeholders = ", ".join("?" for _ in columns)

    insert_sql = f"""
        INSERT INTO "{table_name}"
        ({quoted_columns})
        VALUES ({placeholders})
    """

    row_count = 0
    start_time = time.monotonic()

    with gzip.open(filepath, "rt", encoding="utf-8", newline="") as file:

        reader = csv.reader(
            file,
            delimiter="\t",
            quoting=csv.QUOTE_NONE,
        )

        # Skip header
        header = next(reader)

        if header != column_names:
            raise RuntimeError(
                f"Unexpected header in {filepath}.\n"
                f"Expected: {column_names}\n"
                f"Received: {header}"
            )

        batch = []

        for row in reader:

            if len(row) != len(columns):
                print(
                    f"\nWARNING: skipping malformed row "
                    f"in {dataset['filename']} "
                    f"(expected {len(columns)} columns, "
                    f"got {len(row)})"
                )
                continue

            converted = [
                sqlite_value(value, sqlite_type)
                for value, (_, sqlite_type) in zip(row, columns)
            ]

            batch.append(converted)

            if len(batch) >= BATCH_SIZE:
                connection.executemany(insert_sql, batch)
                row_count += len(batch)
                batch.clear()

                elapsed = time.monotonic() - start_time

                print(
                    f"\r  {row_count:,} rows "
                    f"({row_count / elapsed:,.0f} rows/sec)",
                    end="",
                    flush=True,
                )

        if batch:
            connection.executemany(insert_sql, batch)
            row_count += len(batch)

    connection.commit()

    elapsed = time.monotonic() - start_time

    print(
        f"\n  Finished: {row_count:,} rows "
        f"in {elapsed:.1f}s "
        f"({row_count / elapsed:,.0f} rows/sec)"
    )


# ---------------------------------------------------------------------------
# Combined view
# ---------------------------------------------------------------------------

def create_combined_view(connection: sqlite3.Connection) -> None:
    """
    Create a title-centric view.

    Important:
    title_principals and title_akas contain multiple rows per title.
    A normal JOIN would therefore multiply rows dramatically.

    Instead, this view returns one row per title and aggregates:
        - alternative titles
        - principals
        - directors
        - writers
        - ratings

    SQLite's JSON functions are used for the aggregated relationships.
    """

    print("\nCreating combined view...")

    connection.execute("DROP VIEW IF EXISTS imdb_all")

    connection.execute(
        """
        CREATE VIEW imdb_all AS

        SELECT
            b.tconst,
            b.titleType,
            b.primaryTitle,
            b.originalTitle,
            b.isAdult,
            b.startYear,
            b.endYear,
            b.runtimeMinutes,
            b.genres,

            r.averageRating,
            r.numVotes,

            c.directors,
            c.writers,

            e.parentTconst,
            e.seasonNumber,
            e.episodeNumber,

            (
                SELECT json_group_array(
                    json_object(
                        'ordering', a.ordering,
                        'title', a.title,
                        'region', a.region,
                        'language', a.language,
                        'types', a.types,
                        'attributes', a.attributes,
                        'isOriginalTitle', a.isOriginalTitle
                    )
                )
                FROM title_akas AS a
                WHERE a.titleId = b.tconst
            ) AS alternativeTitles,

            (
                SELECT json_group_array(
                    json_object(
                        'ordering', p.ordering,
                        'nconst', p.nconst,
                        'category', p.category,
                        'job', p.job,
                        'characters', p.characters
                    )
                )
                FROM title_principals AS p
                WHERE p.tconst = b.tconst
            ) AS principals

        FROM title_basics AS b

        LEFT JOIN title_ratings AS r
            ON r.tconst = b.tconst

        LEFT JOIN title_crew AS c
            ON c.tconst = b.tconst

        LEFT JOIN title_episode AS e
            ON e.tconst = b.tconst
        """
    )

    connection.commit()


def create_people_view(connection: sqlite3.Connection) -> None:
    """
    Convenience view joining people with the titles they are principals on.
    """

    connection.execute("DROP VIEW IF EXISTS imdb_people")

    connection.execute(
        """
        CREATE VIEW imdb_people AS

        SELECT
            n.nconst,
            n.primaryName,
            n.birthYear,
            n.deathYear,
            n.primaryProfession,
            n.knownForTitles,

            p.tconst,
            p.ordering,
            p.category,
            p.job,
            p.characters,

            b.primaryTitle,
            b.originalTitle,
            b.titleType,
            b.startYear

        FROM name_basics AS n

        LEFT JOIN title_principals AS p
            ON p.nconst = n.nconst

        LEFT JOIN title_basics AS b
            ON b.tconst = p.tconst
        """
    )

    connection.commit()


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

def configure_database(connection: sqlite3.Connection) -> None:

    # Good defaults for a large bulk import.
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA synchronous = NORMAL")
    connection.execute("PRAGMA temp_store = MEMORY")
    connection.execute("PRAGMA cache_size = -200000")

    # Foreign keys aren't currently declared because IMDb's source data
    # can contain temporary inconsistencies between datasets.
    connection.execute("PRAGMA foreign_keys = OFF")


def build_database() -> None:

    print(f"\nOpening database: {DB_PATH}")

    connection = sqlite3.connect(DB_PATH)

    try:
        configure_database(connection)

        for table_name, dataset in DATASETS.items():
            import_dataset(
                connection,
                table_name,
                dataset,
            )

        create_indexes(connection)

        create_combined_view(connection)

        create_people_view(connection)

        connection.execute("PRAGMA optimize")

        connection.commit()

    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_database() -> None:

    print("\nVerifying database...")

    connection = sqlite3.connect(DB_PATH)

    try:
        for table_name in DATASETS:

            count = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()[0]

            print(
                f"  {table_name:20s} {count:>12,} rows"
            )

        print("\nTesting imdb_all view...")

        result = connection.execute(
            """
            SELECT
                tconst,
                primaryTitle,
                startYear,
                averageRating,
                numVotes
            FROM imdb_all
            WHERE titleType = 'movie'
              AND averageRating IS NOT NULL
            ORDER BY averageRating DESC, numVotes DESC
            LIMIT 10
            """
        ).fetchall()

        print("\nTop 10 rated movies by the imported data:")
        print("-" * 80)

        for row in result:
            print(row)

        print("\nTesting people view...")

        count = connection.execute(
            "SELECT COUNT(*) FROM imdb_people"
        ).fetchone()[0]

        print(
            f"  imdb_people contains {count:,} rows"
        )

    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():

    print("=" * 80)
    print("IMDb -> SQLite importer")
    print("=" * 80)

    print(
        "\nIMDb's public datasets are refreshed daily."
    )

    print(
        "\nThis can require a substantial amount of disk space "
        "and may take a while to import."
    )

    start = time.monotonic()

    download_datasets()

    build_database()

    verify_database()

    elapsed = time.monotonic() - start

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)

    print(f"\nDatabase: {DB_PATH.resolve()}")
    print(f"Total time: {elapsed / 60:.1f} minutes")

    print(
        "\nUseful commands:"
    )

    print(
        "  sqlite3 imdb.db"
    )

    print(
        "  SELECT * FROM imdb_all LIMIT 10;"
    )

    print(
        "  SELECT * FROM imdb_people LIMIT 10;"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(130)
    except Exception as exc:
        print(
            f"\nERROR: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)