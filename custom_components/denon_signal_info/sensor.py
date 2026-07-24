"""Sensor platform for Denon Signal Info."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_MANUFACTURER, CONF_MODEL, DOMAIN
from .coordinator import DenonSignalInfoCoordinator


@dataclass(frozen=True, kw_only=True)
class DenonSignalSensorDescription(SensorEntityDescription):
    """Describe a Denon signal information sensor."""


SENSORS: tuple[DenonSignalSensorDescription, ...] = (
    DenonSignalSensorDescription(
        key="sample_rate",
        translation_key="sample_rate",
        icon="mdi:sine-wave",
    ),
    DenonSignalSensorDescription(
        key="input_signal",
        translation_key="input_signal",
        icon="mdi:audio-input-stereo-minijack",
    ),
    DenonSignalSensorDescription(
        key="audio_format",
        translation_key="audio_format",
        icon="mdi:surround-sound",
    ),
    DenonSignalSensorDescription(
        key="sound_mode",
        translation_key="sound_mode",
        icon="mdi:speaker-multiple",
    ),
    DenonSignalSensorDescription(
        key="hdmi_resolution",
        translation_key="hdmi_resolution",
        icon="mdi:video-high-definition",
    ),
    DenonSignalSensorDescription(
        key="hdr",
        translation_key="hdr",
        icon="mdi:brightness-7",
    ),
    DenonSignalSensorDescription(
        key="color_space",
        translation_key="color_space",
        icon="mdi:palette",
    ),
    DenonSignalSensorDescription(
        key="pixel_depth",
        translation_key="pixel_depth",
        icon="mdi:gradient-horizontal",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Denon signal sensors."""
    coordinator: DenonSignalInfoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DenonSignalSensor(coordinator, entry, description)
        for description in SENSORS
    )


class DenonSignalSensor(
    CoordinatorEntity[DenonSignalInfoCoordinator], SensorEntity
):
    """Representation of one Denon signal sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DenonSignalInfoCoordinator,
        entry: ConfigEntry,
        description: DenonSignalSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            name=entry.title,
            manufacturer=entry.data.get(CONF_MANUFACTURER, "Denon"),
            model=entry.data.get(CONF_MODEL),
            sw_version=coordinator.data.get("firmware_version"),
            configuration_url=coordinator.api.configuration_url,
        )

    @property
    def native_value(self) -> Any:
        """Return the current sensor value."""
        return self.coordinator.data.get(self.entity_description.key)
