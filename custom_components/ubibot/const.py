"""Constants for Ubibot module."""

DOMAIN = "ubibot"
PLATFORMS = ["sensor"]

CONF_CHANNEL = "channel"
DEFAULT_SCAN_INTERVAL = 900  # seconds

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
    },
    "temperature_external": {
        "class": "temperature",
        "unit": "°C",
        "icon": "mdi:thermometer-probe",
        "field": "field8",
    },
}

MODELS = {"ubibot-ws1": "WS1"}
