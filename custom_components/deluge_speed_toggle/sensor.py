"""Deluge monitoring sensors for real-time stats."""
import logging
import asyncio
import aiohttp
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfDataRate, PERCENTAGE
from homeassistant.const import UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)  # Update every 30 seconds

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Deluge sensors from config entry."""
    config = entry.data
    
    # Create data coordinator for efficient updates
    coordinator = DelugeDataCoordinator(hass, config)
    
    # Try initial refresh but don't fail if Deluge is unavailable
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.warning("Initial Deluge connection failed, sensors will retry: %s", err)
    
    # Create sensor entities
    sensors = [
        DelugeDownloadSpeedSensor(coordinator),
        DelugeUploadSpeedSensor(coordinator),
        DelugeTorrentCountSensor(coordinator),
        DelugeActiveTorrentsSensor(coordinator),
        DelugeStatusSensor(coordinator),
    ]
    
    async_add_entities(sensors, update_before_add=False)
    _LOGGER.info("Deluge monitoring sensors added")

class DelugeDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Deluge API."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize."""
        self.host = config["host"]
        self.port = config["port"]
        self.password = config["password"]
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self._fetch_deluge_data()
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with Deluge: {exception}")

    async def _fetch_deluge_data(self):
        """Fetch data from Deluge daemon using same methods as working switch."""
        timeout = aiohttp.ClientTimeout(total=10)
        
        # Create session with cookie jar to maintain authentication
        connector = aiohttp.TCPConnector()
        cookie_jar = aiohttp.CookieJar(unsafe=True)
        
        async with aiohttp.ClientSession(
            connector=connector,
            cookie_jar=cookie_jar,
            timeout=timeout
        ) as session:
            
            # Step 1: Authenticate (same as switch)
            auth_response = await session.post(
                f"http://{self.host}:{self.port}/json",
                json={"method": "auth.login", "params": [self.password], "id": 1}
            )
            
            if auth_response.status != 200:
                raise Exception(f"Authentication HTTP error: {auth_response.status}")
                
            auth_result = await auth_response.json()
            if not auth_result.get("result"):
                raise Exception(f"Authentication failed: {auth_result}")
                
            _LOGGER.debug("Sensor authentication successful")
            
            # Step 2: Get session stats with required keys parameter
            stats_response = await session.post(
                f"http://{self.host}:{self.port}/json",
                json={
                    "method": "core.get_session_status", 
                    "params": [["download_rate", "upload_rate", "num_peers", "dht_nodes"]], 
                    "id": 2
                }
            )
            
            # Step 3: Get torrent list with required filter_dict and keys parameters
            torrents_response = await session.post(
                f"http://{self.host}:{self.port}/json",
                json={
                    "method": "core.get_torrents_status", 
                    "params": [
                        {},  # filter_dict (empty = all torrents)
                        ["name", "state", "progress", "download_payload_rate", "upload_payload_rate", "eta", "ratio", "label", "time_added", "total_size", "total_done", "queue"]  # keys
                    ], 
                    "id": 3
                }
            )
            
            # Step 4: Get config with authenticated session  
            config_response = await session.post(
                f"http://{self.host}:{self.port}/json",
                json={"method": "core.get_config", "params": [], "id": 4}
            )
            
            if stats_response.status != 200:
                raise Exception(f"Stats request failed: HTTP {stats_response.status}")
            if torrents_response.status != 200:
                raise Exception(f"Torrents request failed: HTTP {torrents_response.status}")
            if config_response.status != 200:
                raise Exception(f"Config request failed: HTTP {config_response.status}")
                
            stats = await stats_response.json()
            torrents = await torrents_response.json()
            config = await config_response.json()
            
            # Debug log the raw responses
            _LOGGER.debug("Raw stats response: %s", stats)
            _LOGGER.debug("Raw torrents response: %s", torrents)
            _LOGGER.debug("Raw config response: %s", config)
            
            # Validate API responses
            if not stats or not isinstance(stats, dict):
                raise Exception(f"Invalid stats response from Deluge: {stats}")
            if not torrents or not isinstance(torrents, dict):
                raise Exception(f"Invalid torrents response from Deluge: {torrents}")
            if not config or not isinstance(config, dict):
                raise Exception(f"Invalid config response from Deluge: {config}")
            
            # Check for API errors
            if stats.get("error"):
                raise Exception(f"Deluge stats API error: {stats.get('error')}")
            if torrents.get("error"):
                raise Exception(f"Deluge torrents API error: {torrents.get('error')}")
            if config.get("error"):
                raise Exception(f"Deluge config API error: {config.get('error')}")
            
            # Process torrent data
            torrent_data = torrents.get("result", {})
            if not isinstance(torrent_data, dict):
                torrent_data = {}
                
            torrent_list = []
            active_count = 0
            downloading_count = 0
            seeding_count = 0
            
            for torrent_id, torrent_info in torrent_data.items():
                state = torrent_info.get("state", "Unknown")
                progress = torrent_info.get("progress", 0)
                
                # Format file size
                total_size = torrent_info.get("total_size", 0)
                total_done = torrent_info.get("total_done", 0)
                
                torrent_list.append({
                    "id": torrent_id,
                    "name": torrent_info.get("name", "Unknown"),
                    "state": state,
                    "progress": round(progress, 1),
                    "download_rate": torrent_info.get("download_payload_rate", 0),
                    "upload_rate": torrent_info.get("upload_payload_rate", 0),
                    "eta": torrent_info.get("eta", 0),
                    "ratio": round(torrent_info.get("ratio", 0), 2),
                    "label": torrent_info.get("label", "No Label"),
                    "size": total_size,
                    "size_done": total_done,
                    "queue_position": torrent_info.get("queue", -1),
                    "time_added": torrent_info.get("time_added", 0)
                })
                
                # Count by state
                if state in ["Downloading", "Seeding"]:
                    active_count += 1
                if state == "Downloading":
                    downloading_count += 1
                elif state == "Seeding":
                    seeding_count += 1
            
            session_stats = stats.get("result", {})
            config_values = config.get("result", {})
            
            # Validate the results are dictionaries
            if not isinstance(session_stats, dict):
                session_stats = {}
            if not isinstance(config_values, dict):
                config_values = {}
            
            result_data = {
                "download_rate": session_stats.get("download_rate", 0),  # bytes/sec
                "upload_rate": session_stats.get("upload_rate", 0),      # bytes/sec
                "max_download_speed": config_values.get("max_download_speed", -1) * 1024,  # Convert KiB to bytes
                "max_upload_speed": config_values.get("max_upload_speed", -1) * 1024,      # Convert KiB to bytes
                "total_torrents": len(torrent_list),
                "active_torrents": active_count,
                "downloading_torrents": downloading_count,
                "seeding_torrents": seeding_count,
                "torrents": torrent_list,
                "status": "Connected"
            }
            
            # Debug logging to see what we're actually getting
            _LOGGER.debug("Deluge API Response - Session Stats: %s", session_stats)
            _LOGGER.debug("Deluge API Response - Torrents Count: %d", len(torrent_list))
            _LOGGER.debug("Deluge API Response - Download Rate: %s bytes/sec", result_data["download_rate"])
            _LOGGER.debug("Deluge API Response - Upload Rate: %s bytes/sec", result_data["upload_rate"])
            
            return result_data

