"""Thread-safe SQLite connection helper with WAL mode and foreign key enforcement."""

import sqlite3
import threading
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent / "allpoints.db"
_lock = threading.Lock()
_local = threading.local()


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Return a thread-local SQLite connection.

    - Enables WAL journal mode for concurrent reads.
    - Enforces foreign key constraints.
    - Returns rows as sqlite3.Row (dict-like access).
    """
    path = str(db_path or _DB_PATH)

    conn = getattr(_local, "conn", None)
    if conn is not None:
        try:
            conn.execute("SELECT 1")
            return conn
        except sqlite3.ProgrammingError:
            _local.conn = None

    with _lock:
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        _local.conn = conn
        return conn


def get_schema_path() -> Path:
    """Return the path to schema.sql."""
    return Path(__file__).resolve().parent / "schema.sql"


def get_db_path() -> Path:
    """Return the default database file path."""
    return _DB_PATH


def close_connection() -> None:
    """Close the thread-local connection if open."""
    conn = getattr(_local, "conn", None)
    if conn is not None:
        conn.close()
        _local.conn = None
