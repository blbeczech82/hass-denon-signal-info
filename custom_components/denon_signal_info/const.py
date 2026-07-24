"""Constants for the Denon Signal Info integration."""

from homeassistant.const import Platform

DOMAIN = "denon_signal_info"
PLATFORMS = [Platform.SENSOR]

CONF_USE_SSL = "use_ssl"
CONF_VERIFY_SSL = "verify_ssl"
CONF_MANUFACTURER = "manufacturer"
CONF_MODEL = "model"

DEFAULT_PORT = 10443
DEFAULT_SCAN_INTERVAL = 15
DEFAULT_USE_SSL = True
DEFAULT_VERIFY_SSL = False

INFORMATION_PATH = "/ajax/general/get_config"
FRIENDLY_NAME_PATH = "/ajax/globals/get_config"

INFO_QUERY_TYPE = "12"
FRIENDLY_NAME_QUERY_TYPE = "3"
