# [English](#english) | [Deutsch](#deutsch)

---
#### English

# UbiBot Integration for HomeAssistant

This integration has only been tested with UbiBot WS1. Other models may work but are untested.

## Installation
- Add the repository (https://github.com/Pablo1732/home-assistant-ubibot) to HACS [(guide)](https://hacs.xyz/docs/faq/custom_repositories/)
- Install the UbiBot integration via HACS
- Restart Home Assistant

## Setup
1. Open Home Assistant → Settings → Devices & Services → “Add Integration” → “Ubibot”.
2. Enter:
   - channel: your channel ID from the Ubibot Cloud or App.
   - auth_method: see below.
   - api_key: depending on your selection, enter the matching key (Account Key or Read Key).
   - scan_interval: how often to refresh in seconds (recommendation: 300 seconds).
3. Done – sensors will appear automatically.

## Account Key or Read Key?
- [Account Key:](https://www.ubibot.com/platform-api/1188/generate-account-key/) Grants access to your entire **UbiBot account** → **less secure** (found in your account settings)
- [Read Key:](https://www.ubibot.com/platform-api/1195/generate-channel-read-key/) Grants **read-only access to a single device/channel** → **more secure**

## External temperature probe
- If a probe is connected and provides data, the “External Temperature” sensor appears automatically.

## Tips if something fails
- “cannot_connect”: channel_id or key (api_key/read_key) incorrect.

## Thanks to @ms32035 for the [code base.](https://github.com/ms32035/home-assistant-ubibot)

---
#### Deutsch

# UbiBot Integration für HomeAssistant

Die Integration wurde nur mit den UbiBot WS1 getestet. Andere Modelle könnten funktionieren, sind aber ungetestet.

## Installation
- Repository (https://github.com/Pablo1732/home-assistant-ubibot) zu HACS hinzufügen [(Anleitung)](https://hacs.xyz/docs/faq/custom_repositories/)
- UbiBot Integration über HACS installieren
- Home Assistant neu starten

## Einrichtung
1. Öffne Home Assistant → Einstellungen → Geräte & Dienste → „Integration hinzufügen“ → „Ubibot“.
2. Gib ein:
   - channel: deine Kanal‑ID aus der Ubibot Cloud oder App.
   - auth_method: Siehe unten.
   - api_key: Je nach Auswahl gib hier den passenden Schlüssel ein (Account‑Key oder Read‑Key).
   - scan_interval: Gibt in Sekunden an, wie oft die Daten aktualisiert werden sollen (Empfehlung: 300 Sekunden).
3. Fertig – die Sensoren erscheinen automatisch.

## Account-Key oder Read-Key?
- [Account Key:](https://www.ubibot.com/platform-api/1188/generate-account-key/) Ermöglicht Zugriff auf dein **ganzes UbiBot Konto** → **sehr unsicher** (findest du in den Account‑Einstellungen)
- [Read Key:](https://www.ubibot.com/platform-api/1195/generate-channel-read-key/) Ermöglicht nur **Zugriff auf ein bestimmtes Gerät**/Kanal → **sicherer**

## Externe Temperatursonde
- Wenn eine Sonde angeschlossen ist und Daten liefert, erscheint der Sensor „Externe Temperatur“ automatisch.

## Tipps bei Problemen
- „cannot_connect“: channel_id oder Schlüssel (api_key/read_key) falsch.

## Danke an @ms32035 für die [Codebasis.](https://github.com/ms32035/home-assistant-ubibot)
