/**
 * Brainstorm Hub - Interactive Mindmap Card
 * Version: 1.4.13
 * 
 * An interactive, visual mindmap for Home Assistant ideas and brainstorm notes.
 * Minimalist UI / Mushroom-inspired theme styling.
 */

class BrainstormMindmapCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._selectedCategory = "all"; // 'all', 'Inbox', etc.
    let savedColorMode = "theme";
    try {
      savedColorMode = localStorage.getItem("brainstorm_color_mode") || "theme";
    } catch {}
    this._colorMode = savedColorMode; // 'theme' | 'multicolor'
    this._scale = 1;
    this._panX = 0;
    this._panY = 0;
    this._isPanning = false;
    this._startPan = { x: 0, y: 0 };
    this._nodePositions = new Map(); // id -> {x, y}
    this._centerPos = { x: 400, y: 300 };
    this._activeDrag = null; // { id, startMouseX, startMouseY, startNodeX, startNodeY }
    this._pendingDrag = null; // { id, cloud, startMouseX, startMouseY, startNodeX, startNodeY }
    this._initialized = false;
    this._lastUpdated = null;
    this._lastDataSignature = "";
    this._isModalOpen = false;
  }

  static async getConfigElement() {
    return document.createElement("brainstorm-mindmap-card-editor");
  }

  static getStubConfig(hass) {
    return {
      title: "Brainstorm Mindmap",
      sensor: "sensor.brainstorm_ideen_ubersicht",
      color_mode: "theme",
      height: "calc(100vh - 32px)",
      default_category: "Inbox",
      show_bulb_watermark: true,
      show_toolbar: true,
      show_color_toggle: true,
      show_fullscreen_btn: true,
      show_controls: true,
      show_add_btn: true,
    };
  }

  setConfig(config) {
    this._config = {
      title: "Brainstorm Mindmap",
      sensor: "sensor.brainstorm_ideen_ubersicht",
      color_mode: "theme",
      height: "calc(100vh - 32px)",
      default_category: "Inbox",
      show_bulb_watermark: true,
      show_toolbar: true,
      show_color_toggle: true,
      show_fullscreen_btn: true,
      show_controls: true,
      show_add_btn: true,
      ...config,
    };
    if (config.color_mode) {
      this._colorMode = config.color_mode;
    }
    if (this._config.default_category && !this._initialized) {
      this._selectedCategory = String(this._config.default_category).trim();
    }
    if (this._initialized) {
      this._applyConfigUpdates();
    }
  }

  _applyConfigUpdates() {
    if (!this.shadowRoot) return;
    const titleEl = this.shadowRoot.getElementById("cardTitle");
    if (titleEl) titleEl.textContent = this._config.title !== undefined ? this._config.title : "Brainstorm Mindmap";

    const topBar = this.shadowRoot.querySelector(".top-bar");
    if (topBar) topBar.style.display = this._config.show_toolbar !== false ? "flex" : "none";

    const bulbWrap = this.shadowRoot.querySelector(".center-bulb-wrapper");
    if (bulbWrap) bulbWrap.style.display = this._config.show_bulb_watermark !== false ? "block" : "none";

    const colorModeBtn = this.shadowRoot.getElementById("colorModeBtn");
    if (colorModeBtn) colorModeBtn.style.display = this._config.show_color_toggle !== false ? "inline-flex" : "none";

    const fullscreenBtn = this.shadowRoot.getElementById("fullscreenToggleBtn");
    if (fullscreenBtn) fullscreenBtn.style.display = this._config.show_fullscreen_btn !== false ? "inline-flex" : "none";

    const controlsPanel = this.shadowRoot.querySelector(".controls-panel");
    if (controlsPanel) controlsPanel.style.display = this._config.show_controls !== false ? "flex" : "none";

    const addNoteBtn = this.shadowRoot.getElementById("addNoteBtn");
    if (addNoteBtn) addNoteBtn.style.display = this._config.show_add_btn !== false ? "flex" : "none";

    const cardRoot = this.shadowRoot.getElementById("cardRoot");
    if (cardRoot && this._config.height && !this._isFullscreen) {
      cardRoot.style.height = this._config.height;
    }

    this._lastDataSignature = "";
    this._updateContent();
  }

  getCardSize() {
    return 6;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._initDom();
    }
    const sensor = this._getSensorEntity();
    if (!sensor) return;

    const ideas = sensor.attributes.ideas || [];
    const categories = sensor.attributes.categories || [];
    const sig = `${sensor.last_updated}_${this._selectedCategory}_${ideas.length}_${categories.length}`;
    if (this._lastDataSignature === sig) {
      return;
    }
    // Don't re-render and interrupt active interactions
    if (this._activeDrag || this._pendingDrag || this._isModalOpen) {
      return;
    }
    this._lastDataSignature = sig;
    this._updateContent();
  }

  _getSensorEntity() {
    if (!this._hass) return null;
    const conf = this._config.entity || this._config.sensor;
    if (
      conf &&
      this._hass.states[conf] &&
      this._hass.states[conf].attributes &&
      Array.isArray(this._hass.states[conf].attributes.ideas)
    ) {
      return this._hass.states[conf];
    }
    if (this._hass.states["sensor.brainstorm_hub_brainstorm_ideen_ubersicht"]) {
      return this._hass.states["sensor.brainstorm_hub_brainstorm_ideen_ubersicht"];
    }
    if (this._hass.states["sensor.brainstorm_ideen_ubersicht"]) {
      return this._hass.states["sensor.brainstorm_ideen_ubersicht"];
    }
    return conf && this._hass.states[conf] ? this._hass.states[conf] : null;
  }

  _getCategoryColor(category) {
    if (this._colorMode === "theme") {
      // Dynamic Home Assistant Theme integration
      const themeColors = {
        Inbox: "var(--primary-color, #03a9f4)",
        Smarthome: "color-mix(in srgb, var(--primary-color, #03a9f4) 85%, var(--accent-color, #38bdf8))",
        "Haus & Garten": "color-mix(in srgb, var(--primary-color, #03a9f4) 75%, var(--success-color, #10b981))",
        Projekte: "color-mix(in srgb, var(--primary-color, #03a9f4) 80%, var(--info-color, #818cf8))",
        Alltag: "color-mix(in srgb, var(--primary-color, #03a9f4) 80%, var(--warning-color, #fb923c))",
        Ideen: "color-mix(in srgb, var(--primary-color, #03a9f4) 85%, var(--accent-color, #f472b6))",
        default: "var(--primary-color, #03a9f4)",
      };
      return themeColors[category] || "var(--primary-color, #03a9f4)";
    }

    const colors = {
      Inbox: "var(--primary-color, #3b82f6)",
      Smarthome: "#0284c7",
      "Haus & Garten": "#16a34a",
      Projekte: "#9333ea",
      Alltag: "#ea580c",
      Ideen: "#db2777",
      default: "#475569",
    };
    return colors[category] || colors.default;
  }

  _getSourceIcon(source) {
    if (!source) return "📝";
    const s = String(source).toLowerCase();
    if (s.includes("assist")) return "✨";
    if (s.includes("alexa") || s.includes("voice") || s.includes("speech")) return "🎙️";
    if (s.includes("mobile") || s.includes("handy") || s.includes("companion")) return "📱";
    if (s.includes("dashboard")) return "💻";
    return "📝";
  }

  _formatTime(isoString) {
    if (!isoString) return "";
    try {
      const date = new Date(isoString);
      const now = new Date();
      const diffSec = Math.floor((now - date) / 1000);
      if (diffSec < 60) return "gerade eben";
      if (diffSec < 3600) return `vor ${Math.floor(diffSec / 60)}m`;
      if (diffSec < 86400) return `vor ${Math.floor(diffSec / 3600)}h`;
      return date.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit" });
    } catch {
      return "";
    }
  }

  _initDom() {
    if (!this._hass || !this._config) return;
    this._initialized = true;

    this.shadowRoot.innerHTML = `
      <style>
        * {
          box-sizing: border-box;
          user-select: none;
        }
        :host {
          display: block;
          width: 100%;
          height: 100%;
          font-family: var(--ha-font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif);
        }
        ha-card {
          position: relative;
          width: 100%;
          height: 100%;
          min-height: 480px;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border-radius: var(--ha-card-border-radius, 16px);
          border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.12)));
          box-shadow: var(--ha-card-box-shadow, 0 4px 20px rgba(0,0,0,0.06));
          overflow: hidden;
          display: flex;
          flex-direction: column;
          color: var(--primary-text-color, #212121);
        }

        /* Top Bar */
        .top-bar {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          z-index: 20;
          padding: 12px 16px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: linear-gradient(180deg, var(--ha-card-background, var(--card-background-color, #ffffff)) 0%, transparent 100%);
          pointer-events: none;
        }
        .top-left {
          display: flex;
          align-items: center;
          gap: 10px;
          pointer-events: auto;
        }
        .top-right {
          display: flex;
          align-items: center;
          gap: 8px;
          pointer-events: auto;
        }
        .brand-logo {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          overflow: hidden;
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .brand-logo img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .title {
          font-size: 1.05rem;
          font-weight: 700;
          color: var(--primary-text-color, #212121);
        }
        .top-tool-btn,
        .fullscreen-btn {
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          color: var(--primary-text-color, #212121);
          border-radius: 50%;
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 1.05rem;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
          transition: all 0.2s ease;
        }
        .top-tool-btn:hover,
        .fullscreen-btn:hover {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
          color: var(--primary-color, #03a9f4);
          transform: scale(1.05);
        }
        .fullscreen-btn.is-fullscreen {
          background: var(--error-color, #db4437);
          border-color: var(--error-color, #db4437);
          color: #ffffff;
        }
        .fullscreen-btn.is-fullscreen:hover {
          filter: brightness(0.92);
        }
        ha-card.is-fullscreen {
          position: fixed !important;
          top: 0 !important;
          left: 0 !important;
          width: 100vw !important;
          height: 100vh !important;
          height: 100dvh !important;
          z-index: 99999 !important;
          border-radius: 0 !important;
          margin: 0 !important;
        }
        .pills-container {
          display: flex;
          align-items: center;
          gap: 6px;
          overflow-x: auto;
          max-width: 58%;
          padding: 4px 6px;
          pointer-events: auto;
          scrollbar-width: none;
        }
        .pills-container::-webkit-scrollbar {
          display: none;
        }
        .cat-pill {
          padding: 6px 14px;
          min-height: 34px;
          font-size: 0.8rem;
          font-weight: 600;
          border-radius: 18px;
          cursor: pointer;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          color: var(--secondary-text-color, #64748b);
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
          white-space: nowrap;
          transition: all 0.2s ease;
        }
        .cat-pill:hover {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
          color: var(--primary-text-color, #212121);
          transform: translateY(-1px);
        }
        .cat-pill.active {
          background: color-mix(in srgb, var(--category-color, var(--primary-color)) 12%, var(--card-background-color, #ffffff));
          color: var(--category-color, var(--primary-color));
          border-color: var(--category-color, var(--primary-color));
          box-shadow: 0 1px 6px color-mix(in srgb, var(--category-color, var(--primary-color)) 20%, transparent);
        }

        /* Map Canvas & Viewport */
        .canvas-area {
          flex: 1 1 auto;
          width: 100%;
          height: 100%;
          min-height: 0;
          position: relative;
          cursor: grab;
          overflow: hidden;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
        }
        .canvas-area:active {
          cursor: grabbing;
        }
        .grid-bg {
          position: absolute;
          inset: 0;
          background-image: radial-gradient(var(--divider-color, rgba(127, 127, 127, 0.16)) 1px, transparent 1px);
          background-size: 24px 24px;
          pointer-events: none;
        }
        .viewport {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          transform-origin: 0 0;
          will-change: transform;
        }

        /* SVG Connectors */
        svg.connectors {
          position: absolute;
          top: 0;
          left: 0;
          width: 2000px;
          height: 2000px;
          pointer-events: none;
          z-index: 1;
        }
        .synapse-path {
          fill: none;
          stroke: var(--divider-color, rgba(127, 127, 127, 0.25));
          stroke-width: 1.8;
          stroke-dasharray: 4, 4;
          transition: stroke 0.2s ease, stroke-width 0.2s ease;
        }
        .synapse-path.highlight {
          stroke: var(--primary-color, #03a9f4);
          stroke-width: 2.6;
          stroke-dasharray: none;
        }

        /* Center Node */
        .center-node {
          position: absolute;
          width: 154px;
          height: 154px;
          margin-left: -77px;
          margin-top: -77px;
          border-radius: 50%;
          z-index: 5;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          cursor: pointer;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border: 2.5px solid var(--cat-color, var(--primary-color, #03a9f4));
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
          transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
          overflow: hidden;
          padding: 8px 10px;
          box-sizing: border-box;
        }
        .center-node:hover {
          transform: scale(1.04);
          box-shadow: 0 8px 26px rgba(0, 0, 0, 0.12);
        }
        .center-bulb-wrapper {
          width: 52px;
          height: 52px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 2px;
          filter: drop-shadow(0 2px 8px color-mix(in srgb, var(--cat-color, #03a9f4) 40%, transparent));
        }
        .center-bulb-img {
          width: 100%;
          height: 100%;
          object-fit: contain;
          pointer-events: none;
        }
        .center-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          line-height: 1.15;
        }
        .center-title {
          font-size: 1.05rem;
          font-weight: 700;
          color: var(--primary-text-color, #212121);
          letter-spacing: 0.2px;
        }
        .center-badge {
          margin-top: 3px;
          font-size: 0.72rem;
          font-weight: 600;
          color: var(--cat-color, var(--primary-color, #03a9f4));
          background: color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 12%, transparent);
          border: 1px solid color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 25%, transparent);
          padding: 2px 8px;
          border-radius: 12px;
          display: inline-block;
        }

        /* Note Cards (Mushroom / UI Minimalist style) */
        .note-cloud {
          position: absolute;
          min-width: 170px;
          max-width: 250px;
          margin-left: -90px;
          margin-top: -45px;
          z-index: 10;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          border-left: 4px solid var(--cat-color, var(--primary-color, #03a9f4));
          border-radius: 14px;
          padding: 12px 14px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
          cursor: grab;
          user-select: none;
          transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }
        .note-cloud:hover {
          box-shadow: 0 4px 18px rgba(0, 0, 0, 0.09);
          border-color: color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 40%, var(--divider-color, rgba(127, 127, 127, 0.2)));
          z-index: 15;
        }
        .note-cloud.dragging {
          cursor: grabbing;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
          z-index: 25;
        }

        /* Cloud Top Meta */
        .cloud-meta {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 0.72rem;
          color: var(--secondary-text-color, #64748b);
          margin-bottom: 6px;
        }
        .cat-tag {
          font-weight: 600;
          font-size: 0.68rem;
          text-transform: uppercase;
          letter-spacing: 0.4px;
          padding: 3px 8px;
          border-radius: 8px;
          background: color-mix(in srgb, var(--cat-color, var(--primary-color)) 12%, transparent);
          color: var(--cat-color, var(--primary-color));
          cursor: pointer;
          transition: filter 0.15s ease, transform 0.15s ease;
          display: inline-flex;
          align-items: center;
          gap: 4px;
        }
        .cat-tag:hover {
          filter: brightness(0.92);
          transform: scale(1.03);
        }
        .cloud-source {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 0.72rem;
          color: var(--secondary-text-color, #64748b);
        }

        /* Cloud Text */
        .cloud-text {
          font-size: 0.88rem;
          line-height: 1.35;
          color: var(--primary-text-color, #212121);
          word-break: break-word;
          margin-bottom: 8px;
          user-select: text;
          cursor: pointer;
        }

        /* Cloud Actions */
        .cloud-actions {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 6px;
          opacity: 0.85;
          transition: opacity 0.15s ease;
        }
        .note-cloud:hover .cloud-actions {
          opacity: 1;
        }
        .action-btn {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          color: var(--secondary-text-color, #64748b);
          width: 28px;
          height: 28px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.8rem;
          cursor: pointer;
          transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
        }
        .action-btn:hover {
          background: var(--primary-color, #03a9f4);
          color: #ffffff;
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
        }
        .action-btn.done-btn:hover {
          background: var(--success-color, #16a34a);
          border-color: var(--success-color, #16a34a);
          color: #ffffff;
        }
        .action-btn.del-btn:hover {
          background: var(--error-color, #db4437);
          border-color: var(--error-color, #db4437);
          color: #ffffff;
        }

        /* Controls Panel (Bottom Right) */
        .controls-panel {
          position: absolute;
          bottom: 16px;
          right: 16px;
          z-index: 25;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .control-btn {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          color: var(--primary-text-color, #212121);
          font-size: 1.1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
        }
        .control-btn:hover {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
          color: var(--primary-color, #03a9f4);
          border-color: var(--primary-color, #03a9f4);
        }

        /* Quick Add Button (Bottom Left) */
        .add-note-btn {
          position: absolute;
          bottom: 16px;
          left: 16px;
          z-index: 25;
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
          font-weight: 600;
          font-size: 0.85rem;
          padding: 8px 16px;
          border-radius: 20px;
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 6px;
          box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12);
          transition: all 0.2s ease;
        }
        .add-note-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 5px 14px rgba(0, 0, 0, 0.18);
          filter: brightness(1.06);
        }

        /* Empty State */
        .empty-state {
          position: absolute;
          top: 60%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 0.85rem;
          color: var(--secondary-text-color, #64748b);
          text-align: center;
          pointer-events: none;
        }

        /* Dialog Modal (Mushroom / Minimalist UI) */
        .dialog-backdrop {
          position: absolute;
          inset: 0;
          z-index: 100;
          border-radius: inherit;
          background: rgba(0, 0, 0, 0.45);
          backdrop-filter: blur(6px);
          -webkit-backdrop-filter: blur(6px);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px;
          box-sizing: border-box;
          animation: dialogFadeIn 0.18s ease-out;
        }
        @keyframes dialogFadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .dialog-box {
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          color: var(--primary-text-color, #212121);
          width: 100%;
          max-width: 420px;
          border-radius: 20px;
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
          box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
          overflow: hidden;
          display: flex;
          flex-direction: column;
          animation: dialogSlideUp 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }
        @keyframes dialogSlideUp {
          from { transform: translateY(12px) scale(0.96); opacity: 0; }
          to { transform: translateY(0) scale(1); opacity: 1; }
        }
        .dialog-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px 18px;
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
        }
        .dialog-title {
          font-size: 1rem;
          font-weight: 700;
          color: var(--primary-text-color, #212121);
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .dialog-close {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.2));
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
          color: var(--secondary-text-color, #64748b);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          transition: all 0.15s ease;
        }
        .dialog-close:hover {
          color: var(--primary-text-color, #212121);
          background: var(--divider-color, rgba(127, 127, 127, 0.2));
        }
        .dialog-body {
          padding: 18px;
          display: flex;
          flex-direction: column;
          gap: 14px;
          max-height: 70vh;
          overflow-y: auto;
          box-sizing: border-box;
        }
        .dialog-note-preview {
          font-size: 0.82rem;
          color: var(--secondary-text-color, #64748b);
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.07));
          padding: 8px 12px;
          border-radius: 10px;
          border-left: 3px solid var(--primary-color, #03a9f4);
          line-height: 1.35;
          max-height: 60px;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .dialog-label {
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.6px;
          color: var(--secondary-text-color, #64748b);
        }
        .dialog-categories-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(115px, 1fr));
          gap: 8px;
        }
        .dialog-cat-chip {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 9px 12px;
          border-radius: 14px;
          border: 1.5px solid var(--divider-color, rgba(127, 127, 127, 0.18));
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.05));
          color: var(--primary-text-color, #212121);
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.15s ease;
          text-align: left;
        }
        .dialog-cat-chip:hover {
          border-color: var(--chip-color, var(--primary-color, #03a9f4));
          background: color-mix(in srgb, var(--chip-color, var(--primary-color, #03a9f4)) 12%, transparent);
          transform: translateY(-1px);
        }
        .dialog-cat-chip.selected {
          border-color: var(--chip-color, var(--primary-color, #03a9f4));
          background: color-mix(in srgb, var(--chip-color, var(--primary-color, #03a9f4)) 18%, transparent);
          font-weight: 700;
        }
        .dialog-cat-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: var(--chip-color, var(--primary-color, #03a9f4));
          flex-shrink: 0;
        }
        .dialog-cat-name {
          flex: 1;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .dialog-cat-count {
          font-size: 0.72rem;
          opacity: 0.65;
          font-weight: 600;
        }
        .dialog-new-cat-row {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 4px;
          width: 100%;
        }
        .dialog-input {
          width: 100%;
          box-sizing: border-box;
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
          background: var(--card-background-color, var(--ha-card-background, #ffffff));
          color: var(--primary-text-color, #212121);
          padding: 10px 14px;
          border-radius: 12px;
          font-size: 0.92rem;
          font-family: inherit;
          outline: none;
          min-height: 42px;
          display: block;
        }
        .dialog-new-cat-row .dialog-input {
          flex: 1;
          width: auto;
        }
        .dialog-input:focus {
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary-color, #03a9f4) 20%, transparent);
        }
        .dialog-textarea {
          width: 100%;
          box-sizing: border-box;
          min-height: 80px;
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
          background: var(--card-background-color, var(--ha-card-background, #ffffff));
          color: var(--primary-text-color, #212121);
          padding: 10px 12px;
          border-radius: 12px;
          font-size: 0.9rem;
          font-family: inherit;
          resize: vertical;
          outline: none;
          line-height: 1.4;
        }
        .dialog-textarea:focus {
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary-color, #03a9f4) 20%, transparent);
        }
        .dialog-footer {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 8px;
          margin-top: 6px;
        }
        .dialog-btn {
          padding: 8px 16px;
          border-radius: 12px;
          font-size: 0.85rem;
          font-weight: 600;
          cursor: pointer;
          border: 1px solid transparent;
          transition: all 0.15s ease;
        }
        .dialog-btn-cancel {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
          color: var(--secondary-text-color, #64748b);
          border-color: var(--divider-color, rgba(127, 127, 127, 0.2));
        }
        .dialog-btn-cancel:hover {
          background: var(--divider-color, rgba(127, 127, 127, 0.2));
          color: var(--primary-text-color, #212121);
        }
        .dialog-btn-primary {
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
        }
        .dialog-btn-primary:hover {
          filter: brightness(1.08);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
        .dialog-error {
          color: var(--error-color, #db4437);
          font-size: 0.8rem;
          margin-top: 6px;
          line-height: 1.3;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 4px;
        }
        .dialog-input.input-error,
        .dialog-textarea.input-error {
          border-color: var(--error-color, #db4437) !important;
          box-shadow: 0 0 0 2px color-mix(in srgb, var(--error-color, #db4437) 25%, transparent) !important;
          animation: dialog-shake 0.3s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
        }
        @keyframes dialog-shake {
          10%, 90% { transform: translate3d(-1px, 0, 0); }
          20%, 80% { transform: translate3d(2px, 0, 0); }
          30%, 50%, 70% { transform: translate3d(-3px, 0, 0); }
          40%, 60% { transform: translate3d(3px, 0, 0); }
        }
      </style>

      <ha-card id="cardRoot">
        <!-- Top Bar -->
        <div class="top-bar" style="display: ${this._config.show_toolbar !== false ? 'flex' : 'none'};">
          <div class="top-left">
            <div class="brand-logo">
              <img src="/local/brainstorm-logo.svg" onerror="this.src='/local/brainstorm-logo.png'" alt="Logo" />
            </div>
            <div class="title" id="cardTitle">${this._config.title !== undefined ? this._config.title : "Brainstorm Mindmap"}</div>
          </div>
          <div class="pills-container" id="pillsBar"></div>
          <div class="top-right">
            <button class="top-tool-btn" id="colorModeBtn" style="display: ${this._config.show_color_toggle !== false ? 'inline-flex' : 'none'};" title="${this._colorMode === 'theme' ? 'Farbmodus: Theme-Farben aktiv (Klicken für Bunt)' : 'Farbmodus: Bunt aktiv (Klicken für Theme-Farben)'}">
              ${this._colorMode === 'theme' ? '🎨' : '🌈'}
            </button>
            <button class="fullscreen-btn" id="fullscreenToggleBtn" style="display: ${this._config.show_fullscreen_btn !== false ? 'inline-flex' : 'none'};" title="Vollbild umschalten (ESC zum Beenden)">⛶</button>
          </div>
        </div>

        <!-- Interactive Canvas Area -->
        <div class="canvas-area" id="canvasArea">
          <div class="grid-bg"></div>
          <div class="viewport" id="viewport">
            <svg class="connectors" id="connectorsLayer"></svg>
            <div class="center-node" id="centerNode">
              <div class="center-bulb-wrapper" style="display: ${this._config.show_bulb_watermark !== false ? 'block' : 'none'};">
                <img src="/local/brainstorm-bulb.svg" class="center-bulb-img" alt="Brainstorm" />
              </div>
              <div class="center-content">
                <div class="center-title" id="centerTitle">Inbox</div>
                <div class="center-badge" id="centerBadge">0 Notizen</div>
              </div>
            </div>
            <div id="notesContainer"></div>
            <div class="empty-state" id="emptyState" style="display: none;">
              Keine aktiven Notizen in dieser Kategorie.<br>Klicke unten links auf "+ Idee", um eine hinzuzufügen.
            </div>
          </div>
        </div>

        <!-- Bottom Left: Add Note -->
        <button class="add-note-btn" id="addNoteBtn" style="display: ${this._config.show_add_btn !== false ? 'flex' : 'none'};">
          <span>➕</span>
          <span>Neue Idee</span>
        </button>

        <!-- Bottom Right: Zoom & Reset Controls -->
        <div class="controls-panel" style="display: ${this._config.show_controls !== false ? 'flex' : 'none'};">
          <button class="control-btn" id="zoomInBtn" title="Vergrößern">+</button>
          <button class="control-btn" id="zoomOutBtn" title="Verkleinern">−</button>
          <button class="control-btn" id="resetViewBtn" title="Zentrieren / Anordnen">⟲</button>
        </div>

        <!-- In-Card Modal Dialog (Mushroom Style) -->
        <div class="dialog-backdrop" id="mindmapDialog" style="display: none;">
          <div class="dialog-box" id="dialogBox">
            <div class="dialog-header">
              <div class="dialog-title" id="dialogTitle">Titel</div>
              <button class="dialog-close" id="dialogCloseBtn" title="Schließen (ESC)">✕</button>
            </div>
            <div class="dialog-body" id="dialogBody"></div>
          </div>
        </div>
      </ha-card>
    `;

    this._bindEvents();
  }

  _bindEvents() {
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    const zoomInBtn = this.shadowRoot.getElementById("zoomInBtn");
    const zoomOutBtn = this.shadowRoot.getElementById("zoomOutBtn");
    const resetViewBtn = this.shadowRoot.getElementById("resetViewBtn");
    const addNoteBtn = this.shadowRoot.getElementById("addNoteBtn");
    const centerNode = this.shadowRoot.getElementById("centerNode");
    const mindmapDialog = this.shadowRoot.getElementById("mindmapDialog");
    const dialogCloseBtn = this.shadowRoot.getElementById("dialogCloseBtn");

    // Modal Close
    if (dialogCloseBtn) {
      dialogCloseBtn.addEventListener("click", () => this._closeDialog());
    }
    if (mindmapDialog) {
      mindmapDialog.addEventListener("click", (e) => {
        if (e.target === mindmapDialog) this._closeDialog();
      });
    }

    // Color Mode Toggle (Theme vs Multicolor)
    const colorModeBtn = this.shadowRoot.getElementById("colorModeBtn");
    if (colorModeBtn) {
      colorModeBtn.addEventListener("click", () => {
        this._colorMode = this._colorMode === "theme" ? "multicolor" : "theme";
        try {
          localStorage.setItem("brainstorm_color_mode", this._colorMode);
        } catch {}
        colorModeBtn.innerHTML = this._colorMode === "theme" ? "🎨" : "🌈";
        colorModeBtn.title = this._colorMode === "theme"
          ? "Farbmodus: Theme-Farben aktiv (Klicken für Bunt)"
          : "Farbmodus: Bunt aktiv (Klicken für Theme-Farben)";
        this._lastDataSignature = ""; // force re-render
        this._updateContent();
      });
    }

    // Responsive Canvas Resize Observer (fills 100% of modal height & width)
    if (window.ResizeObserver && canvasArea) {
      if (this._resizeObserver) {
        this._resizeObserver.disconnect();
      }
      this._resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          const w = entry.contentRect.width;
          const h = entry.contentRect.height;
          if (w > 50 && h > 50) {
            this._centerPos = { x: w / 2, y: h / 2 };
            if (centerNode) {
              centerNode.style.left = `${this._centerPos.x}px`;
              centerNode.style.top = `${this._centerPos.y}px`;
            }
            this._drawConnections();
          }
        }
      });
      this._resizeObserver.observe(canvasArea);
    }

    // Canvas Pan (Drag background)
    canvasArea.addEventListener("mousedown", (e) => {
      if (
        e.target.closest(".note-cloud") ||
        e.target.closest(".center-node") ||
        e.target.closest(".action-btn") ||
        e.target.closest(".dialog-box")
      ) {
        return;
      }
      if (e.button !== 0) return;
      this._isPanning = true;
      this._startPan = { x: e.clientX - this._panX, y: e.clientY - this._panY };
    });

    window.addEventListener("mousemove", (e) => {
      // 1. Canvas Pan
      if (this._isPanning) {
        this._panX = e.clientX - this._startPan.x;
        this._panY = e.clientY - this._startPan.y;
        this._applyTransform();
        return;
      }

      // Check pending node drag threshold (5px hysteresis to prevent click jitter)
      if (this._pendingDrag && !this._activeDrag) {
        const dist = Math.hypot(e.clientX - this._pendingDrag.startMouseX, e.clientY - this._pendingDrag.startMouseY);
        if (dist > 5) {
          this._activeDrag = this._pendingDrag;
          if (this._pendingDrag.cloud) {
            this._pendingDrag.cloud.classList.add("dragging");
          }
        }
      }

      // 2. Node Dragging
      if (this._activeDrag) {
        const dx = (e.clientX - this._activeDrag.startMouseX) / this._scale;
        const dy = (e.clientY - this._activeDrag.startMouseY) / this._scale;
        const newX = this._activeDrag.startNodeX + dx;
        const newY = this._activeDrag.startNodeY + dy;

        this._nodePositions.set(this._activeDrag.id, { x: newX, y: newY });
        const el = this.shadowRoot.getElementById(`cloud_${this._activeDrag.id}`);
        if (el) {
          el.style.left = `${newX}px`;
          el.style.top = `${newY}px`;
        }
        this._drawConnections();
      }
    });

    window.addEventListener("mouseup", () => {
      if (this._isPanning) this._isPanning = false;
      if (this._activeDrag) {
        const el = this.shadowRoot.getElementById(`cloud_${this._activeDrag.id}`);
        if (el) el.classList.remove("dragging");
        this._activeDrag = null;
      }
      this._pendingDrag = null;
    });

    // Mouse Wheel Zoom
    canvasArea.addEventListener("wheel", (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
      this._zoomAtPoint(zoomFactor, e.clientX, e.clientY);
    }, { passive: false });

    // Touch Support for Pan & Pinch
    let lastTouchDist = null;
    let touchStartPan = null;

    canvasArea.addEventListener("touchstart", (e) => {
      if (e.touches.length === 1 && !e.target.closest(".note-cloud") && !e.target.closest(".dialog-box")) {
        touchStartPan = {
          x: e.touches[0].clientX - this._panX,
          y: e.touches[0].clientY - this._panY,
        };
      } else if (e.touches.length === 2) {
        lastTouchDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
      }
    });

    canvasArea.addEventListener("touchmove", (e) => {
      // Check touch drag threshold for pending node
      if (this._pendingDrag && !this._activeDrag && e.touches.length === 1) {
        const touch = e.touches[0];
        const dist = Math.hypot(touch.clientX - this._pendingDrag.startMouseX, touch.clientY - this._pendingDrag.startMouseY);
        if (dist > 8) {
          this._activeDrag = this._pendingDrag;
          if (this._pendingDrag.cloud) {
            this._pendingDrag.cloud.classList.add("dragging");
          }
        }
      }

      if (this._activeDrag && e.touches.length === 1) {
        const touch = e.touches[0];
        const dx = (touch.clientX - this._activeDrag.startMouseX) / this._scale;
        const dy = (touch.clientY - this._activeDrag.startMouseY) / this._scale;
        const newX = this._activeDrag.startNodeX + dx;
        const newY = this._activeDrag.startNodeY + dy;

        this._nodePositions.set(this._activeDrag.id, { x: newX, y: newY });
        const el = this.shadowRoot.getElementById(`cloud_${this._activeDrag.id}`);
        if (el) {
          el.style.left = `${newX}px`;
          el.style.top = `${newY}px`;
        }
        this._drawConnections();
        return;
      }

      if (e.touches.length === 1 && touchStartPan && !this._activeDrag) {
        this._panX = e.touches[0].clientX - touchStartPan.x;
        this._panY = e.touches[0].clientY - touchStartPan.y;
        this._applyTransform();
      } else if (e.touches.length === 2 && lastTouchDist) {
        const dist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        const factor = dist / lastTouchDist;
        if (Math.abs(factor - 1) > 0.02) {
          const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
          const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
          this._zoomAtPoint(factor, midX, midY);
          lastTouchDist = dist;
        }
      }
    });

    canvasArea.addEventListener("touchend", () => {
      touchStartPan = null;
      lastTouchDist = null;
      if (this._activeDrag) {
        const el = this.shadowRoot.getElementById(`cloud_${this._activeDrag.id}`);
        if (el) el.classList.remove("dragging");
        this._activeDrag = null;
      }
      this._pendingDrag = null;
    });

    // Fullscreen Toggle
    const fullscreenBtn = this.shadowRoot.getElementById("fullscreenToggleBtn");
    const cardRoot = this.shadowRoot.getElementById("cardRoot");
    const toggleFullscreen = () => {
      const isFs = cardRoot.classList.toggle("is-fullscreen");
      fullscreenBtn.innerHTML = isFs ? "✕" : "⛶";
      fullscreenBtn.classList.toggle("is-fullscreen", isFs);
      fullscreenBtn.title = isFs ? "Vollbild beenden" : "Vollbild umschalten (ESC)";
      setTimeout(() => {
        this._centerLayout(false);
      }, 50);
    };

    if (fullscreenBtn) {
      fullscreenBtn.addEventListener("click", toggleFullscreen);
    }

    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        if (this._isModalOpen) {
          this._closeDialog();
        } else if (cardRoot && cardRoot.classList.contains("is-fullscreen")) {
          toggleFullscreen();
        }
      }
    });

    // Control Buttons
    zoomInBtn.addEventListener("click", () => this._zoomAtPoint(1.2));
    zoomOutBtn.addEventListener("click", () => this._zoomAtPoint(0.8));
    resetViewBtn.addEventListener("click", () => {
      this._centerLayout(true);
    });

    // Quick Add -> Show Dialog Modal
    addNoteBtn.addEventListener("click", () => this._showAddDialog());

    // Center Node Click -> Cycle category
    centerNode.addEventListener("click", () => {
      const sensor = this._getSensorEntity();
      if (!sensor) return;
      const categories = ["all", ...(sensor.attributes.categories || ["Inbox"])];
      const idx = categories.indexOf(this._selectedCategory);
      const nextIdx = (idx + 1) % categories.length;
      this._selectedCategory = categories[nextIdx];
      this._lastDataSignature = ""; // force re-render
      this._centerLayout(true);
      this._updateContent();
    });
  }

  _zoomAtPoint(factor, clientX = null, clientY = null) {
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    if (!canvasArea) return;
    const rect = canvasArea.getBoundingClientRect();
    const cx = clientX !== null ? clientX - rect.left : rect.width / 2;
    const cy = clientY !== null ? clientY - rect.top : rect.height / 2;

    const oldScale = this._scale;
    const newScale = Math.min(Math.max(oldScale * factor, 0.4), 2.5);

    // Keep point under cursor invariant
    this._panX = cx - (cx - this._panX) * (newScale / oldScale);
    this._panY = cy - (cy - this._panY) * (newScale / oldScale);
    this._scale = newScale;

    this._applyTransform();
  }

  _applyTransform() {
    const viewport = this.shadowRoot.getElementById("viewport");
    if (viewport) {
      viewport.style.transform = `translate(${this._panX}px, ${this._panY}px) scale(${this._scale})`;
    }
  }

  _centerLayout(recomputeRadial = false) {
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    if (!canvasArea) return;
    const w = canvasArea.clientWidth || 800;
    const h = canvasArea.clientHeight || 550;

    this._centerPos = { x: w / 2, y: h / 2 };
    this._scale = 1;
    this._panX = 0;
    this._panY = 0;
    this._applyTransform();

    const centerNode = this.shadowRoot.getElementById("centerNode");
    if (centerNode) {
      centerNode.style.left = `${this._centerPos.x}px`;
      centerNode.style.top = `${this._centerPos.y}px`;
    }

    if (recomputeRadial) {
      this._arrangeNodesRadially();
    }
  }

  _arrangeNodesRadially() {
    const sensor = this._getSensorEntity();
    if (!sensor) return;
    const ideas = (sensor.attributes.ideas || []).filter((i) => {
      if (this._selectedCategory === "all") return true;
      return String(i.category || "").trim() === String(this._selectedCategory || "").trim();
    });

    const count = ideas.length;
    if (count === 0) {
      this._drawConnections();
      return;
    }

    // Determine radius based on canvas dimensions and note count
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    const h = canvasArea && canvasArea.clientHeight > 0 ? canvasArea.clientHeight : 600;
    const w = canvasArea && canvasArea.clientWidth > 0 ? canvasArea.clientWidth : 800;
    const minDim = Math.min(w, h);

    const baseRadius = Math.max(180, Math.min(minDim * 0.34, count <= 6 ? 230 : count <= 12 ? 290 : 350));
    const angleStep = (2 * Math.PI) / count;

    ideas.forEach((idea, i) => {
      // Add slight organic offset to give an organic thought cloud feel
      const radiusJitter = (i % 2 === 0 ? 1 : 0.92) * baseRadius;
      const angle = i * angleStep - Math.PI / 2;
      const x = this._centerPos.x + Math.cos(angle) * radiusJitter;
      const y = this._centerPos.y + Math.sin(angle) * radiusJitter;

      this._nodePositions.set(idea.id, { x, y });

      const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
      if (el) {
        el.style.left = `${x}px`;
        el.style.top = `${y}px`;
      }
    });

    this._drawConnections();
  }

  _drawConnections() {
    const svg = this.shadowRoot.getElementById("connectorsLayer");
    if (!svg) return;

    let svgHtml = "";
    this._nodePositions.forEach((pos, id) => {
      const x1 = this._centerPos.x;
      const y1 = this._centerPos.y;
      const x2 = pos.x;
      const y2 = pos.y;

      // Cubic Bézier curve calculation for organic synapse effect
      const dx = x2 - x1;
      const dy = y2 - y1;
      const cx1 = x1 + dx * 0.35;
      const cy1 = y1 + dy * 0.15;
      const cx2 = x1 + dx * 0.65;
      const cy2 = y1 + dy * 0.85;

      const pathData = `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`;
      svgHtml += `
        <path id="path_${id}" class="synapse-path" d="${pathData}" />
      `;
    });

    svg.innerHTML = svgHtml;
  }

  _updateContent() {
    try {
      const sensor = this._getSensorEntity();
      if (!sensor) return;

      const attributes = sensor.attributes || {};
      const categories = attributes.categories || ["Inbox", "Smarthome", "Haus & Garten", "Projekte", "Alltag"];
      const activeIdeas = attributes.ideas || [];

      // Filter ideas by selected category
      const filteredIdeas = activeIdeas.filter((i) => {
        if (this._selectedCategory === "all") return true;
        return String(i.category || "").trim() === String(this._selectedCategory || "").trim();
      });

      // Update Card Elements from Config
      const titleEl = this.shadowRoot.getElementById("cardTitle");
      if (titleEl) titleEl.textContent = this._config.title !== undefined ? this._config.title : "Brainstorm Mindmap";

      const topBar = this.shadowRoot.querySelector(".top-bar");
      if (topBar) topBar.style.display = this._config.show_toolbar !== false ? "flex" : "none";

      const bulbWrap = this.shadowRoot.querySelector(".center-bulb-wrapper");
      if (bulbWrap) bulbWrap.style.display = this._config.show_bulb_watermark !== false ? "block" : "none";

      const colorModeBtn = this.shadowRoot.getElementById("colorModeBtn");
      if (colorModeBtn) {
        colorModeBtn.style.display = this._config.show_color_toggle !== false ? "inline-flex" : "none";
        colorModeBtn.innerHTML = this._colorMode === "theme" ? "🎨" : "🌈";
        colorModeBtn.title = this._colorMode === "theme"
          ? "Farbmodus: Theme-Farben aktiv (Klicken für Bunt)"
          : "Farbmodus: Bunt aktiv (Klicken für Theme-Farben)";
      }

      const fullscreenBtn = this.shadowRoot.getElementById("fullscreenToggleBtn");
      if (fullscreenBtn) fullscreenBtn.style.display = this._config.show_fullscreen_btn !== false ? "inline-flex" : "none";

      const controlsPanel = this.shadowRoot.querySelector(".controls-panel");
      if (controlsPanel) controlsPanel.style.display = this._config.show_controls !== false ? "flex" : "none";

      const addNoteBtn = this.shadowRoot.getElementById("addNoteBtn");
      if (addNoteBtn) addNoteBtn.style.display = this._config.show_add_btn !== false ? "flex" : "none";

      const cardRoot = this.shadowRoot.getElementById("cardRoot");
      if (cardRoot && this._config.height && !this._isFullscreen) {
        cardRoot.style.height = this._config.height;
      }

      // 1. Update Top Category Pills
      const pillsBar = this.shadowRoot.getElementById("pillsBar");
      if (pillsBar) {
        const counts = attributes.category_counts || {};
        pillsBar.innerHTML = `
          <div class="cat-pill ${this._selectedCategory === "all" ? "active" : ""}" data-cat="all" style="--category-color: var(--primary-color, #03a9f4);">
            Alle (${activeIdeas.length})
          </div>
          ${categories
            .map((cat) => {
              const c = counts[cat] || 0;
              return `
                <div class="cat-pill ${String(this._selectedCategory || "").trim() === String(cat || "").trim() ? "active" : ""}" data-cat="${cat}" style="--category-color: ${this._getCategoryColor(cat)};">
                  ${cat} (${c})
                </div>
              `;
            })
            .join("")}
        `;

        pillsBar.querySelectorAll(".cat-pill").forEach((pill) => {
          pill.addEventListener("click", () => {
            this._selectedCategory = String(pill.getAttribute("data-cat") || "").trim();
            this._updateContent();
            this._arrangeNodesRadially();
          });
        });
      }

      // 2. Update Center Node
      const centerTitle = this.shadowRoot.getElementById("centerTitle");
      const centerBadge = this.shadowRoot.getElementById("centerBadge");
      const centerNode = this.shadowRoot.getElementById("centerNode");

      if (centerTitle && centerBadge) {
        const displayCat = this._selectedCategory === "all" ? "Alle" : this._selectedCategory;
        centerTitle.textContent = displayCat;
        centerBadge.textContent = `${filteredIdeas.length} ${filteredIdeas.length === 1 ? "Idee" : "Ideen"}`;

        // Accent border color matching category
        const catColor = this._getCategoryColor(this._selectedCategory === "all" ? "Inbox" : this._selectedCategory);
        centerNode.style.setProperty("--cat-color", catColor);
        centerNode.style.borderColor = catColor;
        centerNode.style.boxShadow = "0 4px 20px rgba(0, 0, 0, 0.08)";
      }

      // 3. Render Note Clouds
      const container = this.shadowRoot.getElementById("notesContainer");
      const emptyState = this.shadowRoot.getElementById("emptyState");

      if (filteredIdeas.length === 0) {
        emptyState.style.display = "block";
        container.innerHTML = "";
        this._nodePositions.clear();
        this._drawConnections();
        return;
      }

      emptyState.style.display = "none";

      // Render notes HTML
      let html = "";
      filteredIdeas.forEach((idea) => {
        const color = this._getCategoryColor(idea.category);
        const sourceIcon = this._getSourceIcon(idea.source);
        const timeAgo = this._formatTime(idea.created_at);

        html += `
          <div class="note-cloud" id="cloud_${idea.id}" data-id="${idea.id}" style="--cat-color: ${color};">
            <div class="cloud-meta">
              <span class="cat-tag" data-cat="${this._escapeHtml(idea.category)}" title="Kategorie ändern">
                🏷️ ${this._escapeHtml(idea.category)}
              </span>
              <span class="cloud-source" title="${idea.source || 'Dashboard'}">
                <span>${sourceIcon}</span>
                <span>${timeAgo}</span>
              </span>
            </div>
            <div class="cloud-text" title="Klicken zum Bearbeiten">${this._escapeHtml(idea.text)}</div>
            <div class="cloud-actions">
              <button class="action-btn done-btn" data-act="done" data-id="${idea.id}" title="Als erledigt markieren">✓</button>
              <button class="action-btn" data-act="edit" data-id="${idea.id}" title="Bearbeiten">✏️</button>
              <button class="action-btn" data-act="move" data-id="${idea.id}" title="Kategorie ändern">📁</button>
              <button class="action-btn del-btn" data-act="delete" data-id="${idea.id}" title="Löschen">🗑️</button>
            </div>
          </div>
        `;
      });
      container.innerHTML = html;

      // Ensure nodes have positions
      const canvasArea = this.shadowRoot.getElementById("canvasArea");
      const w = canvasArea.clientWidth || 800;
      const h = canvasArea.clientHeight || 550;
      this._centerPos = { x: w / 2, y: h / 2 };

      if (centerNode) {
        centerNode.style.left = `${this._centerPos.x}px`;
        centerNode.style.top = `${this._centerPos.y}px`;
      }

      // Check if we need initial radial arrangement
      let needsArrangement = false;
      filteredIdeas.forEach((idea) => {
        if (!this._nodePositions.has(idea.id)) {
          needsArrangement = true;
        }
      });

      if (needsArrangement || this._nodePositions.size !== filteredIdeas.length) {
        this._arrangeNodesRadially();
      } else {
        // Restore existing positions
        filteredIdeas.forEach((idea) => {
          const pos = this._nodePositions.get(idea.id);
          const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
          if (el && pos) {
            el.style.left = `${pos.x}px`;
            el.style.top = `${pos.y}px`;
          }
        });
        this._drawConnections();
      }

      // Attach Node Drag & Action Listeners
      container.querySelectorAll(".note-cloud").forEach((cloud) => {
        const id = cloud.getAttribute("data-id");
        const idea = filteredIdeas.find((i) => i.id === id);
        if (!idea) return;

        // Mouse down records pending drag - only moves if threshold > 5px (prevents click jitter!)
        cloud.addEventListener("mousedown", (e) => {
          if (e.target.closest(".action-btn") || e.target.closest(".cat-tag")) return;
          if (e.button !== 0) return;
          const pos = this._nodePositions.get(id) || { x: 0, y: 0 };
          this._pendingDrag = {
            id: id,
            cloud: cloud,
            startMouseX: e.clientX,
            startMouseY: e.clientY,
            startNodeX: pos.x,
            startNodeY: pos.y,
          };
        });

        // Touch start records pending drag
        cloud.addEventListener("touchstart", (e) => {
          if (e.target.closest(".action-btn") || e.target.closest(".cat-tag")) return;
          if (e.touches.length === 1) {
            const touch = e.touches[0];
            const pos = this._nodePositions.get(id) || { x: 0, y: 0 };
            this._pendingDrag = {
              id: id,
              cloud: cloud,
              startMouseX: touch.clientX,
              startMouseY: touch.clientY,
              startNodeX: pos.x,
              startNodeY: pos.y,
            };
          }
        }, { passive: true });

        // Hover highlight connector
        cloud.addEventListener("mouseenter", () => {
          const path = this.shadowRoot.getElementById(`path_${id}`);
          if (path) path.classList.add("highlight");
        });
        cloud.addEventListener("mouseleave", () => {
          const path = this.shadowRoot.getElementById(`path_${id}`);
          if (path) path.classList.remove("highlight");
        });

        // Text click or edit button -> Edit Dialog
        const textEl = cloud.querySelector(".cloud-text");
        if (textEl) {
          textEl.addEventListener("click", (e) => {
            e.stopPropagation();
            this._showEditDialog(idea.id, idea.text, idea.category);
          });
        }

        // Category Tag click -> Category Picker
        const catTagEl = cloud.querySelector(".cat-tag");
        if (catTagEl) {
          catTagEl.addEventListener("click", (e) => {
            e.stopPropagation();
            this._showCategoryPicker(idea.id, idea.category, idea.text);
          });
        }

        // Action buttons
        cloud.querySelectorAll(".action-btn").forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const act = btn.getAttribute("data-act");
            if (act === "done") this._completeIdea(idea.id);
            else if (act === "edit") this._showEditDialog(idea.id, idea.text, idea.category);
            else if (act === "move") this._showCategoryPicker(idea.id, idea.category, idea.text);
            else if (act === "delete") this._showDeleteConfirm(idea.id, idea.text);
          });
        });
      });
    } catch (e) {
      console.error("[BrainstormMindmapCard] Update error:", e);
    }
  }

  _escapeHtml(text) {
    if (!text) return "";
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // --- Modal Dialog System (Mushroom / Minimalist UI) ---

  _openDialog(title, renderFn) {
    const dialog = this.shadowRoot.getElementById("mindmapDialog");
    const titleEl = this.shadowRoot.getElementById("dialogTitle");
    const bodyEl = this.shadowRoot.getElementById("dialogBody");
    if (!dialog || !titleEl || !bodyEl) return;

    this._isModalOpen = true;
    titleEl.innerHTML = title;
    bodyEl.innerHTML = "";
    renderFn(bodyEl);
    dialog.style.display = "flex";
  }

  _closeDialog() {
    const dialog = this.shadowRoot.getElementById("mindmapDialog");
    if (dialog) dialog.style.display = "none";
    this._isModalOpen = false;
  }

  _showCategoryPicker(id, currentCategory, noteText) {
    const sensor = this._getSensorEntity();
    const categories = sensor ? (sensor.attributes.categories || ["Inbox"]) : ["Inbox"];
    const counts = sensor ? (sensor.attributes.category_counts || {}) : {};

    this._openDialog("🏷️ Kategorie auswählen", (body) => {
      let previewHtml = "";
      if (noteText) {
        previewHtml = `<div class="dialog-note-preview">"${this._escapeHtml(noteText)}"</div>`;
      }

      body.innerHTML = `
        ${previewHtml}
        <div class="dialog-label">Kategorie wählen:</div>
        <div class="dialog-categories-grid">
          ${categories
            .map((cat) => {
              const isSel = cat === currentCategory;
              const color = this._getCategoryColor(cat);
              const count = counts[cat] || 0;
              return `
                <div class="dialog-cat-chip ${isSel ? "selected" : ""}" data-cat="${this._escapeHtml(cat)}" style="--chip-color: ${color};">
                  <span class="dialog-cat-dot"></span>
                  <span class="dialog-cat-name">${this._escapeHtml(cat)}</span>
                  <span class="dialog-cat-count">${isSel ? "✓" : count}</span>
                </div>
              `;
            })
            .join("")}
        </div>
        <div class="dialog-label" style="margin-top: 6px;">Oder neue Kategorie anlegen:</div>
        <div class="dialog-new-cat-row">
          <input type="text" class="dialog-input" id="newCatInput" placeholder="Kategoriename..." />
          <button class="dialog-btn dialog-btn-primary" id="addNewCatBtn">➕ Erstellen</button>
        </div>
        <div class="dialog-error" id="newCatError" style="display: none;"></div>
      `;

      // Select existing category
      body.querySelectorAll(".dialog-cat-chip").forEach((chip) => {
        chip.addEventListener("click", async () => {
          const newCat = chip.getAttribute("data-cat");
          this._closeDialog();
          if (newCat && newCat !== currentCategory) {
            try {
              await this._hass.callService("brainstorm", "update_idea", {
                id: id,
                category: newCat,
              });
            } catch (err) {
              console.error("[BrainstormMindmap] Failed to change category:", err);
            }
          }
        });
      });

      // Add new category with validation
      const newCatInput = body.querySelector("#newCatInput");
      const newCatError = body.querySelector("#newCatError");
      const addNewCatBtn = body.querySelector("#addNewCatBtn");

      const showCatError = (msg) => {
        if (!newCatError || !newCatInput) return;
        newCatError.textContent = msg;
        newCatError.style.display = "flex";
        newCatInput.classList.remove("input-error");
        void newCatInput.offsetWidth;
        newCatInput.classList.add("input-error");
        newCatInput.focus();
      };

      const clearCatError = () => {
        if (newCatError) {
          newCatError.textContent = "";
          newCatError.style.display = "none";
        }
        if (newCatInput) newCatInput.classList.remove("input-error");
      };

      newCatInput.addEventListener("input", clearCatError);

      const handleCreateCat = async () => {
        const val = (newCatInput.value || "").trim();
        if (!val) {
          showCatError("⚠️ Bitte gib einen Kategorienamen ein.");
          return;
        }
        if (categories.some((c) => c.toLowerCase() === val.toLowerCase())) {
          showCatError(`⚠️ Die Kategorie "${val}" existiert bereits.`);
          return;
        }
        this._closeDialog();
        try {
          await this._hass.callService("brainstorm", "add_category", { name: val });
          await this._hass.callService("brainstorm", "update_idea", { id: id, category: val });
        } catch (err) {
          console.error("[BrainstormMindmap] Failed to create category:", err);
        }
      };

      addNewCatBtn.addEventListener("click", handleCreateCat);
      newCatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleCreateCat();
      });
      setTimeout(() => newCatInput && newCatInput.focus(), 60);
    });
  }

  _showEditDialog(id, currentText, currentCategory) {
    const sensor = this._getSensorEntity();
    const categories = sensor ? (sensor.attributes.categories || ["Inbox"]) : ["Inbox"];
    let selectedCat = currentCategory || "Inbox";

    this._openDialog("✏️ Notiz bearbeiten", (body) => {
      body.innerHTML = `
        <div class="dialog-label">Notiztext:</div>
        <textarea class="dialog-textarea" id="editTextarea" rows="3">${this._escapeHtml(currentText)}</textarea>
        <div class="dialog-error" id="editTextError" style="display: none;"></div>

        <div class="dialog-label">Kategorie:</div>
        <div class="dialog-categories-grid" id="editCatGrid">
          ${categories
            .map((cat) => {
              const isSel = cat === selectedCat;
              const color = this._getCategoryColor(cat);
              return `
                <div class="dialog-cat-chip ${isSel ? "selected" : ""}" data-cat="${this._escapeHtml(cat)}" style="--chip-color: ${color};">
                  <span class="dialog-cat-dot"></span>
                  <span class="dialog-cat-name">${this._escapeHtml(cat)}</span>
                </div>
              `;
            })
            .join("")}
        </div>

        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="cancelEditBtn">Abbrechen</button>
          <button class="dialog-btn dialog-btn-primary" id="saveEditBtn">Speichern</button>
        </div>
      `;

      const textarea = body.querySelector("#editTextarea");
      const textError = body.querySelector("#editTextError");
      const saveBtn = body.querySelector("#saveEditBtn");
      const cancelBtn = body.querySelector("#cancelEditBtn");
      const catChips = body.querySelectorAll(".dialog-cat-chip");

      const showTextError = (msg) => {
        if (!textError || !textarea) return;
        textError.textContent = msg;
        textError.style.display = "flex";
        textarea.classList.remove("input-error");
        void textarea.offsetWidth;
        textarea.classList.add("input-error");
        textarea.focus();
      };

      const clearTextError = () => {
        if (textError) {
          textError.textContent = "";
          textError.style.display = "none";
        }
        if (textarea) textarea.classList.remove("input-error");
      };

      textarea.addEventListener("input", clearTextError);

      setTimeout(() => {
        if (textarea) {
          textarea.focus();
          textarea.setSelectionRange(textarea.value.length, textarea.value.length);
        }
      }, 50);

      catChips.forEach((chip) => {
        chip.addEventListener("click", () => {
          catChips.forEach((c) => c.classList.remove("selected"));
          chip.classList.add("selected");
          selectedCat = chip.getAttribute("data-cat");
        });
      });

      const handleSave = async () => {
        const newText = (textarea.value || "").trim();
        if (!newText) {
          showTextError("⚠️ Der Text darf nicht leer sein.");
          return;
        }
        this._closeDialog();

        const payload = { id: id, text: newText };
        if (selectedCat && selectedCat !== currentCategory) {
          payload.category = selectedCat;
        }

        try {
          await this._hass.callService("brainstorm", "update_idea", payload);
        } catch (err) {
          console.error("[BrainstormMindmap] Failed to update idea:", err);
        }
      };

      saveBtn.addEventListener("click", handleSave);
      cancelBtn.addEventListener("click", () => this._closeDialog());
      textarea.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          handleSave();
        }
      });
    });
  }

  _showAddDialog() {
    const sensor = this._getSensorEntity();
    const categories = sensor ? (sensor.attributes.categories || ["Inbox"]) : ["Inbox"];
    let selectedCat = this._selectedCategory && this._selectedCategory !== "all" ? this._selectedCategory : "Inbox";

    this._openDialog("💡 Neue Idee erfassen", (body) => {
      body.innerHTML = `
        <div class="dialog-label">Idee / Gedanke:</div>
        <textarea class="dialog-textarea" id="addTextarea" placeholder="Was möchtest du festhalten?..." rows="3"></textarea>
        <div class="dialog-error" id="addTextError" style="display: none;"></div>

        <div class="dialog-label">Kategorie:</div>
        <div class="dialog-categories-grid" id="addCatGrid">
          ${categories
            .map((cat) => {
              const isSel = cat === selectedCat;
              const color = this._getCategoryColor(cat);
              return `
                <div class="dialog-cat-chip ${isSel ? "selected" : ""}" data-cat="${this._escapeHtml(cat)}" style="--chip-color: ${color};">
                  <span class="dialog-cat-dot"></span>
                  <span class="dialog-cat-name">${this._escapeHtml(cat)}</span>
                </div>
              `;
            })
            .join("")}
        </div>

        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="cancelAddBtn">Abbrechen</button>
          <button class="dialog-btn dialog-btn-primary" id="saveAddBtn">Hinzufügen</button>
        </div>
      `;

      const textarea = body.querySelector("#addTextarea");
      const textError = body.querySelector("#addTextError");
      const saveBtn = body.querySelector("#saveAddBtn");
      const cancelBtn = body.querySelector("#cancelAddBtn");
      const catChips = body.querySelectorAll(".dialog-cat-chip");

      const showTextError = (msg) => {
        if (!textError || !textarea) return;
        textError.textContent = msg;
        textError.style.display = "flex";
        textarea.classList.remove("input-error");
        void textarea.offsetWidth;
        textarea.classList.add("input-error");
        textarea.focus();
      };

      const clearTextError = () => {
        if (textError) {
          textError.textContent = "";
          textError.style.display = "none";
        }
        if (textarea) textarea.classList.remove("input-error");
      };

      textarea.addEventListener("input", clearTextError);

      setTimeout(() => {
        if (textarea) textarea.focus();
      }, 50);

      catChips.forEach((chip) => {
        chip.addEventListener("click", () => {
          catChips.forEach((c) => c.classList.remove("selected"));
          chip.classList.add("selected");
          selectedCat = chip.getAttribute("data-cat");
        });
      });

      const handleAdd = async () => {
        const text = (textarea.value || "").trim();
        if (!text) {
          showTextError("⚠️ Der Text darf nicht leer sein.");
          return;
        }
        this._closeDialog();

        try {
          await this._hass.callService("brainstorm", "add_idea", {
            text: text,
            category: selectedCat,
            source: "dashboard",
          });
        } catch (err) {
          console.error("[BrainstormMindmap] Failed to add idea:", err);
        }
      };

      saveBtn.addEventListener("click", handleAdd);
      cancelBtn.addEventListener("click", () => this._closeDialog());
      textarea.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          handleAdd();
        }
      });
    });
  }

  _showDeleteConfirm(id, noteText) {
    this._openDialog("🗑️ Notiz löschen?", (body) => {
      body.innerHTML = `
        <div class="dialog-note-preview">"${this._escapeHtml(noteText)}"</div>
        <p style="margin: 8px 0; font-size: 0.88rem; color: var(--secondary-text-color, #64748b);">
          Möchtest du diese Notiz wirklich unwiderruflich aus Brainstorm entfernen?
        </p>
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="cancelDelBtn">Abbrechen</button>
          <button class="dialog-btn dialog-btn-primary" id="confirmDelBtn" style="background: var(--error-color, #db4437);">Löschen</button>
        </div>
      `;

      body.querySelector("#cancelDelBtn").addEventListener("click", () => this._closeDialog());
      body.querySelector("#confirmDelBtn").addEventListener("click", async () => {
        this._closeDialog();
        try {
          await this._hass.callService("brainstorm", "delete_idea", { id: id });
        } catch (err) {
          console.error("[BrainstormMindmap] Failed to delete idea:", err);
        }
      });
    });
  }

  async _completeIdea(id) {
    const el = this.shadowRoot.getElementById(`cloud_${id}`);
    if (el) {
      el.style.transition = "opacity 0.25s ease, transform 0.25s ease";
      el.style.opacity = "0.2";
      el.style.transform = "scale(0.85)";
    }
    try {
      await this._hass.callService("brainstorm", "update_idea", {
        id: id,
        status: "completed",
      });
    } catch (e) {
      console.error("[BrainstormMindmap] Failed to complete idea:", e);
      if (el) {
        el.style.opacity = "1";
        el.style.transform = "none";
      }
    }
  }
}

