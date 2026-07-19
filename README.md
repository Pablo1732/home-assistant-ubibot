# UbiBot for Home Assistant

Bring your **UbiBot** sensor readings (temperature, humidity, light, battery and
more) straight into Home Assistant.

**🌐 [English](#english) · [Deutsch](#deutsch)**

> Tested with the **UbiBot WS1**. Other models may work but are untested.

---

<a name="english"></a>
## English

### What you get
Your UbiBot device shows up as a single **device** in Home Assistant with these
sensors (only the ones your device actually provides will appear):

| Sensor | Description |
|--------|-------------|
| 🌡️ Temperature | Built-in temperature |
| 💧 Humidity | Relative humidity |
| 💡 Illuminance | Light level |
| 🌡️ External temperature | Only if a probe is connected |
| 📶 WiFi signal | Signal strength *(Diagnostic)* |
| 🔋 Battery voltage | Supply voltage *(Diagnostic)* |

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
3. Fill in just **two** fields:
   - **Channel ID** – the number of your device (see below).
   - **API key** – either an Account Key **or** a Read Key (see below).
     The type is detected automatically.
4. Click **Submit**. Done – your sensors appear automatically. 🎉

> The update interval defaults to 5 minutes. You can change it later under
> the integration’s **Configure** button (see [Options](#options)).

#### Where do I find my Channel ID and API key?
Log in at **[console.ubibot.com](https://console.ubibot.com)** (or the UbiBot
app), open your device, and go to its **channel settings → API keys**.

- **Channel ID** – shown in the channel settings (a number like `43798`).
- **API key** – you have two choices:

| Key type | Access | Recommendation |
|----------|--------|----------------|
| 🔑 [Read Key](https://www.ubibot.com/platform-api/1195/generate-channel-read-key/) | Read-only, **one device** | ✅ **Recommended – safest** |
| 🔓 [Account Key](https://www.ubibot.com/platform-api/1188/generate-account-key/) | Your **whole account** | ⚠️ Less secure |

**Tip:** For Home Assistant you only ever need to *read* data, so the **Read
Key** is the better, safer choice.

---

<a name="options"></a>
### Options – change the update interval
Go to **Settings → Devices & Services → UbiBot → Configure**, set how often
(in seconds) the data should refresh, and save. Recommended: `300` (5 minutes).

---

### Help & FAQ

<details>
<summary><b>“Cannot connect” when I add the integration</b></summary>

The Channel ID or the key is wrong. Double-check both:
- Is the **Channel ID** the right number (no extra spaces)?
- Did you copy the **whole key**?
- Is your Home Assistant server online?
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
<summary><b>The battery sensor is missing</b></summary>

Some setups don’t report the voltage field. The battery sensor only appears
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

### Was du bekommst
Dein UbiBot-Gerät erscheint als **ein Gerät** in Home Assistant mit diesen
Sensoren (es tauchen nur die auf, die dein Gerät tatsächlich liefert):

| Sensor | Beschreibung |
|--------|--------------|
| 🌡️ Temperatur | Eingebaute Temperatur |
| 💧 Luftfeuchtigkeit | Relative Luftfeuchtigkeit |
| 💡 Beleuchtungsstärke | Helligkeit |
| 🌡️ Externe Temperatur | Nur wenn eine Sonde angeschlossen ist |
| 📶 WLAN-Signal | Signalstärke *(Diagnose)* |
| 🔋 Batteriespannung | Versorgungsspannung *(Diagnose)* |

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
3. Fülle nur **zwei** Felder aus:
   - **Channel-ID** – die Nummer deines Geräts (siehe unten).
   - **API-Schlüssel** – entweder ein Account-Key **oder** ein Read-Key
     (siehe unten). Der Typ wird automatisch erkannt.
4. Klicke **Bestätigen**. Fertig – die Sensoren erscheinen automatisch. 🎉

> Das Abrufintervall steht standardmäßig auf 5 Minuten. Du kannst es später über
> den **Konfigurieren**-Button ändern (siehe [Optionen](#optionen)).

#### Wo finde ich Channel-ID und API-Schlüssel?
Melde dich unter **[console.ubibot.com](https://console.ubibot.com)** (oder in
der UbiBot-App) an, öffne dein Gerät und gehe zu den
**Kanal-Einstellungen → API Keys**.

- **Channel-ID** – steht in den Kanal-Einstellungen (eine Nummer wie `43798`).
- **API-Schlüssel** – du hast zwei Möglichkeiten:

| Schlüsseltyp | Zugriff | Empfehlung |
|--------------|---------|------------|
| 🔑 [Read Key](https://www.ubibot.com/platform-api/1195/generate-channel-read-key/) | Nur lesen, **ein Gerät** | ✅ **Empfohlen – am sichersten** |
| 🔓 [Account Key](https://www.ubibot.com/platform-api/1188/generate-account-key/) | Dein **ganzes Konto** | ⚠️ Weniger sicher |

**Tipp:** Home Assistant muss die Daten nur *lesen* – nimm daher am besten den
**Read Key**, das ist die sicherere Wahl.

---

<a name="optionen"></a>
### Optionen – Abrufintervall ändern
Gehe zu **Einstellungen → Geräte & Dienste → UbiBot → Konfigurieren**, stelle
ein (in Sekunden), wie oft die Daten aktualisiert werden sollen, und speichere.
Empfehlung: `300` (5 Minuten).

---

### Hilfe & FAQ

<details>
<summary><b>„Verbindung fehlgeschlagen“ beim Hinzufügen</b></summary>

Die Channel-ID oder der Schlüssel ist falsch. Prüfe beides:
- Ist die **Channel-ID** die richtige Nummer (keine Leerzeichen)?
- Hast du den **kompletten Schlüssel** kopiert?
- Ist dein Home-Assistant-Server online?
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
<summary><b>Der Batterie-Sensor fehlt</b></summary>

Manche Geräte melden den Spannungswert nicht. Der Batterie-Sensor erscheint nur,
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
