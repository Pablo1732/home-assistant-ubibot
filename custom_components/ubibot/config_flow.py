"""Config-Flow für UbiBot.

Einrichtung mit **einem** Feld für den Schlüssel plus optionaler Channel-ID:

* **Account-Key** (Channel-ID leer) -> alle Geräte werden aufgelistet, der Nutzer
  hakt an, welche hinzugefügt werden. Pro Gerät wird ein Read-Key beschafft
  (bestehenden mit unserer Notiz wiederverwenden, sonst neu erzeugen). Der
  Account-Key wird **nie gespeichert**.
* **Read-Key** (Channel-ID ausgefüllt) -> genau dieser eine Kanal wird
  hinzugefügt.
"""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from . import api
from .const import (
    CONF_ACCOUNT_KEY,
    CONF_CHANNEL,
    CONF_CHANNELS,
    CONF_READ_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def _channel_label(channel: dict) -> str:
    """Anzeigetext für ein Gerät in der Auswahlliste."""
    name = channel.get("name") or channel.get("channel_id")
    net = str(channel.get("net"))
    status = "online" if net == "1" else "offline" if net == "0" else "?"
    return f"{name} ({channel.get('channel_id')}) – {status}"


class UbibotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Ubibot config flow."""

    VERSION = 2

    def __init__(self) -> None:
        # Account-Key nur transient im Speicher während des Flows – nie persistiert.
        self._account_key: str | None = None
        self._channels: list[dict] = []
        self._reauth_entry: config_entries.ConfigEntry | None = None
        self._pending_entry: tuple[str, dict] | None = None
        self._limited_channels: list[str] = []
        self._pending_channel: str | None = None
        self._pending_readkey: str | None = None
        self._pending_readonly: dict[str, str] = {}
        self._fallback_channels: list[str] = []

    # ------------------------------------------------------------------ helpers
    def _configured_channel_ids(self) -> set[str]:
        """Alle bereits eingerichteten Kanal-IDs (über alle Einträge)."""
        ids: set[str] = set()
        for entry in self._async_current_entries():
            for channel_id in entry.data.get(CONF_CHANNELS, {}):
                ids.add(str(channel_id))
        return ids

    # -------------------------------------------------------------------- steps
    async def async_step_user(self, user_input=None):
        """Erster Schritt: Schlüssel (+ optionale Channel-ID)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            key_value = (user_input.get(CONF_API_KEY) or "").strip()
            channel = (user_input.get(CONF_CHANNEL) or "").strip()

            if not key_value:
                errors[CONF_API_KEY] = "required"
            elif channel:
                # ---- Channel-ID angegeben ----
                if channel in self._configured_channel_ids():
                    errors[CONF_CHANNEL] = "already_configured"
                else:
                    # 1) Als Read-Key versuchen.
                    try:
                        await api.async_validate_read_key(self.hass, key_value, channel)
                        is_read_key = True
                    except api.UbibotError:
                        is_read_key = False
                    if is_read_key:
                        return self.async_create_entry(
                            title=f"UbiBot {channel}",
                            data={CONF_CHANNELS: {channel: {CONF_READ_KEY: key_value}}},
                        )
                    # 2) Kein Read-Key -> als Account-Key für diesen Kanal behandeln.
                    self._account_key = key_value
                    self._pending_channel = channel
                    result = await self._async_account_with_channel()
                    if result is not None:
                        return result
                    errors["base"] = "cannot_connect"
            else:
                # ---- Account-Key-Weg: Geräte auflisten ----
                try:
                    channels = await api.async_list_channels(self.hass, key_value)
                except api.UbibotAuthError:
                    # Kein gültiger Account-Key -> evtl. Read-Key ohne Channel-ID
                    errors["base"] = "account_key_invalid"
                except api.UbibotError:
                    errors["base"] = "cannot_connect"
                else:
                    self._account_key = key_value
                    self._channels = channels
                    return await self.async_step_select()

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Optional(CONF_CHANNEL, default=""): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_select(self, user_input=None):
        """Geräteauswahl (nur Account-Key-Weg)."""
        errors: dict[str, str] = {}
        configured = self._configured_channel_ids()
        # Nur Kanäle mit gültiger ID, die noch nicht eingerichtet sind.
        available = [
            ch
            for ch in self._channels
            if ch.get("channel_id") and str(ch["channel_id"]) not in configured
        ]

        if not available:
            return self.async_abort(reason="no_new_devices")

        available_ids = {str(ch["channel_id"]) for ch in available}

        if user_input is not None:
            # Nur (noch) verfügbare Auswahl übernehmen -> schützt vor Doppel-Anlage,
            # falls parallel ein zweiter Setup-Dialog dasselbe Gerät hinzugefügt hat.
            selected = [
                c for c in (user_input.get(CONF_CHANNELS) or []) if c in available_ids
            ]
            if not selected:
                errors["base"] = "no_selection"
            else:
                read_ok: dict[str, str] = {}
                fallback: list[str] = []
                limited: list[str] = []
                for channel_id in selected:
                    cid = str(channel_id)
                    read_key = None
                    is_limited = False
                    try:
                        read_key, is_limited = await api.async_provision_read_key(
                            self.hass, self._account_key, cid
                        )
                        # Read-Key erst prüfen, bevor er gespeichert wird.
                        await api.async_validate_read_key(self.hass, read_key, cid)
                    except api.UbibotError:
                        read_key = None
                    if read_key:
                        read_ok[cid] = read_key
                        if is_limited:
                            limited.append(cid)
                    else:
                        # Kein funktionierender Read-Key -> geht der Account-Key-Abruf?
                        try:
                            await api.async_validate_account_key(
                                self.hass, self._account_key, cid
                            )
                            fallback.append(cid)
                        except api.UbibotError:
                            pass  # dieser Kanal geht gar nicht -> überspringen

                if not read_ok and not fallback:
                    errors["base"] = "cannot_connect"
                else:
                    self._pending_readonly = read_ok
                    self._limited_channels = limited
                    if fallback:
                        # Für manche Geräte kein Read-Key -> Account-Key anbieten.
                        self._fallback_channels = fallback
                        return await self.async_step_select_fallback()
                    return await self._async_finish_selection(read_ok, [], limited)

        options = {str(ch["channel_id"]): _channel_label(ch) for ch in available}
        schema = vol.Schema(
            {vol.Required(CONF_CHANNELS, default=[]): cv.multi_select(options)}
        )
        return self.async_show_form(step_id="select", data_schema=schema, errors=errors)

    async def _async_finish_selection(
        self, read_ok: dict[str, str], account_fallback: list[str], limited: list[str]
    ):
        """Config-Entry aus der Geräteauswahl erstellen (Read-Keys + optional
        Account-Key-Fallback für einzelne Kanäle)."""
        channels_data: dict[str, dict] = {
            cid: {CONF_READ_KEY: read_key} for cid, read_key in read_ok.items()
        }
        for cid in account_fallback:
            channels_data[cid] = {CONF_ACCOUNT_KEY: self._account_key}

        if not channels_data:
            return self.async_abort(reason="cancelled")

        if not account_fallback:
            # Account-Key nicht mehr benötigt -> verwerfen.
            self._account_key = None

        title = (
            f"UbiBot ({len(channels_data)} Geräte)"
            if len(channels_data) > 1
            else f"UbiBot {next(iter(channels_data))}"
        )
        data = {CONF_CHANNELS: channels_data}
        if limited:
            self._pending_entry = (title, data)
            return await self.async_step_limited()
        return self.async_create_entry(title=title, data=data)

    async def async_step_select_fallback(self, user_input=None):
        """Für einige gewählte Geräte war kein funktionierender Read-Key möglich."""
        return self.async_show_menu(
            step_id="select_fallback",
            menu_options=["use_account_key_multi", "add_read_key_only"],
            description_placeholders={"channels": ", ".join(self._fallback_channels)},
        )

    async def async_step_use_account_key_multi(self, user_input=None):
        """Für die betroffenen Geräte bewusst den Account-Key nutzen (unsicherer)."""
        return await self._async_finish_selection(
            self._pending_readonly, self._fallback_channels, self._limited_channels
        )

    async def async_step_add_read_key_only(self, user_input=None):
        """Nur die Geräte hinzufügen, die einen funktionierenden Read-Key haben."""
        return await self._async_finish_selection(
            self._pending_readonly, [], self._limited_channels
        )

    async def async_step_limited(self, user_input=None):
        """Hinweis, dass bei manchen Geräten das Read-Key-Limit erreicht war."""
        if user_input is not None:
            title, data = self._pending_entry  # type: ignore[attr-defined]
            return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="limited",
            data_schema=vol.Schema({}),
            description_placeholders={
                "channels": ", ".join(self._limited_channels)  # type: ignore[attr-defined]
            },
        )

    async def _async_account_with_channel(self):
        """Channel-ID wurde angegeben, aber der Schlüssel ist kein Read-Key.

        Prüft, ob es ein gültiger Account-Key für den Kanal ist, und leitet in den
        Hinweis- bzw. Fallback-Schritt. Gibt None zurück, wenn der Schlüssel weder
        Read- noch Account-Key ist (-> „cannot_connect").
        """
        channel = self._pending_channel
        # Gültiger Account-Key mit Zugriff auf den Kanal? (Read-Key beschaffen)
        try:
            read_key, _ = await api.async_provision_read_key(
                self.hass, self._account_key, channel
            )
        except api.UbibotError:
            return None  # weder Read- noch Account-Key

        # Funktioniert der beschaffte Read-Key wirklich?
        try:
            await api.async_validate_read_key(self.hass, read_key, channel)
        except api.UbibotError:
            # Read-Key geht nicht -> geht wenigstens der Account-Key-Datenabruf?
            try:
                await api.async_validate_account_key(self.hass, self._account_key, channel)
            except api.UbibotError:
                return None
            return await self.async_step_account_fallback()

        # Read-Key funktioniert -> Hinweis-Menü.
        self._pending_readkey = read_key
        return await self.async_step_account_hint()

    async def async_step_account_hint(self, user_input=None):
        """Hinweis: Account-Key erkannt, Channel-ID war nicht nötig."""
        return self.async_show_menu(
            step_id="account_hint",
            menu_options=["add_this_device", "pick_devices"],
            description_placeholders={"channel": str(self._pending_channel)},
        )

    async def async_step_add_this_device(self, user_input=None):
        """Nur das eine (per Account-Key erkannte) Gerät hinzufügen."""
        channel = self._pending_channel
        return self.async_create_entry(
            title=f"UbiBot {channel}",
            data={CONF_CHANNELS: {channel: {CONF_READ_KEY: self._pending_readkey}}},
        )

    async def async_step_pick_devices(self, user_input=None):
        """Doch alle Geräte auflisten (komfortabler Account-Key-Weg)."""
        try:
            self._channels = await api.async_list_channels(self.hass, self._account_key)
        except api.UbibotError:
            return self.async_abort(reason="cannot_connect")
        return await self.async_step_select()

    async def async_step_account_fallback(self, user_input=None):
        """Read-Key ging nicht, aber Account-Key-Abruf schon -> Fallback anbieten."""
        return self.async_show_menu(
            step_id="account_fallback",
            menu_options=["use_account_key", "cancel_setup"],
            description_placeholders={"channel": str(self._pending_channel)},
        )

    async def async_step_use_account_key(self, user_input=None):
        """Bewusst per Account-Key abfragen (unsicherer) – Nutzerentscheidung."""
        channel = self._pending_channel
        return self.async_create_entry(
            title=f"UbiBot {channel}",
            data={CONF_CHANNELS: {channel: {CONF_ACCOUNT_KEY: self._account_key}}},
        )

    async def async_step_cancel_setup(self, user_input=None):
        return self.async_abort(reason="cancelled")

    async def async_step_import(self, import_data):
        """YAML-Import der Alt-Integration (ms32035: sensor: - platform: ubibot).

        Der alte api_key ist ein Account-Key -> wird direkt gespeichert (kein
        API-Call beim Booten -> zuverlässig). Bereits konfigurierte Kanäle werden
        übersprungen, damit keine Duplikate entstehen.
        """
        channel = str(import_data.get(CONF_CHANNEL) or "").strip()
        api_key = import_data.get(CONF_API_KEY)
        if not channel or not api_key:
            return self.async_abort(reason="invalid_import")
        if channel in self._configured_channel_ids():
            return self.async_abort(reason="already_configured")

        scan_interval = import_data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        try:
            scan_interval = int(scan_interval)
        except (TypeError, ValueError):
            scan_interval = DEFAULT_SCAN_INTERVAL

        return self.async_create_entry(
            title=f"UbiBot {channel}",
            data={
                CONF_CHANNELS: {channel: {CONF_ACCOUNT_KEY: api_key}},
                CONF_SCAN_INTERVAL: scan_interval,
            },
        )

    # ------------------------------------------------------------------- reauth
    async def async_step_reauth(self, entry_data):
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Neuen Schlüssel abfragen und Read-Key(s) des Eintrags erneuern."""
        errors: dict[str, str] = {}
        entry = self._reauth_entry
        channels: dict[str, dict] = dict(entry.data.get(CONF_CHANNELS, {}))

        if user_input is not None:
            key_value = (user_input.get(CONF_API_KEY) or "").strip()
            if not key_value:
                errors[CONF_API_KEY] = "required"
            else:
                new_channels = await self._async_reauth_channels(
                    key_value, channels, errors
                )
                if new_channels is not None:
                    # Eintrag aktualisieren UND zuverlässig neu laden (kanonischer
                    # Reauth-Abschluss – lädt auch, wenn sich die Daten nicht ändern).
                    return self.async_update_reload_and_abort(
                        entry,
                        data={**entry.data, CONF_CHANNELS: new_channels},
                    )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
            description_placeholders={"channels": ", ".join(channels)},
        )

    async def _async_reauth_channels(
        self, key_value: str, channels: dict[str, dict], errors: dict[str, str]
    ) -> dict[str, dict] | None:
        """Read-Keys für einen Reauth erneuern. Gibt neue Channel-Daten oder None."""
        # Account-Key? -> Read-Keys für alle Kanäle neu beschaffen.
        try:
            await api.async_list_channels(self.hass, key_value)
            is_account = True
        except api.UbibotAuthError:
            # Definitiv kein Account-Key -> als Read-Key behandeln.
            is_account = False
        except api.UbibotError:
            # Verbindungs-/sonstiger Fehler -> nicht als Read-Key fehldeuten.
            errors["base"] = "cannot_connect"
            return None

        if is_account:
            try:
                new_channels: dict[str, dict] = {}
                for channel_id in channels:
                    read_key, _ = await api.async_provision_read_key(
                        self.hass, key_value, str(channel_id)
                    )
                    new_channels[str(channel_id)] = {CONF_READ_KEY: read_key}
                return new_channels
            except api.UbibotError:
                errors["base"] = "cannot_connect"
                return None

        # Kein Account-Key: nur als Read-Key für einen Einzel-Kanal-Eintrag zulässig.
        if len(channels) == 1:
            channel_id = next(iter(channels))
            try:
                await api.async_validate_read_key(self.hass, key_value, channel_id)
            except api.UbibotError:
                errors["base"] = "cannot_connect"
                return None
            return {channel_id: {CONF_READ_KEY: key_value}}

        # Read-Key für Mehr-Geräte-Eintrag reicht nicht.
        errors["base"] = "need_account_key"
        return None

    # ------------------------------------------------------------------ options
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return UbibotOptionsFlowHandler(config_entry)


class UbibotOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Geändertes Abrufintervall sofort übernehmen -> Eintrag neu laden.
            self.hass.config_entries.async_schedule_reload(self._entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        current = self._entry.options.get(
            CONF_SCAN_INTERVAL,
            self._entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current): vol.All(
                    vol.Coerce(int), vol.Range(min=60, max=3600)
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
