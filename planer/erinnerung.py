"""Tägliche Erinnerung: noch X Nächte bis zum großen Tag.

Aufruf einmal am Tag, z. B. per cron oder systemd-Timer:

    python -m planer.erinnerung

Optionen:
    --trocken   Nur anzeigen, nichts verschicken.
    --nochmal   Auch senden, wenn heute schon eine Mail rausging.
"""
import os
import sqlite3
import sys
from datetime import date

from planer import repo
from planer.countdown import grosser_tag, naechte, tage_bis
from planer.db import get_connection, init_schema
from planer.versand import sende_mail

# Mehrere Adressen mit Komma trennen: "sie@example.com,er@example.com"
EMPFAENGER = os.environ.get("PLANER_ERINNERUNG_AN") or os.environ.get("PLANER_MAIL", "")

MERKER = """
CREATE TABLE IF NOT EXISTS erinnerungen (
    tag   TEXT PRIMARY KEY,
    tage_offen INTEGER NOT NULL
);
"""


# ---------------------------------------------------------------- Merker

def _merker_anlegen(conn: sqlite3.Connection) -> None:
    conn.executescript(MERKER)
    conn.commit()


def schon_geschickt(conn: sqlite3.Connection, tag: date) -> bool:
    """True, wenn für diesen Tag bereits eine Erinnerung raus ist."""
    zeile = conn.execute(
        "SELECT 1 FROM erinnerungen WHERE tag = ?", (tag.isoformat(),)
    ).fetchone()
    return zeile is not None


def merken(conn: sqlite3.Connection, tag: date, offen: int) -> None:
    """Hält fest, dass die Erinnerung für diesen Tag verschickt wurde."""
    conn.execute(
        "INSERT OR REPLACE INTO erinnerungen (tag, tage_offen) VALUES (?, ?)",
        (tag.isoformat(), offen),
    )
    conn.commit()


# ---------------------------------------------------------------- Inhalt

def betreff(offen: int) -> str:
    if offen > 1:
        return f"Noch {offen} Nächte ✦"
    if offen == 1:
        return "Morgen ist es so weit ✦"
    if offen == 0:
        return "Heute ist der Tag ✦"
    return f"Vor {abs(offen)} Tagen war es so weit"


def anrede(offen: int) -> str:
    if offen > 1:
        return f"Wieder ein Tag weniger – {naechte(offen)}."
    if offen == 1:
        return "Nur noch einmal schlafen."
    if offen == 0:
        return "Heute. Endlich."
    return "Der Tag ist vorbei – die Liste bleibt."


def mailtext(offen: int, themen: list) -> str:
    """Reine Textfassung, für Mailprogramme ohne HTML."""
    zeilen = [anrede(offen), f"Der große Tag: {grosser_tag():%d.%m.%Y}", ""]
    if themen:
        minuten = sum(t.minutes for t in themen)
        zeilen.append(
            f"{len(themen)} Themen warten, zusammen {minuten} Minuten:"
        )
        for t in themen:
            stern = " ✦" if t.important else ""
            zeilen.append(f"  – {t.title} ({t.minutes} Min){stern}")
    else:
        zeilen.append("Auf der Liste steht gerade nichts.")
    return "\n".join(zeilen)


def mailhtml(offen: int, themen: list) -> str:
    """HTML in derselben Handschrift wie die Weboberfläche."""
    stern = '<span style="color:#D9A0B8"> ✦</span>'
    if themen:
        punkte = "".join(
            '<tr><td style="padding:6px 0;color:#3A3348;font-size:15px">'
            + t.title
            + (stern if t.important else "")
            + '</td><td style="padding:6px 0;color:#8C85A0;font-size:13px;'
            + 'text-align:right;white-space:nowrap">'
            + f"{t.minutes} Min</td></tr>"
            for t in themen
        )
        liste = (
            '<table role="presentation" width="100%" '
            'style="border-collapse:collapse;margin-top:8px">'
            f"{punkte}</table>"
        )
    else:
        liste = (
            '<p style="color:#8C85A0;font-size:14px;margin:8px 0 0">'
            "Auf der Liste steht gerade nichts.</p>"
        )

    zahl = offen if offen >= 0 else abs(offen)
    label = "Nächte" if offen != 1 else "Nacht"

    return f"""\
<div style="background:#F8F5FA;padding:32px 16px;font-family:Karla,Helvetica,Arial,sans-serif">
  <div style="max-width:520px;margin:0 auto;background:#FFFFFF;border:1px solid #E3DCEA;
              border-radius:20px;padding:34px 30px">
    <div style="font-size:11px;letter-spacing:.26em;text-transform:uppercase;color:#8C85A0">
      Für uns beide
    </div>
    <div style="font-family:Georgia,'Times New Roman',serif;font-weight:300;
                font-size:64px;line-height:1;color:#7E6BA8;margin:14px 0 0">
      {zahl}<span style="font-family:Karla,Arial,sans-serif;font-size:13px;color:#8C85A0;
                        letter-spacing:.16em;text-transform:uppercase;margin-left:12px">{label}</span>
    </div>
    <p style="font-size:16px;color:#3A3348;margin:16px 0 0">{anrede(offen)}</p>
    <p style="font-size:13.5px;color:#8C85A0;margin:4px 0 0">
      Der große Tag: {grosser_tag():%d.%m.%Y}
    </p>
    <hr style="border:none;border-top:1px solid #E3DCEA;margin:24px 0">
    <div style="font-size:11px;font-weight:600;letter-spacing:.22em;
                text-transform:uppercase;color:#8C85A0">Was noch wartet</div>
    {liste}
  </div>
</div>"""


# ---------------------------------------------------------------- Ablauf

def lauf(trocken: bool = False, nochmal: bool = False) -> tuple[bool, str]:
    """Schickt die Erinnerung für heute. Gibt (Erfolg, Meldung) zurück."""
    heute = date.today()
    offen = tage_bis(heute)

    conn = get_connection()
    init_schema(conn)
    _merker_anlegen(conn)

    if not nochmal and schon_geschickt(conn, heute):
        return True, "Für heute ist die Erinnerung schon raus."

    themen = repo.list_topics(conn)
    text = mailtext(offen, themen)

    if trocken:
        return True, f"[Trockenlauf]\nAn: {EMPFAENGER}\n{betreff(offen)}\n\n{text}"

    erfolg, meldung = sende_mail(
        EMPFAENGER, betreff(offen), text, mailhtml(offen, themen)
    )
    if erfolg:
        merken(conn, heute, offen)
    return erfolg, meldung


def main() -> int:
    erfolg, meldung = lauf(
        trocken="--trocken" in sys.argv,
        nochmal="--nochmal" in sys.argv,
    )
    print(meldung)
    return 0 if erfolg else 1


if __name__ == "__main__":
    raise SystemExit(main())