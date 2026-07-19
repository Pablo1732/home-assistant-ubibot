"""Ubibot component modern async setup."""

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_API_KEY

from .const import DOMAIN, PLATFORMS, CONF_CHANNEL, DEFAULT_SCAN_INTERVAL, CONF_READ_KEY

_LOGGER = logging.getLogger(__name__)


class UbibotCoordinator(DataUpdateCoordinator):
    """Coordinator für Ubibot API-Daten."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api_key: str | None, read_key: str | None, channel: str, interval: timedelta) -> None:
        self._hass = hass
        self._api_key = api_key
        self._read_key = read_key
        self._channel = channel
        super().__init__(
            hass,
            _LOGGER,
            name=f"Ubibot {channel}",
            update_interval=interval,
            config_entry=entry,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Daten asynchron von der Ubibot API abrufen."""
        session = async_get_clientsession(self._hass)
        if self._api_key:
            # Account-Key Endpoint
            url = f"https://api.ubibot.io/channels/{self._channel}?account_key={self._api_key}"
        elif self._read_key:
            # Read-Key Endpoint benötigt webapi und Parameter api_key
            url = f"https://webapi.ubibot.com/channels/{self._channel}?api_key={self._read_key}"
        else:
            # Kein Schlüssel hinterlegt -> HA bietet Reauth (neuen Schlüssel eingeben) an
            raise ConfigEntryAuthFailed("Missing credentials: api_key or read_key")

        endpoint = "account-key" if self._api_key else "read-key"
        _LOGGER.debug("Ubibot: fetching channel %s via %s endpoint", self._channel, endpoint)

        timeout = aiohttp.ClientTimeout(total=20)
        try:
            async with session.get(url, timeout=timeout) as resp:
                # Falsche/abgelaufene Keys -> Reauth-Dialog statt endloser Wiederholungen
                if resp.status in (401, 403):
                    raise ConfigEntryAuthFailed(f"Authentication failed (HTTP {resp.status})")
                if resp.status != 200:
                    raise UpdateFailed(f"Unexpected HTTP status {resp.status}")
                try:
                    payload = await resp.json()
                except (aiohttp.ContentTypeError, ValueError) as exc:
                    raise UpdateFailed(f"Invalid JSON from Ubibot API: {exc}") from exc
        except asyncio.TimeoutError as exc:
            raise UpdateFailed("Timeout while contacting Ubibot API") from exc
        except aiohttp.ClientError as exc:
            raise UpdateFailed(f"Connection error contacting Ubibot API: {exc}") from exc

        # Grundstruktur prüfen -> schützt vor unerwartetem API-Umbau
        channel = payload.get("channel")
        if not isinstance(channel, dict):
            raise UpdateFailed("Unexpected API response: missing 'channel' object")

        # last_values kommt als JSON-String -> in dict wandeln
        if isinstance(channel.get("last_values"), str):
            try:
                channel["last_values"] = json.loads(channel["last_values"])
            except (ValueError, TypeError) as exc:
                raise UpdateFailed(f"Invalid last_values format: {exc}") from exc

        last_values = channel.get("last_values", {})
        net = channel.get("net")
        _LOGGER.debug(
            "Ubibot channel %s: net=%s (%s), %d value field(s)",
            self._channel,
            net,
            "online" if str(net) == "1" else "offline" if str(net) == "0" else "unknown",
            len(last_values) if isinstance(last_values, dict) else 0,
        )

        return payload


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Richte einen Ubibot ConfigEntry ein."""
    api_key: str | None = entry.data.get(CONF_API_KEY)
    read_key: str | None = entry.data.get(CONF_READ_KEY)
    channel: str = entry.data[CONF_CHANNEL]
    # Reihenfolge: Optionen > Entry-Daten > Default
    scan_interval_sec: int = entry.options.get("scan_interval", entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL))

    # Falls bisher keine Optionen gesetzt sind, initialisiere sie
    if not entry.options or "scan_interval" not in entry.options:
        hass.config_entries.async_update_entry(entry, options={"scan_interval": scan_interval_sec})

    coordinator = UbibotCoordinator(
        hass,
        entry,
        api_key,
        read_key,
        channel,
        timedelta(seconds=scan_interval_sec),
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as exc:
        raise ConfigEntryNotReady(f"Initial Ubibot refresh failed: {exc}") from exc

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "api_key": api_key,
        "read_key": read_key,
        "channel": channel,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entferne einen Ubibot ConfigEntry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok
