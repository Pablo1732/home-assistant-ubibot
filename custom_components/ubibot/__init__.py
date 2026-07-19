"""Ubibot component modern async setup."""

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any
from urllib.parse import quote

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr, issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_API_KEY

from . import api
from .const import (
    ACCOUNT_DATA_BASE,
    API_BASE,
    CONF_ACCOUNT_KEY,
    CONF_CHANNEL,
    CONF_CHANNELS,
    CONF_READ_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config) -> bool:
    """Beim Start prüfen: ist der YAML-Block weg, die Import-Reparaturmeldung löschen."""

    @callback
    def _cleanup_yaml_issue(hass: HomeAssistant) -> None:
        # async_setup_platform setzt das Flag, wenn YAML noch vorhanden ist.
        if not hass.data.get(DOMAIN, {}).get("yaml_seen"):
            ir.async_delete_issue(hass, DOMAIN, "yaml_import")

    async_at_started(hass, _cleanup_yaml_issue)
    return True


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
        channel_path = quote(str(self._channel), safe="")
        if self._api_key:
            # Account-Key Endpoint (nur migrierte Alt-Einträge)
            url = f"{ACCOUNT_DATA_BASE}/channels/{channel_path}"
            params = {"account_key": self._api_key}
        elif self._read_key:
            # Read-Key Endpoint benötigt webapi und Parameter api_key
            url = f"{API_BASE}/channels/{channel_path}"
            params = {"api_key": self._read_key}
        else:
            # Kein Schlüssel hinterlegt -> HA bietet Reauth (neuen Schlüssel eingeben) an
            raise ConfigEntryAuthFailed("Missing credentials: api_key or read_key")

        endpoint = "account-key" if self._api_key else "read-key"
        _LOGGER.debug("Ubibot: fetching channel %s via %s endpoint", self._channel, endpoint)

        timeout = aiohttp.ClientTimeout(total=20)
        try:
            async with session.get(url, params=params, timeout=timeout) as resp:
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


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Alt-Eintrag (v1: ein Kanal, flache Daten) -> v2 (channels-Dict) migrieren."""
    if entry.version >= 2:
        return True

    old = dict(entry.data)
    channel = str(old.get(CONF_CHANNEL))
    record: dict[str, str] = {}
    if old.get(CONF_READ_KEY):
        record[CONF_READ_KEY] = old[CONF_READ_KEY]
    elif old.get(CONF_API_KEY):
        # Alt-Eintrag mit Account-Key: bleibt funktionsfähig (nicht zwangskonvertiert).
        record[CONF_ACCOUNT_KEY] = old[CONF_API_KEY]

    new_data: dict = {CONF_CHANNELS: {channel: record}}
    if CONF_SCAN_INTERVAL in old:
        new_data[CONF_SCAN_INTERVAL] = old[CONF_SCAN_INTERVAL]

    hass.config_entries.async_update_entry(entry, data=new_data, version=2)
    _LOGGER.debug("Ubibot: migrated entry %s to version 2 (channel %s)", entry.entry_id, channel)
    return True


async def _async_upgrade_account_keys(
    hass: HomeAssistant, entry: ConfigEntry, channels: dict[str, dict]
) -> dict[str, dict]:
    """Account-Keys zu Read-Keys upgraden und aus der Speicherung entfernen.

    Best effort: pro Kanal mit gespeichertem Account-Key wird ein Read-Key
    beschafft (bestehenden HA-Key wiederverwenden, sonst erzeugen). Klappt das,
    wird nur noch der Read-Key gespeichert. Scheitert es (z. B. keine Verbindung),
    bleibt der Account-Key erhalten und es wird beim nächsten Start erneut
    versucht -> das Setup scheitert nie an diesem Schritt.
    """
    updated = dict(channels)
    changed = False
    for channel_id, record in channels.items():
        account_key = record.get(CONF_ACCOUNT_KEY)
        if not account_key or record.get(CONF_READ_KEY):
            continue
        try:
            read_key, _ = await api.async_provision_read_key(
                hass, account_key, str(channel_id)
            )
            # Read-Key erst gegen den Kanal prüfen -> Account-Key wird NUR entfernt,
            # wenn der neue Read-Key nachweislich Daten abruft.
            await api.async_validate_read_key(hass, read_key, str(channel_id))
        except api.UbibotError as exc:
            _LOGGER.debug(
                "Ubibot: read-key upgrade for channel %s deferred: %s", channel_id, exc
            )
            continue
        updated[str(channel_id)] = {CONF_READ_KEY: read_key}
        changed = True
        _LOGGER.info(
            "Ubibot: upgraded channel %s from account key to a stored read key", channel_id
        )

    if changed:
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_CHANNELS: updated}
        )
    return updated


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Richte einen Ubibot ConfigEntry ein (kann mehrere Kanäle enthalten)."""
    channels: dict[str, dict] = entry.data.get(CONF_CHANNELS, {})
    if not channels:
        raise ConfigEntryNotReady("No channels configured for this entry")

    # Gespeicherte Account-Keys (aus YAML-Import / Alt-Migration) einmalig zu
    # Read-Keys upgraden und den Account-Key aus der Speicherung entfernen.
    channels = await _async_upgrade_account_keys(hass, entry, channels)

    scan_interval_sec: int = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )
    interval = timedelta(seconds=scan_interval_sec)
    coordinators: dict[str, UbibotCoordinator] = {}
    for channel_id, record in channels.items():
        coordinators[str(channel_id)] = UbibotCoordinator(
            hass,
            entry,
            record.get(CONF_ACCOUNT_KEY),
            record.get(CONF_READ_KEY),
            str(channel_id),
            interval,
        )

    # Alle Kanäle parallel aktualisieren; scheitern alle -> Eintrag noch nicht bereit.
    await asyncio.gather(*(c.async_refresh() for c in coordinators.values()))
    if not any(c.last_update_success for c in coordinators.values()):
        raise ConfigEntryNotReady("Initial refresh failed for all Ubibot channels")

    # Alt-Gerät (ms32035: Identifier = Seriennummer) auf die neue Channel-ID-Kennung
    # umschreiben, damit Area/Name/Geräte-Kachel beim Umstieg erhalten bleiben.
    for channel_id, coordinator in coordinators.items():
        _migrate_legacy_device(hass, entry, channel_id, coordinator)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinators": coordinators}

    # Falls noch ein Account-Key gespeichert ist (Upgrade beim Setup nicht möglich,
    # z. B. offline): nach jedem erfolgreichen Abruf erneut versuchen -> migriert
    # automatisch, sobald online, ohne Neustart.
    _setup_account_key_upgrade(hass, entry, coordinators)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


