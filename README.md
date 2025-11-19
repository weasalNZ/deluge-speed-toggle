# Deluge Speed Toggle Plugin

A Deluge plugin that allows you to quickly toggle between normal (unlimited) and limited bandwidth speeds. This is particularly useful when accessing your Deluge server remotely while traveling or when you need to limit bandwidth usage to avoid impacting other services.

## Features

- **One-Click Toggle**: Instantly switch between normal and limited speed modes
- **Configurable Limits**: Set custom speed limits for both download and upload
- **Multi-Interface Support**: Works with both GTK UI (desktop) and Web UI
- **Visual Status**: Clear indicator showing current speed mode
- **Persistent Settings**: Configuration saved between sessions

## Use Cases

- **Remote Access**: Limit bandwidth when accessing your server from overseas or on limited connections
- **Bandwidth Management**: Prevent Deluge from consuming all available bandwidth
- **Time-of-Day Control**: Manually switch to limited mode during peak hours
- **Server Sharing**: Ensure other services get adequate bandwidth when needed

## Installation

### Method 1: From Source

1. Clone this repository:
   ```bash
   git clone https://github.com/weasalNZ/deluge-speed-toggle.git
   cd deluge-speed-toggle
   ```

2. Build the plugin egg:
   ```bash
   python setup.py bdist_egg
   ```

3. The plugin egg will be created in the `dist/` directory

4. Install the plugin in Deluge:
   - Open Deluge and go to **Preferences > Plugins**
   - Click **Install Plugin**
   - Select the `.egg` file from the `dist/` directory
   - Enable the **SpeedToggle** plugin

### Method 2: Manual Installation

1. Copy the `speedtoggle` directory to your Deluge plugins directory:
   - Linux: `~/.config/deluge/plugins/`
   - Windows: `%APPDATA%\deluge\plugins\`
   - macOS: `~/Library/Application Support/deluge/plugins/`

2. Restart Deluge and enable the plugin in **Preferences > Plugins**

## Configuration

### Default Settings

- **Normal Mode**: Unlimited download and upload (-1 means unlimited)
- **Limited Mode**: 100 KB/s download, 50 KB/s upload

### Changing Settings

#### GTK UI (Desktop)
The plugin adds a toolbar button labeled "Toggle Speed" or "Speed: Normal/Limited". Click it to toggle between modes.

#### Web UI
1. Go to **Preferences > Speed Toggle**
2. Configure your preferred speeds:
   - **Normal Speed Settings**: Set to -1 for unlimited or specify rates in KB/s
   - **Limited Speed Settings**: Set your bandwidth limits in KB/s
3. Click **Toggle Speed Now** to switch modes immediately

## Usage

### Toggle Speed Mode

Simply click the toggle button in the toolbar (both GTK and Web UI) to switch between:
- **Normal Mode**: Uses your configured normal speeds (default: unlimited)
- **Limited Mode**: Uses your configured limited speeds (default: 100/50 KB/s)

The button text will update to show the current mode:
- "Speed: Normal" - Currently in normal/unlimited mode
- "Speed: Limited" - Currently in bandwidth-limited mode

### Typical Workflow

1. **Setup**: Configure your desired speed limits in the plugin preferences
2. **Normal Operation**: Use normal (unlimited) mode for maximum performance
3. **Remote Access**: Toggle to limited mode before traveling or when bandwidth is constrained
4. **Return**: Toggle back to normal mode when you're back on your home network

## Technical Details

### Speed Limits

- Speed values are in kilobytes per second (KB/s)
- Use `-1` for unlimited speeds
- Minimum limited speed: 1 KB/s
- Maximum speed: 99999 KB/s

### Configuration Storage

The plugin stores its configuration in `speedtoggle.conf` in your Deluge config directory.

### API

The plugin exposes the following RPC methods:

- `toggle_speed()`: Toggle between normal and limited modes
- `get_status()`: Get current status and configuration
- `set_config(config)`: Update configuration values
- `get_config()`: Retrieve current configuration

## Development

### Building from Source

```bash
# Install development dependencies
pip install deluge setuptools

# Build the plugin
python setup.py bdist_egg

# The plugin will be in dist/
```

### Project Structure

```
deluge-speed-toggle/
├── speedtoggle/
│   ├── __init__.py       # Plugin initialization
│   ├── core.py           # Core plugin logic
│   ├── gtkui.py          # GTK UI interface
│   ├── webui.py          # Web UI interface
│   └── data/
│       └── speedtoggle.js # Web UI JavaScript
├── setup.py              # Plugin metadata and build config
└── README.md             # This file
```

## License

This plugin is licensed under the GNU General Public License v3.0 or later, with the additional special exception to link portions of this program with the OpenSSL library.

## Credits

Created by weasalNZ as a side project to learn plugin development and to solve a practical need for bandwidth management when traveling overseas.

## Support

For issues, questions, or contributions, please visit:
https://github.com/weasalNZ/deluge-speed-toggle

## Changelog

### Version 1.0.0
- Initial release
- Toggle between normal and limited speeds
- GTK UI support with toolbar button
- Web UI support with preferences page
- Configurable speed limits
- Persistent configuration