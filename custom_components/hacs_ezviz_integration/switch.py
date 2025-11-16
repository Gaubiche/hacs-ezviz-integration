from homeassistant.components.switch import SwitchEntity
import logging
from .const import DOMAIN
from .api import EzvizAPI

_LOGGER: logging.Logger = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Configure plug entities from entry config."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api: EzvizAPI = data["api"]
    plugs = api.get_smart_plugs()
    entities = [EzvizSmartPlug(plug, plugs[plug], api) for plug in plugs.keys()]
    async_add_entities(entities)


class EzvizSmartPlug(SwitchEntity):
    """Ezviz smart plugs HA adapter."""

    def __init__(self, serial, data:dict, api: EzvizAPI):
        self.serial = serial
        self.data = data
        self.api = api
        self.handle = None
        self.status = None
        _LOGGER.debug("Initialized Ezviz smart plug entity serial=%s name=%s", self.serial, self.data.get("name"))

    @property
    def unique_id(self):
        """Return a unique ID for this plug."""
        return self.serial

    @property
    def name(self):
        """Name of the plug."""
        if not self.status:
            return self.data.get("name")
        return self.status["name"]

    @property
    def is_on(self):
        """Plug power state."""
        if not self.status:
            return False
        return self.status["is_on"]

    @property
    def available(self):
        """Connected/Disconnected state"""
        if not self.status:
            return False
        return self.status["status"]

    async def async_turn_on(self, **kwargs):
        """Turn the plug bulb on."""
        _LOGGER.debug("Turning ON plug serial=%s", self.serial)
        try:
            await self.hass.async_add_executor_job(self.handle.power_on)
        except Exception as err:
            _LOGGER.exception("Failed to turn on plug serial=%s: %s", self.serial, err)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the plug bulb off."""
        _LOGGER.debug("Turning OFF plug serial=%s", self.serial)
        try:
            await self.hass.async_add_executor_job(self.handle.power_off)
        except Exception as err:
            _LOGGER.exception("Failed to turn off plug serial=%s: %s", self.serial, err)
        self.async_write_ha_state()

    async def async_update(self):
        """Update the status of the plug."""
        _LOGGER.debug("Updating plug state serial=%s", self.serial)
        try:
            self.handle = await self.hass.async_add_executor_job(self.api.get_smart_plug, self.serial)
            self.status = self.handle.status()
        except Exception as err:
            _LOGGER.warning("Failed to update plug state serial=%s: %s", self.serial, err)

