# Quick Start Guide - Deluge Speed Toggle Plugin

## Installation (3 steps)

1. **Build the plugin**
   ```bash
   ./build_plugin.sh
   ```
   This creates `dist/SpeedToggle-1.0.0-py3.12.egg`

2. **Install in Deluge**
   - Open Deluge
   - Go to **Edit > Preferences > Plugins**
   - Click **Install Plugin**
   - Select the `.egg` file from `dist/` directory

3. **Enable the plugin**
   - Check the box next to **SpeedToggle** in the plugins list
   - You should see a new button in the toolbar

## First Use

### Desktop (GTK UI)
- Look for toolbar button: "Speed: Normal"
- Click to toggle → "Speed: Limited"
- Click again → "Speed: Normal"

### Web UI
1. Click the **Preferences** icon (gear)
2. Find **Speed Toggle** in the left menu
3. Configure your speeds:
   - Normal: -1 = unlimited
   - Limited: e.g., 100 KB/s download, 50 KB/s upload
4. Click **Toggle Speed Now** to test

## Default Behavior

Out of the box:
- **Normal Mode**: Unlimited download & upload
- **Limited Mode**: 100 KB/s download, 50 KB/s upload
- **Initial State**: Normal (unlimited)

## Common Settings

### Conservative (for remote access)
```
Limited Mode:
  Download: 100 KB/s
  Upload: 50 KB/s
```

### Moderate (sharing bandwidth)
```
Limited Mode:
  Download: 500 KB/s
  Upload: 250 KB/s
```

### High-speed but limited
```
Limited Mode:
  Download: 5000 KB/s (5 MB/s)
  Upload: 2500 KB/s (2.5 MB/s)
```

## Troubleshooting

**Plugin not showing?**
- Make sure it's enabled in Preferences > Plugins
- Restart Deluge after enabling

**Toggle not working?**
- Check Deluge logs for errors
- Verify daemon is running (Web UI)

**Need help?**
- See [README.md](README.md) for full documentation
- See [USAGE.md](USAGE.md) for detailed examples

## That's it!

You now have a one-click solution to manage Deluge bandwidth. Perfect for:
- Accessing your server while traveling
- Limiting bandwidth during peak hours
- Ensuring other services get enough bandwidth
