"""Erzeugt Betreff und Text der Einladung."""
from urllib.parse import quote

from planer.models import Topic, Slot


def puffer_fuer(themen: list[Topic]) -> int:
    """Zeitreserve, damit das Gespräch nicht auf Kante genäht ist."""
    return min(15, 5 + 2 * len(themen)) if themen else 0


def gesamtdauer(themen: list[Topic]) -> int:
    return sum(t.minutes for t in themen) + puffer_fuer(themen)


def betreff(themen: list[Topic]) -> str:
    return f"Unsere Themen ({len(themen)}) – wann passt es dir?"


def mailtext(themen: list[Topic], zeiten: list[Slot]) -> str:
    if not themen:
        return "Hi,\n\naktuell steht nichts an.\n\nIch hab dich lieb <3"

    zeilen = [
        "Hi,",
        "",
        f"bei mir haben sich {len(themen)} Themen angesammelt. "
        f"Zusammen brauchen wir dafür ungefähr {gesamtdauer(themen)} Minuten:",
        "",
    ]
    for t in themen:
        marke = ", wichtig" if t.important else ""
        notiz = f" – {t.note}" if t.note else ""
        zeilen.append(f"• {t.title} ({t.minutes} Min{marke}){notiz}")

    zeilen.append("")
    if zeiten:
        zeilen.append("Bei mir würde passen:")
        zeilen += [f"– {s.text}" for s in zeiten]
        zeilen += ["", "Sag einfach, was davon dir passt, oder schlag was anderes vor."]
    else:
        zeilen.append("Sag mir, wann es dir passt.")

    zeilen += ["", "Ich hab dich lieb :)"]
    return "\n".join(zeilen)


def mailto_link(empfaenger: str, themen: list[Topic], zeiten: list[Slot]) -> str:
    """Link, der das Mailprogramm mit fertigem Entwurf öffnet."""
    return (
        f"mailto:{quote(empfaenger)}"
        f"?subject={quote(betreff(themen))}"
        f"&body={quote(mailtext(themen, zeiten))}"
    )

def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def mailhtml(themen: list[Topic], zeiten: list[Slot], antwort_an: str = "") -> str:
    """Die Einladung im Look der Seite."""
    if not themen:
        return "<p>Aktuell steht nichts an.</p>"

    karten = ""
    for t in themen:
        stern = (
            '<span style="color:#D9A0B8;font-size:13px">&#10022;</span>'
            if t.important
            else ""
        )
        notiz = (
            f'<div style="font-size:13px;color:#8C85A0;margin-top:3px">{_escape(t.note)}</div>'
            if t.note
            else ""
        )
        karten += f"""
        <tr><td style="padding-bottom:10px">
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#FFFFFF;
                 border:1px solid #E3DCEA;border-radius:16px">
            <tr>
              <td style="padding:16px 18px">
                <span style="font-size:16px;font-weight:600;color:#3A3348">{_escape(t.title)}</span> {stern}
                {notiz}
              </td>
              <td align="right" style="padding:16px 18px;font-size:13px;color:#8C85A0;white-space:nowrap">
                {t.minutes} Min
              </td>
            </tr>
          </table>
        </td></tr>"""

    balken = ""
    for t in themen:
        farbe = "#D9A0B8" if t.important else "#B9AAD6"
        balken += (
            f'<td width="{t.minutes}" style="background:{farbe};height:6px;'
            f'font-size:0;line-height:0">&nbsp;</td>'
            f'<td width="1" style="font-size:0;line-height:0">&nbsp;</td>'
        )

    pille = (
        "display:inline-block;background:#FFFFFF;border:1px solid #E3DCEA;"
        "border-radius:99px;padding:11px 20px;margin:0 6px 10px 0;font-size:14.5px;"
        "color:#3A3348;text-decoration:none"
    )

    zeitzeilen = ""
    for s in zeiten:
        link = (
            f"mailto:{quote(antwort_an)}"
            f"?subject={quote('Passt: ' + s.text)}"
            f"&body={quote(s.text + ' passt mir. Bis dann Dipsa me :)')}"
        )
        zeitzeilen += f'<a href="{link}" style="{pille}">{_escape(s.text)}</a>'

    if antwort_an:
        eigener = (
            f"mailto:{quote(antwort_an)}"
            f"?subject={quote('Mein Terminvorschlag')}"
            f"&body={quote('Wie wäre es bei dir am ')}"
        )
        zeitzeilen += (
            f'<a href="{eigener}" style="{pille};border-style:dashed;color:#7E6BA8">'
            "Anderer Vorschlag &rarr;</a>"
        )

    zeitblock = (
        '<tr><td style="padding-top:34px;font-size:11px;letter-spacing:2px;'
        'text-transform:uppercase;color:#8C85A0;padding-bottom:12px">Wann passt es dir?'
        "</td></tr><tr><td>" + zeitzeilen + "</td></tr>"
        if zeitzeilen
        else ""
    )

    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#F8F5FA">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F8F5FA">
<tr><td align="center" style="padding:36px 16px">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;
       font-family:Helvetica,Arial,sans-serif;color:#3A3348">

<tr><td style="font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#8C85A0">
    Für uns beide
  </td></tr>
  <tr><td style="padding-top:6px">
    <img src="cid:falter" width="260" alt="" style="display:block;border:0;margin:0 auto">  </td></tr>
  <tr><td style="font-family:Georgia,serif;font-size:38px;line-height:1.1;font-weight:normal;
                 padding-top:10px">
    Was wir noch<br><i style="color:#7E6BA8">besprechen wollten</i>
  </td></tr>

  <tr><td style="padding-top:28px;font-family:Georgia,serif;font-size:44px;color:#7E6BA8">
    {gesamtdauer(themen)}<span style="font-family:Helvetica,Arial,sans-serif;font-size:12px;
      letter-spacing:2px;color:#8C85A0;text-transform:uppercase">&nbsp;&nbsp;Minuten</span>
  </td></tr>
  <tr><td style="padding-top:14px">
    <table cellpadding="0" cellspacing="0" width="100%"><tr>{balken}</tr></table>
  </td></tr>

  <tr><td style="padding-top:40px;font-size:11px;letter-spacing:2px;text-transform:uppercase;
                 color:#8C85A0;padding-bottom:14px">
    {len(themen)} {'Thema' if len(themen) == 1 else 'Themen'}
  </td></tr>
  <tr><td><table width="100%" cellpadding="0" cellspacing="0">{karten}</table></td></tr>

  {zeitblock}

  <tr><td style="padding-top:24px;font-size:14.5px;line-height:1.6;color:#3A3348">
    Tipp einfach auf einen Vorschlag <3 
  </td></tr>
  <tr><td style="padding-top:28px;font-size:13px;color:#8C85A0">
    Ich freu mich auf dich Dipse me :)
  </td></tr>
<tr><td style="padding-top:30px">
   <img src="cid:elefanten" width="520" alt="" style="display:block;border:0;max-width:100%;margin:20px auto 0">  </td></tr>
</table>
</td></tr></table>
</body></html>"""