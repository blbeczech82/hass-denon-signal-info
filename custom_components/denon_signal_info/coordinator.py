"""Data coordinator for Denon Signal Info."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DenonSignalInfoApi, DenonSignalInfoError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DenonSignalInfoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll a Denon receiver and share one response across all entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: DenonSignalInfoApi,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest receiver information."""
        try:
            return await self.api.async_get_information()
        except DenonSignalInfoError as err:
            raise UpdateFailed(str(err)) from err
