import logging

from homeassistant import config_entries, core
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady

from iqua_softener import IquaSoftener, IquaSoftenerException

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_DEVICE_SERIAL_NUMBER
from .coordinator import IquaSoftenerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up iQua Softener from a config entry."""
    # Get configuration
    config = dict(entry.data)
    if entry.options:
        config.update(entry.options)

    # Create coordinator
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
        _LOGGER.exception("Unexpected error during setup")
        raise ConfigEntryNotReady(f"Unexpected error: {err}") from err

    # Store coordinator and options listener
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "unsub": entry.add_update_listener(options_update_listener),
    }

    # Now safe to forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])
    return True


async def options_update_listener(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, [Platform.SENSOR]
    )

    # Unsubscribe from options updates
    hass.data[DOMAIN][entry.entry_id]["unsub"]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
