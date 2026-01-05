
# Deluge Speed Toggle

A Home Assistant custom component that provides a simple toggle switch to quickly switch between two preset download/upload speed limits for the Deluge torrent client.

## :notebook_with_decorative_cover: Table of Contents

- [Requirements](#requirements)
- [Features & Overview](#sparkles-features--overview)
- [Example Card Screenshot](#camera-example-card-screenshot)
- [Quick Start / Installation](#rocket-quick-start--installation)
  - [Method 1: HACS (Recommended)](#method-1-hacs-recommended)
  - [Method 2: Manual Installation](#method-2-manual-installation)
- [Configuration Wizard](#configuration-wizard)
- [Speed Units](#speed-units)
- [Installation: Custom Lovelace Card](#installation-custom-lovelace-card)
- [Card Configuration Options](#card-configuration-options)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Testing the Deluge JSON-RPC API](#testing-the-deluge-json-rpc-api)
- [Support & Links](#support--links)
- [License](#license)
- [Version History](#version-history)

---


## Requirements

- Home Assistant 2022.0 or newer
- Deluge BitTorrent client (v2.x recommended) with Web UI enabled
- Deluge Web UI password (required for authentication)
- HACS (Home Assistant Community Store) for easy installation (optional, but recommended)

---

## :sparkles: Features & Overview

Deluge Speed Toggle provides a simple way to quickly switch your Deluge torrent client between two speed presets (e.g., "Limited" and "Unlimited") directly from Home Assistant. This is ideal for:

- Instantly throttling or unthrottling your downloads/uploads
- Automating speed changes based on time of day or network conditions
- Integrating Deluge speed control into your Home Assistant dashboards and automations

**Key Features:**

- 🟢 **Toggle Switch**: One Home Assistant switch entity to toggle between two speed presets
- ⚡ **Fast**: Changes take effect immediately in Deluge
- 🛠️ **Configurable**: Set your own speed limits for each preset (including unlimited)
- 🔒 **Secure**: Uses Deluge's built-in authentication
- 📊 **Status Card**: Optional Lovelace card shows current speeds, status, and torrent stats
- 🔄 **Automation Ready**: Use in Home Assistant automations and scripts

---

<!-- Screenshots -->
## :camera: Example Card Screenshot

![Deluge Status Card Example](www/hacsfiles/deluge-status-card/deluge-status-card-example.png)
> The card displays torrent status, speed, and connection state. In this example, Deluge is disconnected, but the card still shows torrent statistics and history.

---

## :rocket: Quick Start / Installation

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


### Method 2: Manual Installation

**Setup Steps:**
1. Copy the component files to your Home Assistant `custom_components` directory:
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
2. Restart Home Assistant to load the custom component

---
**Add Integration**:
   - Go to Settings → Devices & Services
   - Search for "Deluge Speed Toggle"

When you add the integration, you'll be prompted to enter:
#### Connection Settings
- **Host**: IP address or hostname of your Deluge server (default: `localhost`)
- **Port**: Deluge web UI port (default: `8112`)
- **Password**: Deluge web UI password (required)

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

  ---
You can edit these options later by clicking the integration in Home Assistant and selecting "Configure".


  ## Installation: Custom Lovelace Card

  To install the Deluge Status custom Lovelace card in Home Assistant:

1. **Copy the card file to your Home Assistant:**
    ```
    /config/www/hacsfiles/deluge-status-card/deluge-status-card.js
    ```
2. **Add the resource in Home Assistant:**
    - Go to **Settings → Dashboards → Resources**
    - Add resource: `/local/hacsfiles/deluge-status-card/deluge-status-card.js` (type: JavaScript Module)
3. **Add the card to your dashboard:**
    ```yaml
    type: custom:deluge-status-card
    entity: switch.deluge_speed_toggle
    name: "Deluge Server"
    show_speed: true
    show_torrents: true
    ```
  ## Card Configuration Options

  | Option         | Default         | Description                                 |
  |---------------|----------------|---------------------------------------------|
  | `entity`      | **Required**    | Your Deluge speed toggle switch entity       |
  | `name`        | "Deluge Server"| Display name in card header                  |
  | `show_title`  | true           | Show/hide the card header                   |
  | `show_speed`  | true           | Show/hide current speed section             |
  | `show_torrents`| true           | Show/hide torrent statistics                |

  ---

  ## Usage

### Using the Switch in Home Assistant UI
- Go to **Settings → Devices & Services → Entities** in Home Assistant.
- Find the **Deluge Speed Toggle** switch.
- Click the toggle to switch between your configured speed presets:
  - **OFF** = Preset 1 (Limited speeds)
  - **ON** = Preset 2 (Unlimited speeds)

### Using in Automations
You can automate speed changes with Home Assistant automations:
```yaml
automation:
  - alias: "Limit Deluge at night"
      at: "22:00:00"
    action:
      entity_id: switch.deluge_speed_toggle

  - alias: "Unlimited Deluge in morning"
    trigger:
      platform: time
      at: "08:00:00"
    action:
      service: switch.turn_on
      entity_id: switch.deluge_speed_toggle
```
  - `upload`: Upload speed in KiB/s (`-1` for unlimited)
- **Example**:
```yaml
  upload: 500
```
**Error:** "Cannot connect to Deluge" appears during setup
- Verify Deluge is running and accessible on the network
- Test with: `curl -X POST http://DELUGE_HOST:8112/json`
- Confirm the correct web UI password is used
- Make sure Deluge's JSON-RPC API is enabled

### Authentication Failed
**Error:** "Deluge authentication failed: Invalid password"
- Double-check your Deluge web UI password
- Avoid special characters that may cause issues
- Restart Deluge and try again
## Troubleshooting

### Cannot Connect to Deluge
**Error:** "Cannot connect to Deluge" appears during setup
- Verify Deluge is running and accessible on the network
- Test with: `curl -X POST http://DELUGE_HOST:8112/json`
- Confirm the correct web UI password is used
- Make sure Deluge's JSON-RPC API is enabled

### Authentication Failed
**Error:** "Deluge authentication failed: Invalid password"
- Double-check your Deluge web UI password
- Avoid special characters that may cause issues
- Restart Deluge and try again

### Switch Not Responding
- Check Home Assistant logs for errors (Settings → System → Logs)
- Ensure Deluge is running and reachable
- Verify network connectivity between Home Assistant and Deluge
- Restart Home Assistant


### Card Not Displaying or Entity ID Issues
- Ensure the expected entity IDs exist (e.g., `switch.deluge_speed_toggle`).
- If entity IDs have numbers at the end (e.g., `sensor.deluge_download_speed_2`), recreate entity IDs in Home Assistant:
    1. Go to **Settings > Devices & Services**
    2. Find **Deluge Speed Toggle** and click the arrow next to your Deluge Server
    3. Click the three dots (⋮) in the top right corner
    4. Select **Recreate Entity IDs**
    5. Restart Home Assistant if prompted

#### Example: Entity ID Error
If your Deluge Status Card does not display correctly and you notice that entity IDs have numbers at the end (e.g., `sensor.deluge_download_speed_2`), it may look similar to the screenshot below:

![Deluge Status Card Entity ID Error](www/hacsfiles/deluge-status-card/deluge-status-card-entity-id-error.png)

This usually means the card cannot find the expected entities. See the steps above to recreate entity IDs and resolve this issue.

### Logging
Enable debug logging in `configuration.yaml` for more details:
```yaml
logger:
  logs:
    custom_components.deluge_speed: debug
```
Then check logs in Home Assistant UI: **Settings → System → Logs**

### Switch Not Responding
- Check Home Assistant logs for errors (Settings → System → Logs)
- Ensure Deluge is running and reachable
- Verify network connectivity between Home Assistant and Deluge
- Restart Home Assistant

### Card Not Displaying or Entity ID Issues
- Ensure the expected entity IDs exist (e.g., `switch.deluge_speed_toggle`)
- If entity IDs have numbers at the end (e.g., `sensor.deluge_download_speed_2`), recreate entity IDs in Home Assistant:
  1. Go to **Settings > Devices & Services**
  2. Find **Deluge Speed Toggle** and click the arrow next to your Deluge Server
  3. Click the three dots (⋮) in the top right corner
  4. Select **Recreate Entity IDs**
  5. Restart Home Assistant if prompted

#### Example: Entity ID Error
If your Deluge Status Card does not display correctly and you notice that entity IDs have numbers at the end (e.g., `sensor.deluge_download_speed_2`), it may look similar to the screenshot below:

![Deluge Status Card Entity ID Error](www/hacsfiles/deluge-status-card/deluge-status-card-entity-id-error.png)

This usually means the card cannot find the expected entities. See the steps above to recreate entity IDs and resolve this issue.

### Logging
Enable debug logging in `configuration.yaml` for more details:
```yaml
logger:
  logs:
    custom_components.deluge_speed: debug
```
Then check logs in Home Assistant UI: **Settings → System → Logs**

## Testing the Deluge JSON-RPC API

If you encounter connection or authentication issues, you can manually test the Deluge JSON-RPC API using curl:

**Test Connection:**
```bash
curl -X POST http://<DELUGE_HOST>:8112/json \
  -H "Content-Type: application/json" \
  -d '{
    "method": "auth.login",
    "params": ["your-password"],
    "id": 1
**Set Speeds Example:**
```bash
curl -X POST http://<DELUGE_HOST>:8112/json \
  -H "Content-Type: application/json" \
  -d '{
      "max_upload_speed": 100
    }],
    "id": 2
  }'
```

Replace `<DELUGE_HOST>` and `your-password` with your actual Deluge server address and password.

## Support & Links

- **Home Assistant Forum:** [Community Discussions](https://community.home-assistant.io/)
- **GitHub Issues:** [Report bugs or request features](https://github.com/weasalNZ/deluge-speed-toggle/issues)
- **Deluge Documentation:** [Official Deluge Docs](https://deluge-torrent.org/)

## License

This custom component is provided as-is for use with Home Assistant under the MIT License.

## Version History

- **1.2**: Update all files previously under `/www/community/deluge-status-card/` are now under `/www/hacsfiles/deluge-status-card/`.
- **1.1**: Added switch entity toggle, dual preset support, comprehensive error handling and logging
- **1.0**: Initial release with set_speed service