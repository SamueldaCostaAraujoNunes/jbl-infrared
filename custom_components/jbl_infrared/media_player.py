"""Media player entity for the JBL soundbar."""

from typing import Any, override

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_INFRARED_ENTITY_ID, SOUND_MODES, SOURCES, JBLCode
from .entity import JblIrEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the media player when an emitter is configured."""
    if emitter := entry.data.get(CONF_INFRARED_ENTITY_ID):
        async_add_entities([JblIrMediaPlayer(entry, emitter)])


class JblIrMediaPlayer(JblIrEntity, InfraredEmitterConsumerEntity, MediaPlayerEntity):
    """JBL soundbar controlled over IR (state is assumed, never read back)."""

    _attr_name = None
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_assumed_state = True
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.SELECT_SOUND_MODE
    )
    _attr_source_list = list(SOURCES)
    _attr_sound_mode_list = list(SOUND_MODES)

    def __init__(self, entry: ConfigEntry, emitter_entity_id: str) -> None:
        """Initialize the media player."""
        super().__init__(entry, unique_id_suffix="media_player")
        self._infrared_emitter_entity_id = emitter_entity_id
        self._attr_state = MediaPlayerState.ON
        self._attr_is_volume_muted = False

    async def _send(self, code: JBLCode) -> None:
        await self._send_command(code.to_command())

    async def _toggle_power(self, target: MediaPlayerState) -> None:
        # The remote only has a power toggle: send it only when the assumed
        # state differs, so repeated calls do not flip the soundbar back.
        if self._attr_state != target:
            await self._send(JBLCode.POWER)
            self._attr_state = target
            self.async_write_ha_state()

    @override
    async def async_turn_on(self) -> None:
        await self._toggle_power(MediaPlayerState.ON)

    @override
    async def async_turn_off(self) -> None:
        await self._toggle_power(MediaPlayerState.OFF)

    @override
    async def async_volume_up(self) -> None:
        await self._send(JBLCode.VOLUME_UP)

    @override
    async def async_volume_down(self) -> None:
        await self._send(JBLCode.VOLUME_DOWN)

    @override
    async def async_mute_volume(self, mute: bool, **kwargs: Any) -> None:
        # Mute is a toggle on the remote, too.
        if self._attr_is_volume_muted != mute:
            await self._send(JBLCode.MUTE)
            self._attr_is_volume_muted = mute
            self.async_write_ha_state()

    # Play and pause share one toggle key on the remote.
    @override
    async def async_media_play(self) -> None:
        await self._send(JBLCode.PLAY_PAUSE)

    @override
    async def async_media_pause(self) -> None:
        await self._send(JBLCode.PLAY_PAUSE)

    @override
    async def async_media_play_pause(self) -> None:
        await self._send(JBLCode.PLAY_PAUSE)

    @override
    async def async_media_next_track(self) -> None:
        await self._send(JBLCode.NEXT)

    @override
    async def async_media_previous_track(self) -> None:
        await self._send(JBLCode.PREVIOUS)

    @override
    async def async_select_source(self, source: str) -> None:
        if (code := SOURCES.get(source)) is None:
            raise ServiceValidationError(f"Unknown source: {source}")
        await self._send(code)
        self._attr_source = source
        self.async_write_ha_state()

    @override
    async def async_select_sound_mode(self, sound_mode: str) -> None:
        if (code := SOUND_MODES.get(sound_mode)) is None:
            raise ServiceValidationError(f"Unknown sound mode: {sound_mode}")
        await self._send(code)
        self._attr_sound_mode = sound_mode
        self.async_write_ha_state()
