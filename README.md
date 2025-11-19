# Deluge Speed Toggle

A Home Assistant custom component that provides a simple toggle switch to quickly switch between two preset download/upload speed limits for the Deluge torrent client.

## Features

- 🎚️ **Easy Toggle Switch**: One-click switching between two speed presets in the Home Assistant UI
- ⚙️ **Customizable Presets**: Set your own download and upload speed limits for each preset
- 📊 **Both Upload & Download Control**: Adjust both directions simultaneously
- 🔒 **Secure**: Password-protected connection to Deluge
- 📝 **Logging**: Comprehensive logging for troubleshooting
- ✅ **Connection Validation**: Tests Deluge connection before saving configuration

## Installation

### Method 1: HACS (Recommended)

1. **Add Custom Repository** in HACS:
   - Go to HACS → Integrations → ⋮ (three dots) → Custom repositories
   - Add URL: `https://github.com/weasalNZ/deluge-speed-toggle`
   - Category: Integration
   - Click "Add"

2. **Install via HACS**:
   - Search for "Deluge Speed Toggle" in HACS Integrations
   - Click "Download" 
   - Restart Home Assistant

3. **Add Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Deluge Speed Toggle"

### Method 2: Manual Installation

#### Requirements

- Home Assistant (Core 2024.1.0 or later)
- Deluge torrent client with JSON-RPC API enabled  
- Network access to Deluge from Home Assistant

#### Setup Steps

1. **Copy the component files** to your Home Assistant `custom_components` directory:
   ```
   ~/.homeassistant/custom_components/deluge_speed_toggle/
   ├── __init__.py
   ├── config_flow.py
   ├── const.py
   ├── manifest.json
   ├── services.yaml
   ├── speed_toggle.py
   ├── switch.py
   └── README.md
   ```

2. **Restart Home Assistant** to load the custom component

3. **Add the integration** via Settings → Devices & Services → Create Automation:
   - Click **Create Automation**
   - Search for "Deluge Speed"
   - Follow the configuration wizard

## Configuration

### Configuration Wizard

When you add the integration, you'll be prompted to enter:

#### Connection Settings
- **Host**: IP address or hostname of your Deluge server (default: `localhost`)
- **Port**: Deluge web UI port (default: `8112`)
- **Password**: Deluge web UI password (required)

#### Speed Presets
- **Preset 1 Name**: Label for the first preset (default: "Limited")
  - **Download Speed**: Download limit in KiB/s (default: `500`)
  - **Upload Speed**: Upload limit in KiB/s (default: `100`)

- **Preset 2 Name**: Label for the second preset (default: "Unlimited")
  - **Download Speed**: Download limit in KiB/s (default: `-1` for unlimited)
  - **Upload Speed**: Upload limit in KiB/s (default: `-1` for unlimited)

### Speed Units

All speeds are specified in **KiB/s** (kilobytes per second):
- Use `-1` to set unlimited speed for either direction
- Common values:
  - `100` = 100 KiB/s (≈ 0.8 Mbps)
  - `500` = 500 KiB/s (≈ 4 Mbps)
  - `1000` = 1000 KiB/s (≈ 8 Mbps)
  - `5000` = 5000 KiB/s (≈ 40 Mbps)
  - `-1` = Unlimited

## Usage

### Using the Switch in Home Assistant UI

1. Open Home Assistant → **Settings → Devices & Services → Entities**
2. Find **"Deluge Speed Toggle"** switch
3. Click the toggle to switch between presets:
   - **OFF** = Preset 1 (Limited speeds)
   - **ON** = Preset 2 (Unlimited speeds)

### Using in Automations

You can automate speed changes with Home Assistant automations:

```yaml
automation:
  - alias: "Limit Deluge at night"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: switch.turn_off
      entity_id: switch.deluge_speed_toggle

  - alias: "Unlimited Deluge in morning"
    trigger:
      platform: time
      at: "08:00:00"
    action:
      service: switch.turn_on
      entity_id: switch.deluge_speed_toggle
```

### Using the Service Call

You can also make direct service calls for fine-grained control:

**Service**: `deluge_speed.set_speed`

**Parameters**:
- `download`: Download speed in KiB/s (-1 for unlimited)
- `upload`: Upload speed in KiB/s (-1 for unlimited)

