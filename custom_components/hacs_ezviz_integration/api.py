import logging
from typing import Optional, Any
from datetime import datetime, timedelta

from pyezvizapi import EzvizClient
from pyezvizapi import EzvizAuthVerificationCode
from pyezvizapi import EzvizLightBulb, EzvizSmartPlug

_LOGGER: logging.Logger = logging.getLogger(__name__)

class EzvizAPI:
    def __init__(self, username: str, password: str, region: str = "apiieu.ezvizlife.com", debug: bool = False):
        self.username = username
        self.password = password
        self.region = region
        self.debug = debug
        self.client: Optional[EzvizClient] = None
        self.token_creation_time: Optional[datetime] = None

    def connect(self):
        """Authentification to the EzViz servers."""
        _LOGGER.debug("Connecting to Ezviz servers region=%s", self.region)
        self.client = EzvizClient(self.username, self.password, self.region)
        try:
            self.client.login()
        except EzvizAuthVerificationCode:
            _LOGGER.error("MFA required for Ezviz account; interactive MFA not supported in Home Assistant")
            raise
        except Exception as e:
            _LOGGER.exception("Failed to log in to Ezviz: %s", e)
            raise
        _LOGGER.info("Connected to Ezviz")
        self.token_creation_time = datetime.now()
        if self.debug:
            self._enable_debug_logging()

    def refresh_token(self):
        if self.token_creation_time and datetime.now() >= self.token_creation_time + timedelta(hours=12):
            try:
                _LOGGER.info("Refreshing Ezviz token")
                self.client._token["session_id"] = None # a bit hacky but the refresh token method can crash
                self.client.login()
                self.token_creation_time = datetime.now()
                _LOGGER.info("Ezviz token refreshed")
            except Exception as e:
                _LOGGER.exception("Token refresh failed: %s", e)
                raise

    def load_devices(self):
        """Load devices managed by the specified account."""
        self.client.load_devices()
        try:
            count = len(self.client._light_bulbs or {})
        except Exception:
            count = 0
        _LOGGER.debug("Loaded Ezviz devices: light_bulbs=%s", count)

    def get_light_bulbs(self) -> Any:
        """Returns the fetched data of every device."""
        return self.client._light_bulbs

    def get_smart_plugs(self) -> Any:
        """Returns the fetched data of every device."""
        return self.client._smart_plugs

    def get_updated_light_bulbs(self) -> Any:
        """Fetch the data of every device and return."""
        _LOGGER.debug("Fetching updated light bulb states")
        self.client.get_device_infos()
        bulbs = self.client.load_light_bulbs()
        _LOGGER.debug("Fetched %s light bulbs", len(bulbs or {}))
        return bulbs

    def get_light_bulb(self, serial: str) -> EzvizLightBulb:
        """Returns a connected lightbulb instance."""
        return EzvizLightBulb(self.client, serial)

    def get_smart_plug(self, serial: str) -> EzvizSmartPlug:
        """Returns a connected lightbulb instance."""
        return EzvizSmartPlug(self.client, serial)

    def is_light_bulb_on(self, serial: str) -> bool:
        """Returns the state of a lightbulb."""
        light_bulb = self.get_light_bulb(serial=serial)
        return light_bulb.status

    def toggle_light_bulb(self, serial: str) -> bool:
        """Change the state of a light bulb."""
        light_bulb = self.get_light_bulb(serial=serial)
        _LOGGER.debug("Toggling light serial=%s", serial)
        result = light_bulb.toggle_switch()
        _LOGGER.debug("Toggled light serial=%s result=%s", serial, result)
        return result

    def turn_off(self, serial: str):
        """Turn off a light bulb."""
        _LOGGER.debug("Turning OFF light via API serial=%s", serial)
        light_bulb = self.get_light_bulb(serial=serial)
        light_bulb.power_off()

    def turn_on(self, serial: str):
        """Turn on a light bulb."""
        _LOGGER.debug("Turning ON light via API serial=%s", serial)
        light_bulb = self.get_light_bulb(serial=serial)
        light_bulb.power_on()

    def set_brightness(self, serial: str, brightness):
        """Sets the brightness of a light bulb."""
        _LOGGER.debug("Setting the brightness of %s to %s", serial, brightness)
        light_bulb = self.get_light_bulb(serial=serial)
        light_bulb.set_brightness(brightness)

    def close(self):
        """Close api session."""
        if self.client:
            self.client.close_session()
            self.client = None
