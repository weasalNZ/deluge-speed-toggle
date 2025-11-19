# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 weasalNZ
#
# This file is part of Deluge and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

from setuptools import setup, find_packages

__plugin_name__ = 'SpeedToggle'
__author__ = 'weasalNZ'
__author_email__ = 'weasalnz@users.noreply.github.com'
__version__ = '1.0.0'
__url__ = 'https://github.com/weasalNZ/deluge-speed-toggle'
__license__ = 'GPLv3'
__description__ = 'Toggle between normal and limited bandwidth speeds'
__long_description__ = """
Speed Toggle Plugin for Deluge

This plugin allows you to quickly toggle between normal (unlimited) and limited 
bandwidth speeds. This is particularly useful when you need to:
- Access your Deluge server remotely while traveling
- Limit bandwidth usage to avoid impacting other services
- Quickly switch between high-speed and bandwidth-conservative modes

Features:
- One-click toggle between normal and limited speeds
- Configurable speed limits for both modes
- Works with GTK UI (desktop) and Web UI
- Visual status indicator showing current mode
"""

__pkg_data__ = {__plugin_name__.lower(): ['data/*']}

setup(
    name=__plugin_name__,
    version=__version__,
    description=__description__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    license=__license__,
    long_description=__long_description__,

    packages=find_packages(),
    package_data=__pkg_data__,

    entry_points="""
    [deluge.plugin.core]
    %s = speedtoggle:CorePlugin
    [deluge.plugin.gtkui]
    %s = speedtoggle:GtkUIPlugin
    [deluge.plugin.webui]
    %s = speedtoggle:WebUIPlugin
    """ % ((__plugin_name__, )*3)
)
