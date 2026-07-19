# Changelog

All notable changes to this integration are documented here.
Alle wichtigen Änderungen an dieser Integration werden hier dokumentiert.

---

## [1.0.0] – 2026-07-19

First polished release. / Erste ausgereifte Version.

### 🇬🇧 English

**New**
- 🧭 **Pick your devices – no Channel ID needed.** Enter your Account Key and all
  your UbiBot devices are listed; just tick the ones you want. Add several at
  once, and add more later the same way (already-added devices can’t be added
  twice).
- 🔒 **Your Account Key is never stored.** It’s used only to look up your devices
  and fetch a read-only key for each one, then it’s discarded. Home Assistant
  only ever keeps the harmless read keys.
- 🔋 **Battery sensor** – shows the WS1 supply voltage.
- 🔌 **Offline detection** – when UbiBot reports the device as offline, its
  sensors become *unavailable* instead of getting stuck on the last value.
- 🩺 **Download diagnostics** – a support file you can download from the device
  page. Keys and personal data (location, MAC, IP, serial…) are automatically
  removed, so it is safe to share.
- 🌍 **German and English** translations for the whole setup.

**Improved**
- 🏷️ **Cleaner names** – each device is named after your channel (e.g. “Oben”)
  and sensors are simply called “Temperature”, “Humidity”, etc.
- 🛠️ **Fix an invalid key without re-adding** – if a key stops working, Home
  Assistant shows a *Repair* card where you enter a new key.
- ⏱️ **Changing the update interval now works** (it silently didn’t before).
- 💪 **More reliable** – no internet, timeouts, wrong keys or unexpected
  responses no longer crash the integration; sensors go unavailable and recover
  on their own.
- 📉 WiFi signal and battery are grouped under *Diagnostic* so they don’t clutter
  the main view.

**Requirements**
- Home Assistant **2024.8.0 or newer**. (Upgrading from 0.4.5 is automatic.)

### 🇩🇪 Deutsch

**Neu**
- 🧭 **Geräte anhaken – keine Channel-ID nötig.** Du gibst deinen Account-Key ein
  und alle deine UbiBot-Geräte werden aufgelistet; hak einfach die gewünschten
  an. Mehrere auf einmal, und später genauso weitere hinzufügen (bereits
  hinzugefügte Geräte lassen sich nicht doppelt hinzufügen).
- 🔒 **Dein Account-Key wird nie gespeichert.** Er wird nur benutzt, um deine
  Geräte abzufragen und pro Gerät einen Nur-Lese-Schlüssel zu holen, danach wird
  er verworfen. In Home Assistant liegen ausschließlich die harmlosen Read-Keys.
- 🔋 **Batterie-Sensor** – zeigt die Versorgungsspannung des WS1.
- 🔌 **Offline-Erkennung** – wenn UbiBot das Gerät als offline meldet, werden die
  Sensoren *nicht verfügbar*, statt am letzten Wert hängenzubleiben.
- 🩺 **Diagnose herunterladen** – eine Support-Datei, die du auf der Geräteseite
  herunterladen kannst. Schlüssel und persönliche Daten (Standort, MAC, IP,
  Seriennummer…) werden automatisch entfernt – sie kann also bedenkenlos geteilt
  werden.
- 🌍 **Deutsch und Englisch** für die komplette Einrichtung.

**Verbessert**
- 🏷️ **Klarere Namen** – jedes Gerät heißt wie dein Kanal (z. B. „Oben“) und die
  Sensoren einfach „Temperatur“, „Luftfeuchtigkeit“ usw.
- 🛠️ **Ungültigen Schlüssel ohne Neu-Einrichten beheben** – wenn ein Schlüssel
  nicht mehr funktioniert, zeigt Home Assistant eine *Reparieren*-Kachel, in die
  du einen neuen Schlüssel einträgst.
- ⏱️ **Ändern des Abrufintervalls funktioniert jetzt** (vorher still nicht).
- 💪 **Zuverlässiger** – kein Internet, Zeitüberschreitungen, falsche Schlüssel
  oder unerwartete Antworten bringen die Integration nicht mehr zum Absturz; die
  Sensoren werden nicht verfügbar und erholen sich von selbst.
- 📉 WLAN-Signal und Batterie sind unter *Diagnose* gruppiert, damit sie die
  Hauptansicht nicht zumüllen.

**Voraussetzungen**
- Home Assistant **2024.8.0 oder neuer**. (Update von 0.4.5 läuft automatisch.)

---

## [0.4.5] and earlier

Initial versions based on the code base by
[@ms32035](https://github.com/ms32035/home-assistant-ubibot).
Frühere Versionen basierend auf der Codebasis von
[@ms32035](https://github.com/ms32035/home-assistant-ubibot).

[1.0.0]: https://github.com/Pablo1732/home-assistant-ubibot/releases/tag/v1.0.0
