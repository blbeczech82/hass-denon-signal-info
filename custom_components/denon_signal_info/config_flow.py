"""Config flow for Denon Signal Info."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

from .api import (
    DenonSignalInfoApi,
    DenonSignalInfoConnectionError,
    DenonSignalInfoInvalidResponse,
)
from .const import (
    CONF_MANUFACTURER,
    CONF_MODEL,
    CONF_USE_SSL,
    CONF_VERIFY_SSL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USE_SSL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)


def _user_schema(user_input: dict[str, Any] | None = None) -> vol.Schema:
    """Build the user setup schema."""
    values = user_input or {}
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=values.get(CONF_HOST, "")): str,
            vol.Required(
                CONF_PORT, default=values.get(CONF_PORT, DEFAULT_PORT)
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
            vol.Required(
                CONF_USE_SSL,
                default=values.get(CONF_USE_SSL, DEFAULT_USE_SSL),
            ): bool,
            vol.Required(
                CONF_VERIFY_SSL,
                default=values.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            ): bool,
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=values.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
        }
    )


class DenonSignalInfoConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Handle a config flow for Denon Signal Info."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip().lower()
            user_input[CONF_HOST] = host

            if not host or "://" in host or "/" in host:
                errors[CONF_HOST] = "invalid_host"
            else:
                session = async_get_clientsession(
                    self.hass,
                    verify_ssl=user_input[CONF_VERIFY_SSL],
                )
                api = DenonSignalInfoApi(
                    session=session,
                    host=host,
                    port=user_input[CONF_PORT],
                    use_ssl=user_input[CONF_USE_SSL],
                )
                try:
                    details = await api.async_get_device_details()
                    await api.async_get_information()
                except DenonSignalInfoConnectionError:
                    errors["base"] = "cannot_connect"
                except DenonSignalInfoInvalidResponse:
                    errors["base"] = "invalid_response"
                else:
                    unique_id = f"{host}:{user_input[CONF_PORT]}"
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    user_input[CONF_MANUFACTURER] = details.manufacturer
                    user_input[CONF_MODEL] = details.model
                    return self.async_create_entry(
                        title=details.name,
                        data=user_input,
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> DenonSignalInfoOptionsFlow:
        """Return the options flow."""
        return DenonSignalInfoOptionsFlow(config_entry)


class DenonSignalInfoOptionsFlow(config_entries.OptionsFlow):
    """Manage Denon Signal Info options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage polling options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=current.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(
                        vol.Coerce(int), vol.Range(min=5, max=3600)
                    )
                }
            ),
        )
