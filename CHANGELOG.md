# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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