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

  _toggle() {
    this.hass.callService('switch', 'toggle', {
      entity_id: this.config.entity
    });
  }

  static get styles() {
    return css`
      ha-card {
        background: var(--card-background-color);
        border-radius: 8px;
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px 0 rgba(0, 0, 0, 0.14));
        overflow: hidden;
        width: 100%;
        box-sizing: border-box;
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
      }

      .torrent-name-container {
        flex: 1;
        margin-right: 8px;
      }

      .torrent-name {
        font-size: 12px;
        font-weight: 500;
        color: var(--primary-text-color);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.2;
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
        gap: 6px;
        font-size: 10px;
        color: var(--secondary-text-color);
        flex-shrink: 1;
        min-width: 0;
        overflow: hidden;
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