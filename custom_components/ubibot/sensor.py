"""Ubibot sensor (async, coordinator-based)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import SENSOR_TYPES, MODELS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinators = hass.data[DOMAIN][entry.entry_id]["coordinators"]

    entities: list[UbibotSensor] = []
    # Ein Eintrag kann mehrere Kanäle (Geräte) enthalten.
    for channel_id, coordinator in coordinators.items():
        for sensor_type in SENSOR_TYPES:
            entities.append(UbibotSensor(coordinator, sensor_type, str(channel_id)))

    async_add_entities(entities)


class UbibotSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Ubibot Sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, sensor_type: str, channel: str) -> None:
        super().__init__(coordinator)
        self._type = sensor_type
        self._channel = channel
        cfg = SENSOR_TYPES[sensor_type]
        # Name kommt aus den Übersetzungen (entity.sensor.<key>.name)
        self._attr_translation_key = sensor_type
        self._attr_unique_id = f"{channel}_{sensor_type}"
        self._attr_device_class = cfg["class"]
        self._attr_native_unit_of_measurement = cfg["unit"]
        self._attr_icon = cfg["icon"]
        self._attr_state_class = SensorStateClass.MEASUREMENT
        if cfg.get("category") == "diagnostic":
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        # Letzter API-Abruf fehlgeschlagen -> unavailable
        if not self.coordinator.last_update_success:
            return False
        channel = (self.coordinator.data or {}).get("channel", {})
        # Gerät laut UbiBot-Cloud offline (net == "0") -> Entität unavailable,
        # damit HA nicht am letzten (evtl. wochenalten) Wert festhängt.
        if str(channel.get("net")) == "0":
            return False
        last_values = channel.get("last_values", {})
        field = SENSOR_TYPES[self._type]["field"]
        return field in last_values and last_values.get(field) is not None

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
    def device_info(self) -> DeviceInfo:
        channel_info = (self.coordinator.data or {}).get("channel", {})
        full_serial = channel_info.get("full_serial")
        product_id = channel_info.get("product_id")
        # Immer eine gültige Identifier-Menge: bevorzugt Seriennummer,
        # sonst die (stets vorhandene) Channel-ID -> kein "identifiers: None".
        name = channel_info.get("name") or full_serial or f"Ubibot {self._channel}"
        return DeviceInfo(
            identifiers={(DOMAIN, full_serial or self._channel)},
            name=name,
            manufacturer="Ubibot",
            model=MODELS.get(product_id, str(product_id) if product_id else None),
            serial_number=full_serial,
            sw_version=channel_info.get("firmware"),
        )
