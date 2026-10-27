# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Renamed the integration's Home Assistant display name to Deluge RPC Control; the internal domain remains unchanged.
- Setup now asks for an optional **Server Name** (default `Deluge`). It is appended to entity names (e.g. `sensor.download_speed_deluge`, `switch.speed_toggle_deluge`). Unique IDs don't include the name, so existing entities and IDs are unaffected.
- Renamed the speed switch to Speed Toggle Deluge (`switch.speed_toggle_deluge`) and made the switch and toggle service find sensors and the switch by unique ID instead of fixed entity IDs.
- Updated sensor names to use a trailing Deluge marker and made sensor unique IDs specific to each configured server.
- Updated the status card to discover the new sensor IDs while retaining support for legacy IDs.

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