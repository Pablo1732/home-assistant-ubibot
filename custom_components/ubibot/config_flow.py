from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_CHANNEL, DEFAULT_SCAN_INTERVAL, CONF_READ_KEY

_LOGGER = logging.getLogger(__name__)

AUTH_METHOD_ACCOUNT = "account_key"
AUTH_METHOD_READ = "read_key"


async def _async_validate_input(hass: HomeAssistant, auth_method: str, key_value: str, channel: str) -> None:
    """Validiere den angegebenen Schlüssel (Account oder Read) mit einem Probe-Request."""
    session = async_get_clientsession(hass)
    if auth_method == AUTH_METHOD_ACCOUNT:
        url = f"https://api.ubibot.io/channels/{channel}?account_key={key_value}"
    elif auth_method == AUTH_METHOD_READ:
        url = f"https://webapi.ubibot.com/channels/{channel}?api_key={key_value}"
    else:
        raise ValueError("invalid_auth_method")

    async with session.get(url, timeout=15) as resp:
        if resp.status != 200:
            raise ValueError(f"HTTP {resp.status}")


async def _async_detect_auth(hass: HomeAssistant, key_value: str, channel: str) -> str | None:
    """Erkenne automatisch, ob der Schlüssel ein Read- oder Account-Key ist.

    Probiert beide Endpoints durch; gibt die passende Methode zurück, oder None
    wenn keiner funktioniert (falscher Key/Channel oder keine Verbindung).
    """
    for method in (AUTH_METHOD_READ, AUTH_METHOD_ACCOUNT):
        try:
            await _async_validate_input(hass, method, key_value, channel)
            _LOGGER.debug("Ubibot: detected auth method '%s' for channel %s", method, channel)
            return method
        except Exception as exc:
            _LOGGER.debug("Ubibot: auth method '%s' failed for channel %s: %s", method, channel, exc)
            continue
    return None


class UbibotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Ubibot config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(self, user_input=None):
        errors = {}
        channel = (user_input or {}).get(CONF_CHANNEL)
        key_value = (user_input or {}).get(CONF_API_KEY)

        if user_input is not None:
            if not channel:
                errors[CONF_CHANNEL] = "required"
            elif not key_value:
                errors[CONF_API_KEY] = "required"
            else:
                # Key-Typ automatisch erkennen (Read- oder Account-Key)
                auth_method = await _async_detect_auth(self.hass, key_value, channel)
                if auth_method is None:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(str(channel))
                    self._abort_if_unique_id_configured()
                    data = {CONF_CHANNEL: channel, "scan_interval": DEFAULT_SCAN_INTERVAL}
                    if auth_method == AUTH_METHOD_ACCOUNT:
                        data[CONF_API_KEY] = key_value
                    else:
                        data[CONF_READ_KEY] = key_value
                    return self.async_create_entry(title=f"Ubibot {channel}", data=data)

        schema = vol.Schema({
            vol.Required(CONF_CHANNEL, default=channel or ""): str,
            vol.Required(CONF_API_KEY, default=key_value or ""): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, user_input=None):
        # Falls YAML Import (Altbestand) vorhanden ist, mappe auf neuen Flow
        return await self.async_step_user(user_input)

    async def async_step_reauth(self, entry_data):
        """Reauth gestartet (z. B. weil der Schlüssel ungültig wurde)."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Neuen Schlüssel abfragen und den bestehenden Eintrag aktualisieren."""
        errors = {}
        entry = self._reauth_entry
        channel = entry.data[CONF_CHANNEL]

        if user_input is not None:
            key_value = user_input.get(CONF_API_KEY)
            if not key_value:
                errors[CONF_API_KEY] = "required"
            else:
                # Key-Typ wieder automatisch erkennen
                auth_method = await _async_detect_auth(self.hass, key_value, channel)
                if auth_method is None:
                    errors["base"] = "cannot_connect"
                else:
                    # Alten Key durch neuen ersetzen (nur der erkannte Typ bleibt erhalten)
                    new_data = {
                        CONF_CHANNEL: channel,
                        "scan_interval": entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL),
                    }
                    if auth_method == AUTH_METHOD_ACCOUNT:
                        new_data[CONF_API_KEY] = key_value
                    else:
                        new_data[CONF_READ_KEY] = key_value
                    self.hass.config_entries.async_update_entry(entry, data=new_data)
                    await self.hass.config_entries.async_reload(entry.entry_id)
                    return self.async_abort(reason="reauth_successful")

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
        })
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=schema,
            errors=errors,
            description_placeholders={"channel": str(channel)},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return UbibotOptionsFlowHandler(config_entry)


class UbibotOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        # Nicht self.config_entry setzen (in neueren HA-Versionen deprecated),
        # sondern unter eigenem Namen ablegen.
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._entry.options.get(
            "scan_interval", self._entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        )
        options_schema = vol.Schema({
            vol.Required("scan_interval", default=current): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)
