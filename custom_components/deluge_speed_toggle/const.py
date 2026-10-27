DOMAIN = "deluge_speed_toggle"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_PASSWORD = "password"

# Preset 1 - Slow/Limited speeds (in KiB/s)
CONF_PRESET1_DOWNLOAD = "preset1_download"
CONF_PRESET1_UPLOAD = "preset1_upload"

# Preset 2 - Fast/Unlimited speeds (in KiB/s)
CONF_PRESET2_DOWNLOAD = "preset2_download"
CONF_PRESET2_UPLOAD = "preset2_upload"

# Default speed values in KiB/s (-1 means unlimited in Deluge)
DEFAULT_PRESET1_DOWNLOAD = 500
DEFAULT_PRESET1_UPLOAD = 100
DEFAULT_PRESET2_DOWNLOAD = -1  # Unlimited
DEFAULT_PRESET2_UPLOAD = -1    # Unlimited
