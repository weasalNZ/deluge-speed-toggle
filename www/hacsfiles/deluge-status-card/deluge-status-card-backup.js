const LitElement = Object.getPrototypeOf(
  customElements.get("ha-panel-lovelace")
);
const html = LitElement.prototype.html;
const css = LitElement.prototype.css;

class DelugeStatusCard extends LitElement {

  static get properties() {
    return {
      config: {},
      hass: {}
    };
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('entity (switch entity) is required');
    }

    this.config = {
      name: 'Deluge Server',
      show_title: true,
      show_speed: true,
      show_torrents: true,
      ...config
    };
  }

  render() {
    if (!this.config || !this.hass) {
      return html``;
    }

    const entity = this.hass.states[this.config.entity];
    if (!entity) {
      return html`<ha-card>Entity not found: ${this.config.entity}</ha-card>`;
    }

    return html`
      <ha-card>
        ${this.config.show_title ? html`
          <div class="card-header">
            ${this.config.name}
            <div class="switch-container">
              <ha-switch
                .checked=${entity.state === 'on'}
                @change=${this._toggle}
                title="Speed Limit Toggle">
              </ha-switch>
            </div>
          </div>
        ` : ''}
        
        <div class="card-content">
          ${this.renderStatus(entity)}
          ${this.config.show_speed ? this.renderSpeedSection() : ''}
          ${this.config.show_torrents ? this.renderTorrentSection() : ''}
          ${this.renderTorrentManagement()}
        </div>
      </ha-card>
    `;
  }

  renderStatus(entity) {
    const isLimited = entity.state === 'on';
    const statusText = isLimited ? 'Speed Limited' : 'Unlimited Speed';
    const statusColor = isLimited ? '#ff9800' : '#4caf50';
    
    // Get preset info from entity attributes if available
    const preset1Download = entity.attributes?.preset_1_download || '500 KiB/s';
    const preset1Upload = entity.attributes?.preset_1_upload || '100 KiB/s';
    const speedText = isLimited ? `${preset1Download.replace(' KiB/s', '')}/${preset1Upload.replace(' KiB/s', '')} KB/s` : 'No limits';
    
    return html`
      <div class="status-row">
        <div class="status-indicator ${isLimited ? 'limited' : 'unlimited'}" style="background-color: ${statusColor}">
          ${isLimited ? '🚶' : '♾️'}
        </div>
        <div class="status-info">
          <div class="status-primary">${statusText}</div>
          <div class="status-secondary">${speedText}</div>
        </div>
      </div>
    `;
  }

  renderSpeedSection() {
    // Try to find speed sensors
    const downloadEntity = this.hass.states['sensor.deluge_download_speed'];
    const uploadEntity = this.hass.states['sensor.deluge_upload_speed'];
    
    // If sensors don't exist at all
    if (!downloadEntity || !uploadEntity) {
      return html`
        <div class="info-section">
          <div class="section-title">
            <ha-icon icon="mdi:speedometer"></ha-icon>
            Current Speed
          </div>
          <div class="unavailable">Speed monitoring sensors not available</div>
        </div>
      `;
    }
    
    // Sensors exist, use them even if state is unknown/unavailable
    // This handles cases where sensors are initializing

    const downloadSpeed = this.formatSpeed(downloadEntity.state);
    const uploadSpeed = this.formatSpeed(uploadEntity.state);
    
    return html`
      <div class="info-section">
        <div class="section-title">
          <ha-icon icon="mdi:speedometer"></ha-icon>
          Current Speed
        </div>
        <div class="speed-grid">
          <div class="speed-item">
            <ha-icon icon="mdi:download" class="download-icon"></ha-icon>
            <span class="speed-label">Download</span>
            <span class="speed-value">${downloadSpeed}</span>
          </div>
          <div class="speed-item">
            <ha-icon icon="mdi:upload" class="upload-icon"></ha-icon>
            <span class="speed-label">Upload</span>
            <span class="speed-value">${uploadSpeed}</span>
          </div>
        </div>
      </div>
    `;
  }

  renderTorrentSection() {
    // Try to find torrent sensors
    const countEntity = this.hass.states['sensor.deluge_torrent_count'];
    const activeEntity = this.hass.states['sensor.deluge_active_torrents'];
    
    // If sensors don't exist at all
    if (!countEntity) {
      return html`
        <div class="info-section">
          <div class="section-title">
            <ha-icon icon="mdi:download-multiple"></ha-icon>
            Torrents
          </div>
          <div class="unavailable">Torrent monitoring sensors not available</div>
        </div>
      `;
    }
    
    // Sensors exist, use them

    const totalCount = countEntity.state || '0';
    const activeCount = activeEntity ? activeEntity.state : '0';
    const downloading = countEntity.attributes?.downloading || 0;
    const seeding = countEntity.attributes?.seeding || 0;
    
    return html`
      <div class="info-section">
        <div class="section-title">
          <ha-icon icon="mdi:download-multiple"></ha-icon>
          Torrents (${totalCount})
        </div>
        <div class="torrent-grid">
          <div class="torrent-stat">
            <div class="stat-value">${activeCount}</div>
            <div class="stat-label">Active</div>
          </div>
          <div class="torrent-stat">
            <div class="stat-value">${downloading}</div>
            <div class="stat-label">Downloading</div>
          </div>
          <div class="torrent-stat">
            <div class="stat-value">${seeding}</div>
            <div class="stat-label">Seeding</div>
          </div>
          <div class="torrent-stat">
            <div class="stat-value">${totalCount}</div>
            <div class="stat-label">Total</div>
          </div>
        </div>
        ${this.renderTorrentList(activeEntity)}
      </div>
    `;
  }

  renderTorrentList(activeEntity) {
    if (!activeEntity || !activeEntity.attributes) {
      return html`<div class="no-torrents">No torrent details available</div>`;
    }

    const attributes = activeEntity.attributes;
    const torrents = [];
    
    // Extract torrent details from attributes
    for (let i = 1; i <= 15; i++) {
      const torrentKey = `torrent_${i}`;
      if (attributes[torrentKey]) {
        torrents.push(attributes[torrentKey]);
      }
    }

    if (torrents.length === 0) {
      return html`<div class="no-torrents">No active torrents</div>`;
    }

    return html`
      <div class="torrent-list">
        ${torrents.map(torrent => html`
          <div class="torrent-item ${torrent.state.toLowerCase()}">
            <div class="torrent-header">
              <div class="torrent-name-container">
                <div class="torrent-name" title="${torrent.name}">${torrent.name}</div>
                ${torrent.label && torrent.label !== 'No Label' ? html`
                  <div class="torrent-label">${torrent.label}</div>
                ` : ''}
              </div>
              <div class="torrent-state-container">
                <span class="torrent-state ${torrent.state.toLowerCase()}">${torrent.state}</span>
                <span class="torrent-progress">${torrent.progress}%</span>
              </div>
            </div>
            <div class="torrent-details">
              <div class="torrent-speeds">
                <span class="speed-down">↓ ${torrent.download_speed_text || '0 KB/s'}</span>
                <span class="speed-up">↑ ${torrent.upload_speed_text || '0 KB/s'}</span>
                <span class="ratio">Ratio: ${torrent.ratio || '0.00'}</span>
              </div>
              <div class="torrent-progress-bar">
                <div class="progress-fill ${torrent.state.toLowerCase()}" 
                     style="width: ${torrent.progress}%"></div>
              </div>
            </div>
          </div>
        `)}
      </div>
    `;
  }

  formatSpeed(speedKBs) {
    if (!speedKBs || speedKBs === 'unknown' || speedKBs === 'unavailable' || speedKBs == 0) {
      return '0 KB/s';
    }
    
    const kbs = parseFloat(speedKBs);
    if (isNaN(kbs)) return '0 KB/s';
    if (kbs < 1024) return `${kbs.toFixed(1)} KB/s`;
    return `${(kbs / 1024).toFixed(1)} MB/s`;
  }

  renderTorrentManagement() {
    return html`
      <div class="torrent-management">
        <div class="section-title">
          <ha-icon icon="mdi:plus-circle"></ha-icon>
          Add Torrent
        </div>
        <div class="add-torrent-section">
          <div class="input-group">
            <input 
              type="text" 
              placeholder="Paste magnet link or torrent URL here..."
              class="torrent-input"
              @keypress=${this._handleKeyPress}
              id="torrentInput"
            />
            <button class="add-button" @click=${this._addTorrent}>
              <ha-icon icon="mdi:plus"></ha-icon>
            </button>
          </div>
          <div class="file-input-group">
            <input 
              type="file" 
              accept=".torrent"
              class="file-input"
              id="torrentFileInput"
              @change=${this._handleFileUpload}
            />
            <label for="torrentFileInput" class="file-input-label">
              <ha-icon icon="mdi:file-upload"></ha-icon>
              Upload .torrent file
            </label>
          </div>
        </div>
      </div>
    `;
  }

  _toggle() {
    this.hass.callService('switch', 'toggle', {
      entity_id: this.config.entity
    });
  }

  _handleKeyPress(e) {
    if (e.key === 'Enter') {
      this._addTorrent();
    }
  }

  _addTorrent() {
    const input = this.shadowRoot.querySelector('#torrentInput');
    const value = input.value.trim();
    
    if (!value) {
      this._showNotification('Please enter a magnet link or torrent URL', 'warning');
      return;
    }

    if (value.startsWith('magnet:')) {
      this.hass.callService('deluge_speed_toggle', 'add_torrent', {
        magnet_link: value
      }).then(() => {
        this._showNotification('Magnet link added successfully!', 'success');
        input.value = '';
      }).catch(err => {
        this._showNotification('Failed to add magnet link: ' + err.message, 'error');
      });
    } else if (value.startsWith('http://') || value.startsWith('https://')) {
      this.hass.callService('deluge_speed_toggle', 'add_torrent', {
        torrent_url: value
      }).then(() => {
        this._showNotification('Torrent URL added successfully!', 'success');
        input.value = '';
      }).catch(err => {
        this._showNotification('Failed to add torrent URL: ' + err.message, 'error');
      });
    } else {
      this._showNotification('Please enter a valid magnet link (magnet:) or HTTP URL', 'warning');
    }
  }

  _handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.torrent')) {
      this._showNotification('Please select a .torrent file', 'warning');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const arrayBuffer = event.target.result;
        const bytes = new Uint8Array(arrayBuffer);
        
        // Use a safer approach for base64 encoding
        let binary = '';
        const chunkSize = 8192;
        for (let i = 0; i < bytes.length; i += chunkSize) {
          const chunk = bytes.slice(i, i + chunkSize);
          binary += String.fromCharCode.apply(null, chunk);
        }
        const base64String = btoa(binary);
        
        this.hass.callService('deluge_speed_toggle', 'add_torrent', {
          torrent_data: base64String
        }).then(() => {
          this._showNotification('Torrent file uploaded successfully!', 'success');
          e.target.value = '';
        }).catch(err => {
          this._showNotification('Failed to upload torrent file: ' + err.message, 'error');
        });
      } catch (error) {
        this._showNotification('Error processing torrent file: ' + error.message, 'error');
      }
    };

    reader.readAsArrayBuffer(file);
  }

  _showNotification(message, type = 'info') {
    console.log(`Deluge ${type}: ${message}`);
    
    // Try to use Home Assistant's notification system
    if (this.hass && this.hass.callService) {
      this.hass.callService('persistent_notification', 'create', {
        message: message,
        title: 'Deluge Speed Toggle',
        notification_id: 'deluge_' + Date.now()
      }).catch(() => {
        // Fallback - just log to console if notification fails
        console.log(`Deluge notification: ${message}`);
      });
    }
  }

  static get styles() {
    return css`
      ha-card {
        background: var(--card-background-color);
        border-radius: 8px;
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px 0 rgba(0, 0, 0, 0.14));
        overflow: hidden;
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
      }
      
      * {
        box-sizing: border-box;
        max-width: 100%;
      }

      .card-header {
        background: var(--primary-color);
        color: var(--text-primary-color);
        padding: 12px 16px;
        font-weight: 500;
        font-size: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .switch-container {
        display: flex;
        align-items: center;
      }

      .card-content {
        padding: 16px;
        overflow: hidden;
        box-sizing: border-box;
        max-width: 100%;
      }

      .status-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        padding: 8px;
        background: var(--primary-background-color);
        border-radius: 6px;
      }

      .status-indicator {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
      }

      .status-info {
        flex: 1;
      }

      .status-primary {
        font-weight: 500;
        color: var(--primary-text-color);
        margin-bottom: 2px;
      }

      .status-secondary {
        font-size: 12px;
        color: var(--secondary-text-color);
      }

      .info-section {
        margin-bottom: 16px;
      }

      .section-title {
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 500;
        color: var(--primary-text-color);
        margin-bottom: 8px;
        font-size: 14px;
      }

      .speed-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
      }

      .speed-item {
        background: var(--primary-background-color);
        padding: 8px;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
      }

      .download-icon {
        color: #2196f3;
      }

      .upload-icon {
        color: #4caf50;
      }

      .speed-label {
        font-size: 12px;
        color: var(--secondary-text-color);
      }

      .speed-value {
        font-size: 14px;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .torrent-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-bottom: 12px;
      }

      .torrent-stat {
        background: var(--primary-background-color);
        padding: 8px;
        border-radius: 4px;
        text-align: center;
      }

      .stat-value {
        font-size: 16px;
        font-weight: 600;
        color: var(--primary-text-color);
        display: block;
      }

      .stat-label {
        font-size: 10px;
        color: var(--secondary-text-color);
        margin-top: 2px;
        display: block;
      }

      .unavailable, .no-torrents {
        font-size: 12px;
        color: var(--secondary-text-color);
        font-style: italic;
        text-align: center;
        padding: 8px;
      }

      .torrent-list {
        margin-top: 12px;
        max-height: 250px;
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: var(--scrollbar-thumb-color, #888) transparent;
      }

      .torrent-list::-webkit-scrollbar {
        width: 6px;
      }

      .torrent-list::-webkit-scrollbar-track {
        background: transparent;
      }

      .torrent-list::-webkit-scrollbar-thumb {
        background: var(--scrollbar-thumb-color, #888);
        border-radius: 3px;
      }

      .torrent-item {
        background: var(--primary-background-color);
        border-radius: 6px;
        padding: 8px;
        margin-bottom: 6px;
        border-left: 3px solid var(--divider-color);
        overflow: hidden;
        max-width: 100%;
        box-sizing: border-box;
      }

      .torrent-item.downloading {
        border-left-color: #4caf50;
      }

      .torrent-item.seeding {
        border-left-color: #ff9800;
      }

      .torrent-item.paused {
        border-left-color: #9e9e9e;
      }

      .torrent-item.error {
        border-left-color: #f44336;
      }

      .torrent-item:last-child {
        margin-bottom: 0;
      }

      .torrent-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 6px;
        max-width: 100%;
        overflow: hidden;
        width: 100%;
      }

      .torrent-name-container {
        flex: 1;
        margin-right: 8px;
        min-width: 0;
        overflow: hidden;
        max-width: calc(100% - 80px);
        width: 0;
      }

      .torrent-name {
        font-size: 12px;
        font-weight: 500;
        color: var(--primary-text-color);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.2;
        max-width: 100%;
        width: 100%;
        display: block;
      }

      .torrent-label {
        font-size: 10px;
        color: var(--secondary-text-color);
        background: var(--card-background-color);
        padding: 2px 6px;
        border-radius: 12px;
        margin-top: 4px;
        display: inline-block;
        border: 1px solid var(--divider-color);
        font-weight: 500;
      }

      .torrent-state-container {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 2px;
        flex-shrink: 0;
        min-width: 70px;
        width: 70px;
      }

      .torrent-state {
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 10px;
        text-transform: capitalize;
        font-weight: 500;
      }

      .torrent-state.downloading {
        background: rgba(76, 175, 80, 0.2);
        color: #4caf50;
        border: 1px solid rgba(76, 175, 80, 0.3);
      }

      .torrent-state.seeding {
        background: rgba(255, 152, 0, 0.2);
        color: #ff9800;
        border: 1px solid rgba(255, 152, 0, 0.3);
      }

      .torrent-state.paused {
        background: rgba(158, 158, 158, 0.2);
        color: #9e9e9e;
        border: 1px solid rgba(158, 158, 158, 0.3);
      }

      .torrent-state.error {
        background: rgba(244, 67, 54, 0.2);
        color: #f44336;
        border: 1px solid rgba(244, 67, 54, 0.3);
      }

      .torrent-state.queued {
        background: rgba(156, 39, 176, 0.2);
        color: #9c27b0;
        border: 1px solid rgba(156, 39, 176, 0.3);
      }

      .torrent-progress {
        font-size: 10px;
        color: var(--secondary-text-color);
        font-weight: 500;
      }

      .torrent-details {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 4px;
        min-width: 0;
        flex-wrap: nowrap;
      }

      .torrent-speeds {
        display: flex;
        gap: 4px;
        font-size: 9px;
        color: var(--secondary-text-color);
        flex-shrink: 1;
        min-width: 0;
        overflow: hidden;
        white-space: nowrap;
      }

      .speed-down {
        color: #2196f3;
        white-space: nowrap;
      }

      .speed-up {
        color: #4caf50;
        white-space: nowrap;
      }

      .ratio {
        color: var(--secondary-text-color);
        white-space: nowrap;
        flex-shrink: 0;
      }

      .torrent-progress-bar {
        width: 60px;
        min-width: 60px;
        height: 4px;
        background: var(--divider-color);
        border-radius: 2px;
        overflow: hidden;
        flex-shrink: 0;
      }

      .progress-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.3s ease;
      }

      .progress-fill.downloading {
        background: linear-gradient(90deg, #4caf50, #66bb6a);
        box-shadow: 0 0 4px rgba(76, 175, 80, 0.3);
      }

      .progress-fill.seeding {
        background: linear-gradient(90deg, #ff9800, #ffb74d);
        box-shadow: 0 0 4px rgba(255, 152, 0, 0.3);
      }

      .progress-fill.paused {
        background: linear-gradient(90deg, #9e9e9e, #bdbdbd);
      }

      .progress-fill.error {
        background: linear-gradient(90deg, #f44336, #ef5350);
        box-shadow: 0 0 4px rgba(244, 67, 54, 0.3);
      }

      .progress-fill.queued {
        background: linear-gradient(90deg, #9c27b0, #ba68c8);
      }

      ha-icon {
        --mdc-icon-size: 16px;
      }

      .status-indicator ha-icon {
        --mdc-icon-size: 20px;
      }

      /* Torrent Management Styles */
      .torrent-management {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid var(--divider-color);
      }

      .add-torrent-section {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .input-group {
        display: flex;
        gap: 8px;
        align-items: center;
      }

      .torrent-input {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        background: var(--primary-background-color);
        color: var(--primary-text-color);
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s;
      }

      .torrent-input:focus {
        border-color: var(--primary-color);
      }

      .torrent-input::placeholder {
        color: var(--secondary-text-color);
      }

      .add-button {
        padding: 8px 12px;
        border: none;
        border-radius: 4px;
        background: var(--primary-color);
        color: var(--text-primary-color);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 14px;
        transition: background-color 0.2s;
        white-space: nowrap;
      }

      .add-button:hover {
        background: var(--primary-color-dark, var(--primary-color));
        opacity: 0.9;
      }

      .file-input-group {
        display: flex;
        align-items: center;
      }

      .file-input {
        display: none;
      }

      .file-input-label {
        padding: 8px 12px;
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        transition: background-color 0.2s, border-color 0.2s;
        white-space: nowrap;
      }

      .file-input-label:hover {
        background: var(--primary-background-color);
        border-color: var(--primary-color);
      }
    `;
  }
}

// Only define if not already defined
if (!customElements.get('deluge-status-card')) {
  customElements.define('deluge-status-card', DelugeStatusCard);
}

// Add to custom card registry
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'deluge-status-card',
  name: 'Deluge Status Card',
  preview: true,
  description: 'Monitor Deluge torrent client with speed control and statistics.',
});