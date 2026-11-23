"""Config flow for the JBL Infrared integration."""

from typing import Any

import voluptuous as vol

from homeassistant.components import infrared
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_INFRARED_ENTITY_ID,
    CONF_INFRARED_RECEIVER_ENTITY_ID,
    CONF_MODEL,
    DOMAIN,
    JBLModel,
)


class JblIrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up a JBL soundbar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick the model and the infrared emitter and/or receiver."""
        emitters = list(infrared.async_get_emitters(self.hass))
        receivers = list(infrared.async_get_receivers(self.hass))
        if not emitters and not receivers:
            return self.async_abort(reason="no_infrared_entities")

        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input.get(CONF_INFRARED_ENTITY_ID) and not user_input.get(
                CONF_INFRARED_RECEIVER_ENTITY_ID
            ):
                errors["base"] = "missing_infrared_entity"
            else:
                return self.async_create_entry(
                    title=f"JBL {user_input[CONF_MODEL]}", data=user_input
                )

        schema: dict[Any, Any] = {
            vol.Required(CONF_MODEL, default=JBLModel.SB190): SelectSelector(
                SelectSelectorConfig(
                    options=[model.value for model in JBLModel],
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
        }
        if emitters:
            schema[vol.Optional(CONF_INFRARED_ENTITY_ID)] = EntitySelector(
                EntitySelectorConfig(domain="infrared", include_entities=emitters)
            )
        if receivers:
            schema[vol.Optional(CONF_INFRARED_RECEIVER_ENTITY_ID)] = EntitySelector(
                EntitySelectorConfig(domain="infrared", include_entities=receivers)
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(schema), user_input
            ),
            errors=errors,
        )
