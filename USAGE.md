# Speed Toggle Plugin - Example Usage

This document provides examples of how to use the Speed Toggle plugin.

## Installation Verification

After installing the plugin:

1. Open Deluge
2. Go to **Edit > Preferences > Plugins**
3. Enable **SpeedToggle**
4. You should see a new button in the toolbar

## GTK UI (Desktop Client)

### Toolbar Button
- Look for the toolbar button labeled "Speed: Normal" or "Speed: Limited"
- Click it to toggle between modes
- The button text updates to reflect current state

### Visual Indicators
- **"Speed: Normal"** - No bandwidth limits applied
- **"Speed: Limited"** - Using configured limited speeds

## Web UI

### Access Plugin Settings
1. Go to **Preferences** (click the gear icon)
2. Look for **Speed Toggle** in the left sidebar
3. Configure your speeds:
   - Normal Download/Upload Rate (-1 for unlimited)
   - Limited Download/Upload Rate (in KB/s)

### Toggle Speed
- Click **Toggle Speed Now** button in preferences
- Or use the toolbar button in the main interface
- Status field shows current mode

### Toolbar Integration
- The toolbar includes a "Toggle Speed" button
- Button text shows current status
- Click to instantly toggle modes

## Configuration Examples

### Example 1: Unlimited to Conservative
```
Normal Mode:
  Download: -1 (unlimited)
  Upload: -1 (unlimited)

Limited Mode:
  Download: 100 KB/s
  Upload: 50 KB/s
```

### Example 2: High-Speed to Moderate
```
Normal Mode:
  Download: 10000 KB/s (10 MB/s)
  Upload: 5000 KB/s (5 MB/s)

Limited Mode:
  Download: 1000 KB/s (1 MB/s)
  Upload: 500 KB/s (500 KB/s)
```

### Example 3: Asymmetric Limits
```
Normal Mode:
  Download: -1 (unlimited)
  Upload: 1000 KB/s (seed at 1 MB/s)

Limited Mode:
  Download: 500 KB/s
  Upload: 100 KB/s
```

## Use Case Scenarios

### Scenario 1: Traveling Overseas
**Problem**: You're traveling and need to access your home Deluge server, but you're on a limited or slow connection.

**Solution**:
1. Before leaving, set reasonable limited speeds (e.g., 100/50 KB/s)
2. While traveling, toggle to limited mode via Web UI
3. Your torrents continue downloading without overwhelming your connection
4. Toggle back to normal when you return home

### Scenario 2: Peak Hours Management
**Problem**: Your ISP throttles during peak hours or you share bandwidth with family.

**Solution**:
1. Configure limited mode to be respectful (e.g., 200/100 KB/s)
2. Manually toggle to limited during peak hours
3. Toggle back to normal during off-peak times

### Scenario 3: Background Downloading
**Problem**: You want torrents to download in background without affecting streaming/gaming.

**Solution**:
1. Set limited mode to conservative speeds
2. Toggle to limited when you need bandwidth for other activities
3. Toggle back to normal when you're done

## Troubleshooting

### Plugin Not Visible
- Ensure plugin is enabled in Preferences > Plugins
- Restart Deluge after enabling
- Check Deluge logs for errors

### Toggle Not Working
- Verify plugin is enabled
- Check that you have permission to change settings
- Ensure Deluge daemon is running (if using Web UI)

### Settings Not Saved
- Configuration is stored in `speedtoggle.conf`
- Ensure Deluge has write permissions to config directory
- Check for config file conflicts

## Advanced Usage

### Command Line (if using Deluge Console)
If you're using the Deluge console client, you can interact with the plugin via RPC:

```python
# Get status
deluge-console "plugin.method('speedtoggle', 'get_status')"

# Toggle speed
deluge-console "plugin.method('speedtoggle', 'toggle_speed')"

# Set configuration
deluge-console "plugin.method('speedtoggle', 'set_config', {'limited_download_rate': 200})"
```

### Automation Ideas
While the plugin doesn't include automatic scheduling, you could:
- Use cron/Task Scheduler to call toggle commands at specific times
- Integrate with home automation systems
- Create scripts that toggle based on network conditions

## FAQ

**Q: Can I set different speeds for different torrents?**
A: No, this plugin sets global speed limits for all torrents.

**Q: Does this plugin schedule automatic toggles?**
A: No, toggling is manual. You need to click the button to switch modes.

**Q: Will my settings persist after restart?**
A: Yes, the plugin saves your configuration and current state.

**Q: Can I use this with Deluge Daemon?**
A: Yes, the plugin works with daemon mode via Web UI.

**Q: What happens if I change Deluge's speed settings manually?**
A: The plugin won't override manual changes until you toggle again.
