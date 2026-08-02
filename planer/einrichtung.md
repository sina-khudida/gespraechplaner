# Tägliche Erinnerung einrichten

Beide Dateien nach `planer/` legen:

- `planer/countdown.py`
- `planer/erinnerung.py`

## 1. Umgebungsvariablen

```bash
export GMAIL_ADRESSE="deine@gmail.com"
export GMAIL_APP_PASSWORT="xxxx xxxx xxxx xxxx"
export PLANER_ERINNERUNG_AN="du@example.com,er@example.com"
export PLANER_DB="$HOME/.local/share/gespraechplaner/planer.db"

# Optional – Standard sind 23 Tage vor Silvester (8. Dezember)
export PLANER_TAGE_VOR_JAHRESENDE=23
# Oder ein festes Datum, dann zählt nur dieses:
# export PLANER_GROSSER_TAG=2026-12-08
```

## 2. Erst trocken testen

```bash
python -m planer.erinnerung --trocken
```

Zeigt Betreff und Text an, verschickt nichts.

## 3. Täglich laufen lassen

### cron (einfach, Rechner muss um 8 Uhr an sein)

`crontab -e`:

```
0 8 * * * cd /pfad/zum/projekt && /pfad/zum/venv/bin/python -m planer.erinnerung >> ~/.local/share/gespraechplaner/erinnerung.log 2>&1
```

cron kennt deine Umgebungsvariablen nicht. Entweder oben im crontab setzen
oder – sauberer – in eine Datei schreiben und im Befehl laden:

```
0 8 * * * cd /pfad/zum/projekt && set -a && . ./.env && set +a && /pfad/zum/venv/bin/python -m planer.erinnerung
```

### systemd-Timer (holt verpasste Läufe nach)

`~/.config/systemd/user/erinnerung.service`:

```ini
[Unit]
Description=Tägliche Erinnerung an den großen Tag

[Service]
Type=oneshot
WorkingDirectory=/pfad/zum/projekt
EnvironmentFile=/pfad/zum/projekt/.env
ExecStart=/pfad/zum/venv/bin/python -m planer.erinnerung
```

`~/.config/systemd/user/erinnerung.timer`:

```ini
[Unit]
Description=Erinnerung jeden Morgen um 8

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Aktivieren:

```bash
systemctl --user daemon-reload
systemctl --user enable --now erinnerung.timer
systemctl --user list-timers erinnerung.timer
loginctl enable-linger $USER   # läuft auch ohne Anmeldung
```

`Persistent=true` sorgt dafür, dass ein verpasster Tag beim nächsten
Hochfahren nachgeholt wird.

## Doppelte Mails

Die Tabelle `erinnerungen` merkt sich pro Datum, ob schon etwas rausging.
Ein zweiter Aufruf am selben Tag tut nichts. Zum Erzwingen:

```bash
python -m planer.erinnerung --nochmal
```