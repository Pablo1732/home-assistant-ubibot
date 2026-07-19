# Changelog

All notable changes to this integration are documented here.
Alle wichtigen Änderungen an dieser Integration werden hier dokumentiert.

---

## [1.0.0] – 2026-07-19

First polished release. / Erste ausgereifte Version.

### 🇬🇧 English

**New**
- 🔋 **Battery sensor** – shows the WS1 supply voltage.
- 🔌 **Offline detection** – when UbiBot reports the device as offline, its
  sensors now correctly become *unavailable* instead of getting stuck on the
  last measured value.
- 🩺 **Download diagnostics** – a support file you can download from the device
  page. Keys and personal data (location, MAC, IP, serial…) are automatically
  removed, so it is safe to share.
- 🌍 **German and English** translations for the whole setup.

**Improved**
- ✨ **Much simpler setup** – only two fields now: *Channel ID* and *API key*.
  The key type (Account or Read key) is detected automatically, no more
  choosing from a dropdown.
- 🏷️ **Cleaner names** – the device is named after your channel (e.g. “Oben”)
  and sensors are simply called “Temperature”, “Humidity”, etc.
- 🛠️ **Fix invalid key without re-adding** – if a key stops working, Home
  Assistant shows a *Repair* card where you just enter a new key.
- ⏱️ **Changing the update interval now works** (it silently didn’t before).
- 💪 **More reliable** – no internet, timeouts, wrong keys or unexpected
  responses no longer crash the integration; sensors simply go unavailable and
  recover on their own.
- 📉 WiFi signal and battery are now grouped under *Diagnostic* so they don’t
  clutter the main view.

**Requirements**
- Home Assistant **2024.8.0 or newer**.

### 🇩🇪 Deutsch

**Neu**
- 🔋 **Batterie-Sensor** – zeigt die Versorgungsspannung des WS1.
- 🔌 **Offline-Erkennung** – wenn UbiBot das Gerät als offline meldet, werden
  die Sensoren jetzt korrekt *nicht verfügbar*, statt am letzten Messwert
  hängenzubleiben.
- 🩺 **Diagnose herunterladen** – eine Support-Datei, die du auf der Geräteseite
  herunterladen kannst. Schlüssel und persönliche Daten (Standort, MAC, IP,
  Seriennummer…) werden automatisch entfernt – sie kann also bedenkenlos
  geteilt werden.
- 🌍 **Deutsch und Englisch** für die komplette Einrichtung.

**Verbessert**
- ✨ **Viel einfachere Einrichtung** – nur noch zwei Felder: *Channel-ID* und
  *API-Schlüssel*. Der Schlüsseltyp (Account- oder Read-Key) wird automatisch
  erkannt, kein Auswählen mehr nötig.
- 🏷️ **Klarere Namen** – das Gerät heißt wie dein Kanal (z. B. „Oben“) und die
  Sensoren einfach „Temperatur“, „Luftfeuchtigkeit“ usw.
- 🛠️ **Ungültigen Schlüssel ohne Neu-Einrichten beheben** – wenn ein Schlüssel
  nicht mehr funktioniert, zeigt Home Assistant eine *Reparieren*-Kachel, in der
  du einfach einen neuen Schlüssel einträgst.
- ⏱️ **Ändern des Abrufintervalls funktioniert jetzt** (vorher hatte es still
  nicht funktioniert).
- 💪 **Zuverlässiger** – kein Internet, Zeitüberschreitungen, falsche Schlüssel
  oder unerwartete Antworten bringen die Integration nicht mehr zum Absturz; die
  Sensoren werden einfach nicht verfügbar und erholen sich von selbst.
- 📉 WLAN-Signal und Batterie sind jetzt unter *Diagnose* gruppiert, damit sie
  die Hauptansicht nicht zumüllen.

**Voraussetzungen**
- Home Assistant **2024.8.0 oder neuer**.

---

## [0.4.5] and earlier

Initial versions based on the code base by
[@ms32035](https://github.com/ms32035/home-assistant-ubibot).
Frühere Versionen basierend auf der Codebasis von
[@ms32035](https://github.com/ms32035/home-assistant-ubibot).

[1.0.0]: https://github.com/Pablo1732/home-assistant-ubibot/releases/tag/v1.0.0
