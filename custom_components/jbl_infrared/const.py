"""Constants and IR codes for the JBL Infrared integration."""

from enum import IntEnum, StrEnum

from infrared_protocols.commands.nec import NECCommand

DOMAIN = "jbl_infrared"

CONF_MODEL = "model"
CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_INFRARED_RECEIVER_ENTITY_ID = "infrared_receiver_entity_id"


class JBLModel(StrEnum):
    """Soundbars that share the same remote."""

    SB120 = "SB120"
    SB140 = "SB140"
    SB160 = "SB160"
    SB170 = "SB170"
    SB190 = "SB190"


# NEC address of the JBL soundbar remote, in the same 16-bit format that
# NECCommand.from_raw_timings() returns (address_low | address_high << 8).
# Captured from the SB190 remote: "Received NEC: address=0xBD02".
JBL_ADDRESS = 0xBD02


class JBLCode(IntEnum):
    """NEC command bytes of the JBL soundbar remote (captured from an SB190).

    ESPHome logs the command as 16 bits, with the complement in the high byte
    (e.g. command=0xAC53); only the low byte goes here (0x53).
    """

    POWER = 0x53
    MUTE = 0xAD
    VOLUME_UP = 0x26
    VOLUME_DOWN = 0x28
    PREVIOUS = 0x25
    NEXT = 0x27
    PLAY_PAUSE = 0x0D
    SOURCE_HDMI_IN = 0x6C
    SOURCE_HDMI_ARC = 0x6D
    SOURCE_OPTICAL = 0x4D
    SOURCE_BLUETOOTH = 0x1B
    MODE_MUSIC = 0x20
    MODE_MOVIE = 0x08
    MODE_NEWS = 0x6B
    VOICE = 0x16
    DOLBY_ATMOS = 0x17
    BASS = 0x18

    def to_command(self) -> NECCommand:
        """Build the NEC command to transmit this code."""
        return NECCommand(address=JBL_ADDRESS, command=int(self))


# Event type and button translation key for each code (lowercase enum name).
CODE_TO_KEY: dict[JBLCode, str] = {code: code.name.lower() for code in JBLCode}

# Sources and sound modes exposed by the media player, as shown on the remote.
SOURCES: dict[str, JBLCode] = {
    "HDMI IN": JBLCode.SOURCE_HDMI_IN,
    "HDMI ARC": JBLCode.SOURCE_HDMI_ARC,
    "Optical": JBLCode.SOURCE_OPTICAL,
    "Bluetooth": JBLCode.SOURCE_BLUETOOTH,
}
SOUND_MODES: dict[str, JBLCode] = {
    "Music": JBLCode.MODE_MUSIC,
    "Movie": JBLCode.MODE_MOVIE,
    "News": JBLCode.MODE_NEWS,
}
