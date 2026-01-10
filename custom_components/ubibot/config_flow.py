from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_CHANNEL, DEFAULT_SCAN_INTERVAL, CONF_READ_KEY


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


class UbibotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Ubibot config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._auth_method: str = AUTH_METHOD_ACCOUNT

    async def async_step_user(self, user_input=None):
        errors = {}
        auth_selected = (user_input or {}).get("auth_method", self._auth_method)
        channel = (user_input or {}).get(CONF_CHANNEL)
        scan_interval = (user_input or {}).get("scan_interval", DEFAULT_SCAN_INTERVAL)
        key_value = (user_input or {}).get(CONF_API_KEY)

        if user_input is not None:
            self._auth_method = auth_selected
            if not channel:
                errors[CONF_CHANNEL] = "required"
            elif not key_value:
                errors[CONF_API_KEY] = "required"
            else:
                try:
                    await _async_validate_input(self.hass, auth_selected, key_value, channel)
                except Exception:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(str(channel))
                    self._abort_if_unique_id_configured()
                    data = {CONF_CHANNEL: channel, "scan_interval": scan_interval}
                    if auth_selected == AUTH_METHOD_ACCOUNT:
                        data[CONF_API_KEY] = key_value
                    else:
                        data[CONF_READ_KEY] = key_value
                    return self.async_create_entry(title=f"Ubibot {channel}", data=data)

        schema = vol.Schema({
            vol.Required("auth_method", default=self._auth_method): vol.In({AUTH_METHOD_ACCOUNT: "Account Key", AUTH_METHOD_READ: "Read Key"}),
            vol.Required(CONF_CHANNEL, default=channel or ""): str,
            vol.Required(CONF_API_KEY, default=key_value or ""): str,
            vol.Optional("scan_interval", default=scan_interval): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, user_input=None):
        # Falls YAML Import (Altbestand) vorhanden ist, mappe auf neuen Flow
        return await self.async_step_user(user_input)


class UbibotOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Options", data=user_input)

        current = self.config_entry.options.get("scan_interval", self.config_entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL))
        options_schema = vol.Schema({
            vol.Required("scan_interval", default=current): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)


def async_get_options_flow(config_entry: config_entries.ConfigEntry):
    return UbibotOptionsFlowHandler(config_entry)