class DelugeBaseSensor(SensorEntity):
    """Base class for Deluge sensors."""

    def __init__(self, coordinator: DelugeDataCoordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_should_poll = False
        
        # Add device info to group sensors with the switch
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.host}_{coordinator.port}")},
            "name": "Deluge Server",
            "manufacturer": "Deluge",
            "model": "Torrent Client",
            "sw_version": "1.1",
        }

    async def async_added_to_hass(self):
        """Connect to dispatcher when entity is added."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

class DelugeDownloadSpeedSensor(DelugeBaseSensor):
    """Deluge download speed sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Deluge Download Speed"
        self._attr_unique_id = f"{DOMAIN}_download_speed_kbs"
        self._attr_device_class = SensorDeviceClass.DATA_RATE  
        self._attr_native_unit_of_measurement = "kB/s"
        self._attr_icon = "mdi:download"

    @property
    def native_value(self):
        """Return the download speed in KB/s."""
        bytes_per_sec = self.coordinator.data.get("download_rate", 0) if self.coordinator.data else 0
        return round(bytes_per_sec / 1024, 2) if bytes_per_sec > 0 else 0

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}
        
        max_speed = self.coordinator.data.get("max_download_speed", -1)
        return {
            "max_speed_bytes_per_sec": max_speed,
            "max_speed_limited": max_speed != -1,
            "speed_limit_kb_s": f"{max_speed // 1024} KB/s" if max_speed > 0 else "Unlimited"
        }

