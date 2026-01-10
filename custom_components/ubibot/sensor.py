"""Ubibot sensor (async, coordinator-based)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import SENSOR_TYPES, MODELS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    channel: str = data["channel"]

    entities: list[UbibotSensor] = []
    for sensor_type in SENSOR_TYPES.keys():
        entities.append(UbibotSensor(coordinator, sensor_type, channel))

    async_add_entities(entities)


class UbibotSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Ubibot Sensor."""

    def __init__(self, coordinator, sensor_type: str, channel: str) -> None:
        super().__init__(coordinator)
        self._type = sensor_type
        self._channel = channel
        self._attr_name = f"Ubibot - {channel} - {sensor_type}"
        self._attr_unique_id = f"{channel}_{sensor_type}"
        # map device class and unit
        self._attr_device_class = SENSOR_TYPES[self._type]["class"]
        self._attr_native_unit_of_measurement = SENSOR_TYPES[self._type]["unit"]
        self._attr_icon = SENSOR_TYPES[self._type]["icon"]
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        data = self.coordinator.data
        if not data:
            return None
        try:
            return data["channel"]["last_values"][SENSOR_TYPES[self._type]["field"]][
                "value"
            ]
        except Exception as exc:
            _LOGGER.debug("Value read error: %s", exc)
            return None

    @property
    def device_info(self):
        data = self.coordinator.data or {}
        channel_info = data.get("channel", {})
        full_serial = channel_info.get("full_serial")
        product_id = channel_info.get("product_id")
        firmware = channel_info.get("firmware")
        return {
            "identifiers": {(DOMAIN, full_serial)} if full_serial else None,
            "name": full_serial,
            "manufacturer": "Ubibot",
            "model": MODELS.get(product_id, str(product_id)),
            "sw_version": firmware,
        }
