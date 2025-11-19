import logging
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .speed_toggle import async_setup_services

_LOGGER = logging.getLogger(__name__)

# Platform constants for compatibility
try:
    from homeassistant.const import Platform
    PLATFORMS = [Platform.SWITCH]
except ImportError:
    # Older HA versions don't have Platform enum
    PLATFORMS = ["switch"]

async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up Deluge Speed from a config entry."""
    try:
        _LOGGER.debug("Setting up Deluge Speed integration")
        hass.data[DOMAIN] = entry.data
        await async_setup_services(hass)
        
        # Set up switch platform for HA 2025.x
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.info("Deluge Speed integration setup complete")
        return True
        
    except Exception as err:
        _LOGGER.error("Error setting up Deluge Speed: %s", err)
        return False

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    try:
        _LOGGER.debug("Unloading Deluge Speed integration")
        
        # Unload switch platform for HA 2025.x
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        
        # Clean up stored data
        if DOMAIN in hass.data:
            del hass.data[DOMAIN]
        
        _LOGGER.info("Deluge Speed integration unloaded")
        return unload_ok
        
    except Exception as err:
        _LOGGER.error("Error unloading Deluge Speed: %s", err)
        return False
