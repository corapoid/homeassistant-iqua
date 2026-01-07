"""Diagnostics support for iQua Softener."""
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_IS_HUB, CONF_USERNAME, CONF_DEVICE_SERIAL_NUMBER


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    
    data = hass.data[DOMAIN][entry.entry_id]
    is_hub = entry.data.get(CONF_IS_HUB, False)
    
    if is_hub:
        # Hub diagnostics
        hub = data["hub"]
        
        return {
            "type": "hub",
            "username": entry.data[CONF_USERNAME],
            "devices_count": len(hub.devices),
            "devices": [
                {
                    "serial": device_serial,
                    "model": device_info.get("model"),
                    "state": device_info.get("state"),
                }
                for device_serial, device_info in hub.devices.items()
            ],
        }
    else:
        # Device diagnostics
        coordinator = data["coordinator"]
        
        diagnostics_data = {
            "type": "device",
            "serial": entry.data[CONF_DEVICE_SERIAL_NUMBER],
            "hub_id": data.get("hub_id"),
            "coordinator": {
                "last_update_success": coordinator.last_update_success,
                "last_update_time": coordinator.last_update_success_time.isoformat()
                if coordinator.last_update_success_time
                else None,
                "update_interval": str(coordinator.update_interval),
            },
        }
        
        # Add device data if available
        if coordinator.data:
            device_data = coordinator.data
            diagnostics_data["device_data"] = {
                "state": str(device_data.state.value) if hasattr(device_data, 'state') else None,
                "salt_level": device_data.salt_level_percent if hasattr(device_data, 'salt_level_percent') else None,
                "device_date_time": device_data.device_date_time.isoformat() if hasattr(device_data, 'device_date_time') else None,
                "volume_unit": str(device_data.volume_unit.value) if hasattr(device_data, 'volume_unit') else None,
                "model": getattr(device_data, 'model', None),
                "firmware": getattr(device_data, 'firmware_version', None),
                "total_water_available": getattr(device_data, 'total_water_available', None),
                "current_water_flow": getattr(device_data, 'current_water_flow', None),
                "today_use": getattr(device_data, 'today_use', None),
                "average_daily_use": getattr(device_data, 'average_daily_use', None),
            }
        
        return diagnostics_data
