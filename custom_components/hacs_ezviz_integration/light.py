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
        return self.data.get("is_on")

    @property
    def available(self):
        """Connected/Disconnected state"""
        self.async_update()
        return self.data.get("status")==1

    async def async_turn_on(self, **kwargs):
        """Turn the light bulb on."""
        await self.hass.async_add_executor_job(self.api.turn_off, self.serial)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the light bulb off."""
        await self.hass.async_add_executor_job(self.api.turn_on, self.serial)
        self.async_write_ha_state()

    async def async_update(self):
        """Update the status of the lightbulb."""
        lights = await self.hass.async_add_executor_job(self.api.get_updated_light_bulbs)
        self.data = lights[self.serial]

