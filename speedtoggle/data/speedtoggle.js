/*!
 * speedtoggle.js
 *
 * Copyright (C) 2025 weasalNZ
 *
 * This file is part of Deluge and is licensed under GNU General Public License 3.0, or later, with
 * the additional special exception to link portions of this program with the OpenSSL library.
 * See LICENSE for more details.
 */

Ext.ns('Deluge.ux.preferences');

/**
 * @class Deluge.ux.preferences.SpeedTogglePage
 * @extends Ext.Panel
 */
Deluge.ux.preferences.SpeedTogglePage = Ext.extend(Ext.Panel, {
    title: _('Speed Toggle'),
    header: false,
    layout: 'fit',
    border: false,

    initComponent: function() {
        Deluge.ux.preferences.SpeedTogglePage.superclass.initComponent.call(this);

        this.form = this.add({
            xtype: 'form',
            layout: 'form',
            border: false,
            autoHeight: true,
            bodyStyle: 'padding: 5px;',
            items: [{
                xtype: 'fieldset',
                title: _('Normal Speed Settings'),
                autoHeight: true,
                defaultType: 'spinnerfield',
                items: [{
                    fieldLabel: _('Download Rate (KB/s)'),
                    name: 'normal_download_rate',
                    value: -1,
                    minValue: -1,
                    maxValue: 99999,
                    decimalPrecision: 0
                }, {
                    fieldLabel: _('Upload Rate (KB/s)'),
                    name: 'normal_upload_rate',
                    value: -1,
                    minValue: -1,
                    maxValue: 99999,
                    decimalPrecision: 0
                }]
            }, {
                xtype: 'fieldset',
                title: _('Limited Speed Settings'),
                autoHeight: true,
                defaultType: 'spinnerfield',
                items: [{
                    fieldLabel: _('Download Rate (KB/s)'),
                    name: 'limited_download_rate',
                    value: 100,
                    minValue: 1,
                    maxValue: 99999,
                    decimalPrecision: 0
                }, {
                    fieldLabel: _('Upload Rate (KB/s)'),
                    name: 'limited_upload_rate',
                    value: 50,
                    minValue: 1,
                    maxValue: 99999,
                    decimalPrecision: 0
                }]
            }, {
                xtype: 'container',
                layout: 'hbox',
                items: [{
                    xtype: 'button',
                    text: _('Toggle Speed Now'),
                    handler: this.onToggleClick,
                    scope: this
                }, {
                    xtype: 'displayfield',
                    id: 'speedToggleStatus',
                    value: _('Status: Normal'),
                    style: 'margin-left: 10px; padding-top: 5px;'
                }]
            }]
        });

        this.on('show', this.loadConfig, this);
    },

    loadConfig: function() {
        deluge.client.speedtoggle.get_config({
            success: function(config) {
                this.form.getForm().setValues(config);
                this.updateStatus();
            },
            scope: this
        });
    },

    updateStatus: function() {
        deluge.client.speedtoggle.get_status({
            success: function(status) {
                var statusField = Ext.getCmp('speedToggleStatus');
                if (statusField) {
                    statusField.setValue(status.is_limited ? 
                        _('Status: Limited') : _('Status: Normal'));
                }
            },
            scope: this
        });
    },

    onToggleClick: function() {
        deluge.client.speedtoggle.toggle_speed({
            success: function(is_limited) {
                var statusField = Ext.getCmp('speedToggleStatus');
                if (statusField) {
                    statusField.setValue(is_limited ? 
                        _('Status: Limited') : _('Status: Normal'));
                }
                Deluge.Notification.info(
                    _('Speed Toggled'),
                    is_limited ? _('Speed limited mode enabled') : 
                                _('Normal speed mode enabled')
                );
            },
            scope: this
        });
    }
});

Deluge.plugins.SpeedTogglePlugin = Ext.extend(Deluge.Plugin, {
    name: 'SpeedToggle',

    onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function() {
        this.prefsPage = deluge.preferences.addPage(
            new Deluge.ux.preferences.SpeedTogglePage()
        );

        // Add toolbar button
        this.speedToggleBtn = deluge.toolbar.add({
            id: 'speedToggleBtn',
            text: _('Toggle Speed'),
            iconCls: 'icon-preferences',
            handler: this.onToolbarToggle,
            scope: this
        });

        this.updateToolbarButton();
        
        // Update button every 5 seconds
        this.updateTask = Ext.TaskMgr.start({
            run: this.updateToolbarButton,
            scope: this,
            interval: 5000
        });
    },

    onToolbarToggle: function() {
        deluge.client.speedtoggle.toggle_speed({
            success: function(is_limited) {
                this.updateToolbarButton();
                Deluge.Notification.info(
                    _('Speed Toggled'),
                    is_limited ? _('Speed limited mode enabled') : 
                                _('Normal speed mode enabled')
                );
            },
            scope: this
        });
    },

    updateToolbarButton: function() {
        deluge.client.speedtoggle.get_status({
            success: function(status) {
                if (this.speedToggleBtn) {
                    this.speedToggleBtn.setText(status.is_limited ? 
                        _('Speed: Limited') : _('Speed: Normal'));
                }
            },
            scope: this
        });
    }
});

Deluge.registerPlugin('SpeedToggle', Deluge.plugins.SpeedTogglePlugin);
