# Ubibot Integration für Home Assistant

Diese Custom Integration bindet Ubibot Thermometer/WS1-Kanäle als Sensoren in Home Assistant ein. Die Integration wurde auf den aktuellen Home Assistant-Standard (UI-Konfiguration, asynchrone Datenabfrage, DataUpdateCoordinator) modernisiert.

## Installation

- Empfohlen: Installation über HACS (Home Assistant Community Store).
- Alternativ: Kopiere den Ordner `custom_components/ubibot` in deinen Home Assistant `config/custom_components`-Pfad und starte Home Assistant neu.

## Einrichtung (UI)

1. Öffne Home Assistant → Einstellungen → Geräte & Dienste → Integration hinzufügen.
2. Suche nach "Ubibot" und wähle die Integration aus.
3. Gib deinen Ubibot `API Key` und die `Channel`-ID ein und bestätige.
4. Optional kannst du im Options-Dialog das `scan_interval` (Aktualisierungsintervall in Sekunden) anpassen.

Nach der Einrichtung werden folgende Sensoren erzeugt (falls vom Gerät bereitgestellt):
- Temperatur (°C)
- Luftfeuchtigkeit (%)
- Beleuchtungsstärke (lx)
- WLAN RSSI (dBm)

## Optionen

- `scan_interval` (Standard: 900 Sekunden) steuert das Abfrageintervall der Cloud-API.

## Migration von YAML

Die frühere YAML-Konfiguration (`sensor: platform: ubibot ...`) ist nicht mehr erforderlich und wird nicht mehr unterstützt. Entferne alte YAML-Einträge aus `configuration.yaml` und richte die Integration über die UI neu ein.

## Fehlerbehebung

- "Kann keine Verbindung herstellen": Prüfe API Key und Channel-ID und ob der Ubibot-Clouddienst erreichbar ist.
- Leere Sensorwerte: Möglicherweise liefert der Kanal keine aktuellen Messwerte; prüfe die Ubibot-App/Weboberfläche.
- Rate Limit/429: Das Abfrageintervall ggf. erhöhen.

## Hinweise

- Die Integration ruft die Ubibot Cloud-API periodisch ab und ist daher als `cloud_polling` klassifiziert.
- Bei mehreren Kanälen lege jeweils einen separaten Integrationseintrag an.

## Lizenz und Support

Dieses Projekt ist Community-getrieben. Issues und Beiträge sind willkommen: https://github.com/ms32035/home-assistant-ubibot/issues
