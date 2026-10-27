# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Renamed the integration's Home Assistant display name to Deluge RPC Control; the internal domain remains unchanged.
- Entities now use Home Assistant's standard device-name + entity-name naming (has_entity_name): sensors are Download Speed, Upload Speed, Torrent Count, Active Torrents and Status, and the switch is Speed Toggle, giving IDs like sensor.deluge_download_speed and switch.deluge_speed_toggle. The device is named after the optional **Server Name** entered at setup (default `Deluge`), so IDs follow that name (e.g. `sensor.seedbox_status`).
- Sensor unique IDs are now specific to each configured host and port, and the switch and toggle service find sensors and the switch by unique ID instead of fixed entity IDs.
- The card derives the sensor prefix from the switch entity and supports an explicit `sensors:` mapping.

## [1.4] - 2025-11-19

### Added
- Initial release of Deluge Speed Toggle integration
- Toggle switch for quick speed preset switching  
- Configuration flow with connection validation
- Support for custom download/upload speed presets
- Three-tier authentication fallback system
- Comprehensive logging and error handling
- Services for manual speed control and testing

### Features
- Switch entity with ON=limited speed, OFF=unlimited speed
- Configurable speed presets (default: 500/100 KiB/s limited)
- Secure password-protected Deluge API connection
- Real-time connection testing and validation
- Home Assistant 2025.x compatibility

### Technical Details
- Domain: `deluge_speed_toggle`
- Platform: `switch`
- Config Flow: ✅ Enabled
- IoT Class: Local Polling
- Minimum HA Version: 2024.1.0