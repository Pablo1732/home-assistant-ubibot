from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_CHANNEL, DEFAULT_SCAN_INTERVAL


async def _async_validate_input(hass: HomeAssistant, api_key: str, channel: str) -> None:
    """Validiere API-Key und Channel mit einem Probe-Request."""
    session = async_get_clientsession(hass)
    url = f"https://api.ubibot.io/channels/{channel}?account_key={api_key}"
    async with session.get(url, timeout=15) as resp:
        if resp.status != 200:
            raise ValueError(f"HTTP {resp.status}")


class UbibotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Ubibot config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            api_key = user_input.get(CONF_API_KEY)
            channel = user_input.get(CONF_CHANNEL)
            try:
                await _async_validate_input(self.hass, api_key, channel)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(str(channel))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"Ubibot {channel}", data={
                    CONF_API_KEY: api_key,
                    CONF_CHANNEL: channel,
                })

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_CHANNEL): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_import(self, user_input=None):
        # Falls YAML Import (Altbestand) vorhanden ist, mappe auf neuen Flow
        return await self.async_step_user(user_input)

    def async_get_options_flow(self, config_entry):
        return UbibotOptionsFlowHandler(config_entry)


class UbibotOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Options", data=user_input)

        options_schema = vol.Schema({
            vol.Required("scan_interval", default=self.config_entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)):
                vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)
