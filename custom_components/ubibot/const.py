"""Constants for Ubibot module."""

DOMAIN = "ubibot"
PLATFORMS = ["sensor"]

# Config-Eintrag: ein Eintrag kann mehrere Kanäle verwalten.
# entry.data[CONF_CHANNELS] = { "<channel_id>": { "read_key": "..."} , ... }
CONF_CHANNELS = "channels"
CONF_CHANNEL = "channel"            # Einzel-Kanal-Feld im Setup-Formular (optional)
CONF_READ_KEY = "read_key"
CONF_ACCOUNT_KEY = "account_key"    # nur für migrierte Alt-Einträge; neu nie gespeichert
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 300  # seconds

# API-Endpoints
API_BASE = "https://webapi.ubibot.com"        # Standard-API (Read-Key, Account-Key-Verwaltung)
ACCOUNT_DATA_BASE = "https://api.ubibot.io"    # Account-Key Einzel-Kanal-Daten (Alt-Einträge)

# Read-Key-Verwaltung
READ_KEY_NOTE = "homeassistant-ubibot"  # Notiz, an der wir "unseren" Read-Key wiedererkennen
MAX_READ_KEYS = 10                       # UbiBot-Limit an Read-Keys pro Kanal

SENSOR_TYPES = {
    "temperature": {
        "class": "temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "field": "field1",
    },
    "humidity": {
        "class": "humidity",
        "unit": "%",
        "icon": "mdi:water-percent",
        "field": "field2",
    },
    "lux": {
        "class": "illuminance",
        "unit": "lx",
        "icon": "mdi:lightbulb-on-outline",
        "field": "field3",
    },
    "wifi_rssi": {
        "class": "signal_strength",
        "unit": "dBm",
        "icon": "mdi:wifi",
        "field": "field5",
        "category": "diagnostic",
    },
    "battery_voltage": {
        "class": "voltage",
        "unit": "V",
        "icon": "mdi:battery",
        "field": "field4",
        "category": "diagnostic",
    },
    "temperature_external": {
        "class": "temperature",
        "unit": "°C",
        "icon": "mdi:thermometer-probe",
        "field": "field8",
    },
}

MODELS = {"ubibot-ws1": "WS1"}
