import logging
import asyncio
import aiohttp
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import HomeAssistantError
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

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up switch platform from a config entry."""
    _LOGGER.debug("Setting up Deluge Speed switch entity")
    config = entry.data
    switch = DelugeSpeedToggleSwitch(hass, config)
    async_add_entities([switch])
    _LOGGER.info("Deluge Speed switch entity added")

async def async_setup_services(hass: HomeAssistant):
    import voluptuous as vol
    from homeassistant.helpers import config_validation as cv
    
    # Service schema for set_speed
    SET_SPEED_SCHEMA = vol.Schema({
        vol.Required("download"): int,
        vol.Required("upload"): int,
    })

    async def handle_set_speed(call: ServiceCall):
        config = hass.data[DOMAIN]
        host = config["host"]
        port = config["port"]
        password = config["password"]

        download = call.data["download"]
        upload = call.data["upload"]

        try:
            _LOGGER.debug(
                "Setting Deluge speeds - Download: %s KiB/s, Upload: %s KiB/s",
                download,
                upload,
            )
            
            async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
                # Authenticate
                try:
                    async with session.post(
                        f"http://{host}:{port}/json",
                        json={"method": "auth.login", "params": [password], "id": 1},
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status != 200:
                            _LOGGER.error(
                                "Deluge authentication failed with status %s", resp.status
                            )
                            raise HomeAssistantError(
                                f"Deluge authentication failed: HTTP {resp.status}"
                            )
                        
                        result = await resp.json()
                        if not result.get("result"):
                            _LOGGER.error(
                                "Deluge authentication failed: Invalid response - %s",
                                result,
                            )
                            raise HomeAssistantError(
                                "Deluge authentication failed: Invalid password or connection"
                            )
                        _LOGGER.debug("Successfully authenticated with Deluge")
                
                except asyncio.TimeoutError:
                    _LOGGER.error("Deluge authentication timeout")
                    raise HomeAssistantError("Deluge connection timeout")
                except aiohttp.ClientError as err:
                    _LOGGER.error("Deluge connection error: %s", err)
                    raise HomeAssistantError(f"Deluge connection error: {err}")

                # Set speed
                try:
                    async with session.post(
                        f"http://{host}:{port}/json",
                        json={
                            "method": "core.set_config",
                            "params": [
                                {
                                    "max_download_speed": download,
                                    "max_upload_speed": upload,
                                }
                            ],
                            "id": 2,
                        },
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status != 200:
                            _LOGGER.error(
                                "Failed to set speeds: HTTP %s", resp.status
                            )
                            raise HomeAssistantError(
                                f"Failed to set speeds: HTTP {resp.status}"
                            )
                        
                        result = await resp.json()
                        if result.get("error"):
                            _LOGGER.error(
                                "Deluge set_config error: %s", result.get("error")
                            )
                            raise HomeAssistantError(
                                f"Deluge error: {result.get('error')}"
                            )
                        _LOGGER.info(
                            "Successfully set Deluge speeds - Download: %s, Upload: %s",
                            download,
                            upload,
                        )
                
                except asyncio.TimeoutError:
                    _LOGGER.error("Deluge speed set timeout")
                    raise HomeAssistantError("Deluge connection timeout")
                except aiohttp.ClientError as err:
                    _LOGGER.error("Deluge error when setting speeds: %s", err)
                    raise HomeAssistantError(f"Deluge error: {err}")

        except HomeAssistantError:
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error setting Deluge speeds: %s", err)
            raise HomeAssistantError(f"Unexpected error: {err}")

    # Register services
    hass.services.async_register(DOMAIN, "set_speed", handle_set_speed, schema=SET_SPEED_SCHEMA)
    _LOGGER.debug("Registered deluge_speed_toggle.set_speed service")
    
    # Register toggle service 
    async def handle_toggle_speed(call: ServiceCall):
        """Handle toggle_download_speed service call."""
        # Find the switch entity and toggle it
        # Find the switch entity dynamically since unique_id now includes host/port
        config = hass.data[DOMAIN]
        host = config.get("host", "localhost")
        port = config.get("port", 8112)
        switch_entity_id = f"switch.{DOMAIN}_{host}_{port}_switch"
        switch_state = hass.states.get(switch_entity_id)
        
        if switch_state is None:
            _LOGGER.error("Deluge speed toggle switch not found")
            raise HomeAssistantError("Deluge speed toggle switch not found")
        
        # Toggle the switch
        service_name = "turn_off" if switch_state.state == "on" else "turn_on"
        await hass.services.async_call("switch", service_name, {"entity_id": switch_entity_id})
        _LOGGER.info("Toggled Deluge speed switch")
    
    hass.services.async_register(DOMAIN, "toggle_download_speed", handle_toggle_speed)
    _LOGGER.debug("Registered deluge_speed_toggle.toggle_download_speed service")
    
    # Add diagnostic service
    async def handle_test_connection(call: ServiceCall):
        """Test connection to Deluge."""
        config = hass.data[DOMAIN]
        host = config["host"]
        port = config["port"]
        password = config["password"]
        
        try:
            _LOGGER.info("Testing Deluge connection to %s:%s", host, port)
            async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
                async with session.post(
                    f"http://{host}:{port}/json",
                    json={"method": "auth.login", "params": [password], "id": 1},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        _LOGGER.error("Connection test failed: HTTP %s", resp.status)
                        return
                    
                    result = await resp.json()
                    if result.get("result"):
                        _LOGGER.info("✅ Deluge connection test SUCCESSFUL")
                    else:
                        _LOGGER.error("❌ Deluge authentication failed")
        except Exception as err:
            _LOGGER.error("❌ Deluge connection test FAILED: %s", err)
    
    hass.services.async_register(DOMAIN, "test_connection", handle_test_connection)
    _LOGGER.debug("Registered deluge_speed_toggle.test_connection service")
    
    # Add API diagnostic service
    async def handle_test_api(call: ServiceCall):
        """Test various Deluge API methods to see what works."""
        config = hass.data[DOMAIN]
        host = config["host"]
        port = config["port"]
        password = config["password"]
        
        try:
            _LOGGER.info("Testing Deluge API methods...")
            connector = aiohttp.TCPConnector()
            cookie_jar = aiohttp.CookieJar(unsafe=True)
            
            async with aiohttp.ClientSession(
                connector=connector, 
                cookie_jar=cookie_jar,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                
                # Authenticate first
                auth_response = await session.post(
                    f"http://{host}:{port}/json",
                    json={"method": "auth.login", "params": [password], "id": 1}
                )
                
                auth_result = await auth_response.json()
                if not auth_result.get("result"):
                    _LOGGER.error("❌ API Test: Authentication failed - %s", auth_result)
                    return
                    
                _LOGGER.info("✅ API Test: Authentication successful")
                
                # Test different API methods with authenticated session and correct parameters
                test_calls = [
                    {"method": "daemon.get_method_list", "params": []},
                    {"method": "core.get_session_status", "params": [["download_rate", "upload_rate"]]}, 
                    {"method": "core.get_torrents_status", "params": [{}, ["name", "state", "progress"]]},
                    {"method": "core.get_config", "params": []}
                ]
                
                for test_call in test_calls:
                    method = test_call["method"]
                    try:
                        response = await session.post(
                            f"http://{host}:{port}/json",
                            json={"method": method, "params": test_call["params"], "id": 2}
                        )
                        result = await response.json()
                        if result.get("error"):
                            _LOGGER.warning("⚠️  API Test: %s returned error: %s", method, result.get("error"))
                        else:
                            _LOGGER.info("✅ API Test: %s works - returned %d bytes", method, len(str(result)))
                            if method == "daemon.get_method_list":
                                methods = result.get("result", [])
                                _LOGGER.info("📋 Available methods: %s", methods[:10])  # Show first 10
                            elif method == "core.get_session_status":
                                session_data = result.get("result", {})
                                _LOGGER.info("📊 Session stats: download=%s, upload=%s", 
                                           session_data.get("download_rate", 0),
                                           session_data.get("upload_rate", 0))
                    except Exception as err:
                        _LOGGER.error("❌ API Test: %s failed: %s", method, err)
                        
        except Exception as err:
            _LOGGER.error("❌ API Test failed: %s", err)
    
    hass.services.async_register(DOMAIN, "test_api", handle_test_api)
    _LOGGER.debug("Registered deluge_speed_toggle.test_api service")

class DelugeSpeedToggleSwitch(SwitchEntity):
    """Switch to toggle between two presets of Deluge download/upload speeds."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the switch."""
        self.hass = hass
        self.config = config
        self._attr_name = "Deluge Speed Toggle"
        host = config.get("host", "localhost")
        port = config.get("port", 8112)
        self._attr_unique_id = f"{DOMAIN}_{host}_{port}_switch"
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._is_on = False
        self._attr_should_poll = True  # Enable polling to refresh attributes with sensor data
        self._available = True
        
        # Add device info for better integration
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{config.get('host', 'localhost')}_{config.get('port', 8112)}")},
            "name": "Deluge Server",
            "manufacturer": "Deluge",
            "model": "Torrent Client", 
            "sw_version": "1.1",
        }
        
        _LOGGER.debug("Initialized DelugeSpeedToggleSwitch")

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        _LOGGER.info("Deluge Speed Toggle switch added to Home Assistant with ID: %s", self.unique_id)
        # Restore previous state if available
        try:
            if (last_state := await self.async_get_last_state_with_restored_native_value()) is not None:
                self._is_on = last_state.state == "on"
                _LOGGER.debug("Restored previous switch state: %s", "ON" if self._is_on else "OFF")
        except AttributeError:
            # Fallback for different HA versions
            _LOGGER.debug("State restoration not available, will detect from Deluge")
        
        # Test connection and detect current state on startup
        try:
            await self._test_connection()
            _LOGGER.info("Initial Deluge connection test successful")
            
            # Detect current Deluge speed settings to sync switch state
            await self._detect_current_state()
            
        except Exception as err:
            _LOGGER.warning("Initial Deluge connection/state detection failed: %s", err)
            self._available = False

    async def _test_connection(self) -> bool:
        """Test connection to Deluge without changing any settings."""
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 8112)
        password = self.config.get("password")
        
        _LOGGER.debug("Testing connection to Deluge at %s:%s", host, port)
        
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
            async with session.post(
                f"http://{host}:{port}/json",
                json={"method": "auth.login", "params": [password], "id": 1},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    raise HomeAssistantError(f"HTTP {resp.status}")
                
                result = await resp.json()
                if not result.get("result"):
                    raise HomeAssistantError("Authentication failed")
                
                return True

    async def _detect_current_state(self):
        """Detect current Deluge speed settings and set switch state accordingly."""
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 8112)
        password = self.config.get("password")
        
        preset1_download = self.config.get(CONF_PRESET1_DOWNLOAD, DEFAULT_PRESET1_DOWNLOAD)
        preset1_upload = self.config.get(CONF_PRESET1_UPLOAD, DEFAULT_PRESET1_UPLOAD)
        preset2_download = self.config.get(CONF_PRESET2_DOWNLOAD, DEFAULT_PRESET2_DOWNLOAD)
        preset2_upload = self.config.get(CONF_PRESET2_UPLOAD, DEFAULT_PRESET2_UPLOAD)
        
        _LOGGER.debug("Detecting current Deluge speed configuration...")
        
        try:
            connector = aiohttp.TCPConnector()
            cookie_jar = aiohttp.CookieJar(unsafe=True)
            
            async with aiohttp.ClientSession(
                connector=connector,
                cookie_jar=cookie_jar,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                
                # Authenticate
                auth_response = await session.post(
                    f"http://{host}:{port}/json",
                    json={"method": "auth.login", "params": [password], "id": 1}
                )
                
                auth_result = await auth_response.json()
                if not auth_result.get("result"):
                    _LOGGER.warning("Could not authenticate to detect current state")
                    return
                
                # Get current config
                config_response = await session.post(
                    f"http://{host}:{port}/json",
                    json={"method": "core.get_config", "params": [], "id": 2}
                )
                
                config_result = await config_response.json()
                if config_result.get("error"):
                    _LOGGER.warning("Could not get config to detect current state: %s", config_result.get("error"))
                    return
                
                # Convert to regular dict to avoid mappingproxy issues
                current_config = dict(config_result.get("result", {}))
                current_download = current_config.get("max_download_speed", -1)
                current_upload = current_config.get("max_upload_speed", -1)
                
                _LOGGER.debug("Current Deluge config - Download: %s, Upload: %s", current_download, current_upload)
                _LOGGER.debug("Preset 1 (Limited) - Download: %s, Upload: %s", preset1_download, preset1_upload)
                _LOGGER.debug("Preset 2 (Unlimited) - Download: %s, Upload: %s", preset2_download, preset2_upload)
                
                # Determine which preset matches current settings
                preset1_match = (current_download == preset1_download and current_upload == preset1_upload)
                preset2_match = (current_download == preset2_download and current_upload == preset2_upload)
                
                if preset1_match:
                    self._is_on = True
                    _LOGGER.info("Detected Deluge is using Preset 1 (Limited) - Switch ON")
                elif preset2_match:
                    self._is_on = False
                    _LOGGER.info("Detected Deluge is using Preset 2 (Unlimited) - Switch OFF")
                else:
                    # Current settings don't match either preset
                    # Check if speeds are limited (not unlimited)
                    speeds_are_limited = (current_download != -1 or current_upload != -1)
                    
                    if speeds_are_limited:
                        # Deluge has custom limited speeds - adapt Preset 1 to match and set switch ON
                        self._is_on = True
                        _LOGGER.info("Detected custom limited speeds in Deluge (Download: %s, Upload: %s) - Setting Switch ON and adapting Preset 1", 
                                   current_download, current_upload)
                        
                        # Update our internal preset 1 to match current Deluge settings
                        # This allows the switch to work with whatever speeds are currently set
                        self.config[CONF_PRESET1_DOWNLOAD] = current_download
                        self.config[CONF_PRESET1_UPLOAD] = current_upload
                        
                        # Log the adaptation
                        _LOGGER.info("Adapted Preset 1 to match current Deluge settings: Download=%s KiB/s, Upload=%s KiB/s", 
                                   current_download, current_upload)
                        
                        # Save the adapted preset to config entry for persistence
                        await self._save_adapted_preset(current_download, current_upload)
                        
                    else:
                        # Speeds are unlimited (-1, -1) but don't match preset 2 exactly (shouldn't happen)
                        self._is_on = False
                        _LOGGER.info("Detected unlimited speeds - Switch OFF")
                
                # Update Home Assistant state
                self.async_write_ha_state()
                
        except Exception as err:
            _LOGGER.warning("Could not detect current Deluge state: %s", err)

    async def _save_adapted_preset(self, download_speed: int, upload_speed: int):
        """Save adapted preset speeds to config entry for persistence."""
        try:
            # Get the config entry
            config_entry = None
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                if entry.data.get("host") == self.config.get("host") and entry.data.get("port") == self.config.get("port"):
                    config_entry = entry
                    break
            
            if config_entry:
                # Update the config entry with new preset 1 values
                new_data = dict(config_entry.data)
                new_data[CONF_PRESET1_DOWNLOAD] = download_speed
                new_data[CONF_PRESET1_UPLOAD] = upload_speed
                
                self.hass.config_entries.async_update_entry(
                    config_entry, 
                    data=new_data
                )
                
                _LOGGER.info("Saved adapted Preset 1 to configuration: Download=%s, Upload=%s", download_speed, upload_speed)
            else:
                _LOGGER.warning("Could not find config entry to save adapted preset")
                
        except Exception as err:
            _LOGGER.warning("Could not save adapted preset: %s", err)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on (set to preset 1 - limited speeds)."""
        preset1_download = self.config.get(
            CONF_PRESET1_DOWNLOAD, DEFAULT_PRESET1_DOWNLOAD
        )
        preset1_upload = self.config.get(
            CONF_PRESET1_UPLOAD, DEFAULT_PRESET1_UPLOAD
        )
        _LOGGER.info(
            "Turning ON - Setting Preset 1 (Limited): Download=%s, Upload=%s",
            preset1_download,
            preset1_upload,
        )
        
        try:
            await self._set_speed(preset1_download, preset1_upload)
            # Only set state to on if speed setting succeeded
            self._is_on = True
            self._available = True
            self.async_write_ha_state()
            _LOGGER.info("Successfully switched to Preset 1 (Limited)")
        except HomeAssistantError as err:
            _LOGGER.error("Failed to turn on switch: %s", err)
            # Keep current state, mark as unavailable temporarily
            self._available = False
            self.async_write_ha_state()
            # Don't re-raise, just log the error
        except Exception as err:
            _LOGGER.error("Unexpected error turning on switch: %s", err)
            self._available = False
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off (set to preset 2 - unlimited speeds)."""
        preset2_download = self.config.get(
            CONF_PRESET2_DOWNLOAD, DEFAULT_PRESET2_DOWNLOAD
        )
        preset2_upload = self.config.get(
            CONF_PRESET2_UPLOAD, DEFAULT_PRESET2_UPLOAD
        )
        _LOGGER.info(
            "Turning OFF - Setting Preset 2 (Unlimited): Download=%s, Upload=%s",
                preset2_download,
                preset2_upload,
        )
        
        try:
            await self._set_speed(preset2_download, preset2_upload)
            # Only set state to off if speed setting succeeded
            self._is_on = False
            self._available = True
            self.async_write_ha_state()
            _LOGGER.info("Successfully switched to Preset 2 (Unlimited)")
        except HomeAssistantError as err:
            _LOGGER.error("Failed to turn off switch: %s", err)
            # Keep current state, mark as unavailable temporarily
            self._available = False
            self.async_write_ha_state()
            # Don't re-raise, just log the error
        except Exception as err:
            _LOGGER.error("Unexpected error turning off switch: %s", err)
            self._available = False
            self.async_write_ha_state()

    async def _set_speed(self, download: int, upload: int) -> None:
        """Set both download and upload speeds."""
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 8112)
        password = self.config.get("password")

        if not password:
            _LOGGER.error("Deluge password not configured")
            raise HomeAssistantError("Deluge password not configured")

        # New approach: Try to exactly mimic what curl does
        try:
            _LOGGER.debug("Connecting to Deluge at %s:%s using curl-like approach", host, port)
            
            speed_config = {
                "max_download_speed": download,
                "max_upload_speed": upload,
            }
            
            # Method 1: Use the simplest approach that mirrors curl exactly
            timeout = aiohttp.ClientTimeout(total=30)  # Longer timeout like curl
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'HomeAssistant-DelugeSpeedToggle/1.0'
            }
            
            # Try with explicit cookie jar and headers like curl
            jar = aiohttp.CookieJar(unsafe=True)  # Allow all cookies
            async with aiohttp.ClientSession(cookie_jar=jar, headers=headers, timeout=timeout) as session:
                
                # Step 1: Authenticate (exactly like curl)
                auth_payload = {
                    "method": "auth.login",
                    "params": [password], 
                    "id": 1
                }
                _LOGGER.debug("Auth payload: %s", {**auth_payload, "params": ["***"]})
                
                async with session.post(f"http://{host}:{port}/json", json=auth_payload) as auth_resp:
                    auth_text = await auth_resp.text()
                    _LOGGER.debug("Auth response status: %s, text: %s", auth_resp.status, auth_text)
                    
                    if auth_resp.status != 200:
                        raise HomeAssistantError(f"Auth HTTP error: {auth_resp.status}")
                    
                    try:
                        auth_result = await auth_resp.json()
                    except:
                        auth_result = {"result": False, "error": f"Invalid JSON: {auth_text}"}
                    
                    if not auth_result.get("result"):
                        raise HomeAssistantError(f"Auth failed: {auth_result}")
                    
                    _LOGGER.debug("Authentication successful, cookies: %s", [str(c) for c in session.cookie_jar])
                
                # Step 2: Set config using authenticated session
                config_payload = {
                    "method": "core.set_config",
                    "params": [speed_config],
                    "id": 2
                }
                _LOGGER.debug("Config payload: %s", config_payload)
                
                async with session.post(f"http://{host}:{port}/json", json=config_payload) as config_resp:
                    config_text = await config_resp.text()
                    _LOGGER.debug("Config response status: %s, text: %s", config_resp.status, config_text)
                    
                    if config_resp.status != 200:
                        raise HomeAssistantError(f"Config HTTP error: {config_resp.status}")
                    
                    try:
                        config_result = await config_resp.json()
                    except:
                        config_result = {"error": f"Invalid JSON: {config_text}"}
                    
                    _LOGGER.debug("Config result: %s", config_result)
                    
                    if config_result.get("error"):
                        error_info = config_result.get("error")
                        if isinstance(error_info, dict):
                            error_msg = error_info.get("message", str(error_info))
                        else:
                            error_msg = str(error_info)
                        
                        _LOGGER.error("Deluge returned error: %s", error_msg)
                        
                        # If authentication error, this might be a Deluge version/config issue
                        if "not authenticated" in error_msg.lower():
                            # Try one final approach - maybe Deluge needs different auth handling
                            return await self._try_alternative_auth(host, port, password, speed_config)
                        
                        raise HomeAssistantError(f"Deluge error: {error_msg}")
                    
                    # Check for success - Deluge returns result: null for successful set_config
                    if config_result.get("error") is None:
                        _LOGGER.info("✅ Successfully set Deluge speeds: %s", speed_config)
                        return
                    else:
                        _LOGGER.warning("Unexpected response format: %s", config_result)
                        raise HomeAssistantError("Unexpected response from Deluge")

        except HomeAssistantError:
            raise
        except Exception as err:
            _LOGGER.error("Curl-like approach failed: %s", err)
            raise HomeAssistantError(f"All connection methods failed: {err}")

    async def _set_speed_single_request(self, host: str, port: int, password: str, speed_config: dict) -> None:
        """Alternative method: Single session with proper timing."""
        try:
            _LOGGER.debug("Using single session with timing approach")
            
            # Use single session but with proper request timing
            connector = aiohttp.TCPConnector(keepalive_timeout=30, enable_cleanup_closed=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Step 1: Authenticate
                _LOGGER.debug("Authenticating for single session method")
                async with session.post(
                    f"http://{host}:{port}/json",
                    json={"method": "auth.login", "params": [password], "id": 1},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as auth_resp:
                    if auth_resp.status != 200:
                        raise HomeAssistantError(f"Auth failed: HTTP {auth_resp.status}")
                    
                    auth_result = await auth_resp.json()
                    _LOGGER.debug("Single session auth result: %s", auth_result)
                    
                    if not auth_result.get("result"):
                        raise HomeAssistantError("Authentication failed in single session method")
                
                # Small delay to ensure session is established
                await asyncio.sleep(0.2)
                
                # Step 2: Set config using authenticated session
                _LOGGER.debug("Setting config in authenticated session")
                async with session.post(
                    f"http://{host}:{port}/json",
                    json={
                        "method": "core.set_config",
                        "params": [speed_config],
                        "id": 2,
                    },
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as config_resp:
                    if config_resp.status != 200:
                        raise HomeAssistantError(f"Config failed: HTTP {config_resp.status}")
                    
                    config_result = await config_resp.json()
                    _LOGGER.debug("Single session config result: %s", config_result)
                    
                    if config_result.get("error"):
                        error_info = config_result.get("error")
                        error_msg = error_info.get("message") if isinstance(error_info, dict) else str(error_info)
                        
                        # If still getting auth errors, try one more time with fresh approach
                        if "not authenticated" in error_msg.lower():
                            _LOGGER.warning("Still getting auth errors, trying completely fresh session")
                            return await self._set_speed_fresh_session(host, port, password, speed_config)
                        
                        raise HomeAssistantError(f"Speed setting failed: {error_msg}")
                    
                    _LOGGER.info("Successfully set speeds using single session method")
        
        except HomeAssistantError:
            raise
        except Exception as err:
            _LOGGER.error("Single session method failed: %s", err)
            raise HomeAssistantError(f"Could not set Deluge speeds: {err}")

    async def _set_speed_fresh_session(self, host: str, port: int, password: str, speed_config: dict) -> None:
        """Final fallback: Completely separate sessions."""
        _LOGGER.debug("Using completely fresh sessions approach (last resort)")
        
        # Method: Each API call gets its own session (most compatible but inefficient)
        for attempt in range(2):  # Try twice
            try:
                # Fresh session just for config setting
                async with aiohttp.ClientSession() as session:
                    # Authenticate
                    async with session.post(
                        f"http://{host}:{port}/json",
                        json={"method": "auth.login", "params": [password], "id": 1},
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as auth_resp:
                        auth_result = await auth_resp.json()
                        if not auth_result.get("result"):
                            raise HomeAssistantError("Fresh session auth failed")
                    
                    # Tiny delay
                    await asyncio.sleep(0.05)
                    
                    # Set config immediately
                    async with session.post(
                        f"http://{host}:{port}/json",
                        json={
                            "method": "core.set_config",
                            "params": [speed_config],
                            "id": 2,
                        },
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as config_resp:
                        config_result = await config_resp.json()
                        if config_result.get("error"):
                            error_msg = config_result.get("error").get("message", "Unknown error")
                            if "not authenticated" in error_msg.lower() and attempt == 0:
                                _LOGGER.warning("Attempt %d failed, retrying...", attempt + 1)
                                await asyncio.sleep(0.5)  # Wait longer before retry
                                continue
                            raise HomeAssistantError(f"Fresh session config failed: {error_msg}")
                        
                        _LOGGER.info("Successfully set speeds using fresh sessions method")
                        return  # Success!
                        
            except HomeAssistantError:
                if attempt == 1:  # Last attempt
                    raise
                _LOGGER.warning("Fresh session attempt %d failed, retrying...", attempt + 1)
                await asyncio.sleep(1.0)
            except Exception as err:
                if attempt == 1:
                    raise HomeAssistantError(f"Fresh session method failed: {err}")
                _LOGGER.warning("Fresh session attempt %d error: %s, retrying...", attempt + 1, err)
                await asyncio.sleep(1.0)

    async def _try_alternative_auth(self, host: str, port: int, password: str, speed_config: dict) -> None:
        """Try alternative authentication methods that some Deluge setups might need."""
        _LOGGER.debug("Trying alternative authentication approach")
        
        # Some Deluge versions might need different auth approach
        try:
            # Method: Try without cookies, just basic HTTP
            timeout = aiohttp.ClientTimeout(total=15)
            
            # Try 1: Basic approach without any session management
            async with aiohttp.ClientSession(timeout=timeout) as session:
                
                # Test 1: Maybe we need to call auth differently
                auth_data = {"method": "auth.login", "params": [password], "id": 1}
                
                async with session.post(f"http://{host}:{port}/json", json=auth_data) as resp:
                    result = await resp.json()
                    _LOGGER.debug("Alt auth result: %s", result)
                    
                    if result.get("result"):
                        # Try setting config immediately in same request cycle
                        config_data = {"method": "core.set_config", "params": [speed_config], "id": 2}
                        
                        async with session.post(f"http://{host}:{port}/json", json=config_data) as config_resp:
                            config_result = await config_resp.json()
                            _LOGGER.debug("Alt config result: %s", config_result)
                            
                            if not config_result.get("error"):
                                _LOGGER.info("✅ Alternative auth method succeeded!")
                                return
                            else:
                                raise HomeAssistantError(f"Alt method failed: {config_result.get('error')}")
                    else:
                        raise HomeAssistantError("Alternative auth failed")
        
        except Exception as err:
            _LOGGER.error("Alternative auth method also failed: %s", err)
            # Final message to user
            raise HomeAssistantError(
                f"All authentication methods failed. This may be a Deluge configuration issue. "
                f"Please verify that:\n"
                f"1. Deluge daemon is running\n"
                f"2. Web UI is accessible at http://{host}:{port}\n"
                f"3. Password is correct\n"
                f"4. No firewall is blocking the connection"
            )

    async def async_update(self):
        """Update the switch state and refresh attributes from sensor data."""
        # The state itself doesn't change from sensors, but this ensures 
        # attributes are refreshed regularly to show current torrent data
        _LOGGER.debug("Refreshing switch attributes from sensor data")
        # The extra_state_attributes property will be called automatically
        # and will pull fresh data from the sensor entities

    @property
    def is_on(self):
        """Return True if switch is on (preset 2)."""
        return self._is_on
    
    @property
    def available(self):
        """Return True if entity is available."""
        return self._available
    
    @property
    def icon(self):
        """Return the icon for the switch."""
        return "mdi:speedometer-slow" if self._is_on else "mdi:speedometer"
    
    @property
    def extra_state_attributes(self):
        """Return extra state attributes including monitoring data."""
        preset1_down = self.config.get(CONF_PRESET1_DOWNLOAD, DEFAULT_PRESET1_DOWNLOAD)
        preset1_up = self.config.get(CONF_PRESET1_UPLOAD, DEFAULT_PRESET1_UPLOAD)
        preset2_down = self.config.get(CONF_PRESET2_DOWNLOAD, DEFAULT_PRESET2_DOWNLOAD)
        preset2_up = self.config.get(CONF_PRESET2_UPLOAD, DEFAULT_PRESET2_UPLOAD)
        
        # Base attributes for speed presets
        attributes = {
            "preset_1_download": f"{preset1_down} KiB/s" if preset1_down != -1 else "Unlimited",
            "preset_1_upload": f"{preset1_up} KiB/s" if preset1_up != -1 else "Unlimited",
            "preset_2_download": f"{preset2_down} KiB/s" if preset2_down != -1 else "Unlimited", 
            "preset_2_upload": f"{preset2_up} KiB/s" if preset2_up != -1 else "Unlimited",
            "current_preset": "Preset 1 (Limited)" if self._is_on else "Preset 2 (Unlimited)",
            "deluge_host": f"{self.config.get('host', 'localhost')}:{self.config.get('port', 8112)}"
        }
        
        # Try to get live monitoring data from sensor entities
        try:
            # Get sensor states from the registry
            download_speed_entity = self.hass.states.get("sensor.deluge_download_speed")
            upload_speed_entity = self.hass.states.get("sensor.deluge_upload_speed")
            torrent_count_entity = self.hass.states.get("sensor.deluge_torrent_count")
            active_torrents_entity = self.hass.states.get("sensor.deluge_active_torrents")
            status_entity = self.hass.states.get("sensor.deluge_status")
            
            if download_speed_entity and download_speed_entity.state not in ["unknown", "unavailable"]:
                # Add current speeds
                download_speed = float(download_speed_entity.state) if download_speed_entity.state else 0
                upload_speed = float(upload_speed_entity.state) if upload_speed_entity and upload_speed_entity.state else 0
                
                # Convert bytes/sec to KB/s for better readability
                download_kbps = round(download_speed / 1024, 2) if download_speed > 0 else 0
                upload_kbps = round(upload_speed / 1024, 2) if upload_speed > 0 else 0
                
                attributes.update({
                    "current_download_speed": f"{download_kbps} KB/s",
                    "current_upload_speed": f"{upload_kbps} KB/s",
                    "download_speed_bytes": download_speed,
                    "upload_speed_bytes": upload_speed,
                })
            
            if torrent_count_entity and torrent_count_entity.state not in ["unknown", "unavailable"]:
                # Add torrent counts
                attributes.update({
                    "total_torrents": torrent_count_entity.state,
                    "active_torrents": torrent_count_entity.attributes.get("active_torrents", 0),
                    "downloading_torrents": torrent_count_entity.attributes.get("downloading", 0),
                    "seeding_torrents": torrent_count_entity.attributes.get("seeding", 0),
                })
            
            if active_torrents_entity:
                # Add active torrents list (up to 5 most recent for display)
                torrents = active_torrents_entity.attributes.get("torrents", [])
                if torrents:
                    attributes["torrent_list"] = torrents[:5]  # Limit to first 5 for display
                    attributes["torrent_count_display"] = len(torrents)
            
            if status_entity:
                # Add connection status
                attributes.update({
                    "connection_status": status_entity.state,
                    "last_update": status_entity.attributes.get("last_update", "Never"),
                })
                
        except Exception as err:
            _LOGGER.debug("Could not fetch sensor data for switch attributes: %s", err)
            # Continue with basic attributes if sensor data unavailable
        
        return attributes
