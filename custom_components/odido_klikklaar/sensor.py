"""Sensor platform for knmi."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    PERCENTAGE,
    UnitOfSoundPressure,
    UnitOfDataRate
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (DOMAIN,
                    EP_CELLINFO,
                    EP_DEVICESTATUS,
                    EP_LANINFO)
from .coordinator import RouterDataUpdateCoordinator


@dataclass(kw_only=True, frozen=True)
class RouterSensorDescription(SensorEntityDescription):
    """Class describing Router sensor entities."""

    value_fn: Callable[[dict[str, Any]], StateType | datetime | None]
    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] = lambda _: {}


DESCRIPTIONS: list[RouterSensorDescription] = [
    RouterSensorDescription(
        key='rssi',
        icon='mdi:wifi-check',
        value_fn=lambda coordinator: coordinator.get_value(EP_CELLINFO, ["CellIntfInfo", "RSSI"]),
        native_unit_of_measurement=UnitOfSoundPressure.WEIGHTED_DECIBEL_A,
        device_class=SensorDeviceClass.SOUND_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key='rssi',
        entity_registry_enabled_default=True,
    ),
    RouterSensorDescription(
        key='rsrq',
        icon='mdi:wifi-arrow-up-down',
        value_fn=lambda coordinator: coordinator.get_value(EP_CELLINFO, ["CellIntfInfo", "X_ZYXEL_RSRQ"]),
        native_unit_of_measurement=UnitOfSoundPressure.DECIBEL,
        device_class=SensorDeviceClass.SOUND_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key='rsrq',
        entity_registry_enabled_default=False
    ),
    RouterSensorDescription(
        key='rsrp',
        icon='mdi:wifi-arrow-down',
        value_fn=lambda coordinator: coordinator.get_value(EP_CELLINFO, ["CellIntfInfo", "X_ZYXEL_RSRP"]),
        native_unit_of_measurement=UnitOfSoundPressure.WEIGHTED_DECIBEL_A,
        device_class=SensorDeviceClass.SOUND_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key='rsrp',
        entity_registry_enabled_default=False
    ),
    RouterSensorDescription(
        key='sinr',
        icon='mdi:wifi-alert',
        value_fn=lambda coordinator: coordinator.get_value(EP_CELLINFO, ["CellIntfInfo", "X_ZYXEL_SINR"]),
        state_class=SensorStateClass.MEASUREMENT,
        translation_key='sinr',
        entity_registry_enabled_default=False
    ),
    RouterSensorDescription(
        key='network_technology',
        icon='mdi:radio-tower',
        value_fn=lambda coordinator: coordinator.get_value(EP_CELLINFO, ["CellIntfInfo", "CurrentAccessTechnology"]),
        translation_key='network_technology',
        entity_registry_enabled_default=True
    ),
    RouterSensorDescription(
        key='network_band',
        icon='mdi:signal-5g',
        value_fn=lambda coordinator: coordinator.get_value(EP_CELLINFO, ["CellIntfInfo", "CurrentAccessTechnology"]),
        translation_key='network_band',
        entity_registry_enabled_default=False,
    ),
    # RouterSensorDescription(
    #     key='network_devices',
    #     state_class=SensorStateClass.MEASUREMENT,
    #     translation_key='network_devices',
    #     entity_registry_enabled_default=True
    # )
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Router sensors based on a config entry."""
    conf_name = entry.data.get(CONF_NAME)
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[RouterSensor] = []

    # Add all sensors described above.
    for description in DESCRIPTIONS:
        entities.append(
            RouterSensor(
                conf_name=conf_name,
                coordinator=coordinator,
                description=description,
            )
        )

    async_add_entities(entities)


class RouterSensor(CoordinatorEntity[RouterDataUpdateCoordinator], SensorEntity):
    """Defines a Router sensor."""

    _attr_has_entity_name = True
    entity_description: RouterSensorDescription

    def __init__(
        self,
        conf_name: str,
        coordinator: RouterDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize Router sensor."""
        super().__init__(coordinator=coordinator)

        #self._attr_attribution = self.coordinator.get_value(["api", 0, "bron"])
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{conf_name}_{description.key}".lower()

        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the state."""
        return self.entity_description.value_fn(self.coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return self.entity_description.attr_fn(self.coordinator)
    