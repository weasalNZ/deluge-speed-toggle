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

from gi.repository import Gtk

from deluge.ui.client import client
from deluge.plugins.pluginbase import Gtk3PluginBase
import deluge.component as component

log = logging.getLogger(__name__)


class GtkUI(Gtk3PluginBase):
    def enable(self):
        self.builder = Gtk.Builder()
        self.window = component.get('MainWindow')
        self.toolbar = self.window.get_toolbar()
        
        # Create toggle button
        self.toggle_button = Gtk.ToolButton()
        self.toggle_button.set_icon_name('network-transmit-receive')
        self.toggle_button.set_label('Toggle Speed')
        self.toggle_button.set_tooltip_text('Toggle between normal and limited bandwidth')
        self.toggle_button.connect('clicked', self.on_toggle_clicked)
        
        # Add button to toolbar
        self.toolbar.insert(self.toggle_button, -1)
        self.toggle_button.show()
        
        # Update button state
        self.update_button_state()
        
        log.info('Speed Toggle GTK UI enabled')

    def disable(self):
        if self.toggle_button:
            self.toolbar.remove(self.toggle_button)
        log.info('Speed Toggle GTK UI disabled')

    def on_toggle_clicked(self, widget):
        """Handle toggle button click"""
        client.speedtoggle.toggle_speed().addCallback(self.on_toggle_complete)

    def on_toggle_complete(self, is_limited):
        """Callback after toggle completes"""
        status = "Limited" if is_limited else "Normal"
        log.info('Speed toggled to: %s', status)
        self.update_button_state()

    def update_button_state(self):
        """Update button appearance based on current state"""
        client.speedtoggle.get_status().addCallback(self.on_status_received)

    def on_status_received(self, status):
        """Update UI with current status"""
        if status['is_limited']:
            self.toggle_button.set_label('Speed: Limited')
        else:
            self.toggle_button.set_label('Speed: Normal')
