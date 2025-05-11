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
                    EP_LANINFO,
                    EP_TRAFFIC,
                    EP_COMMON)
from .coordinator import RouterCoordinator


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
        value_fn=lambda coordinator: coordinator.get_value(EP_CELLINFO, ["CellIntfInfo", "X_ZYXEL_CurrentBand"]),
        translation_key='network_band',
        entity_registry_enabled_default=False,
    ),
    RouterSensorDescription(
        key='wan_downloaded',
        icon='mdi:cloud-download',
        value_fn=lambda coordinator: coordinator.get_value(EP_TRAFFIC, ['ipIfaceSt', 1, 'BytesReceived']) \
            + coordinator.get_value(EP_TRAFFIC, ['ipIfaceSt', 2, 'BytesReceived']),
        native_unit_of_measurement='B',
        suggested_unit_of_measurement='GB',
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL,
        translation_key='wan_downloaded',
        entity_registry_enabled_default=False
    ),
    RouterSensorDescription(
        key='wan_uploaded',
        icon='mdi:cloud-upload',
        value_fn=lambda coordinator: coordinator.get_value(EP_TRAFFIC, ['ipIfaceSt', 1, 'BytesSent']) \
            + coordinator.get_value(EP_TRAFFIC, ['ipIfaceSt', 2, 'BytesSent']),
        native_unit_of_measurement='B',
        suggested_unit_of_measurement='GB',
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL,
        translation_key='wan_uploaded',
        entity_registry_enabled_default=False,
        
    ),
    RouterSensorDescription(
        key='eth1_downloaded',
        icon='mdi:download-network',
        # Reverse sent because the is what the router is sending to the port
        # thus what the port is downloading
        value_fn=lambda coordinator: coordinator.get_value(EP_TRAFFIC, ['ethIfaceSt', 0, 'BytesSent']),
        native_unit_of_measurement='B',
        suggested_unit_of_measurement='GB',
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL,
        translation_key='eth1_downloaded',
        entity_registry_enabled_default=False
    ),
    RouterSensorDescription(
        key='eth1_uploaded',
        icon='mdi:upload-network',
        # Reverse receive because the is what the router is receiving to the port
        # thus what the port is uploading
        value_fn=lambda coordinator: coordinator.get_value(EP_TRAFFIC, ['ethIfaceSt', 0, 'BytesReceived']),
        native_unit_of_measurement='B',
        suggested_unit_of_measurement='GB',
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL,
        translation_key='eth1_uploaded',
        entity_registry_enabled_default=False,
        
    ),
    RouterSensorDescription(
        key='eth2_downloaded',
        icon='mdi:download-network',
        # Reverse sent because the is what the router is sending to the port
        # thus what the port is downloading
        value_fn=lambda coordinator: coordinator.get_value(EP_TRAFFIC, ['ethIfaceSt', 1, 'BytesSent']),
        native_unit_of_measurement='B',
        suggested_unit_of_measurement='GB',
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL,
        translation_key='eth2_downloaded',
        entity_registry_enabled_default=False
    ),
    RouterSensorDescription(
        key='eth2_uploaded',
        icon='mdi:upload-network',
        # Reverse receive because the is what the router is receiving to the port
        # thus what the port is uploading
        value_fn=lambda coordinator: coordinator.get_value(EP_TRAFFIC, ['ethIfaceSt', 1, 'BytesReceived']),
        native_unit_of_measurement='B',
        suggested_unit_of_measurement='GB',
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL,
        translation_key='eth2_uploaded',
        entity_registry_enabled_default=False,
        
    ),
    RouterSensorDescription(
        key='wan_ip_address',
        icon='mdi:ip-network',
        value_fn=lambda coordinator: coordinator.get_value(EP_COMMON, ['WanLanInfo', 1, 'IPv4Address', 0, 'IPAddress']),
        translation_key='wan_ip_address',
        entity_registry_enabled_default=False
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
    coordinator = entry.runtime_data.coordinator
    #coordinator = hass.data[DOMAIN][entry.entry_id]

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


class RouterSensor(CoordinatorEntity[RouterCoordinator], SensorEntity):
    """Defines a Router sensor."""

    _attr_has_entity_name = True
    entity_description: RouterSensorDescription

    def __init__(
        self,
        conf_name: str,
        coordinator: RouterCoordinator,
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
    