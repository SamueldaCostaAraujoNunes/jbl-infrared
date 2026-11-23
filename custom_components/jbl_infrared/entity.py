"""Base entity for the JBL Infrared integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import CONF_MODEL, DOMAIN


class JblIrEntity(Entity):
    """Common device info and unique ID for all JBL entities."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, unique_id_suffix: str) -> None:
        """Initialize the entity."""
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="JBL",
            model=entry.data[CONF_MODEL],
            name=entry.title,
        )
