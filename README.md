# UbiBot for Home Assistant

Bring your **UbiBot** sensor readings (temperature, humidity, light, voltage and
more) straight into Home Assistant.

**🌐 [English](#english) · [Deutsch](#deutsch)**

> Tested with the **UbiBot WS1**. Other models may work but are untested.

> ℹ️ **About this integration:** Built with the help of AI, but every release is
> carefully reviewed — I test each scenario myself before publishing, and it runs
> in production in my own Home Assistant.

---

<a name="english"></a>
## English

### What you get
Each UbiBot device you add shows up as its own **device** in Home Assistant with
these sensors (only the ones your device actually provides will appear):

| Sensor | Description |
|--------|-------------|
| 🌡️ Temperature | Built-in temperature |
| 💧 Humidity | Relative humidity |
| 💡 Illuminance | Light level |
| 🌡️ External temperature | Only if a probe is connected |
| 📶 WiFi signal | Signal strength *(Diagnostic)* |
| ⚡ Voltage | Supply voltage – USB or battery *(Diagnostic)* |

When your device goes **offline**, its sensors automatically show as
*unavailable* – so you never look at a stale value and think it’s current.

---

### Requirements
- **Home Assistant 2024.8.0 or newer.** (Older versions are blocked automatically.)
- [HACS](https://hacs.xyz/) installed.

---

### Installation (via HACS)
1. In Home Assistant, open **HACS**.
2. Click the **⋮** menu (top right) → **Custom repositories**.
3. Paste `https://github.com/Pablo1732/home-assistant-ubibot`, choose category
   **Integration**, and click **Add**.
   ([Detailed HACS guide](https://hacs.xyz/docs/faq/custom_repositories/))
4. Search for **UbiBot**, click **Download**.
5. **Restart Home Assistant.**

---

### Setup
1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **UbiBot**.
3. Enter your **API key** and click **Submit**:
   - **Easiest – Account Key:** leave *Channel ID* empty. You’ll get a list of
     **all your devices** – just tick the ones you want to add. ✅
   - **Read Key:** if you prefer a per-device read key, also enter its
     **Channel ID**.
4. Done – your sensors appear automatically. 🎉

> 🔒 **Only read keys are stored, not your Account Key.** It’s used to list your
> devices and create a read-only key for each, then discarded. (If a read key
> can’t be set up right away, the Account Key is kept only until one works, then
> removed automatically.)

> The update interval defaults to 5 minutes; change it later under the
> integration’s **Configure** button (see [Options](#options)).

#### Where do I find my API key (and Channel ID)?
Log in at **[console.ubibot.com](https://console.ubibot.com)** (or the UbiBot
app), open your device, and go to its **channel settings → API keys**.

| Key type | What to do | Notes |
|----------|-----------|-------|
| 🔓 [Account Key](https://www.ubibot.com/platform-api/1188/generate-account-key/) | Paste it, leave Channel ID empty, pick your devices | Easiest; **not stored** – only read keys are kept |
| 🔑 [Read Key](https://www.ubibot.com/platform-api/1195/generate-channel-read-key/) | Paste it **and** the **Channel ID** (a number like `43798`) | For a single device |

---

<a name="options"></a>
### Options – change the update interval
Go to **Settings → Devices & Services → UbiBot → Configure**, set how often
(in seconds) the data should refresh, and save. Recommended: `300` (5 minutes).

---

### Help & FAQ

<details>
<summary><b>“Cannot connect” or “not a valid Account Key”</b></summary>

- Using an **Account Key**? Leave the *Channel ID* empty.
- Using a **Read Key**? You must also enter its **Channel ID**.
- Did you copy the **whole key** (no extra spaces)?
- Is your Home Assistant server online?
</details>

<details>
<summary><b>How do I add another device later?</b></summary>

Just add the integration again with your Account Key – only devices you haven’t
added yet will be offered. You can’t add the same device twice.
</details>

<details>
<summary><b>I'm coming from the old YAML version (ms32035)</b></summary>

Nothing to do manually – on the first start your old `sensor: - platform: ubibot`
configuration is **imported automatically**. Your entities, history and device
(area, name) are kept. You'll get a repair notice reminding you to remove the
`- platform: ubibot` block from your `configuration.yaml` and restart; after that
you can dismiss the notice.
</details>

<details>
<summary><b>My sensors show “unavailable”</b></summary>

This is expected when your **device is offline** (out of power, no WiFi, or
UbiBot shows it as offline in the app). As soon as it comes back online, the
sensors update by themselves. You can confirm the device status in the UbiBot
app.
</details>

<details>
<summary><b>Home Assistant shows a “Repair” notification for UbiBot</b></summary>

That happens if your key stopped working (e.g. it was regenerated). Click
**Repair**, enter a new key, and you’re done – no need to remove and re-add the
integration.
</details>

<details>
<summary><b>The voltage sensor is missing</b></summary>

Some setups don’t report the voltage field. The voltage sensor only appears
when your device actually sends that value.
</details>

<details>
<summary><b>Something isn’t working – how do I get help?</b></summary>

1. On the UbiBot **device page**, click **⋮ → Download diagnostics**. This file
   is safe to share – all keys and personal data are removed automatically.
2. Optionally enable debug logging: integration page → **Enable debug logging**.
3. Open an
   [issue on GitHub](https://github.com/Pablo1732/home-assistant-ubibot/issues)
   and attach the diagnostics file.
</details>

---

### Credits
Based on the code base by
[@ms32035](https://github.com/ms32035/home-assistant-ubibot). Thank you! 🙏

See the [changelog](CHANGELOG.md) for what’s new.

---

<a name="deutsch"></a>
## Deutsch

> ℹ️ **Über diese Integration:** Mit Hilfe von KI entwickelt, aber jede Version
> wird sorgfältig geprüft — ich teste jedes Szenario vor der Veröffentlichung
> selbst durch, und sie läuft bei mir produktiv im Einsatz.

### Was du bekommst
Jedes hinzugefügte UbiBot-Gerät erscheint als **eigenes Gerät** in Home Assistant
mit diesen Sensoren (es tauchen nur die auf, die dein Gerät tatsächlich liefert):

| Sensor | Beschreibung |
|--------|--------------|
| 🌡️ Temperatur | Eingebaute Temperatur |
| 💧 Luftfeuchtigkeit | Relative Luftfeuchtigkeit |
| 💡 Beleuchtungsstärke | Helligkeit |
| 🌡️ Externe Temperatur | Nur wenn eine Sonde angeschlossen ist |
| 📶 WLAN-Signal | Signalstärke *(Diagnose)* |
| ⚡ Spannung | Versorgungsspannung – USB oder Batterie *(Diagnose)* |

Wenn dein Gerät **offline** geht, werden seine Sensoren automatisch als
*nicht verfügbar* angezeigt – du siehst also nie einen alten Wert und hältst ihn
für aktuell.

---

### Voraussetzungen
- **Home Assistant 2024.8.0 oder neuer.** (Ältere Versionen werden automatisch blockiert.)
- [HACS](https://hacs.xyz/) installiert.

---

### Installation (über HACS)
1. Öffne in Home Assistant **HACS**.
2. Klicke oben rechts auf **⋮** → **Benutzerdefinierte Repositories**.
3. Füge `https://github.com/Pablo1732/home-assistant-ubibot` ein, wähle als
   Kategorie **Integration** und klicke **Hinzufügen**.
   ([Ausführliche HACS-Anleitung](https://hacs.xyz/docs/faq/custom_repositories/))
4. Suche nach **UbiBot** und klicke **Herunterladen**.
5. **Home Assistant neu starten.**

---

### Einrichtung
1. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
2. Suche nach **UbiBot**.
3. Gib deinen **API-Schlüssel** ein und klicke **Bestätigen**:
   - **Am einfachsten – Account-Key:** *Channel-ID* leer lassen. Du bekommst eine
     Liste **all deiner Geräte** – hak einfach die gewünschten an. ✅
   - **Read-Key:** wenn du lieber einen Gerät-Schlüssel nutzt, gib zusätzlich
     dessen **Channel-ID** ein.
4. Fertig – die Sensoren erscheinen automatisch. 🎉

> 🔒 **Gespeichert werden nur Read-Keys, nicht dein Account-Key.** Er dient dazu,
> deine Geräte aufzulisten und pro Gerät einen Nur-Lese-Schlüssel anzulegen, und
> wird danach verworfen. (Klappt ein Read-Key mal nicht sofort, bleibt der
> Account-Key nur so lange, bis einer funktioniert, und wird dann automatisch
> entfernt.)

> Das Abrufintervall steht standardmäßig auf 5 Minuten; ändern kannst du es später
> über den **Konfigurieren**-Button (siehe [Optionen](#optionen)).

#### Wo finde ich meinen API-Schlüssel (und die Channel-ID)?
Melde dich unter **[console.ubibot.com](https://console.ubibot.com)** (oder in
der UbiBot-App) an, öffne dein Gerät und gehe zu den
**Kanal-Einstellungen → API Keys**.

| Schlüsseltyp | Was tun | Hinweis |
|--------------|---------|---------|
| 🔓 [Account Key](https://www.ubibot.com/platform-api/1188/generate-account-key/) | Einfügen, Channel-ID leer lassen, Geräte anhaken | Am einfachsten; **wird nicht gespeichert** – nur Read-Keys bleiben |
| 🔑 [Read Key](https://www.ubibot.com/platform-api/1195/generate-channel-read-key/) | Einfügen **und** die **Channel-ID** (Nummer wie `43798`) | Für ein einzelnes Gerät |

---

<a name="optionen"></a>
### Optionen – Abrufintervall ändern
Gehe zu **Einstellungen → Geräte & Dienste → UbiBot → Konfigurieren**, stelle
ein (in Sekunden), wie oft die Daten aktualisiert werden sollen, und speichere.
Empfehlung: `300` (5 Minuten).

---

### Hilfe & FAQ

<details>
<summary><b>„Verbindung fehlgeschlagen“ oder „kein gültiger Account-Key“</b></summary>

- Nutzt du einen **Account-Key**? Lass die *Channel-ID* leer.
- Nutzt du einen **Read-Key**? Dann musst du zusätzlich die **Channel-ID** eingeben.
- Hast du den **kompletten Schlüssel** kopiert (keine Leerzeichen)?
- Ist dein Home-Assistant-Server online?
</details>

<details>
<summary><b>Wie füge ich später ein weiteres Gerät hinzu?</b></summary>

Füge die Integration einfach nochmal mit deinem Account-Key hinzu – es werden
nur Geräte angeboten, die du noch nicht hinzugefügt hast. Dasselbe Gerät kann
nicht doppelt hinzugefügt werden.
</details>

<details>
<summary><b>Ich komme von der alten YAML-Version (ms32035)</b></summary>

Du musst nichts von Hand machen – beim ersten Start wird deine alte
`sensor: - platform: ubibot`-Konfiguration **automatisch importiert**. Entitäten,
Verlauf und Gerät (Area, Name) bleiben erhalten. Du bekommst eine
Reparatur-Meldung, die dich erinnert, den `- platform: ubibot`-Block aus deiner
`configuration.yaml` zu entfernen und neu zu starten; danach kannst du die
Meldung schließen.
</details>

<details>
<summary><b>Meine Sensoren zeigen „nicht verfügbar“</b></summary>

Das ist normal, wenn dein **Gerät offline** ist (kein Strom, kein WLAN, oder
UbiBot zeigt es in der App als offline). Sobald es wieder online ist,
aktualisieren sich die Sensoren von selbst. Den Gerätestatus kannst du in der
UbiBot-App prüfen.
</details>

<details>
<summary><b>Home Assistant zeigt eine „Reparieren“-Meldung für UbiBot</b></summary>

Das passiert, wenn dein Schlüssel nicht mehr funktioniert (z. B. weil er neu
erstellt wurde). Klicke auf **Reparieren**, gib einen neuen Schlüssel ein –
fertig. Ein Entfernen und Neu-Hinzufügen ist nicht nötig.
</details>

<details>
<summary><b>Der Spannungs-Sensor fehlt</b></summary>

Manche Geräte melden den Spannungswert nicht. Der Spannungs-Sensor erscheint nur,
wenn dein Gerät diesen Wert auch sendet.
</details>

<details>
<summary><b>Etwas funktioniert nicht – wie bekomme ich Hilfe?</b></summary>

1. Klicke auf der UbiBot-**Geräteseite** auf **⋮ → Diagnose herunterladen**.
   Diese Datei kannst du bedenkenlos teilen – alle Schlüssel und persönlichen
   Daten werden automatisch entfernt.
2. Optional Debug-Protokollierung aktivieren: Integrationsseite →
   **Debug-Protokollierung aktivieren**.
3. Öffne ein
   [Issue auf GitHub](https://github.com/Pablo1732/home-assistant-ubibot/issues)
   und häng die Diagnose-Datei an.
</details>

---

### Danke
Basiert auf der Codebasis von
[@ms32035](https://github.com/ms32035/home-assistant-ubibot). Danke! 🙏

Was neu ist, steht im [Changelog](CHANGELOG.md).