const MINDMAP_CARD_SCHEMA = [
  {
    name: "title",
    label: "Mindmap-Titel",
    selector: { text: {} },
  },
  {
    name: "sensor",
    label: "Sensor-Entität",
    selector: { entity: { domain: ["sensor"], integration: "brainstorm" } },
  },
  {
    name: "color_mode",
    label: "Standard-Farbmodus",
    selector: {
      select: {
        mode: "dropdown",
        options: [
          { value: "theme", label: "🎨 Theme-Farben (Dynamisch nach Home Assistant Theme)" },
          { value: "multicolor", label: "🌈 Bunt (Multicolor-Kategoriefarben)" },
        ],
      },
    },
  },
  {
    name: "height",
    label: "Höhe der Mindmap (z.B. 600px, 75vh, calc(100vh - 32px))",
    selector: { text: {} },
  },
  {
    name: "default_category",
    label: "Standard-Kategorie im Fokus",
    selector: { text: {} },
  },
  {
    name: "show_bulb_watermark",
    label: "Leuchtende Glühbirne im Zentrum als Wasserzeichen anzeigen",
    selector: { boolean: {} },
  },
  {
    name: "show_toolbar",
    label: "Obere Werkzeugleiste (Titel & Filter-Pills) anzeigen",
    selector: { boolean: {} },
  },
  {
    name: "show_color_toggle",
    label: "Farbmodus-Umschalter (🎨/🌈) in Toolbar anzeigen",
    selector: { boolean: {} },
  },
  {
    name: "show_fullscreen_btn",
    label: "Vollbild-Schaltfläche (⛶) anzeigen",
    selector: { boolean: {} },
  },
  {
    name: "show_controls",
    label: "Zoom- & Zentrieren-Schaltflächen anzeigen",
    selector: { boolean: {} },
  },
  {
    name: "show_add_btn",
    label: "Neue Notiz-Schaltfläche (+ Idee) anzeigen",
    selector: { boolean: {} },
  },
];

class BrainstormMindmapCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._form = null;
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._form) {
      this._form.hass = hass;
    }
  }

  async _render() {
    if (!this.shadowRoot) return;

    if (window.loadCardHelpers) {
      try {
        const helpers = await window.loadCardHelpers();
        if (helpers && helpers.createCardElement) {
          await helpers.createCardElement({ type: "entities", entities: [] });
        }
      } catch {}
    }

    if (this._form) {
      this._form.data = this._config;
      if (this._hass) this._form.hass = this._hass;
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        .editor-container {
          display: flex;
          flex-direction: column;
          gap: 14px;
          padding: 8px 0;
          font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
        }
        .editor-header {
          display: flex;
          align-items: center;
          gap: 10px;
          padding-bottom: 10px;
          border-bottom: 1px solid var(--divider-color, rgba(0,0,0,0.12));
          color: var(--primary-text-color, #212121);
          font-weight: 600;
          font-size: 1.05rem;
        }
        .editor-header img {
          width: 26px;
          height: 26px;
          object-fit: contain;
        }
        .fallback-container {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .fallback-row {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .fallback-label {
          font-size: 0.85rem;
          font-weight: 500;
          color: var(--secondary-text-color, #757575);
        }
        .fallback-input, .fallback-select {
          padding: 8px 12px;
          border-radius: 8px;
          border: 1px solid var(--divider-color, #ccc);
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color, #000);
          font-size: 0.9rem;
        }
      </style>
      <div class="editor-container">
        <div class="editor-header">
          <img src="/local/brainstorm-bulb.svg" alt="Brainstorm" onerror="this.style.display='none'" />
          <span>Brainstorm Mindmap – Visuelle Kartenkonfiguration</span>
        </div>
        <div id="formContainer"></div>
      </div>
    `;

    const formContainer = this.shadowRoot.getElementById("formContainer");

    if (customElements.get("ha-form")) {
      const form = document.createElement("ha-form");
      form.hass = this._hass;
      form.data = this._config;
      form.schema = MINDMAP_CARD_SCHEMA;
      form.computeLabel = (s) => s.label || s.name;
      form.computeHelper = (s) => s.helper || "";
      form.addEventListener("value-changed", (ev) => {
        if (!ev.detail || !ev.detail.value) return;
        this._config = { ...this._config, ...ev.detail.value };
        this.dispatchEvent(
          new CustomEvent("config-changed", {
            detail: { config: this._config },
            bubbles: true,
            composed: true,
          })
        );
      });
      formContainer.appendChild(form);
      this._form = form;
    } else {
      this._renderFallback(formContainer);
    }
  }

  _renderFallback(container) {
    container.innerHTML = `
      <div class="fallback-container">
        <div class="fallback-row">
          <label class="fallback-label">Mindmap-Titel</label>
          <input class="fallback-input" id="fbTitle" type="text" value="${this._config.title || 'Brainstorm Mindmap'}" />
        </div>
        <div class="fallback-row">
          <label class="fallback-label">Sensor-Entität</label>
          <input class="fallback-input" id="fbSensor" type="text" value="${this._config.sensor || 'sensor.brainstorm_ideen_ubersicht'}" />
        </div>
        <div class="fallback-row">
          <label class="fallback-label">Farbmodus</label>
          <select class="fallback-select" id="fbColorMode">
            <option value="theme" ${(this._config.color_mode || 'theme') === 'theme' ? 'selected' : ''}>🎨 Theme-Farben</option>
            <option value="multicolor" ${this._config.color_mode === 'multicolor' ? 'selected' : ''}>🌈 Bunt (Multicolor)</option>
          </select>
        </div>
      </div>
    `;
    const fbTitle = container.querySelector("#fbTitle");
    const fbSensor = container.querySelector("#fbSensor");
    const fbColorMode = container.querySelector("#fbColorMode");

    const emitChange = () => {
      this._config = {
        ...this._config,
        title: fbTitle ? fbTitle.value : this._config.title,
        sensor: fbSensor ? fbSensor.value : this._config.sensor,
        color_mode: fbColorMode ? fbColorMode.value : this._config.color_mode,
      };
      this.dispatchEvent(
        new CustomEvent("config-changed", {
          detail: { config: this._config },
          bubbles: true,
          composed: true,
        })
      );
    };

    if (fbTitle) fbTitle.addEventListener("input", emitChange);
    if (fbSensor) fbSensor.addEventListener("input", emitChange);
    if (fbColorMode) fbColorMode.addEventListener("change", emitChange);
  }
}

if (!customElements.get("brainstorm-mindmap-card-editor")) {
  customElements.define("brainstorm-mindmap-card-editor", BrainstormMindmapCardEditor);
}

// Register custom element & Lovelace customCard entry
if (!customElements.get("brainstorm-mindmap-card")) {
  customElements.define("brainstorm-mindmap-card", BrainstormMindmapCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "brainstorm-mindmap-card")) {
  window.customCards.push({
    type: "brainstorm-mindmap-card",
    name: "Brainstorm Mindmap Card",
    description: "Interaktive Mindmap-Darstellung für deine Brainstorm Hub Notizen und Ideen.",
    preview: true,
    documentationURL: "https://github.com/nukleuz80/ha_brainstorm",
  });
}

console.info(
  "%c BRAINSTORM-MINDMAP-CARD %c v1.4.13 ",
  "color: #07070e; background: #00f5ff; font-weight: bold; border-radius: 4px 0 0 4px; padding: 2px 4px;",
  "color: #ffffff; background: #9d4edd; font-weight: bold; border-radius: 0 4px 4px 0; padding: 2px 4px;"
);
