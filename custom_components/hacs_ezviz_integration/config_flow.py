from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN, CONF_USER, CONF_PASSWORD  # Assurez-vous que ces constantes sont définies dans const.py

class EzvizConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for Ezviz integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Configuration flow initiated by the user."""
        errors = {}

        if user_input is not None:
            username = user_input.get(CONF_USER)
            password = user_input.get(CONF_PASSWORD)

            if not username or not password:
                errors["base"] = "invalid_auth"
            else:
                return self.async_create_entry(
                    title="Ezviz",
                    data=user_input
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USER): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Options flow getter for ezviz integration."""
        return EzvizOptionsFlow(config_entry)


class EzvizOptionsFlow(config_entries.OptionsFlow):
    """Options flow for ezviz integration."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle origin options. Just a template for now"""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self._config_entry, options=user_input
            )
            return self.async_create_entry(title="", data={})

        options_schema = vol.Schema(
            {
                vol.Optional("example_option", default=self._config_entry.options.get("example_option", True)): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
