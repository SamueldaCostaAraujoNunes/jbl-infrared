"""Event entity that reports keys pressed on the physical JBL remote."""

import logging
from typing import override

from infrared_protocols.commands.nec import NECCommand

from homeassistant.components.event import EventEntity
from homeassistant.components.infrared import (
    InfraredReceivedSignal,
    InfraredReceiverConsumerEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CODE_TO_KEY, CONF_INFRARED_RECEIVER_ENTITY_ID, JBL_ADDRESS, JBLCode
from .entity import JblIrEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0

EVENT_TYPE_UNKNOWN = "unknown"
EVENT_TYPES = [*CODE_TO_KEY.values(), EVENT_TYPE_UNKNOWN]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the event entity when a receiver is configured."""
    if receiver := entry.data.get(CONF_INFRARED_RECEIVER_ENTITY_ID):
        async_add_entities([JblIrReceivedCommandEvent(entry, receiver)])


class JblIrReceivedCommandEvent(JblIrEntity, InfraredReceiverConsumerEntity, EventEntity):
    """Fires an event for every key received from the JBL remote."""

    _attr_translation_key = "received_command"
    _attr_event_types = EVENT_TYPES

    def __init__(self, entry: ConfigEntry, receiver_entity_id: str) -> None:
        """Initialize the event entity."""
        super().__init__(entry, unique_id_suffix="received_command")
        self._infrared_receiver_entity_id = receiver_entity_id

    @override
    @callback
    def _handle_signal(self, signal: InfraredReceivedSignal) -> None:
        nec = NECCommand.from_raw_timings(signal.timings)
        if nec is None:
            return

        # Logged for every NEC signal, so the codes of the real remote can be
        # captured by enabling debug logging for this integration.
        _LOGGER.debug(
            "NEC received: address=0x%04X command=0x%02X", nec.address, nec.command
        )
        if nec.address != JBL_ADDRESS:
            return

        try:
            event_type = CODE_TO_KEY[JBLCode(nec.command)]
        except ValueError:
            event_type = EVENT_TYPE_UNKNOWN

        self._trigger_event(event_type, {"command": f"0x{nec.command:02X}"})
        self.async_write_ha_state()
