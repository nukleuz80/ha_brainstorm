/**
 * Brainstorm Hub - Interactive Mindmap Card
 * Version: 1.4.47 - Optional Alexa Skill for One-Sentence Voice Input
 * 
 * An interactive, visual mindmap for Home Assistant ideas and brainstorm notes.
 * Minimalist UI / Mushroom-inspired theme styling.
 */

const BRAINSTORM_MINDMAP_DEFAULTS = {
  title: "Brainstorm Mindmap",
  sensor: "sensor.brainstorm_ideen_ubersicht",
  show_last_alexa: false,
  last_alexa_entity: "sensor.last_alexa",
  color_mode: "multicolor",
  height: "calc(100vh - 32px)",
  default_category: "all",
  show_logo: true,
  show_bulb_watermark: true,
  show_grid: true,
  show_toolbar: true,
  show_color_toggle: true,
  show_fullscreen_btn: true,
  show_controls: true,
  show_add_btn: true,
  hide_empty_categories: true,
};

class BrainstormMindmapCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = { ...BRAINSTORM_MINDMAP_DEFAULTS };
    this._hass = null;
    this._selectedCategory = "all"; // 'all', 'Inbox', etc.
    let savedColorMode = "multicolor";
    try {
      savedColorMode = localStorage.getItem("brainstorm_color_mode") || "multicolor";
    } catch {}
    this._colorMode = savedColorMode; // 'multicolor' | 'theme'
    this._scale = 1;
    this._panX = 0;
    this._panY = 0;
    this._isPanning = false;
    this._startPan = { x: 0, y: 0 };
    this._nodePositions = new Map(); // id -> {x, y}
    this._userMovedNodes = new Set();
    this._centerPos = { x: 400, y: 300 };
    this._activeDrag = null; // { id, startMouseX, startMouseY, startNodeX, startNodeY }
    this._pendingDrag = null; // { id, cloud, startMouseX, startMouseY, startNodeX, startNodeY }
    this._initialized = false;
    this._lastUpdated = null;
    this._lastAlexaKey = null;
    this._lastDataSignature = "";
    this._isModalOpen = false;
  }

  static async getConfigElement() {
    if (window.loadCardHelpers) {
      try {
        const helpers = await window.loadCardHelpers();
        if (helpers && helpers.createCardElement) {
          await helpers.createCardElement({ type: "entities", entities: [] });
        }
      } catch {}
    }
    return document.createElement("brainstorm-mindmap-card-editor");
  }

  getConfigElement() {
    return BrainstormMindmapCard.getConfigElement();
  }

  static getStubConfig(hass) {
    return {
      ...BRAINSTORM_MINDMAP_DEFAULTS,
      show_last_alexa: false,
      last_alexa_entity: "sensor.last_alexa",
    };
  }

  setConfig(config) {
    if (!config) config = {};
    this._rawConfig = config;
    const parsedConfig = { ...BRAINSTORM_MINDMAP_DEFAULTS };
    for (const key of Object.keys(BRAINSTORM_MINDMAP_DEFAULTS)) {
      if (key in config) {
        if (typeof BRAINSTORM_MINDMAP_DEFAULTS[key] === "boolean") {
          parsedConfig[key] = config[key] === true || config[key] === "true";
        } else {
          parsedConfig[key] = config[key];
        }
      }
    }
    this._config = { ...config, ...parsedConfig };

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
    if (topBar) topBar.style.display = this._config.show_toolbar === true ? "flex" : "none";

    const bulbWrap = this.shadowRoot.querySelector(".center-bulb-wrapper");
    if (bulbWrap) bulbWrap.style.display = this._config.show_bulb_watermark === true ? "block" : "none";

    const gridBg = this.shadowRoot.getElementById("gridBg");
    if (gridBg) gridBg.style.display = this._config.show_grid !== false ? "block" : "none";

    const colorModeBtn = this.shadowRoot.getElementById("colorModeBtn");
    if (colorModeBtn) colorModeBtn.style.display = this._config.show_color_toggle === true ? "inline-flex" : "none";

    const fullscreenBtn = this.shadowRoot.getElementById("fullscreenToggleBtn");
    if (fullscreenBtn) fullscreenBtn.style.display = this._config.show_fullscreen_btn === true ? "inline-flex" : "none";

    const controlsPanel = this.shadowRoot.querySelector(".controls-panel");
    if (controlsPanel) controlsPanel.style.display = this._config.show_controls === true ? "flex" : "none";

    const addNoteBtn = this.shadowRoot.getElementById("addNoteBtn");
    if (addNoteBtn) addNoteBtn.style.display = this._config.show_add_btn === true ? "flex" : "none";

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
    const alexaInfo = this._getLastAlexaInfo();
    const currentAlexaKey = alexaInfo ? `${alexaInfo.entityId}_${alexaInfo.name}_${alexaInfo.state}` : "";
    const sig = `${sensor.last_updated}_${this._selectedCategory}_${ideas.length}_${categories.length}_${currentAlexaKey}`;
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

  _getLastAlexaInfo() {
    if (!this._config || this._config.show_last_alexa !== true) return null;
    const entityId = (this._config && this._config.last_alexa_entity) || "sensor.last_alexa";
    if (!this._hass || !this._hass.states || !this._hass.states[entityId]) {
      return null;
    }
    const stateObj = this._hass.states[entityId];
    if (!stateObj || stateObj.state === "unavailable" || stateObj.state === "unknown" || !stateObj.state) {
      return null;
    }

    let targetEntityId = stateObj.state;
    let displayName = "";
    let mediaState = null;

    if (
      typeof targetEntityId === "string" &&
      (targetEntityId.startsWith("media_player.") || targetEntityId.startsWith("sensor."))
    ) {
      const targetObj = this._hass.states[targetEntityId];
      if (targetObj) {
        displayName = (targetObj.attributes && targetObj.attributes.friendly_name) || targetEntityId;
        mediaState = targetObj.state;
      } else {
        displayName = targetEntityId.replace(/^media_player\./, "").replace(/_/g, " ");
      }
    } else if (stateObj.entity_id.startsWith("media_player.")) {
      displayName = (stateObj.attributes && stateObj.attributes.friendly_name) || stateObj.entity_id;
      mediaState = stateObj.state;
      targetEntityId = stateObj.entity_id;
    } else {
      displayName = stateObj.state;
      targetEntityId = stateObj.entity_id;
    }

    return {
      entityId: targetEntityId,
      name: displayName,
      state: mediaState || stateObj.state,
    };
  }

  _openEntityMoreInfo(entityId) {
    if (!entityId) return;
    this.dispatchEvent(
      new CustomEvent("hass-more-info", {
        detail: { entityId },
        bubbles: true,
        composed: true,
      })
    );
  }

  _getCategoryColor(category) {
    if (this._colorMode === "theme") {
      return "var(--primary-color, #a855f7)";
    }
    if (!category) return "#2563eb";

    // 0. Check custom color from sensor attributes first
    const sensor = this._getSensorEntity();
    if (sensor && sensor.attributes && sensor.attributes.category_colors) {
      const customColor = sensor.attributes.category_colors[category];
      if (customColor && CSS.supports("color", customColor)) return customColor;
    }

    const catNorm = String(category).trim().toLowerCase();

    // 1. Curated, high-contrast, beautiful palette for all standard categories
    const categoryPalette = {
      "inbox": "#2563eb",         // Royal / Tech Blue 🔵
      "smarthome": "#06b6d4",     // Vivid Aqua / Cyan 🔷
      "haus & garten": "#10b981", // Fresh Emerald Green 🟢
      "haus": "#10b981",
      "garten": "#10b981",
      "projekte": "#6366f1",      // Vibrant Indigo 🟣
      "projekt": "#6366f1",
      "alltag": "#f59e0b",        // Warm Amber / Gold 🟡
      "brainstorm": "#a855f7",    // Electric Purple 🔮
      "ideen": "#ec4899",         // Vivid Pink / Rose 🌸
      "idee": "#ec4899",
      "einkauf": "#ea580c",       // Coral Orange 🍊
      "shopping": "#ea580c",
      "finanzen": "#14b8a6",      // Mint / Teal 🪙
      "finanz": "#14b8a6",
      "familie": "#f43f5e",       // Deep Rose ❤️
      "kinder": "#fb7185",
      "arbeit": "#0284c7",        // Sky Blue 💼
      "beruf": "#0284c7",
      "work": "#0284c7",
      "gesundheit": "#84cc16",    // Lime Green 🍏
      "sport": "#84cc16",
      "fitness": "#84cc16",
      "auto": "#e11d48",          // Crimson 🚗
      "urlaub": "#38bdf8",        // Ocean Cyan 🏖️
      "reise": "#38bdf8",
      "notizen": "#8b5cf6",
      "schlaue antworten": "#8b5cf6",
    };

    if (categoryPalette[catNorm]) {
      return categoryPalette[catNorm];
    }

    // 2. Deterministic hash palette for any custom/new user-defined category
    const fallbackPalette = [
      "#06b6d4", // Cyan
      "#10b981", // Emerald
      "#f59e0b", // Amber
      "#a855f7", // Purple
      "#ec4899", // Pink
      "#2563eb", // Blue
      "#ea580c", // Orange
      "#14b8a6", // Teal
      "#6366f1", // Indigo
      "#f43f5e", // Rose
      "#84cc16", // Lime
      "#0284c7", // Sky Blue
      "#d946ef", // Fuchsia
      "#eab308", // Yellow
    ];

    let hash = 0;
    for (let i = 0; i < catNorm.length; i++) {
      hash = (hash << 5) - hash + catNorm.charCodeAt(i);
      hash |= 0;
    }
    const idx = Math.abs(hash) % fallbackPalette.length;
    return fallbackPalette[idx];
  }

  _getCategoryIcon(category) {
    if (!category) return "mdi:bookmark-outline";
    if (category === "all") return "mdi:layers-outline";

    // 1. Check custom icon from sensor attributes first
    const sensor = this._getSensorEntity();
    if (sensor && sensor.attributes && sensor.attributes.category_icons) {
      const customIcon = sensor.attributes.category_icons[category];
      if (customIcon && /^[\w-]+:[\w-]+$/.test(customIcon)) return customIcon;
    }

    // 2. Curated default icons
    const catNorm = String(category).trim().toLowerCase();
    const defaultIcons = {
      "inbox": "mdi:inbox",
      "smarthome": "mdi:home-automation",
      "smart home": "mdi:home-automation",
      "haus & garten": "mdi:flower",
      "haus": "mdi:home-roof",
      "garten": "mdi:flower",
      "projekte": "mdi:clipboard-check-outline",
      "projekt": "mdi:clipboard-check-outline",
      "alltag": "mdi:calendar-check",
      "brainstorm": "mdi:brain",
      "ideen": "mdi:lightbulb-outline",
      "idee": "mdi:lightbulb-outline",
      "familie": "mdi:account-group",
      "kinder": "mdi:account-child",
      "einkauf": "mdi:cart",
      "shopping": "mdi:cart",
      "schlaue antworten": "mdi:comment-question-outline",
      "finanzen": "mdi:cash-multiple",
      "finanz": "mdi:cash-multiple",
      "arbeit": "mdi:briefcase",
      "beruf": "mdi:briefcase",
      "work": "mdi:briefcase",
      "gesundheit": "mdi:heart-pulse",
      "fitness": "mdi:dumbbell",
      "sport": "mdi:dumbbell",
      "auto": "mdi:car",
      "urlaub": "mdi:beach",
      "reise": "mdi:airplane",
      "notizen": "mdi:notebook-outline",
      "notiz": "mdi:notebook-outline",
    };
    return defaultIcons[catNorm] || "mdi:tag-outline";
  }

  _getSourceBadge(source, device) {
    if (!source && !device) return "📝";
    const s = String(source || "").toLowerCase();
    let icon = "📝";
    if (s.includes("assist")) icon = "✨";
    else if (s.includes("alexa") || s.includes("voice") || s.includes("speech")) icon = "🗣️";
    else if (s.includes("mobile") || s.includes("handy") || s.includes("companion")) icon = "📱";
    else if (s.includes("dashboard")) icon = "💻";

    if (device && String(device).trim()) {
      return `${icon} <span class="cloud-device" title="Gerät: ${this._escapeHtml(String(device).trim())}">(${this._escapeHtml(String(device).trim())})</span>`;
    }
    return `${icon}`;
  }

  _getSourceIcon(source) {
    return this._getSourceBadge(source);
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

  _getPriorityBadge(priority, id = "") {
    const p = (priority || "medium").toLowerCase();
    const idAttr = id ? `data-id="${this._escapeHtml(id)}"` : "";
    if (p === "urgent") {
      return `<span class="prio-tag urgent" ${idAttr} data-prio="urgent" title="Priorität: 🔥 Dringend (Klicken zum Umschalten)">🔥 Dringend</span>`;
    }
    if (p === "high") {
      return `<span class="prio-tag high" ${idAttr} data-prio="high" title="Priorität: 🔴 Hoch (Klicken zum Umschalten)">🔴 Hoch</span>`;
    }
    if (p === "low") {
      return `<span class="prio-tag low" ${idAttr} data-prio="low" title="Priorität: 🟢 Niedrig (Klicken zum Umschalten)">🟢 Niedrig</span>`;
    }
    return `<span class="prio-tag medium" ${idAttr} data-prio="medium" title="Priorität: 🟡 Mittel (Klicken zum Umschalten)">🟡 Mittel</span>`;
  }

  _cyclePriority(currentPrio) {
    const cycle = {
      medium: "high",
      high: "urgent",
      urgent: "low",
      low: "medium",
    };
    return cycle[currentPrio] || "medium";
  }

  async _toggleItemPriority(id, currentPrio) {
    const nextPrio = this._cyclePriority(currentPrio);
    try {
      await this._hass.callService("brainstorm", "update_idea", {
        id: id,
        priority: nextPrio,
      });
    } catch (err) {
      console.error("[BrainstormMindmap] Failed to toggle priority:", err);
    }
  }

  _renderLogoSvg(uniqueId = "mindmap") {
    return `
      <svg viewBox="136 58 240 261" class="brand-logo-svg" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="bsCyan_${uniqueId}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#00f5ff"/>
            <stop offset="100%" stop-color="#0284c7"/>
          </linearGradient>
          <linearGradient id="bsPurple_${uniqueId}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ff2a8d"/>
            <stop offset="50%" stop-color="#a855f7"/>
            <stop offset="100%" stop-color="#6366f1"/>
          </linearGradient>
          <linearGradient id="bsAmber_${uniqueId}" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#fef08a"/>
            <stop offset="50%" stop-color="#fbbf24"/>
            <stop offset="100%" stop-color="#f97316"/>
          </linearGradient>
          <linearGradient id="bsMetal_${uniqueId}" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#64748b"/>
            <stop offset="50%" stop-color="#cbd5e1"/>
            <stop offset="100%" stop-color="#475569"/>
          </linearGradient>
          <filter id="bsGlow_${uniqueId}" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <!-- Soft Ambient Light Halo (Transparent Background) -->
        <circle cx="256" cy="178" r="85" fill="#00f5ff" opacity="0.16" filter="url(#bsGlow_${uniqueId})"/>
        <!-- Outer Bulb Glass Contour (Fuller, bolder, fills 100% of space) -->
        <path d="M 144 178 C 144 116, 194 66, 256 66 C 318 66, 368 116, 368 178 C 368 222, 326 248, 306 272 L 206 272 C 186 248, 144 222, 144 178 Z" fill="none" stroke="url(#bsCyan_${uniqueId})" stroke-width="12" stroke-linejoin="round" opacity="0.95"/>
        <!-- Glass Highlight Reflection -->
        <path d="M 166 150 C 166 112, 196 86, 238 78" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.8"/>
        <!-- Digital Circuit Brain Synapses (Left Hemisphere) -->
        <g filter="url(#bsGlow_${uniqueId})">
          <path d="M 240 110 C 206 106, 180 134, 182 165 C 183 186, 202 192, 206 208 C 210 224, 196 236, 206 254 C 214 266, 228 268, 238 270" fill="none" stroke="url(#bsCyan_${uniqueId})" stroke-width="11" stroke-linecap="round"/>
          <path d="M 195 170 Q 220 178 238 178" fill="none" stroke="url(#bsCyan_${uniqueId})" stroke-width="7" stroke-linecap="round"/>
          <path d="M 206 215 Q 225 218 238 224" fill="none" stroke="url(#bsCyan_${uniqueId})" stroke-width="7" stroke-linecap="round"/>
          <circle cx="182" cy="165" r="6" fill="#00f5ff"/>
          <circle cx="206" cy="208" r="6" fill="#00f5ff"/>
          <circle cx="206" cy="254" r="6" fill="#00f5ff"/>
        </g>
        <!-- Creative Folds Brain (Right Hemisphere) -->
        <g filter="url(#bsGlow_${uniqueId})">
          <path d="M 272 110 C 306 106, 332 134, 330 165 C 329 186, 310 192, 306 208 C 302 224, 316 236, 306 254 C 298 266, 284 268, 274 270" fill="none" stroke="url(#bsPurple_${uniqueId})" stroke-width="11" stroke-linecap="round"/>
          <path d="M 317 170 Q 292 178 274 178" fill="none" stroke="url(#bsPurple_${uniqueId})" stroke-width="7" stroke-linecap="round"/>
          <path d="M 306 215 Q 287 218 274 224" fill="none" stroke="url(#bsPurple_${uniqueId})" stroke-width="7" stroke-linecap="round"/>
          <circle cx="330" cy="165" r="6" fill="#ff2a8d"/>
          <circle cx="306" cy="208" r="6" fill="#ff2a8d"/>
          <circle cx="306" cy="254" r="6" fill="#ff2a8d"/>
        </g>
        <!-- Central Idea Lightning Bolt / Spark -->
        <g filter="url(#bsGlow_${uniqueId})">
          <path d="M 258 100 L 244 158 L 268 158 L 246 226 L 274 168 L 252 168 Z" fill="url(#bsAmber_${uniqueId})"/>
        </g>
        <circle cx="256" cy="162" r="8" fill="#ffffff"/>
        <!-- Compact Metallic Base Fitting -->
        <rect x="202" y="275" width="108" height="13" rx="6.5" fill="url(#bsMetal_${uniqueId})" stroke="rgba(0,0,0,0.18)" stroke-width="1.5"/>
        <rect x="212" y="290" width="88" height="12" rx="6" fill="url(#bsMetal_${uniqueId})" stroke="rgba(0,0,0,0.18)" stroke-width="1.5"/>
        <path d="M 230 304 C 230 304, 238 316, 256 316 C 274 316, 282 304, 282 304 Z" fill="#334155"/>
        <circle cx="256" cy="310" r="4" fill="#00f5ff"/>
      </svg>
    `;
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
          container-type: inline-size;
          container-name: brainstorm-mindmap;
          width: 100%;
          height: 100%;
          box-sizing: border-box;
          font-family: var(--ha-font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif);
        }
        ha-card {
          container-type: inline-size;
          container-name: brainstorm-mindmap-card;
          position: relative;
          width: 100%;
          height: 100%;
          min-height: clamp(360px, 60vh, 550px);
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border-radius: var(--ha-card-border-radius, 16px);
          border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.12)));
          box-shadow: var(--ha-card-box-shadow, 0 4px 20px rgba(0,0,0,0.06));
          overflow: hidden;
          display: flex;
          flex-direction: column;
          color: var(--primary-text-color, #212121);
          box-sizing: border-box;
        }

        /* Top Bar */
        .top-bar {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          z-index: 20;
          padding: 10px 14px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
          flex-wrap: nowrap;
          background: linear-gradient(180deg, var(--ha-card-background, var(--card-background-color, #ffffff)) 0%, color-mix(in srgb, var(--ha-card-background, var(--card-background-color, #ffffff)) 0%, transparent) 100%);
          pointer-events: none;
        }
        .top-left {
          display: flex;
          align-items: center;
          gap: 8px;
          flex: 0 0 auto;
          pointer-events: auto;
        }
        .top-right {
          display: flex;
          align-items: center;
          gap: 6px;
          flex: 1 1 auto;
          min-width: 0;
          justify-content: flex-end;
          pointer-events: auto;
        }
        .brand-logo {
          width: 36px;
          height: 36px;
          border-radius: 9px;
          overflow: hidden;
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 12%, var(--card-background-color, #ffffff));
          border: 1px solid color-mix(in srgb, var(--primary-color, #03a9f4) 25%, var(--divider-color, rgba(127, 127, 127, 0.15)));
          box-shadow: 0 2px 8px color-mix(in srgb, var(--primary-color, #03a9f4) 18%, transparent);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 1px;
          box-sizing: border-box;
          flex-shrink: 0;
          transition: all 0.25s ease;
        }
        .brand-logo:hover {
          transform: scale(1.06);
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 3px 12px color-mix(in srgb, var(--primary-color, #03a9f4) 30%, transparent);
        }
        .brand-logo svg {
          width: 100%;
          height: 100%;
          object-fit: contain;
          display: block;
        }
        .title {
          font-size: 1.05rem;
          font-weight: 700;
          color: var(--primary-text-color, #212121);
        }
        .last-alexa-wrap {
          display: inline-flex;
          align-items: center;
        }
        .last-alexa-badge {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 14%, var(--card-background-color, #1e1e24));
          border: 1px solid color-mix(in srgb, var(--primary-color, #03a9f4) 28%, var(--divider-color, rgba(127, 127, 127, 0.2)));
          border-radius: 10px;
          padding: 2px 7px;
          font-size: 0.72rem;
          font-weight: 500;
          color: var(--primary-text-color, #ffffff);
          cursor: pointer;
          user-select: none;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          max-width: 180px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          line-height: 1.35;
          flex-shrink: 0;
        }
        .last-alexa-badge:hover {
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 22%, var(--card-background-color, #1e1e24));
          border-color: var(--primary-color, #03a9f4);
          transform: translateY(-1px);
          box-shadow: 0 2px 6px color-mix(in srgb, var(--primary-color, #03a9f4) 25%, transparent);
        }
        .alexa-badge-icon {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          color: var(--primary-color, #03a9f4);
          flex-shrink: 0;
        }
        .alexa-badge-icon svg {
          display: block;
        }
        .alexa-badge-name {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
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
          -webkit-overflow-scrolling: touch;
          flex: 1 1 auto;
          min-width: 0;
          max-width: none;
          padding: 2px 4px;
          pointer-events: auto;
          scrollbar-width: none;
        }
        .pills-container::-webkit-scrollbar {
          display: none;
        }
        @container (max-width: 600px), (max-width: 600px) {
          .cat-pill[data-cat="all"] {
            display: none !important;
          }
          .title {
            display: none !important;
          }
          .cat-pill {
            padding: 4px 10px !important;
            min-height: 28px !important;
            font-size: 0.74rem !important;
            border-radius: 14px !important;
          }
          .pill-dot {
            width: 7px !important;
            height: 7px !important;
          }
          .top-tool-btn,
          .fullscreen-btn {
            width: 32px !important;
            height: 32px !important;
            font-size: 0.95rem !important;
          }
          .note-cloud {
            padding: 7px 10px !important;
            min-width: 130px !important;
            max-width: 190px !important;
            margin-left: -65px !important;
            margin-top: -32px !important;
            border-radius: 12px !important;
          }
          .cloud-text {
            font-size: 0.82rem !important;
            line-height: 1.24 !important;
            margin-bottom: 5px !important;
          }
          .cloud-meta {
            font-size: 0.68rem !important;
            margin-bottom: 4px !important;
          }
          .center-node {
            width: 115px !important;
            height: 115px !important;
            margin-left: -57px !important;
            margin-top: -57px !important;
            padding: 6px !important;
          }
          .center-bulb-wrapper {
            width: 38px !important;
            height: 38px !important;
          }
          .center-title {
            font-size: 0.9rem !important;
          }
          .center-badge {
            font-size: 0.62rem !important;
            padding: 1px 5px !important;
          }
          .add-note-btn {
            bottom: 10px !important;
            left: 10px !important;
            padding: 6px 12px !important;
            font-size: 0.78rem !important;
            border-radius: 16px !important;
          }
          .controls-panel {
            bottom: 10px !important;
            right: 10px !important;
            gap: 6px !important;
          }
          .control-btn {
            width: 32px !important;
            height: 32px !important;
            font-size: 1rem !important;
          }
        }
        @container (max-width: 380px), (max-width: 380px) {
          .add-note-btn .btn-text {
            display: none !important;
          }
          .add-note-btn {
            width: 34px !important;
            height: 34px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            justify-content: center !important;
          }
        }
        @media (max-width: 480px) {
          .dialog-backdrop {
            padding: 8px !important;
          }
          .dialog-box {
            max-width: 100% !important;
            border-radius: 16px !important;
            max-height: calc(100dvh - 16px) !important;
          }
          .dialog-header {
            padding: 12px 14px !important;
          }
          .dialog-body {
            padding: 12px 14px !important;
            gap: 10px !important;
            max-height: calc(80dvh - 60px) !important;
          }
          .dialog-prio-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 6px !important;
          }
          .dialog-categories-grid {
            grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)) !important;
            gap: 6px !important;
          }
          .dialog-input,
          .dialog-textarea {
            font-size: 16px !important;
          }
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
          display: inline-flex;
          align-items: center;
          gap: 6px;
          transition: all 0.2s ease;
        }
        .cat-pill:hover {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
          color: var(--primary-text-color, #212121);
          transform: translateY(-1px);
        }
        .cat-pill.active {
          background: color-mix(in srgb, var(--category-color, var(--primary-color)) 15%, var(--card-background-color, #ffffff));
          color: var(--category-color, var(--primary-color));
          border-color: var(--category-color, var(--primary-color));
          box-shadow: 0 2px 8px color-mix(in srgb, var(--category-color, var(--primary-color)) 25%, transparent);
        }
        .pill-dot {
          display: inline-block;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--category-color, var(--primary-color));
          flex-shrink: 0;
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
          background: transparent;
        }
        .canvas-area:active {
          cursor: grabbing;
        }
        .grid-bg {
          position: absolute;
          inset: 0;
          background-image: radial-gradient(circle at center, var(--divider-color, rgba(127, 127, 127, 0.22)) 0.75px, transparent 1.6px);
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
        }

        /* SVG Connectors */
        svg.connectors {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          overflow: visible;
          pointer-events: none;
          z-index: 1;
        }
        .synapse-path {
          fill: none;
          stroke: var(--path-color, var(--divider-color, rgba(127, 127, 127, 0.25)));
          stroke-opacity: 0.38;
          stroke-width: 1.8;
          stroke-dasharray: 4, 4;
          transition: stroke 0.2s ease, stroke-width 0.2s ease, stroke-opacity 0.2s ease;
        }
        .synapse-path.highlight {
          stroke: var(--path-color, var(--primary-color, #03a9f4)) !important;
          stroke-opacity: 0.95 !important;
          stroke-width: 2.8 !important;
          stroke-dasharray: none !important;
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
        .note-cloud.cloud-urgent {
          border-left-color: #ef4444 !important;
          box-shadow: 0 0 14px rgba(239, 68, 68, 0.28) !important;
        }
        .note-cloud.cloud-high {
          border-left-color: #f97316 !important;
        }
        .prio-tag {
          font-weight: 600;
          font-size: 0.68rem;
          padding: 2px 7px;
          border-radius: 8px;
          cursor: pointer;
          user-select: none;
          transition: transform 0.15s ease, filter 0.15s ease;
          display: inline-flex;
          align-items: center;
          gap: 3px;
        }
        .prio-tag:hover {
          transform: scale(1.05);
          filter: brightness(0.92);
        }
        .prio-tag.urgent {
          color: #ef4444;
          background: color-mix(in srgb, #ef4444 14%, var(--card-background-color, #ffffff));
          border: 1px solid color-mix(in srgb, #ef4444 35%, transparent);
          box-shadow: 0 0 6px rgba(239, 68, 68, 0.2);
        }
        .prio-tag.high {
          color: #f97316;
          background: color-mix(in srgb, #f97316 14%, var(--card-background-color, #ffffff));
          border: 1px solid color-mix(in srgb, #f97316 35%, transparent);
        }
        .prio-tag.medium {
          color: #eab308;
          background: color-mix(in srgb, #eab308 12%, var(--card-background-color, #ffffff));
          border: 1px solid color-mix(in srgb, #eab308 25%, transparent);
        }
        .prio-tag.low {
          color: #10b981;
          background: color-mix(in srgb, #10b981 12%, var(--card-background-color, #ffffff));
          border: 1px solid color-mix(in srgb, #10b981 25%, transparent);
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
        .cloud-device {
          font-size: 0.68rem;
          opacity: 0.85;
          max-width: 110px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          display: inline-block;
          vertical-align: middle;
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
          grid-template-columns: repeat(auto-fill, minmax(95px, 1fr));
          gap: 6px;
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
        .dialog-prio-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(75px, 1fr));
          gap: 6px;
          margin-bottom: 14px;
        }
        .dialog-prio-chip {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
          padding: 8px 6px;
          border-radius: 10px;
          font-size: 0.82rem;
          font-weight: 600;
          cursor: pointer;
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
          background: var(--card-background-color, var(--ha-card-background, #ffffff));
          color: var(--primary-text-color, #222);
          transition: all 0.15s ease;
          user-select: none;
        }
        .dialog-prio-chip:hover {
          border-color: var(--chip-prio-color, var(--primary-color, #03a9f4));
          background: color-mix(in srgb, var(--chip-prio-color, var(--primary-color, #03a9f4)) 10%, transparent);
        }
        .dialog-prio-chip.selected {
          border-color: var(--chip-prio-color, var(--primary-color, #03a9f4));
          background: color-mix(in srgb, var(--chip-prio-color, var(--primary-color, #03a9f4)) 18%, transparent);
          color: var(--chip-prio-color, var(--primary-color, #03a9f4));
          font-weight: 700;
          box-shadow: 0 0 0 1px var(--chip-prio-color, var(--primary-color, #03a9f4));
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
        <div class="top-bar" style="display: ${this._config.show_toolbar === true ? 'flex' : 'none'};">
          <div class="top-left">
            <div class="brand-logo" id="brandLogo" style="display: ${this._config.show_logo !== false ? 'flex' : 'none'};">
              ${this._renderLogoSvg("mindmap")}
            </div>
            <div class="title" id="cardTitle">${this._config.title !== undefined ? this._config.title : "Brainstorm Mindmap"}</div>
            <div id="mindmapLastAlexaWrap" class="last-alexa-wrap" style="display: none;"></div>
          </div>
          <div class="pills-container" id="pillsBar"></div>
          <div class="top-right">
            <button class="top-tool-btn" id="colorModeBtn" style="display: ${this._config.show_color_toggle === true ? 'inline-flex' : 'none'};" title="${this._colorMode === 'theme' ? 'Farbmodus: Theme-Farben aktiv (Klicken für Bunt)' : 'Farbmodus: Bunt aktiv (Klicken für Theme-Farben)'}">
              ${this._colorMode === 'theme' ? '🎨' : '🌈'}
            </button>
            <button class="fullscreen-btn" id="fullscreenToggleBtn" style="display: ${this._config.show_fullscreen_btn === true ? 'inline-flex' : 'none'};" title="Vollbild umschalten (ESC zum Beenden)">⛶</button>
          </div>
        </div>

        <!-- Interactive Canvas Area -->
        <div class="canvas-area" id="canvasArea">
          <div class="grid-bg" id="gridBg" style="display: ${this._config.show_grid !== false ? 'block' : 'none'};"></div>
          <div class="viewport" id="viewport">
            <svg class="connectors" id="connectorsLayer"></svg>
            <div class="center-node" id="centerNode">
              <div class="center-bulb-wrapper" style="display: ${this._config.show_bulb_watermark === true ? 'block' : 'none'};">
                <img src="/local/brainstorm-bulb.svg" class="center-bulb-img" alt="Brainstorm" />
              </div>
              <div class="center-content">
                <div class="center-icon" id="centerIcon" style="display: flex; justify-content: center; margin-bottom: 2px;"></div>
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
        <button class="add-note-btn" id="addNoteBtn" style="display: ${this._config.show_add_btn === true ? 'flex' : 'none'};">
          <span>➕</span>
          <span class="btn-text">Neue Idee</span>
        </button>

        <!-- Bottom Right: Zoom & Reset Controls -->
        <div class="controls-panel" style="display: ${this._config.show_controls === true ? 'flex' : 'none'};">
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
            if (!this._userMovedNodes || this._userMovedNodes.size === 0) {
              this._arrangeNodesRadially();
            } else {
              this._drawConnections();
            }
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
        if (this._userMovedNodes) {
          this._userMovedNodes.add(this._activeDrag.id);
        }
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
        if (this._userMovedNodes) {
          this._userMovedNodes.add(this._activeDrag.id);
        }
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
      const attributes = sensor.attributes || {};
      const hideEmptyCategories = this._rawConfig && this._rawConfig.hide_empty_categories !== undefined
        ? (this._rawConfig.hide_empty_categories === true || this._rawConfig.hide_empty_categories === "true")
        : (attributes.hide_empty_categories !== undefined ? attributes.hide_empty_categories === true : true);
      const allCats = attributes.categories || ["Inbox"];
      const counts = attributes.category_counts || {};
      const validCats = hideEmptyCategories
        ? allCats.filter((c) => (counts[c] || 0) > 0 || this._selectedCategory === c)
        : allCats;
      const isMobile = window.matchMedia && window.matchMedia("(max-width: 600px)").matches;
      const categories = isMobile ? validCats : ["all", ...validCats];
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
    const gridBg = this.shadowRoot.getElementById("gridBg");
    if (gridBg) {
      const size = Math.max(12, Math.min(60, 24 * this._scale));
      gridBg.style.backgroundPosition = `${this._panX}px ${this._panY}px`;
      gridBg.style.backgroundSize = `${size}px ${size}px`;
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
      if (this._userMovedNodes) this._userMovedNodes.clear();
      this._nodePositions.clear();
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
      this._nodePositions.clear();
      this._drawConnections();
      return;
    }

    // Clean up _nodePositions: remove any nodes not in current filtered ideas
    const activeIds = new Set(ideas.map((i) => i.id));
    for (const id of this._nodePositions.keys()) {
      if (!activeIds.has(id)) {
        this._nodePositions.delete(id);
      }
    }

    // Determine dimensions from canvas
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    let w = 800;
    let h = 600;
    if (canvasArea) {
      const rect = canvasArea.getBoundingClientRect();
      w = canvasArea.clientWidth || rect.width || 800;
      h = canvasArea.clientHeight || rect.height || 600;
    }

    this._centerPos = { x: w / 2, y: h / 2 };

    const centerNode = this.shadowRoot.getElementById("centerNode");
    if (centerNode) {
      centerNode.style.left = `${this._centerPos.x}px`;
      centerNode.style.top = `${this._centerPos.y}px`;
    }

    // Partition nodes into concentric elliptical rings to prevent clustering
    const rings = [];
    if (count <= 6) {
      rings.push(ideas);
    } else if (count <= 12) {
      const nInner = Math.min(5, Math.max(3, Math.floor(count * 0.42)));
      rings.push(ideas.slice(0, nInner));
      rings.push(ideas.slice(nInner));
    } else if (count <= 20) {
      const n1 = 5;
      const n2 = Math.min(7, Math.floor((count - 5) * 0.55));
      rings.push(ideas.slice(0, n1));
      rings.push(ideas.slice(n1, n1 + n2));
      rings.push(ideas.slice(n1 + n2));
    } else {
      let rem = [...ideas];
      let cap = 5;
      while (rem.length > 0) {
        const take = Math.min(cap, rem.length);
        rings.push(rem.slice(0, take));
        rem = rem.slice(take);
        cap += 3;
      }
    }

    // Concentric elliptical radii (adaptive to screen/card width)
    const isNarrow = w < 550;
    const rx0 = count <= 6
      ? Math.max(isNarrow ? 125 : 260, Math.min(w * (isNarrow ? 0.35 : 0.30), isNarrow ? 220 : 360))
      : Math.max(isNarrow ? 115 : 250, Math.min(w * (isNarrow ? 0.28 : 0.22), isNarrow ? 190 : 310));
    const ry0 = count <= 6
      ? Math.max(isNarrow ? 90 : 180, Math.min(h * (isNarrow ? 0.32 : 0.30), isNarrow ? 160 : 220))
      : Math.max(isNarrow ? 85 : 175, Math.min(h * (isNarrow ? 0.25 : 0.24), isNarrow ? 140 : 185));
    const drx = isNarrow ? Math.max(120, Math.min(w * 0.16, 170)) : Math.max(210, Math.min(w * 0.16, 250));
    const dry = isNarrow ? Math.max(70, Math.min(h * 0.14, 95)) : Math.max(110, Math.min(h * 0.16, 135));

    const positionedItems = [];

    rings.forEach((ringIdeas, r) => {
      const n = ringIdeas.length;
      if (n === 0) return;
      const rx = rx0 + r * drx;
      const ry = ry0 + r * dry;
      const phase = -Math.PI / 2 + (r * Math.PI / (n * 2));
      const angleStep = (2 * Math.PI) / n;

      ringIdeas.forEach((idea, j) => {
        // If user already moved this specific node manually, preserve its position
        if (this._userMovedNodes && this._userMovedNodes.has(idea.id) && this._nodePositions.has(idea.id)) {
          const existingPos = this._nodePositions.get(idea.id);
          positionedItems.push({ idea, x: existingPos.x, y: existingPos.y, fixed: true });
          return;
        }

        const angle = phase + j * angleStep;
        const x = this._centerPos.x + Math.cos(angle) * rx;
        const y = this._centerPos.y + Math.sin(angle) * ry;
        positionedItems.push({ idea, x, y, fixed: false });
      });
    });

    // Collision relaxation pass: repel from center bulb and avoid card overlaps
    const cardW = isNarrow ? 160 : 230;
    const cardH = isNarrow ? 70 : 100;
    const minCenterDistX = isNarrow ? 115 : 185;
    const minCenterDistY = isNarrow ? 85 : 135;

    for (let iter = 0; iter < 25; iter++) {
      // 1. Center push-out
      for (const item of positionedItems) {
        if (item.fixed) continue;
        const cdx = item.x - this._centerPos.x;
        const cdy = item.y - this._centerPos.y;
        const norm = (cdx / minCenterDistX) ** 2 + (cdy / minCenterDistY) ** 2;
        if (norm < 1.0 && norm > 0.0001) {
          const factor = Math.sqrt(1.0 / norm) * 1.04;
          item.x = this._centerPos.x + cdx * factor;
          item.y = this._centerPos.y + cdy * factor;
        }
      }

      // 2. Card-to-card repulsion
      for (let i = 0; i < positionedItems.length; i++) {
        for (let j = i + 1; j < positionedItems.length; j++) {
          const a = positionedItems[i];
          const b = positionedItems[j];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const adx = Math.abs(dx);
          const ady = Math.abs(dy);

          if (adx < cardW && ady < cardH) {
            const ox = cardW - adx;
            const oy = cardH - ady;
            if (ox / cardW < oy / cardH) {
              const pushX = (dx >= 0 ? 1 : -1) * (ox / 2 + 1.5);
              if (!a.fixed) a.x -= pushX;
              if (!b.fixed) b.x += pushX;
            } else {
              const pushY = (dy >= 0 ? 1 : -1) * (oy / 2 + 1.5);
              if (!a.fixed) a.y -= pushY;
              if (!b.fixed) b.y += pushY;
            }
          }
        }
      }
    }

    // Apply positions to state & DOM
    positionedItems.forEach((item) => {
      this._nodePositions.set(item.idea.id, { x: item.x, y: item.y });
      const el = this.shadowRoot.getElementById(`cloud_${item.idea.id}`);
      if (el) {
        el.style.left = `${item.x}px`;
        el.style.top = `${item.y}px`;
      }
    });

    // Auto-fit scale if nodes exceed viewport and view is at default scale
    if (positionedItems.length > 0 && this._scale >= 0.95 && this._scale <= 1.05) {
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      positionedItems.forEach((item) => {
        if (item.x - 120 < minX) minX = item.x - 120;
        if (item.x + 120 > maxX) maxX = item.x + 120;
        if (item.y - 55 < minY) minY = item.y - 55;
        if (item.y + 55 > maxY) maxY = item.y + 55;
      });

      const spanW = maxX - minX + 50;
      const spanH = maxY - minY + 50;

      if (spanW > w || spanH > h) {
        const scaleX = w / spanW;
        const scaleY = h / spanH;
        const minFitLimit = isNarrow ? 0.35 : 0.65;
        const fitScale = Math.max(minFitLimit, Math.min(1.0, Math.min(scaleX, scaleY) * 0.92));
        this._scale = fitScale;
        this._panX = (w / 2) * (1 - this._scale);
        this._panY = (h / 2) * (1 - this._scale);
        this._applyTransform();
      }
    }

    this._drawConnections();
  }

  _drawConnections() {
    const svg = this.shadowRoot.getElementById("connectorsLayer");
    if (!svg) return;

    const sensor = this._getSensorEntity();
    if (!sensor) {
      svg.innerHTML = "";
      return;
    }

    const allIdeas = (sensor.attributes && sensor.attributes.ideas) || [];
    const activeIdeas = allIdeas.filter((i) => {
      if (this._selectedCategory === "all") return true;
      return String(i.category || "").trim() === String(this._selectedCategory || "").trim();
    });

    if (!this._centerPos) {
      const canvasArea = this.shadowRoot.getElementById("canvasArea");
      const w = (canvasArea && canvasArea.clientWidth) || 800;
      const h = (canvasArea && canvasArea.clientHeight) || 600;
      this._centerPos = { x: w / 2, y: h / 2 };
    }

    let svgHtml = "";
    activeIdeas.forEach((idea) => {
      const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
      const pos = this._nodePositions.get(idea.id);
      // ONLY draw connection if node is currently rendered in the DOM and has coordinates
      if (!el || !pos) return;

      const catColor = this._getCategoryColor(idea.category);
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
        <path id="path_${idea.id}" class="synapse-path" d="${pathData}" style="--path-color: ${catColor};" />
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

      // Reset node positions and layout when selected category changes
      if (this._lastRenderedCategory !== this._selectedCategory) {
        this._nodePositions.clear();
        if (this._userMovedNodes) this._userMovedNodes.clear();
        this._lastRenderedCategory = this._selectedCategory;
      }

      // Update Card Elements from Config
      const titleEl = this.shadowRoot.getElementById("cardTitle");
      if (titleEl) titleEl.textContent = this._config.title !== undefined ? this._config.title : "Brainstorm Mindmap";

      const lastAlexaWrap = this.shadowRoot.getElementById("mindmapLastAlexaWrap");
      if (lastAlexaWrap) {
        const alexaInfo = this._getLastAlexaInfo();
        if (this._config.show_last_alexa === true && alexaInfo && alexaInfo.name) {
          lastAlexaWrap.style.display = "inline-flex";
          lastAlexaWrap.innerHTML = `
            <div class="last-alexa-badge" title="Zuletzt aktive Alexa: ${this._escapeHtml(alexaInfo.name)} (Klicken für Details)">
              <span class="alexa-badge-icon">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5-3c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
              </span>
              <span class="alexa-badge-name">${this._escapeHtml(alexaInfo.name)}</span>
            </div>
          `;
          const badgeInner = lastAlexaWrap.querySelector(".last-alexa-badge");
          if (badgeInner) {
            badgeInner.addEventListener("click", (e) => {
              e.stopPropagation();
              this._openEntityMoreInfo(alexaInfo.entityId);
            });
          }
        } else {
          lastAlexaWrap.style.display = "none";
          lastAlexaWrap.innerHTML = "";
        }
      }

      const topBar = this.shadowRoot.querySelector(".top-bar");
      if (topBar) topBar.style.display = this._config.show_toolbar === true ? "flex" : "none";

      const bulbWrap = this.shadowRoot.querySelector(".center-bulb-wrapper");
      if (bulbWrap) bulbWrap.style.display = this._config.show_bulb_watermark === true ? "block" : "none";

      const gridBg = this.shadowRoot.getElementById("gridBg");
      if (gridBg) gridBg.style.display = this._config.show_grid !== false ? "block" : "none";

      const colorModeBtn = this.shadowRoot.getElementById("colorModeBtn");
      if (colorModeBtn) {
        colorModeBtn.style.display = this._config.show_color_toggle === true ? "inline-flex" : "none";
        colorModeBtn.innerHTML = this._colorMode === "theme" ? "🎨" : "🌈";
        colorModeBtn.title = this._colorMode === "theme"
          ? "Farbmodus: Theme-Farben aktiv (Klicken für Bunt)"
          : "Farbmodus: Bunt aktiv (Klicken für Theme-Farben)";
      }

      const fullscreenBtn = this.shadowRoot.getElementById("fullscreenToggleBtn");
      if (fullscreenBtn) fullscreenBtn.style.display = this._config.show_fullscreen_btn === true ? "inline-flex" : "none";

      const controlsPanel = this.shadowRoot.querySelector(".controls-panel");
      if (controlsPanel) controlsPanel.style.display = this._config.show_controls === true ? "flex" : "none";

      const addNoteBtn = this.shadowRoot.getElementById("addNoteBtn");
      if (addNoteBtn) addNoteBtn.style.display = this._config.show_add_btn === true ? "flex" : "none";

      const cardRoot = this.shadowRoot.getElementById("cardRoot");
      if (cardRoot && this._config.height && !this._isFullscreen) {
        cardRoot.style.height = this._config.height;
      }

      // 1. Update Top Category Pills
      const pillsBar = this.shadowRoot.getElementById("pillsBar");
      if (pillsBar) {
        const counts = attributes.category_counts || {};
        const hideEmptyCategories = this._rawConfig && this._rawConfig.hide_empty_categories !== undefined
          ? (this._rawConfig.hide_empty_categories === true || this._rawConfig.hide_empty_categories === "true")
          : (attributes.hide_empty_categories !== undefined ? attributes.hide_empty_categories === true : true);

        const visibleCategories = categories.filter((cat) => {
          if (!hideEmptyCategories) return true;
          const count = counts[cat] || 0;
          const isActive = String(this._selectedCategory || "").trim() === String(cat || "").trim();
          return count > 0 || isActive;
        });

        const isMobile = window.matchMedia && window.matchMedia("(max-width: 600px)").matches;
        if (isMobile && this._selectedCategory === "all" && visibleCategories.length > 0) {
          this._selectedCategory = visibleCategories[0];
        }

        pillsBar.innerHTML = `
          <div class="cat-pill ${this._selectedCategory === "all" ? "active" : ""}" data-cat="all" style="--category-color: var(--primary-color, #a855f7);">
            <ha-icon icon="mdi:layers-outline" style="--mdc-icon-size: 14px; width: 14px; height: 14px; margin-right: 4px; display: inline-flex; align-items: center; vertical-align: middle; color: ${this._selectedCategory === 'all' ? '#ffffff' : 'var(--primary-color, #a855f7)'};"></ha-icon>
            <span>Alle (${activeIdeas.length})</span>
          </div>
          ${visibleCategories
            .map((cat) => {
              const c = counts[cat] || 0;
              const catColor = this._getCategoryColor(cat);
              const catIcon = this._getCategoryIcon(cat);
              const isActive = String(this._selectedCategory || "").trim() === String(cat || "").trim();
              return `
                <div class="cat-pill ${isActive ? "active" : ""}" data-cat="${this._escapeHtml(cat)}" style="--category-color: ${catColor};">
                  <ha-icon icon="${catIcon}" style="--mdc-icon-size: 14px; width: 14px; height: 14px; margin-right: 4px; display: inline-flex; align-items: center; vertical-align: middle; color: ${isActive ? '#ffffff' : catColor};"></ha-icon>
                  <span>${this._escapeHtml(cat)}</span>
                  <span style="opacity: 0.75; font-size: 0.72rem;">(${c})</span>
                </div>
              `;
            })
            .join("")}
        `;

        pillsBar.querySelectorAll(".cat-pill").forEach((pill) => {
          pill.addEventListener("click", () => {
            const newCat = String(pill.getAttribute("data-cat") || "").trim();
            if (this._selectedCategory !== newCat) {
              this._selectedCategory = newCat;
              this._nodePositions.clear();
              if (this._userMovedNodes) this._userMovedNodes.clear();
              this._lastDataSignature = "";
              this._centerLayout(true);
              this._updateContent();
            }
          });
        });
      }

      // 2. Update Center Node
      const centerTitle = this.shadowRoot.getElementById("centerTitle");
      const centerBadge = this.shadowRoot.getElementById("centerBadge");
      const centerNode = this.shadowRoot.getElementById("centerNode");
      const centerIcon = this.shadowRoot.getElementById("centerIcon");

      if (centerTitle && centerBadge) {
        const displayCat = this._selectedCategory === "all" ? "Alle" : this._selectedCategory;
        centerTitle.textContent = displayCat;
        centerBadge.textContent = `${filteredIdeas.length} ${filteredIdeas.length === 1 ? "Idee" : "Ideen"}`;

        // Accent border color matching category
        const catColor = this._selectedCategory === "all"
          ? "var(--primary-color, #a855f7)"
          : this._getCategoryColor(this._selectedCategory);
        centerNode.style.setProperty("--cat-color", catColor);
        centerNode.style.borderColor = catColor;
        centerNode.style.boxShadow = `0 4px 20px color-mix(in srgb, ${catColor} 25%, transparent)`;

        if (centerIcon) {
          const ic = this._getCategoryIcon(this._selectedCategory);
          centerIcon.innerHTML = `<ha-icon icon="${ic}" style="--mdc-icon-size: 26px; width: 26px; height: 26px; color: ${catColor};"></ha-icon>`;
        }
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
        const sourceBadge = this._getSourceBadge(idea.source, idea.device);
        const timeAgo = this._formatTime(idea.created_at);
        const prio = (idea.priority || "medium").toLowerCase();
        const prioClass = prio === "urgent" ? "cloud-urgent" : prio === "high" ? "cloud-high" : "";
        const prioBadge = this._getPriorityBadge(idea.priority, idea.id);

        html += `
          <div class="note-cloud ${prioClass}" id="cloud_${idea.id}" data-id="${idea.id}" style="--cat-color: ${color};">
            <div class="cloud-meta">
              <span class="cat-tag" data-cat="${this._escapeHtml(idea.category)}" title="Kategorie ändern">
                <ha-icon icon="${this._getCategoryIcon(idea.category)}" style="--mdc-icon-size: 12px; width: 12px; height: 12px; display: inline-flex; align-items: center; vertical-align: middle;"></ha-icon> ${this._escapeHtml(idea.category)}
              </span>
              ${prioBadge}
              <span class="cloud-source" title="Quelle: ${this._escapeHtml(idea.source || 'Dashboard')}${idea.device ? ' • Gerät: ' + this._escapeHtml(idea.device) : ''}">
                <span>${sourceBadge}</span>
                <span>•</span>
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

      const activeIds = new Set(filteredIdeas.map((i) => i.id));
      for (const id of this._nodePositions.keys()) {
        if (!activeIds.has(id)) {
          this._nodePositions.delete(id);
          needsArrangement = true;
        }
      }

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
          if (e.target.closest(".action-btn") || e.target.closest(".cat-tag") || e.target.closest(".prio-tag")) return;
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
          if (e.target.closest(".action-btn") || e.target.closest(".cat-tag") || e.target.closest(".prio-tag")) return;
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

        // Priority Tag click -> Cycle Priority
        const prioTagEl = cloud.querySelector(".prio-tag");
        if (prioTagEl) {
          prioTagEl.addEventListener("click", (e) => {
            e.stopPropagation();
            this._toggleItemPriority(idea.id, idea.priority || "medium");
          });
        }

        // Text click or edit button -> Edit Dialog
        const textEl = cloud.querySelector(".cloud-text");
        if (textEl) {
          textEl.addEventListener("click", (e) => {
            e.stopPropagation();
            this._showEditDialog(idea.id, idea.text, idea.category, idea.priority);
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
            else if (act === "edit") this._showEditDialog(idea.id, idea.text, idea.category, idea.priority);
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

  _showEditDialog(id, currentText, currentCategory, currentPriority = "medium") {
    const sensor = this._getSensorEntity();
    const categories = sensor ? (sensor.attributes.categories || ["Inbox"]) : ["Inbox"];
    let selectedCat = currentCategory || "Inbox";
    let selectedPrio = (currentPriority || "medium").toLowerCase();

    this._openDialog("✏️ Notiz bearbeiten", (body) => {
      body.innerHTML = `
        <div class="dialog-label">Notiztext:</div>
        <textarea class="dialog-textarea" id="editTextarea" rows="3">${this._escapeHtml(currentText)}</textarea>
        <div class="dialog-error" id="editTextError" style="display: none;"></div>

        <div class="dialog-label">Priorität:</div>
        <div class="dialog-prio-grid" id="editPrioGrid">
          <div class="dialog-prio-chip ${selectedPrio === "low" ? "selected" : ""}" data-prio="low">🟢 Niedrig</div>
          <div class="dialog-prio-chip ${selectedPrio === "medium" ? "selected" : ""}" data-prio="medium">🟡 Mittel</div>
          <div class="dialog-prio-chip ${selectedPrio === "high" ? "selected" : ""}" data-prio="high">🔴 Hoch</div>
          <div class="dialog-prio-chip ${selectedPrio === "urgent" ? "selected" : ""}" data-prio="urgent">🔥 Dringend</div>
        </div>

        <div class="dialog-label" style="margin-top: 10px;">Kategorie:</div>
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
      const prioChips = body.querySelectorAll("#editPrioGrid .dialog-prio-chip");

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

      prioChips.forEach((chip) => {
        chip.addEventListener("click", () => {
          prioChips.forEach((c) => c.classList.remove("selected"));
          chip.classList.add("selected");
          selectedPrio = chip.getAttribute("data-prio") || "medium";
        });
      });

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

        const payload = { id: id, text: newText, priority: selectedPrio };
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
    let selectedPrio = "medium";

    this._openDialog("💡 Neue Idee erfassen", (body) => {
      body.innerHTML = `
        <div class="dialog-label">Idee / Gedanke:</div>
        <textarea class="dialog-textarea" id="addTextarea" placeholder="Was möchtest du festhalten?..." rows="3"></textarea>
        <div class="dialog-error" id="addTextError" style="display: none;"></div>

        <div class="dialog-label">Priorität:</div>
        <div class="dialog-prio-grid" id="addPrioGrid">
          <div class="dialog-prio-chip" data-prio="low">🟢 Niedrig</div>
          <div class="dialog-prio-chip selected" data-prio="medium">🟡 Mittel</div>
          <div class="dialog-prio-chip" data-prio="high">🔴 Hoch</div>
          <div class="dialog-prio-chip" data-prio="urgent">🔥 Dringend</div>
        </div>

        <div class="dialog-label" style="margin-top: 10px;">Kategorie:</div>
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
      const prioChips = body.querySelectorAll("#addPrioGrid .dialog-prio-chip");

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

      prioChips.forEach((chip) => {
        chip.addEventListener("click", () => {
          prioChips.forEach((c) => c.classList.remove("selected"));
          chip.classList.add("selected");
          selectedPrio = chip.getAttribute("data-prio") || "medium";
        });
      });

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
            priority: selectedPrio,
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

class BrainstormMindmapCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = { ...BRAINSTORM_MINDMAP_DEFAULTS };
    this._hass = null;
    this._form = null;
  }

  connectedCallback() {
    this._render();
  }

  setConfig(config) {
    this._config = {
      ...BRAINSTORM_MINDMAP_DEFAULTS,
      ...(config || {}),
    };
    if (this._form) {
      this._form.schema = this._getSchema();
      this._form.data = this._config;
      if (this._hass) this._form.hass = this._hass;
    } else {
      this._render();
    }
  }

  set hass(hass) {
    this._hass = hass;
    if (this._form) {
      this._form.hass = hass;
      this._form.schema = this._getSchema();
    } else if (this.shadowRoot && !this._form) {
      this._render();
    }
  }

  _escapeHtml(text) {
    return String(text ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  _getCategoryOptions() {
    const defaultList = ["Inbox", "Smarthome", "Haus & Garten", "Projekte", "Alltag", "Brainstorm"];
    const categories = [];
    const sensorName = (this._config && this._config.sensor) || "sensor.brainstorm_ideen_ubersicht";
    if (this._hass && this._hass.states && this._hass.states[sensorName]) {
      const stateObj = this._hass.states[sensorName];
      if (stateObj.attributes && Array.isArray(stateObj.attributes.categories)) {
        stateObj.attributes.categories.forEach((c) => {
          if (!categories.includes(c)) categories.push(c);
        });
      }
    }
    defaultList.forEach((c) => {
      if (!categories.includes(c)) categories.push(c);
    });
    if (this._config && this._config.default_category && this._config.default_category !== "all" && !categories.includes(this._config.default_category)) {
      categories.push(this._config.default_category);
    }

    const icons = {
      inbox: "📥",
      smarthome: "🔷",
      "haus & garten": "🟢",
      haus: "🟢",
      garten: "🟢",
      projekte: "🟣",
      alltag: "🟡",
      brainstorm: "🔮",
      ideen: "🌸",
      einkauf: "🍊",
      finanzen: "🪙",
      familie: "❤️",
      arbeit: "💼",
      gesundheit: "🍏",
    };

    return [
      { value: "all", label: "🌟 Alle Kategorien (Gesamtübersicht)" },
      ...categories.map((c) => {
        const icon = icons[c.toLowerCase()] || "🏷️";
        return { value: c, label: `${icon} ${c}` };
      }),
    ];
  }

  _getSchema() {
    const catOptions = this._getCategoryOptions();
    return [
      {
        name: "title",
        label: "Mindmap-Titel",
        default: "Brainstorm Mindmap",
        selector: { text: {} },
      },
      {
        name: "sensor",
        label: "Sensor-Entität",
        default: "sensor.brainstorm_ideen_ubersicht",
        selector: { entity: { domain: ["sensor"] } },
      },
      {
        name: "show_last_alexa",
        label: "Zuletzt aktive Alexa (Last Alexa) anzeigen",
        default: false,
        selector: { boolean: {} },
      },
      {
        name: "last_alexa_entity",
        label: "Last Alexa Entität (Echo / Sensor)",
        default: "sensor.last_alexa",
        selector: { entity: { domain: ["sensor", "media_player"] } },
      },
      {
        name: "color_mode",
        label: "Standard-Farbmodus",
        default: "theme",
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
        default: "calc(100vh - 32px)",
        selector: { text: {} },
      },
      {
        name: "default_category",
        label: "Standard-Kategorie im Fokus",
        default: "all",
        selector: {
          select: {
            mode: "dropdown",
            custom_value: true,
            options: catOptions,
          },
        },
      },
      {
        name: "show_bulb_watermark",
        label: "Leuchtende Glühbirne im Zentrum als Wasserzeichen anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_grid",
        label: "Punktraster im Hintergrund anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_logo",
        label: "Brainstorm Logo in Toolbar anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_toolbar",
        label: "Obere Werkzeugleiste (Titel & Filter-Pills) anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "hide_empty_categories",
        label: "Kategorien ohne Notizen (0) ausblenden",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_color_toggle",
        label: "Farbmodus-Umschalter (🎨/🌈) in Toolbar anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_fullscreen_btn",
        label: "Vollbild-Schaltfläche (⛶) anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_controls",
        label: "Zoom- & Zentrieren-Schaltflächen anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_add_btn",
        label: "Neue Notiz-Schaltfläche (+ Idee) anzeigen",
        default: true,
        selector: { boolean: {} },
      },
    ];
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
      this._form.schema = this._getSchema();
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
      form.schema = this._getSchema();
      form.computeLabel = (s) => s.label || s.name;
      form.computeHelper = (s) => s.helper || "";
      form.addEventListener("value-changed", (ev) => {
        ev.stopPropagation();
        if (!ev.detail || !ev.detail.value) return;
        this._config = {
          ...this._config,
          ...ev.detail.value,
        };
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
          <label class="fallback-label" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" id="fbShowLastAlexa" ${this._config.show_last_alexa ? 'checked' : ''} />
            <span>Zuletzt aktive Alexa (Last Alexa) anzeigen</span>
          </label>
        </div>
        <div class="fallback-row">
          <label class="fallback-label">Last Alexa Entität</label>
          <input class="fallback-input" id="fbLastAlexaEntity" type="text" value="${this._config.last_alexa_entity || 'sensor.last_alexa'}" />
        </div>
        <div class="fallback-row">
          <label class="fallback-label">Standard-Kategorie im Fokus</label>
          <select class="fallback-select" id="fbDefaultCat">
            ${this._getCategoryOptions().map(o => `<option value="${this._escapeHtml(o.value)}" ${(this._config.default_category || 'all') === o.value ? 'selected' : ''}>${this._escapeHtml(o.label)}</option>`).join("")}
          </select>
        </div>
        <div class="fallback-row">
          <label class="fallback-label">Farbmodus</label>
          <select class="fallback-select" id="fbColorMode">
            <option value="theme" ${(this._config.color_mode || 'theme') === 'theme' ? 'selected' : ''}>🎨 Theme-Farben</option>
            <option value="multicolor" ${this._config.color_mode === 'multicolor' ? 'selected' : ''}>🌈 Bunt (Multicolor)</option>
          </select>
        </div>
        <div class="fallback-row">
          <label class="fallback-label" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" id="fbShowLogo" ${this._config.show_logo !== false ? 'checked' : ''} />
            <span>Brainstorm Logo in Toolbar anzeigen</span>
          </label>
        </div>
        <div class="fallback-row">
          <label class="fallback-label" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" id="fbHideEmpty" ${this._config.hide_empty_categories ? 'checked' : ''} />
            <span>Kategorien ohne Notizen (0) ausblenden</span>
          </label>
        </div>
      </div>
    `;
    const fbTitle = container.querySelector("#fbTitle");
    const fbSensor = container.querySelector("#fbSensor");
    const fbShowLastAlexa = container.querySelector("#fbShowLastAlexa");
    const fbLastAlexaEntity = container.querySelector("#fbLastAlexaEntity");
    const fbDefaultCat = container.querySelector("#fbDefaultCat");
    const fbColorMode = container.querySelector("#fbColorMode");
    const fbShowLogo = container.querySelector("#fbShowLogo");
    const fbHideEmpty = container.querySelector("#fbHideEmpty");

    const emitChange = () => {
      this._config = {
        ...this._config,
        title: fbTitle ? fbTitle.value : this._config.title,
        sensor: fbSensor ? fbSensor.value : this._config.sensor,
        show_last_alexa: fbShowLastAlexa ? fbShowLastAlexa.checked : Boolean(this._config.show_last_alexa),
        last_alexa_entity: fbLastAlexaEntity ? fbLastAlexaEntity.value : this._config.last_alexa_entity,
        default_category: fbDefaultCat ? fbDefaultCat.value : this._config.default_category,
        color_mode: fbColorMode ? fbColorMode.value : this._config.color_mode,
        show_logo: fbShowLogo ? fbShowLogo.checked : this._config.show_logo !== false,
        hide_empty_categories: fbHideEmpty ? fbHideEmpty.checked : Boolean(this._config.hide_empty_categories),
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
    if (fbShowLastAlexa) fbShowLastAlexa.addEventListener("change", emitChange);
    if (fbLastAlexaEntity) fbLastAlexaEntity.addEventListener("input", emitChange);
    if (fbDefaultCat) fbDefaultCat.addEventListener("change", emitChange);
    if (fbColorMode) fbColorMode.addEventListener("change", emitChange);
    if (fbShowLogo) fbShowLogo.addEventListener("change", emitChange);
    if (fbHideEmpty) fbHideEmpty.addEventListener("change", emitChange);
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
  "%c BRAINSTORM-MINDMAP-CARD %c v1.4.47 ",
  "color: #07070e; background: #00f5ff; font-weight: bold; border-radius: 4px 0 0 4px; padding: 2px 4px;",
  "color: #ffffff; background: #9d4edd; font-weight: bold; border-radius: 0 4px 4px 0; padding: 2px 4px;"
);
