"""Hub for EcoWater account managing multiple devices."""
import logging
from typing import Dict, Optional

from iqua_softener import IquaSoftener, IquaSoftenerException

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class IquaHub:
    """Represents an EcoWater account (hub) that can manage multiple devices."""

    def __init__(self, hass: HomeAssistant, username: str, password: str) -> None:
        """Initialize the hub."""
        self.hass = hass
        self._username = username
        self._password = password
        self._devices: Dict[str, dict] = {}

    @property
    def username(self) -> str:
        """Return the username."""
        return self._username

    @property
    def password(self) -> str:
        """Return the password."""
        return self._password

    @property
    def devices(self) -> Dict[str, dict]:
        """Return discovered devices."""
        return self._devices

    async def async_setup(self) -> bool:
        """Set up the hub and discover devices."""
        try:
            # Verify credentials by creating IquaSoftener instance
            # API doesn't support list_devices(), so we use mock mode
            await self.hass.async_add_executor_job(
                self._verify_credentials
            )
            
            _LOGGER.info(
                "Hub setup successful for account %s (manual device mode)",
                self._username,
            )
            return True
        except IquaSoftenerException as err:
            _LOGGER.error("Failed to setup hub: %s", err)
            return False

    def _verify_credentials(self) -> None:
        """Verify credentials by attempting to create API instance."""
        # Create instance without serial to verify account exists
        # This will fail if credentials are wrong
        _ = IquaSoftener(self._username, self._password, None)
        # If we get here, credentials are valid

    async def async_get_device(self, device_serial: str) -> Optional[dict]:
        """
        Get specific device by serial number.
        
        Since API doesn't provide device list, this method fetches
        device data to verify it exists and is accessible.
        """
        if device_serial in self._devices:
            return self._devices[device_serial]
        
        # Try to fetch device data to verify it exists
        try:
            softener = IquaSoftener(self._username, self._password, device_serial)
            data = await self.hass.async_add_executor_job(softener.get_data)
            
            device_info = {
                'serial': device_serial,
                'model': data.model if hasattr(data, 'model') else 'iQua Water Softener',
                'firmware': getattr(data, 'firmware_version', None),
                'state': str(data.state.value) if hasattr(data, 'state') else 'Unknown',
            }
            
            self._devices[device_serial] = device_info
            _LOGGER.info(
                "Device %s added to hub: %s",
                device_serial,
                device_info['model']
            )
            return device_info
            
        except IquaSoftenerException as err:
            _LOGGER.error("Failed to get device %s: %s", device_serial, err)
            return None

    def get_softener_for_device(self, device_serial: str) -> IquaSoftener:
        """Get IquaSoftener instance for specific device."""
        return IquaSoftener(self._username, self._password, device_serial)

    async def async_remove_device(self, device_serial: str) -> None:
        """Remove device from hub cache."""
        if device_serial in self._devices:
            self._devices.pop(device_serial)
            _LOGGER.info("Device %s removed from hub", device_serial)
