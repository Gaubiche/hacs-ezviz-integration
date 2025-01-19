"""Custom integration for Ezviz lightbulbs for Home Assistant."""
from homeassistant.core import Config, HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.hacs_ezviz_integration.api import EzvizAPI

from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Conf via UI only"""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuration via UI"""
    hass.data.setdefault(DOMAIN, {})
    api = EzvizAPI(entry.data["username"], entry.data["password"])
    await hass.async_add_executor_job(api.connect)
    await hass.async_add_executor_job(api.load_devices)

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api
    }

    if api.get_light_bulbs():
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "light")
        )

    return True
