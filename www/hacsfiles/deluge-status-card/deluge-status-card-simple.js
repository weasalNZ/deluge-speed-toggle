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
      return html`<div>Loading...</div>`;
    }

    const entity = this.hass.states[this.config.entity];
    if (!entity) {
      return html`<ha-card>Entity not found: ${this.config.entity}</ha-card>`;
    }

    return html`
      <ha-card>
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
        
        <div class="card-content">
          <div>Status: ${entity.state}</div>
          <div>Test message - card is working!</div>
        </div>
      </ha-card>
    `;
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

      .card-content {
        padding: 16px;
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