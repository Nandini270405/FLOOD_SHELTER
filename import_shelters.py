import csv
import sqlite3
import sys
from pathlib import Path


REQUIRED_COLUMNS = [
    "name",
    "capacity",
    "available_beds",
    "distance",
    "accessibility",
    "elevation_level",
    "proximity_to_water",
    "medical_facility",
    "latitude",
    "longitude",
]


def _read_rows(csv_path: Path) -> list[tuple]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV file is missing a header row.")

        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV file is missing required columns: {', '.join(missing)}")

        rows = []
        for line_number, row in enumerate(reader, start=2):
            # FIX: check name BEFORE appending so bad rows never enter the list
            name = row["name"].strip()
            if not name:
                raise ValueError(f"Missing shelter name on CSV line {line_number}.")
            try:
                rows.append(
                    (
                        name,
                        int(row["capacity"]),
                        int(row["available_beds"]),
                        float(row["distance"]),
                        row["accessibility"].strip().lower(),
                        row["elevation_level"].strip().lower(),
                        row["proximity_to_water"].strip().lower(),
                        row["medical_facility"].strip().lower(),
                        float(row["latitude"]),
                        float(row["longitude"]),
                    )
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid data on CSV line {line_number}: {exc}") from exc

        if not rows:
            raise ValueError("CSV file contains no shelter rows.")
        return rows


def import_csv(csv_path: Path, db_path: Path) -> None:
    rows = _read_rows(csv_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS app_metadata")
    cursor.execute("DROP TABLE IF EXISTS shelters")

    cursor.execute(
        """
        CREATE TABLE shelters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            capacity INTEGER,
            available_beds INTEGER,
            distance REAL,
            accessibility TEXT,
            elevation_level TEXT,
            proximity_to_water TEXT,
            medical_facility TEXT,
            latitude REAL,
            longitude REAL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE app_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )

    cursor.executemany(
        """
        INSERT INTO shelters
        (name, capacity, available_beds, distance, accessibility, elevation_level, proximity_to_water, medical_facility, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    cursor.executemany(
        "INSERT INTO app_metadata (key, value) VALUES (?, ?)",
        [
            ("source_type", "custom"),
            ("dataset_name", csv_path.stem),
        ],
    )

    conn.commit()
    conn.close()


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("Usage: python import_shelters.py <csv_path> [db_path]")
        return 1

    csv_path = Path(sys.argv[1]).resolve()
    db_path = Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else Path("shelter.db").resolve()

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        return 1

    try:
        import_csv(csv_path, db_path)
    except ValueError as exc:
        print(f"Import failed: {exc}")
        return 1

    print(f"Imported shelters from {csv_path} into {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