**Example**:
```yaml
service: deluge_speed.set_speed
data:
  download: 2000
  upload: 500
```

## Troubleshooting

### Connection Failed

**Error**: "Cannot connect to Deluge" appears during setup

**Solutions**:
1. **Verify Deluge is running**: Check that Deluge daemon/service is active
2. **Check host/port**: Ensure the correct IP/hostname and port are entered
   - Verify port is not blocked by firewall
   - Test: `curl -X POST http://DELUGE_HOST:8112/json`
3. **Check password**: Ensure you're using the correct web UI password
4. **Enable JSON-RPC**: Verify Deluge has JSON-RPC API enabled in preferences
5. **Network connectivity**: Verify Home Assistant can reach Deluge (same network or routing)

### Deluge Authentication Failed

**Error**: "Deluge authentication failed: Invalid password"

**Solutions**:
1. Check your Deluge web UI password in Deluge settings
2. Ensure no special characters are causing issues
3. Verify the password isn't set to empty
4. Restart Deluge and try again

### Switch Not Responding

**Error**: Toggle switch exists but doesn't respond to clicks

**Solutions**:
1. Check Home Assistant logs for errors:
   ```
   Settings → System → Logs → Search for "deluge_speed"
   ```
2. Verify Deluge is still running and reachable
3. Check network connectivity between Home Assistant and Deluge
4. Restart Home Assistant

### Logs Show "Connection Timeout"

**Error**: Logs show repeated timeout errors

**Solutions**:
1. Increase network timeout by checking firewall/network latency
2. Verify Deluge JSON-RPC is responding:
   ```bash
   curl -X POST http://localhost:8112/json \
     -H "Content-Type: application/json" \
     -d '{"method":"auth.login","params":["your-password"],"id":1}'
   ```
3. Check if Deluge host is overloaded
4. Consider using hostname instead of IP (or vice versa)

## Logging

The component provides detailed logging for troubleshooting. Enable debug logging in `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.deluge_speed: debug
```

Then check logs in Home Assistant UI: **Settings → System → Logs**

### Common Log Messages

| Message | Meaning |
|---------|---------|
| `Initialized DelugeSpeedToggleSwitch` | Component loaded successfully |
| `Successfully authenticated with Deluge` | Connected to Deluge successfully |
| `Successfully set Deluge speeds` | Speed preset applied successfully |
| `Deluge authentication failed` | Password is incorrect or connection failed |
| `Cannot connect to Deluge` | Network issue or Deluge offline |
| `Deluge connection timeout` | Response taking too long (>10 seconds) |

## Deluge JSON-RPC API

This component communicates with Deluge via its JSON-RPC API. For manual testing:

**Test Connection**:
```bash
curl -X POST http://localhost:8112/json \
  -H "Content-Type: application/json" \
  -d '{
    "method": "auth.login",
    "params": ["your-password"],
    "id": 1
  }'
```

**Set Speeds**:
```bash
curl -X POST http://localhost:8112/json \
  -H "Content-Type: application/json" \
  -d '{
    "method": "core.set_config",
    "params": [{
      "max_download_speed": 500,
      "max_upload_speed": 100
    }],
    "id": 2
  }'
```

## Development

### Project Structure

```
deluge_speed/
├── __init__.py              # Integration entry point
├── config_flow.py           # Configuration UI
├── const.py                 # Constants and defaults
├── manifest.json            # Integration metadata
├── services.yaml            # Service definitions
├── speed_toggle.py          # Switch entity and service logic
├── README.md                # This file
└── .github/
    └── copilot-instructions.md  # AI agent documentation
```

### Making Changes

1. **Update constants**: Modify `const.py` if adding new config keys
2. **Modify services**: Update `services.yaml` for new services
3. **Add features**: Implement in `speed_toggle.py` and register in `__init__.py`
4. **Test thoroughly**: Verify with a real Deluge instance

## Support & Issues

- **Home Assistant Forum**: [Community Discussions](https://community.home-assistant.io/)
- **GitHub Issues**: Report bugs or request features
- **Deluge Documentation**: [Official Deluge Docs](https://deluge-torrent.org/)

## License

This custom component is provided as-is for use with Home Assistant.

## Version History

- **1.1**: Added switch entity toggle, dual preset support, comprehensive error handling and logging
- **1.0**: Initial release with set_speed service
