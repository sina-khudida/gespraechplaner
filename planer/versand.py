"""Mailversand über Resend."""
import base64
import os
from pathlib import Path

import httpx

ABSENDER = os.environ.get("PLANER_ABSENDER", "onboarding@resend.dev")


def _bilder() -> list[dict]:
    """Elefanten und Falter als eingebettete Anhänge."""
    anhaenge = []
    ordner = Path(__file__).parent / "bilder"
    for name in ("elefanten.gif", "falter.gif"):
        pfad = ordner / name
        if pfad.exists():
            anhaenge.append(
                {
                    "filename": name,
                    "content": base64.b64encode(pfad.read_bytes()).decode(),
                    "content_id": name.replace(".gif", ""),
                }
            )
    return anhaenge


def sende_mail(
    empfaenger: str, betreff: str, text: str, html: str | None = None
) -> tuple[bool, str]:
    """Verschickt eine Mail. Gibt (Erfolg, Meldung) zurück."""
    key = os.environ.get("RESEND_KEY")
    if not key:
        return False, "Kein RESEND_KEY gesetzt."
    if not empfaenger:
        return False, "Keine Empfängeradresse gesetzt."

    inhalt = {"from": ABSENDER, "to": [empfaenger], "subject": betreff, "text": text}
    if html:
        inhalt["html"] = html

    anhaenge = _bilder()
    if anhaenge:
        inhalt["attachments"] = anhaenge

    try:
        antwort = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {key}"},
            json=inhalt,
            timeout=20,
        )
    except httpx.RequestError as fehler:
        return False, f"Keine Verbindung: {fehler}"

    if antwort.status_code == 200:
        return True, "Einladung ist unterwegs."
    return False, f"Fehler {antwort.status_code}: {antwort.text}"