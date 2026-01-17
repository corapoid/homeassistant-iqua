"""Hub for EcoWater account managing multiple devices."""
import logging
from typing import Dict, List, Optional

import requests

from iqua_softener import IquaSoftener, IquaSoftenerException

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://apioem.ecowater.com/v1"
USER_AGENT = "okhttp/3.12.1"


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
            # Authenticate and discover devices
            devices = await self.hass.async_add_executor_job(
                self._authenticate_and_list_devices
            )
            
            # Store discovered devices
            for device in devices:
                self._devices[device['serial']] = device
            
            _LOGGER.info(
                "Hub setup successful for account %s, found %d device(s)",
                self._username,
                len(devices),
            )
            return True
        except IquaSoftenerException as err:
            _LOGGER.error("Failed to setup hub: %s", err)
            raise

    def _authenticate_and_list_devices(self) -> List[dict]:
        """Authenticate and fetch list of devices from EcoWater API."""
        session = requests.Session()
        headers = {"User-Agent": USER_AGENT, "Content-Type": "application/json"}
        
        # Authenticate
        try:
            auth_response = session.post(
                f"{API_BASE_URL}/auth/signin",
                json={"username": self._username, "password": self._password},
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.Timeout:
            raise IquaSoftenerException("Connection timeout - server not responding")
        except requests.exceptions.ConnectionError:
            raise IquaSoftenerException("Cannot connect to EcoWater servers")
        except requests.exceptions.RequestException as err:
            raise IquaSoftenerException(f"Connection error: {err}")
        
        if auth_response.status_code == 401:
            raise IquaSoftenerException("Authentication error: Invalid username or password")
        if auth_response.status_code == 502:
            raise IquaSoftenerException("Server unavailable (502) - try again later")
        if auth_response.status_code != 200:
            raise IquaSoftenerException(f"Authentication failed: HTTP {auth_response.status_code}")
        
        try:
            auth_data = auth_response.json()
        except ValueError:
            raise IquaSoftenerException("Invalid response from server")
            
        if auth_data.get("code") != "OK":
            raise IquaSoftenerException(f"Authentication failed: {auth_data.get('message')}")
        
        token = auth_data["data"]["token"]
        token_type = auth_data["data"]["tokenType"]
        
        # Fetch devices list
        headers["Authorization"] = f"{token_type} {token}"
        try:
            devices_response = session.get(
                f"{API_BASE_URL}/system",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as err:
            raise IquaSoftenerException(f"Failed to fetch devices: {err}")
        
        if devices_response.status_code != 200:
            raise IquaSoftenerException(f"Failed to fetch devices: HTTP {devices_response.status_code}")
        
        try:
            devices_data = devices_response.json()
        except ValueError:
            raise IquaSoftenerException("Invalid response when fetching devices")
            
        if devices_data.get("code") != "OK":
            raise IquaSoftenerException(f"Failed to fetch devices: {devices_data.get('message')}")
        
        # Parse devices
        devices = []
        for device in devices_data.get("data", []):
            devices.append({
                'serial': device.get('serialNumber'),
                'nickname': device.get('nickname', 'Device'),
                'model': device.get('modelDescription', 'Water Softener'),
                'model_id': device.get('modelName'),
                'system_type': device.get('systemType'),
                'product_image': device.get('productImage'),
            })
        
        return devices

    async def async_discover_devices(self) -> List[dict]:
        """Discover devices (can be called to refresh device list)."""
        devices = await self.hass.async_add_executor_job(
            self._authenticate_and_list_devices
        )
        
        # Update stored devices
        for device in devices:
            self._devices[device['serial']] = device
        
        return devices

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
