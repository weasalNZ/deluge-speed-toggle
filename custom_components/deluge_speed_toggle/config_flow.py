import logging
import voluptuous as vol
import aiohttp
import asyncio
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN,
    CONF_PRESET1_DOWNLOAD,
    CONF_PRESET1_UPLOAD,
    CONF_PRESET2_DOWNLOAD,
    CONF_PRESET2_UPLOAD,
    DEFAULT_PRESET1_DOWNLOAD,
    DEFAULT_PRESET1_UPLOAD,
    DEFAULT_PRESET2_DOWNLOAD,
    DEFAULT_PRESET2_UPLOAD,
)

_LOGGER = logging.getLogger(__name__)

async def validate_deluge_connection(hass: HomeAssistant, user_input: dict) -> bool:
    """Validate connection to Deluge."""
    host = user_input.get(CONF_HOST, "localhost")
    port = user_input.get(CONF_PORT, 8112)
    password = user_input.get(CONF_PASSWORD, "")

    try:
        _LOGGER.debug("Validating Deluge connection to %s:%s", host, port)
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
            async with session.post(
                f"http://{host}:{port}/json",
                json={"method": "auth.login", "params": [password], "id": 1},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Deluge connection failed: HTTP %s", resp.status)
                    return False

                result = await resp.json()
                if not result.get("result"):
                    _LOGGER.error("Deluge authentication failed: Invalid password")
                    return False

                _LOGGER.debug("Deluge connection validated successfully")
                return True

    except asyncio.TimeoutError:
        _LOGGER.error("Deluge connection timeout")
        return False
    except aiohttp.ClientError as err:
        _LOGGER.error("Deluge connection error: %s", err)
        return False
    except Exception as err:
        _LOGGER.error("Unexpected error validating Deluge: %s", err)
        return False

class DelugeSpeedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate connection
            if not await validate_deluge_connection(self.hass, user_input):
                errors["base"] = "cannot_connect"
            else:
                _LOGGER.info("Creating new Deluge Speed config entry")
                return self.async_create_entry(title="Deluge Speed", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default="localhost"): str,
                vol.Required(CONF_PORT, default=8112): int,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional("preset_1_name", default="Limited"): str,
                vol.Required(CONF_PRESET1_DOWNLOAD, default=DEFAULT_PRESET1_DOWNLOAD): int,
                vol.Required(CONF_PRESET1_UPLOAD, default=DEFAULT_PRESET1_UPLOAD): int,
                vol.Optional("preset_2_name", default="Unlimited"): str,
                vol.Required(CONF_PRESET2_DOWNLOAD, default=DEFAULT_PRESET2_DOWNLOAD): int,
                vol.Required(CONF_PRESET2_UPLOAD, default=DEFAULT_PRESET2_UPLOAD): int,
            }),
            errors=errors,
            description_placeholders={
                "test_connection": "Connection settings will be tested"
            },
        )
