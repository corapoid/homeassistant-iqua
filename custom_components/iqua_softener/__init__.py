"""iQua Water Softener integration with hub support."""
import logging

from homeassistant import config_entries, core
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from iqua_softener import IquaSoftener, IquaSoftenerException

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_SERIAL_NUMBER,
    CONF_IS_HUB,
    CONF_HUB_ID,
)
from .coordinator import IquaSoftenerCoordinator
from .hub import IquaHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up iQua Softener from a config entry."""
    
    # Get configuration
    config = dict(entry.data)
    if entry.options:
        config.update(entry.options)

    # Determine if this is a hub or device entry
    is_hub = config.get(CONF_IS_HUB, False)
    
    if is_hub:
        return await async_setup_hub(hass, entry, config)
    else:
        return await async_setup_device(hass, entry, config)


async def async_setup_hub(
    hass: core.HomeAssistant,
    entry: config_entries.ConfigEntry,
    config: dict,
) -> bool:
    """Set up hub (EcoWater account)."""
    
    # Create hub
    hub = IquaHub(
        hass,
        config[CONF_USERNAME],
        config[CONF_PASSWORD],
    )
    
    # Setup and verify credentials (also discovers devices)
    try:
        await hub.async_setup()
    except IquaSoftenerException as err:
        raise ConfigEntryNotReady(f"Unable to connect to hub: {err}") from err
    except Exception as err:
        _LOGGER.exception("Unexpected error during hub setup")
        raise ConfigEntryNotReady(f"Unexpected error: {err}") from err

    # Store hub in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "hub": hub,
        "devices": {},
        "unsub": entry.add_update_listener(options_update_listener),
    }
    
    _LOGGER.info(
        "Hub setup complete for account %s, discovered %d device(s)",
        config[CONF_USERNAME],
        len(hub.devices),
    )
    
    # Auto-create device entries for discovered devices
    for device_serial, device_info in hub.devices.items():
        # Check if device is already configured
        existing_entries = [
            e for e in hass.config_entries.async_entries(DOMAIN)
            if e.data.get(CONF_DEVICE_SERIAL_NUMBER) == device_serial
        ]
        
        if existing_entries:
            _LOGGER.debug("Device %s already configured, skipping", device_serial)
            continue
        
        # Create config entry for device
        _LOGGER.info(
            "Auto-adding device: %s (%s)",
            device_serial,
            device_info.get('model', 'Unknown'),
        )
        
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "auto_discovery"},
                data={
                    CONF_IS_HUB: False,
                    CONF_HUB_ID: entry.entry_id,
                    CONF_DEVICE_SERIAL_NUMBER: device_serial,
                    "device_info": device_info,
                },
            )
        )
    
    return True


async def async_setup_device(
    hass: core.HomeAssistant,
    entry: config_entries.ConfigEntry,
    config: dict,
) -> bool:
    """Set up device (water softener)."""
    
    # Get hub reference if device is linked to hub
    hub_id = config.get(CONF_HUB_ID)
    hub = None
    
    if hub_id and hub_id in hass.data.get(DOMAIN, {}):
        hub = hass.data[DOMAIN][hub_id]["hub"]
        _LOGGER.debug("Device linked to hub %s", hub_id)
    
    # Create coordinator
    if hub:
        # Device is part of hub - use hub credentials
        softener = hub.get_softener_for_device(config[CONF_DEVICE_SERIAL_NUMBER])
        coordinator = IquaSoftenerCoordinator(hass, softener)
    else:
        # Standalone device (legacy mode)
        coordinator = IquaSoftenerCoordinator(
            hass,
            IquaSoftener(
                config[CONF_USERNAME],
                config[CONF_PASSWORD],
                config[CONF_DEVICE_SERIAL_NUMBER],
            ),
        )

    # Validate connection BEFORE forwarding to platforms
    try:
        await coordinator.async_config_entry_first_refresh()
    except IquaSoftenerException as err:
        raise ConfigEntryNotReady(f"Unable to connect: {err}") from err
    except Exception as err:
        _LOGGER.exception("Unexpected error during device setup")
        raise ConfigEntryNotReady(f"Unexpected error: {err}") from err

    # Get device data for better device info
    device_data = coordinator.data

    # Register device in device registry
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, config[CONF_DEVICE_SERIAL_NUMBER])},
        manufacturer="EcoWater Systems",
        model=getattr(device_data, 'model', "iQua Water Softener"),
        name=entry.title or f"Water Softener {config[CONF_DEVICE_SERIAL_NUMBER][-6:]}",
        sw_version=getattr(device_data, 'firmware_version', None),
        suggested_area="Basement",
        via_device=(DOMAIN, hub_id) if hub_id else None,  # Link to hub
    )

    # Store coordinator and options listener
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "device_id": device_entry.id,
        "hub_id": hub_id,
        "unsub": entry.add_update_listener(options_update_listener),
    }
    
    # If linked to hub, also store in hub's devices dict
    if hub_id and hub_id in hass.data[DOMAIN]:
        hass.data[DOMAIN][hub_id]["devices"][entry.entry_id] = coordinator

    # Now safe to forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])
    
    _LOGGER.info(
        "Device setup complete for %s%s",
        config[CONF_DEVICE_SERIAL_NUMBER],
        f" (via hub {hub_id})" if hub_id else "",
    )
    
    return True


async def options_update_listener(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    
    config = dict(entry.data)
    is_hub = config.get(CONF_IS_HUB, False)
    
    if is_hub:
        # Unloading hub - also unload all devices
        if entry.entry_id in hass.data.get(DOMAIN, {}):
            hub_data = hass.data[DOMAIN][entry.entry_id]
            
            # Unload all linked devices
            for device_entry_id in list(hub_data.get("devices", {}).keys()):
                await hass.config_entries.async_unload(device_entry_id)
            
            # Cleanup hub
            hub_data["unsub"]()
            hass.data[DOMAIN].pop(entry.entry_id)
        
        return True
    else:
        # Unloading device
        unload_ok = await hass.config_entries.async_unload_platforms(
            entry, [Platform.SENSOR]
        )

        # Always cleanup, even if unload failed
        if entry.entry_id in hass.data.get(DOMAIN, {}):
            device_data = hass.data[DOMAIN][entry.entry_id]
            device_data["unsub"]()
            
            # Remove from hub's device list if applicable
            hub_id = device_data.get("hub_id")
            if hub_id and hub_id in hass.data.get(DOMAIN, {}):
                hass.data[DOMAIN][hub_id]["devices"].pop(entry.entry_id, None)
            
            if unload_ok:
                hass.data[DOMAIN].pop(entry.entry_id)

        return unload_ok
