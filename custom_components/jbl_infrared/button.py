"""Buttons that send single JBL remote commands."""

from typing import override

from homeassistant.components.button import ButtonEntity
from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CODE_TO_KEY, CONF_INFRARED_ENTITY_ID, JBLCode
from .entity import JblIrEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up one button per remote key when an emitter is configured."""
    if emitter := entry.data.get(CONF_INFRARED_ENTITY_ID):
        async_add_entities(JblIrButton(entry, emitter, code) for code in JBLCode)


class JblIrButton(JblIrEntity, InfraredEmitterConsumerEntity, ButtonEntity):
    """A single key of the JBL remote."""

    def __init__(self, entry: ConfigEntry, emitter_entity_id: str, code: JBLCode) -> None:
        """Initialize the button."""
        key = CODE_TO_KEY[code]
        super().__init__(entry, unique_id_suffix=f"button_{key}")
        self._infrared_emitter_entity_id = emitter_entity_id
        self._attr_translation_key = key
        self._code = code

    @override
    async def async_press(self) -> None:
        await self._send_command(self._code.to_command())
