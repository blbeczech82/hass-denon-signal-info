"""HTTP API client for Denon Signal Info."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from xml.etree import ElementTree

from aiohttp import ClientError, ClientSession

from .const import (
    FRIENDLY_NAME_PATH,
    FRIENDLY_NAME_QUERY_TYPE,
    INFORMATION_PATH,
    INFO_QUERY_TYPE,
)


class DenonSignalInfoError(Exception):
    """Base exception for Denon Signal Info."""


class DenonSignalInfoConnectionError(DenonSignalInfoError):
    """Raised when the receiver cannot be reached."""


class DenonSignalInfoInvalidResponse(DenonSignalInfoError):
    """Raised when the receiver returns unexpected data."""


@dataclass(frozen=True, slots=True)
class DenonDeviceDetails:
    """Receiver details discovered during setup."""

    name: str
    manufacturer: str
    model: str


class DenonSignalInfoApi:
    """Read signal information from a Denon receiver."""

    def __init__(
        self,
        session: ClientSession,
        host: str,
        port: int,
        use_ssl: bool,
    ) -> None:
        """Initialize the API client."""
        scheme = "https" if use_ssl else "http"
        self._session = session
        self._base_url = f"{scheme}://{host}:{port}"

    @property
    def configuration_url(self) -> str:
        """Return the receiver web interface URL."""
        return f"{self._base_url}/general/general.html"

    async def _async_get_xml(
        self, path: str, query_type: str
    ) -> ElementTree.Element:
        """Fetch and parse one Denon XML response."""
        try:
            async with self._session.get(
                f"{self._base_url}{path}",
                params={"type": query_type},
                timeout=10,
            ) as response:
                response.raise_for_status()
                payload = await response.text()
        except (ClientError, TimeoutError) as err:
            raise DenonSignalInfoConnectionError(str(err)) from err

        try:
            return ElementTree.fromstring(payload)
        except ElementTree.ParseError as err:
            raise DenonSignalInfoInvalidResponse(
                "Receiver returned invalid XML"
            ) from err

    async def async_get_device_details(self) -> DenonDeviceDetails:
        """Get the receiver friendly name and derive device details."""
        root = await self._async_get_xml(
            FRIENDLY_NAME_PATH, FRIENDLY_NAME_QUERY_TYPE
        )
        name = (root.text or "").strip()
        if root.tag != "FriendlyName" or not name:
            raise DenonSignalInfoInvalidResponse(
                "Receiver did not return a FriendlyName"
            )

        first_word, separator, remainder = name.partition(" ")
        if first_word.casefold() in {"denon", "marantz"}:
            manufacturer = first_word
            model = remainder if separator else name
        else:
            manufacturer = "Denon"
            model = name

        return DenonDeviceDetails(
            name=name,
            manufacturer=manufacturer,
            model=model,
        )

    async def async_get_information(self) -> dict[str, Any]:
        """Get current audio, video, and firmware information."""
        root = await self._async_get_xml(INFORMATION_PATH, INFO_QUERY_TYPE)
        if root.tag != "Information":
            raise DenonSignalInfoInvalidResponse(
                "Receiver did not return Information"
            )

        def text(path: str) -> str | None:
            value = root.findtext(path)
            if value is None:
                return None
            value = value.strip()
            return value or None

        return {
            "sound_mode": text("./Audio/SoundMode"),
            "input_signal": text("./Audio/InputSignal"),
            "sample_rate": text("./Audio/SampleRate"),
            "audio_format": text("./Audio/Format"),
            "hdmi_resolution": text("./Video/HDMISignalInfo/Resolution"),
            "hdr": text("./Video/HDMISignalInfo/HDR"),
            "color_space": text("./Video/HDMISignalInfo/ColorSpace"),
            "pixel_depth": text("./Video/HDMISignalInfo/PixelDepth"),
            "firmware_version": text("./Firmware/Version"),
        }