class DelugeUploadSpeedSensor(DelugeBaseSensor):
    """Deluge upload speed sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Deluge Upload Speed"
        self._attr_unique_id = f"{DOMAIN}_upload_speed_kbs"
        self._attr_device_class = SensorDeviceClass.DATA_RATE
        self._attr_native_unit_of_measurement = "kB/s"
        self._attr_icon = "mdi:upload"

    @property
    def native_value(self):
        """Return the upload speed in KB/s."""
        bytes_per_sec = self.coordinator.data.get("upload_rate", 0) if self.coordinator.data else 0
        return round(bytes_per_sec / 1024, 2) if bytes_per_sec > 0 else 0

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}
        
        max_speed = self.coordinator.data.get("max_upload_speed", -1)
        return {
            "max_speed_bytes_per_sec": max_speed,
            "max_speed_limited": max_speed != -1,
            "speed_limit_kb_s": f"{max_speed // 1024} KB/s" if max_speed > 0 else "Unlimited"
        }

class DelugeTorrentCountSensor(DelugeBaseSensor):
    """Deluge torrent count sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Deluge Torrent Count"
        self._attr_unique_id = f"{DOMAIN}_torrent_count"
        self._attr_icon = "mdi:file-download-outline"

    @property
    def native_value(self):
        """Return the total torrent count."""
        return self.coordinator.data.get("total_torrents", 0) if self.coordinator.data else 0

    @property
    def extra_state_attributes(self):
        """Return torrent breakdown."""
        if not self.coordinator.data:
            return {}
        
        return {
            "active_torrents": self.coordinator.data.get("active_torrents", 0),
            "downloading": self.coordinator.data.get("downloading_torrents", 0),
            "seeding": self.coordinator.data.get("seeding_torrents", 0)
        }

class DelugeActiveTorrentsSensor(DelugeBaseSensor):
    """Deluge active torrents sensor with detailed info."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Deluge Active Torrents"
        self._attr_unique_id = f"{DOMAIN}_active_torrents"
        self._attr_icon = "mdi:download-multiple"

    @property
    def native_value(self):
        """Return the active torrent count."""
        return self.coordinator.data.get("active_torrents", 0) if self.coordinator.data else 0

    @property
    def extra_state_attributes(self):
        """Return detailed torrent information."""
        if not self.coordinator.data:
            return {}
        
        torrents = self.coordinator.data.get("torrents", [])
        torrent_details = {}
        
        for i, torrent in enumerate(torrents[:15]):  # Show more torrents
            # Format file size
            size_mb = torrent['size'] / (1024 * 1024) if torrent['size'] > 0 else 0
            size_str = f"{size_mb:.1f} MB" if size_mb < 1024 else f"{size_mb/1024:.1f} GB"
            
            torrent_details[f"torrent_{i+1}"] = {
                "name": torrent["name"][:60],  # Longer names
                "state": torrent["state"],
                "progress": torrent['progress'],
                "progress_text": f"{torrent['progress']}%",
                "download_speed": torrent['download_rate'] // 1024,
                "upload_speed": torrent['upload_rate'] // 1024,
                "download_speed_text": f"{torrent['download_rate'] // 1024} KB/s" if torrent['download_rate'] > 0 else "0 KB/s",
                "upload_speed_text": f"{torrent['upload_rate'] // 1024} KB/s" if torrent['upload_rate'] > 0 else "0 KB/s",
                "label": torrent.get("label", "No Label"),
                "ratio": torrent["ratio"],
                "size": size_str,
                "eta": torrent["eta"] if torrent["eta"] > 0 else None
            }
        
        return torrent_details

class DelugeStatusSensor(DelugeBaseSensor):
    """Deluge connection status sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Deluge Status"
        self._attr_unique_id = f"{DOMAIN}_status"
        self._attr_icon = "mdi:server-network"

    @property
    def native_value(self):
        """Return the connection status."""
        if not self.coordinator.data:
            return "Disconnected"
        return self.coordinator.data.get("status", "Unknown")

    @property
    def extra_state_attributes(self):
        """Return connection details."""
        if not self.coordinator.data:
            return {"last_update": "Never"}
        
        return {
            "host": self.coordinator.host,
            "port": self.coordinator.port,
            "last_update": self.coordinator.last_update_success
        }