#!/usr/bin/env python3
"""One-command database setup: create schema + seed data.

Usage:
    python setup_database.py          # Create schema + seed
    python setup_database.py --reset  # Drop and recreate
"""

import argparse
import sqlite3
import sys
import time
from pathlib import Path

# Ensure the project root is on sys.path so `shared` can be imported
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.database.connection import get_connection, get_db_path, get_schema_path
from shared.database.seed_data import seed_all


def main() -> None:
    parser = argparse.ArgumentParser(description="All Points Agents — Database Setup")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate the database")
    args = parser.parse_args()

    db_path = get_db_path()
    schema_path = get_schema_path()

    if args.reset and db_path.exists():
        print(f"Removing existing database: {db_path}")
        db_path.unlink()

    if db_path.exists() and not args.reset:
        print(f"Database already exists at {db_path}")
        print("Use --reset to drop and recreate.")
        # Still show counts
        conn = get_connection(db_path)
        _print_counts(conn)
        return

    print(f"Creating database at {db_path}")

    # Read and execute schema
    schema_sql = schema_path.read_text()
    conn = sqlite3.connect(str(db_path))
    conn.executescript(schema_sql)
    conn.close()

    # Seed data
    print("Seeding data...")
    t0 = time.time()
    conn = get_connection(db_path)
    counts = seed_all(conn)
    elapsed = time.time() - t0

    print(f"\nSeeding complete in {elapsed:.1f}s")
    print("-" * 40)
    for table, count in sorted(counts.items()):
        print(f"  {table:<25} {count:>6}")
    print("-" * 40)
    total = sum(counts.values())
    print(f"  {'TOTAL':<25} {total:>6}")

    # Verify foreign key integrity
    print("\nVerifying foreign key integrity...")
    violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
    if violations:
        print(f"  WARNING: {len(violations)} foreign key violation(s) found!")
        for v in violations[:10]:
            print(f"    {v}")
    else:
        print("  All foreign key constraints satisfied.")

    print(f"\nDatabase ready: {db_path}")


def _print_counts(conn: sqlite3.Connection) -> None:
    """Print row counts for all tables."""
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    print("-" * 40)
    total = 0
    for (table_name,) in tables:
        count = conn.execute(f"SELECT count(*) FROM [{table_name}]").fetchone()[0]
        print(f"  {table_name:<25} {count:>6}")
        total += count
    print("-" * 40)
    print(f"  {'TOTAL':<25} {total:>6}")


if __name__ == "__main__":
    main()
