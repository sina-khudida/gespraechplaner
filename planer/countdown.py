"""Der große Tag und wie viele Nächte noch dazwischenliegen."""
import os
from datetime import date, timedelta

STANDARD_ABSTAND = 23  # Tage vor Silvester


def _abstand() -> int:
    """Wie viele Tage vor dem 31.12. der große Tag liegt."""
    return int(os.environ.get("PLANER_TAGE_VOR_JAHRESENDE", STANDARD_ABSTAND))


def grosser_tag(heute: date | None = None) -> date:
    """Der nächste große Tag.

    Entweder fest über PLANER_GROSSER_TAG (z. B. 2026-12-08) gesetzt,
    sonst N Tage vor Silvester. Ist der Tag dieses Jahr vorbei,
    zählt automatisch das nächste Jahr.
    """
    fest = os.environ.get("PLANER_GROSSER_TAG")
    if fest:
        return date.fromisoformat(fest)

    heute = heute or date.today()
    ziel = date(heute.year, 12, 31) - timedelta(days=_abstand())
    if ziel < heute:
        ziel = date(heute.year + 1, 12, 31) - timedelta(days=_abstand())
    return ziel


def tage_bis(heute: date | None = None) -> int:
    """Verbleibende Tage. 0 = heute ist es so weit, negativ = vorbei."""
    heute = heute or date.today()
    return (grosser_tag(heute) - heute).days


def naechte(anzahl: int) -> str:
    """'noch 1 Nacht' / 'noch 5 Nächte' – ohne Zahlensalat im Text."""
    if anzahl == 1:
        return "noch 1 Nacht"
    return f"noch {anzahl} Nächte"