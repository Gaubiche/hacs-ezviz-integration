import logging
from typing import Optional, Any
from datetime import datetime, timedelta

from pyezvizapi import EzvizClient
from pyezvizapi import EzvizAuthVerificationCode
from pyezvizapi import EzvizLightBulb

_LOGGER: logging.Logger = logging.getLogger(__name__)

class EzvizAPI:
    def __init__(self, username: str, password: str, region: str = "apiieu.ezvizlife.com", debug: bool = False):
        self.username = username
        self.password = password
        self.region = region
        self.debug = debug
        self.client: Optional[EzvizClient] = None

    def connect(self):
        """Authentification to the EzViz servers."""
        _LOGGER.debug("Connection to EzViz servers")
        self.client = EzvizClient(self.username, self.password, self.region)
        try:
            self.client.login()
        except EzvizAuthVerificationCode:
            _LOGGER.debug("MFA code required")
            mfa_code = input("MFA code required, please input MFA code:\n")
            self.client.login(sms_code=mfa_code)
        except Exception as e:
            _LOGGER.error(f"Failed to log in: {e}")
            raise
        _LOGGER.debug("connected")
        self.token_creation_time = datetime.now()
        if self.debug:
            self._enable_debug_logging()

    def refresh_token(self):
        if datetime.now() >= self.token_creation_time + timedelta(hours=12):
            try:
                _LOGGER.info("Token update")
                self.client.login()
                self.token_creation_time = datetime.now()
                _LOGGER.info("Token updated")
            except Exception as e:
                _LOGGER.info("Token update failed")
                raise

    def load_devices(self):
        """Load devices managed by the specified account."""
        self.refresh_token()
        self.client.load_devices()

    def get_light_bulbs(self) -> Any:
        """Returns the fetched data of every device."""
        return self.client._light_bulbs

    def get_updated_light_bulbs(self) -> Any:
        """Fetch the data of every device and return."""
        self.refresh_token()
        self.client.get_device_infos()
        return self.client.load_light_bulbs()

    def get_light_bulb(self, serial: str) -> EzvizLightBulb:
        """Returns a connected lightbulb instance."""
        return EzvizLightBulb(self.client, serial)
    
    def is_light_bulb_on(self, serial: str) -> bool:
        """Returns the state of a lightbulb."""
        light_bulb = self.get_light_bulb(serial=serial)
        return light_bulb.status
    
    def toggle_light_bulb(self, serial: str) -> bool:
        """Change the state of a light bulb."""
        light_bulb = self.get_light_bulb(serial=serial)
        return light_bulb.toggle_switch()
    
    def turn_off(self, serial: str):
        """Turn off a light bulb."""
        self.toggle_light_bulb(serial)
        # self.get_light_bulb(serial=serial).power_off()

    def turn_on(self, serial: str):
        """Turn on a light bulb."""
        self.toggle_light_bulb(serial)
        # self.get_light_bulb(serial=serial).power_on()

    def close(self):
        """Close api session."""
        if self.client:
            self.client.close_session()
            self.client = None
