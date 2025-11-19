# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 weasalNZ
#
# This file is part of Deluge and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

from __future__ import unicode_literals

import logging

from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export

log = logging.getLogger(__name__)

DEFAULT_PREFS = {
    'normal_download_rate': -1,  # -1 means unlimited
    'normal_upload_rate': -1,
    'limited_download_rate': 100,  # 100 KB/s
    'limited_upload_rate': 50,  # 50 KB/s
    'is_limited': False
}


class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager('speedtoggle.conf', DEFAULT_PREFS)
        self.core = component.get('Core')
        log.info('Speed Toggle plugin enabled')

    def disable(self):
        log.info('Speed Toggle plugin disabled')

    def update(self):
        pass

    @export
    def toggle_speed(self):
        """Toggle between normal and limited speed settings"""
        is_limited = self.config['is_limited']
        
        if is_limited:
            # Switch to normal (unlimited) speed
            download_rate = self.config['normal_download_rate']
            upload_rate = self.config['normal_upload_rate']
            log.info('Switching to normal speed (unlimited)')
        else:
            # Switch to limited speed
            download_rate = self.config['limited_download_rate']
            upload_rate = self.config['limited_upload_rate']
            log.info('Switching to limited speed (down: %d KB/s, up: %d KB/s)', 
                    download_rate, upload_rate)
        
        # Apply the speed limits
        self.core.set_config({'max_download_speed': download_rate})
        self.core.set_config({'max_upload_speed': upload_rate})
        
        # Toggle the state
        self.config['is_limited'] = not is_limited
        
        return not is_limited  # Return new state

    @export
    def get_status(self):
        """Get current speed toggle status"""
        return {
            'is_limited': self.config['is_limited'],
            'normal_download_rate': self.config['normal_download_rate'],
            'normal_upload_rate': self.config['normal_upload_rate'],
            'limited_download_rate': self.config['limited_download_rate'],
            'limited_upload_rate': self.config['limited_upload_rate'],
        }

    @export
    def set_config(self, config):
        """Set configuration values"""
        for key in config.keys():
            self.config[key] = config[key]

    @export
    def get_config(self):
        """Get configuration values"""
        return self.config.config
