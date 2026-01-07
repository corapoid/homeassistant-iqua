"""Config flow for iQua Softener integration with hub support."""
import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries, core
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from iqua_softener import IquaSoftener, IquaSoftenerException

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_SERIAL_NUMBER,
    CONF_IS_HUB,
    CONF_HUB_ID,
)
from .hub import IquaHub

_LOGGER = logging.getLogger(__name__)

# Schema for hub setup (account credentials only)
DATA_SCHEMA_HUB = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

# Schema for manual device addition
DATA_SCHEMA_DEVICE = vol.Schema(
    {
        vol.Required(CONF_DEVICE_SERIAL_NUMBER): str,
        vol.Optional("custom_name"): str,
    }
)

# Legacy schema (backward compatibility)
DATA_SCHEMA_LEGACY = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_DEVICE_SERIAL_NUMBER): str,
    }
)


class IquaSoftenerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iQua Softener with hub support."""

    VERSION = 2

    def __init__(self):
        """Initialize config flow."""
        self._hub_data: Optional[Dict[str, Any]] = None

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step - choose setup type."""
        
        # Show menu: Hub setup vs Legacy device setup
        return self.async_show_menu(
            step_id="user",
            menu_options=["hub", "legacy"],
        )

    async def async_step_hub(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle hub setup (modern way)."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            # Validate credentials
            try:
                hub = IquaHub(
                    self.hass,
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
                
                # Setup hub (verifies credentials)
                await hub.async_setup()
                
                # Store hub data for next step
                self._hub_data = {
                    CONF_IS_HUB: True,
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                }
                
                # Create hub entry
                return self.async_create_entry(
                    title=f"EcoWater Hub ({user_input[CONF_USERNAME]})",
                    data=self._hub_data,
                )
                
            except IquaSoftenerException as err:
                error_str = str(err).lower()
                _LOGGER.debug("Validation error type: %s", type(err).__name__)
                
                if "authentication error" in error_str or "invalid user" in error_str:
                    errors["base"] = "invalid_auth"
                elif "502" in error_str:
                    errors["base"] = "server_unavailable"
                else:
                    errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
                _LOGGER.exception("Unexpected error during hub validation")

        return self.async_show_form(
            step_id="hub",
            data_schema=DATA_SCHEMA_HUB,
            errors=errors,
        )

    async def async_step_device(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle adding a device to existing hub."""
        errors: Dict[str, str] = {}
        
        # Get hub entry
        hub_entries = [
            entry
            for entry in self.hass.config_entries.async_entries(DOMAIN)
            if entry.data.get(CONF_IS_HUB)
        ]
        
        if not hub_entries:
            return self.async_abort(reason="no_hub")
        
        hub_entry = hub_entries[0]  # Use first hub
        hub = self.hass.data[DOMAIN][hub_entry.entry_id]["hub"]
        
        if user_input is not None:
            device_serial = user_input[CONF_DEVICE_SERIAL_NUMBER]
            custom_name = user_input.get("custom_name")
            
            # Check if already configured
            await self.async_set_unique_id(device_serial.lower())
            self._abort_if_unique_id_configured()
            
            # Validate device exists and is accessible
            try:
                device_info = await hub.async_get_device(device_serial)
                
                if not device_info:
                    errors["base"] = "device_not_found"
                else:
                    # Create device entry
                    return self.async_create_entry(
                        title=custom_name or f"Water Softener {device_serial[-6:]}",
                        data={
                            CONF_IS_HUB: False,
                            CONF_HUB_ID: hub_entry.entry_id,
                            CONF_DEVICE_SERIAL_NUMBER: device_serial,
                        },
                    )
                    
            except IquaSoftenerException as err:
                error_str = str(err).lower()
                _LOGGER.debug("Device validation error: %s", type(err).__name__)
                
                if "device" in error_str or "serial" in error_str:
                    errors["base"] = "device_not_found"
                else:
                    errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
                _LOGGER.exception("Unexpected error during device validation")

        return self.async_show_form(
            step_id="device",
            data_schema=DATA_SCHEMA_DEVICE,
            errors=errors,
        )

    async def async_step_legacy(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle legacy setup (single device without hub)."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            # Check if already configured
            await self.async_set_unique_id(
                user_input[CONF_DEVICE_SERIAL_NUMBER].lower()
            )
            self._abort_if_unique_id_configured()
            
            # Validate credentials before creating entry
            try:
                await self._test_credentials(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_DEVICE_SERIAL_NUMBER],
                )
            except IquaSoftenerException as err:
                error_str = str(err).lower()
                _LOGGER.debug("Validation error type: %s", type(err).__name__)
                
                if "authentication error" in error_str or "invalid user" in error_str:
                    errors["base"] = "invalid_auth"
                elif "502" in error_str:
                    errors["base"] = "server_unavailable"
                elif "device" in error_str or "serial" in error_str:
                    errors["base"] = "device_not_found"
                else:
                    errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
                _LOGGER.exception("Unexpected error during validation")
            else:
                # Connection successful - create entry (legacy mode)
                return self.async_create_entry(
                    title=f"iQua {user_input[CONF_DEVICE_SERIAL_NUMBER][-6:]}",
                    data={
                        CONF_IS_HUB: False,
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_DEVICE_SERIAL_NUMBER: user_input[CONF_DEVICE_SERIAL_NUMBER],
                    },
                )

        return self.async_show_form(
            step_id="legacy",
            data_schema=DATA_SCHEMA_LEGACY,
            errors=errors,
        )

    async def _test_credentials(
        self, username: str, password: str, serial_number: str
    ) -> None:
        """Test if credentials are valid."""
        softener = IquaSoftener(username, password, serial_number)
        # Attempt to fetch data to validate credentials
        await self.hass.async_add_executor_job(softener.get_data)
