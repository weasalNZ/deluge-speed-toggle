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

from deluge.ui.client import client
from deluge.plugins.pluginbase import WebPluginBase

from deluge.common import resource_filename

log = logging.getLogger(__name__)


class WebUI(WebPluginBase):
    
    scripts = [resource_filename(__package__, 'data/speedtoggle.js')]

    def enable(self):
        log.info('Speed Toggle Web UI enabled')

    def disable(self):
        log.info('Speed Toggle Web UI disabled')
