"""Custom integration for Ezviz lightbulbs for Home Assistant."""
from datetime import timedelta

from homeassistant.core import Config, HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_time_interval

from custom_components.hacs_ezviz_integration.api import EzvizAPI

from .const import DOMAIN
import logging

logging.basicConfig(
    filename='hacs_ezviz_integration.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

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

    async def refresh_token(_):
        try:
            _LOGGER.info("Refreshing Ezviz API token...")
            await hass.async_add_executor_job(api.refresh_token)
            _LOGGER.info("Token refreshed successfully.")
        except Exception as e:
            _LOGGER.error(f"Failed to refresh token: {e}")

    async_track_time_interval(hass, refresh_token, timedelta(hours=12))

    if api.get_light_bulbs():
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "light")
        )

    return True
