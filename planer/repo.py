"""Datenbankzugriffe für Themen und Zeitfenster."""
import sqlite3
from datetime import datetime

from planer.models import Topic, Slot


def add_topic(
    conn: sqlite3.Connection,
    title: str,
    note: str = "",
    minutes: int = 15,
    important: bool = False,
) -> int:
    """Legt ein Thema an und gibt die neue ID zurück."""
    cur = conn.execute(
        """
        INSERT INTO topics (title, note, minutes, important, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, note, minutes, int(important), datetime.now().isoformat()),
    )
    conn.commit()
    return cur.lastrowid


def list_topics(
    conn: sqlite3.Connection,
    include_discussed: bool = False,
) -> list[Topic]:
    """Themen, wichtige zuerst, sonst chronologisch."""
    sql = "SELECT * FROM topics"
    if not include_discussed:
        sql += " WHERE discussed_at IS NULL"
    sql += " ORDER BY important DESC, created_at ASC"
    return [Topic.from_row(row) for row in conn.execute(sql)]


def mark_discussed(
    conn: sqlite3.Connection,
    topic_id: int,
    when: datetime | None = None,
) -> bool:
    """Markiert ein Thema als besprochen. False, wenn die ID nicht existiert."""
    cur = conn.execute(
        "UPDATE topics SET discussed_at = ? WHERE id = ?",
        ((when or datetime.now()).isoformat(), topic_id),
    )
    conn.commit()
    return cur.rowcount > 0


def delete_topic(conn: sqlite3.Connection, topic_id: int) -> bool:
    """Löscht ein Thema. False, wenn die ID nicht existiert."""
    cur = conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
    conn.commit()
    return cur.rowcount > 0


def add_slot(conn: sqlite3.Connection, text: str) -> int:
    """Legt ein Zeitfenster an und gibt die neue ID zurück."""
    cur = conn.execute("INSERT INTO slots (text) VALUES (?)", (text,))
    conn.commit()
    return cur.lastrowid


def list_slots(conn: sqlite3.Connection) -> list[Slot]:
    """Zeitfenster in Eingabereihenfolge."""
    return [
        Slot.from_row(row)
        for row in conn.execute("SELECT * FROM slots ORDER BY id ASC")
    ]


def delete_slot(conn: sqlite3.Connection, slot_id: int) -> bool:
    """Löscht ein Zeitfenster. False, wenn die ID nicht existiert."""
    cur = conn.execute("DELETE FROM slots WHERE id = ?", (slot_id,))
    conn.commit()
    return cur.rowcount > 0