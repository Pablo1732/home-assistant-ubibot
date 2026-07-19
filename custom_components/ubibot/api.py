"""API-Hilfen für die Einrichtung (Kanäle auflisten, Read-Keys verwalten).

Diese Funktionen laufen nur zur **Setup-Zeit** im Config-Flow. Der Account-Key
wird ausschließlich hier verwendet (Geräte abfragen, Read-Key holen/erzeugen) und
danach verworfen – gespeichert wird in Home Assistant nur der Read-Key.
"""

from __future__ import annotations

import asyncio
import logging
from urllib.parse import quote

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_BASE, MAX_READ_KEYS, READ_KEY_NOTE

_LOGGER = logging.getLogger(__name__)
_TIMEOUT = aiohttp.ClientTimeout(total=20)


class UbibotError(Exception):
    """Allgemeiner UbiBot-API-Fehler."""


class UbibotAuthError(UbibotError):
    """Ungültiger Schlüssel (HTTP 401/403)."""


def _channel_path(channel_id: str) -> str:
    """URL-Pfad für einen Kanal – Channel-ID sicher kodieren (gegen Fehleingaben)."""
    return f"{API_BASE}/channels/{quote(str(channel_id), safe='')}"


async def _request_json(
    session: aiohttp.ClientSession,
    url: str,
    method: str = "GET",
    params: dict | None = None,
) -> dict:
    """HTTP-Request ausführen und JSON zurückgeben; Fehler sauber übersetzen.

    Query-Parameter werden über ``params`` übergeben (aiohttp kodiert sie sauber),
    damit Sonderzeichen in Schlüsseln/IDs die Anfrage nicht zerlegen.
    """
    try:
        async with session.request(method, url, params=params, timeout=_TIMEOUT) as resp:
            if resp.status in (401, 403):
                raise UbibotAuthError(f"HTTP {resp.status}")
            if resp.status != 200:
                raise UbibotError(f"HTTP {resp.status}")
            try:
                return await resp.json()
            except (aiohttp.ContentTypeError, ValueError) as exc:
                raise UbibotError(f"Invalid JSON: {exc}") from exc
    except (asyncio.TimeoutError, aiohttp.ClientError) as exc:
        raise UbibotError(f"Connection error: {exc}") from exc


async def async_list_channels(hass: HomeAssistant, account_key: str) -> list[dict]:
    """Alle Kanäle eines Accounts auflisten (nur mit Account-Key möglich)."""
    session = async_get_clientsession(hass)
    data = await _request_json(
        session, f"{API_BASE}/channels", params={"account_key": account_key}
    )
    channels = data.get("channels")
    if not isinstance(channels, list):
        raise UbibotError("Unexpected response: no channels list")
    return channels


async def async_validate_read_key(hass: HomeAssistant, read_key: str, channel_id: str) -> None:
    """Read-Key gegen einen Kanal prüfen (wirft bei ungültig/nicht erreichbar)."""
    session = async_get_clientsession(hass)
    await _request_json(session, _channel_path(channel_id), params={"api_key": read_key})


async def async_provision_read_key(
    hass: HomeAssistant, account_key: str, channel_id: str
) -> tuple[str, bool]:
    """Read-Key für einen Kanal beschaffen.

    Ablauf:
      1. Existiert bereits ein Read-Key mit unserer Notiz -> wiederverwenden.
      2. Sonst, falls noch Platz (< MAX_READ_KEYS) -> neuen erzeugen.
      3. Sonst (Limit erreicht) -> bestehenden Read-Key wiederverwenden.

    Rückgabe: ``(read_key, limited)`` – ``limited=True`` bedeutet, dass wegen des
    Limits ein bestehender (fremder) Schlüssel genutzt werden musste.
    """
    session = async_get_clientsession(hass)
    base = f"{_channel_path(channel_id)}/api_keys"

    data = await _request_json(
        session, base, params={"action": "list", "account_key": account_key}
    )
    read_keys = data.get("read_keys") or []

    # 1) vorhandenen HA-Read-Key wiederverwenden
    for key in read_keys:
        if key.get("note") == READ_KEY_NOTE and key.get("read_key"):
            _LOGGER.debug("Ubibot: reusing existing HA read key for channel %s", channel_id)
            return key["read_key"], False

    # 2) neuen Read-Key erzeugen, solange Platz ist
    if len(read_keys) < MAX_READ_KEYS:
        gen = await _request_json(
            session,
            base,
            method="POST",
            params={
                "action": "generate_read_key",
                "note": READ_KEY_NOTE,
                "account_key": account_key,
            },
        )
        read_key = gen.get("read_key")
        if not read_key:
            raise UbibotError("Generate read key returned no key")
        _LOGGER.debug("Ubibot: generated new HA read key for channel %s", channel_id)
        return read_key, False

    # 3) Limit erreicht -> einen bestehenden Read-Key wiederverwenden
    for key in read_keys:
        if key.get("read_key"):
            _LOGGER.warning(
                "Ubibot: channel %s already has %d read keys (max %d); reusing an existing one",
                channel_id,
                len(read_keys),
                MAX_READ_KEYS,
            )
            return key["read_key"], True

    raise UbibotError("No read key available and none could be created")
