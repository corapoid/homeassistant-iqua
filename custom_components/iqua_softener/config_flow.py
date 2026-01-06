"""Config flow for iQua Softener integration."""
import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries, core
import voluptuous as vol

from iqua_softener import IquaSoftener, IquaSoftenerException

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_DEVICE_SERIAL_NUMBER

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA_USER = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_DEVICE_SERIAL_NUMBER): str,
    }
)


class IquaSoftenerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iQua Softener."""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            # Validate credentials before creating entry
            try:
                await self._test_credentials(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_DEVICE_SERIAL_NUMBER],
                )
            except IquaSoftenerException as err:
                error_str = str(err).lower()
                if "authentication error" in error_str or "invalid user" in error_str:
                    errors["base"] = "invalid_auth"
                elif "502" in error_str:
                    errors["base"] = "server_unavailable"
                elif "device" in error_str or "serial" in error_str:
                    errors["base"] = "device_not_found"
                else:
                    errors["base"] = "cannot_connect"
                _LOGGER.error("Validation error: %s", err)
            except Exception as err:
                errors["base"] = "unknown"
                _LOGGER.exception("Unexpected error during validation")
            else:
                # Connection successful - create entry
                self.data = user_input
                return self.async_create_entry(
                    title=f"iQua {self.data[CONF_DEVICE_SERIAL_NUMBER]}",
                    data=self.data,
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA_USER, errors=errors
        )

    async def _test_credentials(
        self, username: str, password: str, serial_number: str
    ) -> None:
        """Test if credentials are valid."""
        softener = IquaSoftener(username, password, serial_number)
        # Attempt to fetch data to validate credentials
        await self.hass.async_add_executor_job(softener.get_data)
