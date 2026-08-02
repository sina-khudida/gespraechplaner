"""Mailversand über Gmail (SMTP)."""
import os
import smtplib
from email.message import EmailMessage


def sende_mail(
    empfaenger: str, betreff: str, text: str, html: str | None = None
) -> tuple[bool, str]:
    """Verschickt eine Mail über Gmail. Gibt (Erfolg, Meldung) zurück."""
    absender = os.environ.get("GMAIL_ADRESSE")
    passwort = os.environ.get("GMAIL_APP_PASSWORT")

    if not absender or not passwort:
        return False, "GMAIL_ADRESSE oder GMAIL_APP_PASSWORT fehlt."
    if not empfaenger:
        return False, "Keine Empfängeradresse gesetzt."

    nachricht = EmailMessage()
    nachricht["From"] = absender
    nachricht["To"] = empfaenger
    nachricht["Subject"] = betreff
    nachricht.set_content(text)
    if html:
        nachricht.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(absender, passwort)
            server.send_message(nachricht)
    except smtplib.SMTPAuthenticationError:
        return False, "Anmeldung fehlgeschlagen – App-Passwort prüfen."
    except Exception as fehler:
        return False, f"Fehler beim Senden: {fehler}"

    return True, "Einladung ist unterwegs."