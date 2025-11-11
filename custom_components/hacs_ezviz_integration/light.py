from homeassistant.components.light import LightEntity
import logging
from .const import DOMAIN
from .api import EzvizAPI

_LOGGER: logging.Logger = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Configure light entities from entry config."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api: EzvizAPI = data["api"]
    lights = api.get_light_bulbs()
    entities = [EzvizLight(light, lights[light], api) for light in lights.keys()]
    async_add_entities(entities)


class EzvizLight(LightEntity):
    """Ezviz Light HA adapter."""

    def __init__(self, serial, data: dict, api: EzvizAPI):
        self.serial = serial
        self.data = data
        self.api = api
        _LOGGER.debug("Initialized Ezviz light entity serial=%s name=%s", self.serial, self.data.get("name"))

    @property
    def unique_id(self):
        """Return a unique ID for this light."""
        return self.serial

    @property
    def name(self):
        """Name of the light."""
        return self.data.get("name")

    @property
    def is_on(self):
        """Light power state."""
        return self.data.get("is_on", self.data.get("status") == 1)

    @property
    def available(self):
        """Connected/Disconnected state"""
        return self.data.get("status") == 1

    async def async_turn_on(self, **kwargs):
        """Turn the light bulb on."""
        _LOGGER.debug("Turning ON light serial=%s", self.serial)
        try:
            await self.hass.async_add_executor_job(self.api.turn_on, self.serial)
        except Exception as err:
            _LOGGER.exception("Failed to turn on light serial=%s: %s", self.serial, err)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the light bulb off."""
        _LOGGER.debug("Turning OFF light serial=%s", self.serial)
        try:
            await self.hass.async_add_executor_job(self.api.turn_off, self.serial)
        except Exception as err:
            _LOGGER.exception("Failed to turn off light serial=%s: %s", self.serial, err)
        self.async_write_ha_state()

    async def async_update(self):
        """Update the status of the lightbulb."""
        _LOGGER.debug("Updating light state serial=%s", self.serial)
        try:
            lights = await self.hass.async_add_executor_job(self.api.get_updated_light_bulbs)
            self.data = lights[self.serial]
        except Exception as err:
            _LOGGER.warning("Failed to update light state serial=%s: %s", self.serial, err)

