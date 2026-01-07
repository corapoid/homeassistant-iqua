"""DataUpdateCoordinator for iQua Softener."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from iqua_softener import IquaSoftener, IquaSoftenerData, IquaSoftenerException

_LOGGER = logging.getLogger(__name__)
UPDATE_INTERVAL = timedelta(minutes=5)


class IquaSoftenerCoordinator(DataUpdateCoordinator[IquaSoftenerData]):
    """Coordinator for fetching iQua Softener data with retry logic."""

    def __init__(self, hass: HomeAssistant, iqua_softener: IquaSoftener) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Iqua Softener",
            update_interval=UPDATE_INTERVAL,
        )
        self._iqua_softener = iqua_softener

    async def _async_update_data(self) -> IquaSoftenerData:
        """Fetch data with retry logic for transient errors."""
        retries = 3
        backoff = 1.0

        for attempt in range(retries):
            try:
                _LOGGER.debug(
                    "Fetching data for device %s (attempt %d/%d)",
                    self._iqua_softener.device_serial_number,
                    attempt + 1,
                    retries,
                )
                data = await self.hass.async_add_executor_job(
                    self._iqua_softener.get_data
                )
                _LOGGER.info(
                    "Successfully fetched data for device %s - State: %s, Salt: %s%%",
                    self._iqua_softener.device_serial_number,
                    data.state.value,
                    data.salt_level_percent,
                )
                return data
            except IquaSoftenerException as err:
                error_str = str(err)

                # Retry on 502 Bad Gateway or network errors
                if (
                    "502" in error_str or "timeout" in error_str.lower()
                ) and attempt < retries - 1:
                    _LOGGER.warning(
                        "Transient error (attempt %d/%d): %s. Retrying in %.1fs...",
                        attempt + 1,
                        retries,
                        err,
                        backoff,
                    )
                    await asyncio.sleep(backoff)
                    backoff *= 2  # Exponential backoff
                    continue

                # Non-retryable error or final attempt
                _LOGGER.error("Failed to fetch data: %s", err)
                raise UpdateFailed(f"Get data failed: {err}") from err
