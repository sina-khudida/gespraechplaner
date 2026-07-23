"""Weboberfläche."""
import os
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from planer.db import get_connection, init_schema
from planer.einladung import (
    betreff,
    gesamtdauer,
    mailhtml,
    mailtext,
    mailto_link,
    puffer_fuer,
)
from planer.versand import sende_mail
from planer import repo

EMPFAENGER = os.environ.get("PLANER_MAIL", "")
ANTWORT_AN = os.environ.get("PLANER_ANTWORT", EMPFAENGER)
app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def conn():
    c = get_connection()
    init_schema(c)
    return c


def zurueck() -> RedirectResponse:
    """Nach jedem Formular zurück zur Liste – verhindert doppeltes Absenden."""
    return RedirectResponse("/", status_code=303)


@app.get("/")
def start(request: Request, meldung: str = ""):
    c = conn()
    themen = repo.list_topics(c)
    zeiten = repo.list_slots(c)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "themen": themen,
            "zeiten": zeiten,
            "gesamt": gesamtdauer(themen),
            "puffer": puffer_fuer(themen),
            "mailto": mailto_link(EMPFAENGER, themen, zeiten),
            "meldung": meldung,
        },
    )


@app.post("/themen")
def thema_anlegen(
    title: str = Form(...),
    minutes: int = Form(15),
    important: bool = Form(False),
):
    repo.add_topic(conn(), title=title, minutes=minutes, important=important)
    return zurueck()


@app.post("/themen/{topic_id}/erledigt")
def thema_erledigt(topic_id: int):
    repo.mark_discussed(conn(), topic_id)
    return zurueck()


@app.post("/themen/{topic_id}/loeschen")
def thema_loeschen(topic_id: int):
    repo.delete_topic(conn(), topic_id)
    return zurueck()


@app.post("/zeiten")
def zeit_anlegen(text: str = Form(...)):
    repo.add_slot(conn(), text)
    return zurueck()


@app.post("/zeiten/{slot_id}/loeschen")
def zeit_loeschen(slot_id: int):
    repo.delete_slot(conn(), slot_id)
    return zurueck()


@app.post("/senden")
def einladung_senden():
    c = conn()
    themen = repo.list_topics(c)
    zeiten = repo.list_slots(c)
    erfolg, meldung = sende_mail(
        EMPFAENGER,
        betreff(themen),
        mailtext(themen, zeiten),
        mailhtml(themen, zeiten, ANTWORT_AN),
    )
    return RedirectResponse(f"/?meldung={quote(meldung)}", status_code=303)