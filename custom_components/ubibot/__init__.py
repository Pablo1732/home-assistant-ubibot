"""Ubibot component modern async setup."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_API_KEY

from .const import DOMAIN, PLATFORMS, CONF_CHANNEL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class UbibotCoordinator(DataUpdateCoordinator):
    """Coordinator für Ubibot API-Daten."""

    def __init__(self, hass: HomeAssistant, api_key: str, channel: str, interval: timedelta) -> None:
        self._hass = hass
        self._api_key = api_key
        self._channel = channel
        self.data: dict[str, Any] | None = None
        super().__init__(
            hass,
            _LOGGER,
            name=f"Ubibot {channel}",
            update_interval=interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Daten asynchron von der Ubibot API abrufen."""
        session = async_get_clientsession(self._hass)
        url = f"https://api.ubibot.io/channels/{self._channel}?account_key={self._api_key}"
        try:
            async with session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}")
                payload = await resp.json()
                # last_values ist ein JSON-String, in JSON wandeln
                if isinstance(payload.get("channel", {}).get("last_values"), str):
                    import json as _json
                    try:
                        payload["channel"]["last_values"] = _json.loads(payload["channel"]["last_values"])  # type: ignore[index]
                    except Exception as exc:
                        raise UpdateFailed(f"Invalid last_values format: {exc}") from exc
                return payload
        except Exception as exc:
            raise UpdateFailed(f"Error fetching Ubibot data: {exc}") from exc


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Richte einen Ubibot ConfigEntry ein."""
    api_key: str = entry.data[CONF_API_KEY]
    channel: str = entry.data[CONF_CHANNEL]
    scan_interval_sec: int = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    coordinator = UbibotCoordinator(
        hass,
        api_key,
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
