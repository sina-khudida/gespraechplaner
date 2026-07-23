"""Verbindung + Schema."""
import os
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS topics (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    note        TEXT    NOT NULL DEFAULT '',
    minutes     INTEGER NOT NULL DEFAULT 15,
    important   INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL,
    discussed_at TEXT
);

CREATE TABLE IF NOT EXISTS slots (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL
);
"""


def db_path() -> Path:
    """Pfad zur Datenbankdatei. Legt den Ordner an, falls nötig."""
    raw = os.environ.get("PLANER_DB")
    if raw:
        p = Path(raw)
    else:
        p = Path.home() / ".local" / "share" / "gespraechplaner" / "planer.db"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def get_connection() -> sqlite3.Connection:
    """Verbindung mit Zugriff per Spaltenname."""
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Legt die Tabellen an, falls sie fehlen. Idempotent."""
    conn.executescript(SCHEMA)
    conn.commit()