"""Diagnostics-Unterstützung für Ubibot.

Erzeugt den Inhalt für den "Diagnose herunterladen"-Button auf der
Integrations-/Geräteseite. Schlüssel und persönliche Daten werden
automatisch geschwärzt, damit die Datei gefahrlos geteilt werden kann
(z. B. für Support/Bug-Reports).
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_ACCOUNT_KEY, CONF_READ_KEY

# Felder, die niemals in der Diagnose-Datei landen dürfen:
# Zugangsschlüssel und personenbezogene / standortbezogene Daten.
TO_REDACT = {
    CONF_API_KEY,
    CONF_READ_KEY,
    CONF_ACCOUNT_KEY,
    "write_key",
    "user_id",
    "username",
    "last_ip",
    "mac",
    "mac_address",
    "serial",
    "full_serial",
    "device_id",
    "latitude",
    "longitude",
    "status",  # enthält SSID + MAC
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Diagnose-Daten für einen Config-Eintrag zurückgeben."""
    store = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    coordinators = store.get("coordinators", {})

    diagnostics: dict[str, Any] = {
        "entry": {
            "title": entry.title,
            "version": entry.version,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": dict(entry.options),
        },
        "channels": {
            channel_id: {
                "last_update_success": coordinator.last_update_success,
                "update_interval": str(coordinator.update_interval),
                "data": async_redact_data(coordinator.data or {}, TO_REDACT),
            }
            for channel_id, coordinator in coordinators.items()
        },
    }

    return diagnostics