def _setup_account_key_upgrade(
    hass: HomeAssistant, entry: ConfigEntry, coordinators: dict[str, "UbibotCoordinator"]
) -> None:
    """Ausstehende Account-Key->Read-Key-Upgrades im laufenden Betrieb nachholen."""

    def _pending() -> bool:
        return any(
            record.get(CONF_ACCOUNT_KEY) and not record.get(CONF_READ_KEY)
            for record in entry.data.get(CONF_CHANNELS, {}).values()
        )

    if not _pending():
        return

    state = {"running": False}

    async def _try_upgrade() -> None:
        if state["running"] or not _pending():
            return
        state["running"] = True
        try:
            await _async_upgrade_account_keys(
                hass, entry, dict(entry.data.get(CONF_CHANNELS, {}))
            )
        finally:
            state["running"] = False

    def _make_listener(coordinator: "UbibotCoordinator"):
        @callback
        def _on_update() -> None:
            # Nur nach einem erfolgreichen Abruf (online) und solange noch offen.
            if coordinator.last_update_success and _pending():
                hass.async_create_task(_try_upgrade())

        return _on_update

    for coordinator in coordinators.values():
        entry.async_on_unload(coordinator.async_add_listener(_make_listener(coordinator)))


def _migrate_legacy_device(
    hass: HomeAssistant, entry: ConfigEntry, channel_id: str, coordinator: "UbibotCoordinator"
) -> None:
    """Altes Gerät (Seriennummer-Kennung) auf die Channel-ID-Kennung umschreiben.

    Erhält Area-Zuordnung, eigenen Gerätenamen und Entitäten beim Umstieg von der
    alten YAML-Integration (ms32035). No-op für frische Installs / 1.0.0-Nutzer.
    """
    channel = (coordinator.data or {}).get("channel", {})
    full_serial = channel.get("full_serial")
    if not full_serial:
        return

    registry = dr.async_get(hass)
    new_identifier = (DOMAIN, str(channel_id))
    # Gibt es schon ein Gerät mit der neuen Kennung? Dann nichts umschreiben.
    if registry.async_get_device(identifiers={new_identifier}):
        return
    old_device = registry.async_get_device(identifiers={(DOMAIN, full_serial)})
    if old_device is None:
        return

    registry.async_update_device(
        old_device.id,
        new_identifiers={new_identifier},
        add_config_entry_id=entry.entry_id,
    )
    _LOGGER.info(
        "Ubibot: migrated legacy device (serial %s) to channel-id identifier %s",
        full_serial,
        channel_id,
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entferne einen Ubibot ConfigEntry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok
