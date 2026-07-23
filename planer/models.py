"""Datenklassen für Themen und Zeitfenster."""
from dataclasses import dataclass
from datetime import datetime
import sqlite3


@dataclass
class Topic:
    id: int
    title: str
    note: str
    minutes: int
    important: bool
    created_at: datetime
    discussed_at: datetime | None = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Topic":
        """Baut ein Topic aus einer Datenbankzeile."""
        return cls(
            id=row["id"],
            title=row["title"],
            note=row["note"],
            minutes=row["minutes"],
            important=bool(row["important"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            discussed_at=(
                datetime.fromisoformat(row["discussed_at"])
                if row["discussed_at"]
                else None
            ),
        )


@dataclass
class Slot:
    id: int
    text: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Slot":
        """Baut ein Slot aus einer Datenbankzeile."""
        return cls(id=row["id"], text=row["text"])