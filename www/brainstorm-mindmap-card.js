/**
 * Brainstorm Hub - Interactive Mindmap Card
 * Version: 1.3.0
 * 
 * An interactive, visual mindmap for Home Assistant ideas and brainstorm notes.
 * Features:
 * - Dynamic radial synapse layout
 * - Central Hub with translucent Brainstorm logo
 * - Note nodes styled as interactive thought clouds with dashed/glowing borders
 * - Dynamic SVG connector lines (Cubic Bézier curves)
 * - Drag & drop nodes freely across the canvas
 * - Canvas pan & zoom (mouse wheel, touch, controls)
 * - Category filter pills & inline actions (Complete, Edit, Move, Delete)
 */

class BrainstormMindmapCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._selectedCategory = "all"; // 'all', 'Inbox', etc.
    this._scale = 1;
    this._panX = 0;
    this._panY = 0;
    this._isPanning = false;
    this._startPan = { x: 0, y: 0 };
    this._nodePositions = new Map(); // id -> {x, y}
    this._centerPos = { x: 400, y: 300 };
    this._activeDrag = null; // { id, startMouseX, startMouseY, startNodeX, startNodeY }
    this._initialized = false;
    this._lastUpdated = null;
    this._lastIdeasHash = "";
  }

  static getStubConfig() {
    return {
      title: "Brainstorm Mindmap",
      height: "580px",
      default_category: "Inbox",
    };
  }

  setConfig(config) {
    this._config = {
      title: "Brainstorm Mindmap",
      height: "580px",
      default_category: "Inbox",
      ...config,
    };
    if (this._config.default_category && !this._initialized) {
      this._selectedCategory = this._config.default_category;
    }
  }

  getCardSize() {
    return 6;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._initDom();
    }
    this._updateContent();
  }

  _getSensorEntity() {
    if (!this._hass) return null;
    if (this._config.entity && this._hass.states[this._config.entity]) {
      return this._hass.states[this._config.entity];
    }
    if (this._hass.states["sensor.brainstorm_hub_brainstorm_ideen_ubersicht"]) {
      return this._hass.states["sensor.brainstorm_hub_brainstorm_ideen_ubersicht"];
    }
    if (this._hass.states["sensor.brainstorm_ideen_ubersicht"]) {
      return this._hass.states["sensor.brainstorm_ideen_ubersicht"];
    }
    return null;
  }

  _getCategoryColor(category) {
    const colors = {
      Inbox: "#00f5ff",
      Smarthome: "#38bdf8",
      "Haus & Garten": "#10b981",
      Projekte: "#a855f7",
      Alltag: "#f59e0b",
      Ideen: "#ec4899",
      default: "#8b5cf6",
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
          font-family: var(--ha-font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif);
        }
        ha-card {
          position: relative;
          width: 100%;
          height: ${this._config.height || "580px"};
          background: var(--ha-card-background, var(--card-background-color, #0f141c));
          border-radius: var(--ha-card-border-radius, 16px);
          border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color, rgba(255,255,255,0.08)));
          box-shadow: var(--ha-card-box-shadow, 0 8px 30px rgba(0,0,0,0.18));
          overflow: hidden;
          display: flex;
          flex-direction: column;
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
          background: linear-gradient(180deg, rgba(13,17,23,0.85) 0%, rgba(13,17,23,0) 100%);
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
          width: 28px;
          height: 28px;
          border-radius: 7px;
          overflow: hidden;
          box-shadow: 0 0 10px rgba(0, 245, 255, 0.4);
        }
        .brand-logo img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .title {
          font-size: 1.05rem;
          font-weight: 700;
          color: var(--primary-text-color, #f0f6fc);
          text-shadow: 0 1px 4px rgba(0,0,0,0.5);
        }
        .fullscreen-btn {
          background: rgba(255,255,255,0.08);
          border: 1px solid rgba(255,255,255,0.15);
          color: var(--primary-text-color, #f0f6fc);
          border-radius: 8px;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 0.95rem;
          backdrop-filter: blur(8px);
          transition: all 0.2s ease;
        }
        .fullscreen-btn:hover {
          background: rgba(0, 245, 255, 0.25);
          border-color: #00f5ff;
          color: #fff;
          transform: scale(1.08);
        }
        ha-card.is-fullscreen {
          position: fixed !important;
          top: 0 !important;
          left: 0 !important;
          width: 100vw !important;
          height: 100vh !important;
          z-index: 99999 !important;
          border-radius: 0 !important;
          margin: 0 !important;
        }
        .pills-container {
          display: flex;
          align-items: center;
          gap: 6px;
          overflow-x: auto;
          max-width: 55%;
          padding: 4px 6px;
          pointer-events: auto;
          scrollbar-width: none;
        }
        .pills-container::-webkit-scrollbar {
          display: none;
        }
        .cat-pill {
          padding: 5px 11px;
          font-size: 0.78rem;
          font-weight: 600;
          border-radius: 20px;
          cursor: pointer;
          background: rgba(255,255,255,0.07);
          color: var(--secondary-text-color, #8b949e);
          border: 1px solid rgba(255,255,255,0.12);
          backdrop-filter: blur(8px);
          white-space: nowrap;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .cat-pill:hover {
          background: rgba(255,255,255,0.15);
          color: #fff;
          transform: translateY(-1px);
        }
        .cat-pill.active {
          background: linear-gradient(135deg, rgba(0, 245, 255, 0.25), rgba(157, 78, 221, 0.25));
          color: #00f5ff;
          border-color: #00f5ff;
          box-shadow: 0 0 12px rgba(0, 245, 255, 0.3);
        }

        /* Map Canvas & Viewport */
        .canvas-area {
          flex: 1;
          width: 100%;
          height: 100%;
          position: relative;
          cursor: grab;
          overflow: hidden;
          background: radial-gradient(circle at center, rgba(30,30,56,0.3) 0%, rgba(10,12,18,0.95) 100%);
        }
        .canvas-area:active {
          cursor: grabbing;
        }
        .grid-bg {
          position: absolute;
          inset: 0;
          background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
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
          stroke: rgba(0, 245, 255, 0.35);
          stroke-width: 2.2;
          stroke-dasharray: 6, 4;
          transition: stroke 0.2s ease, stroke-width 0.2s ease;
        }
        .synapse-path.highlight {
          stroke: #00f5ff;
          stroke-width: 3.5;
          stroke-dasharray: none;
          filter: drop-shadow(0 0 6px #00f5ff);
        }

        /* Center Node */
        .center-node {
          position: absolute;
          width: 160px;
          height: 160px;
          margin-left: -80px;
          margin-top: -80px;
          border-radius: 50%;
          z-index: 5;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          cursor: pointer;
          background: rgba(18, 24, 38, 0.85);
          border: 2px solid rgba(0, 245, 255, 0.6);
          box-shadow: 0 0 35px rgba(0, 245, 255, 0.25), inset 0 0 20px rgba(0, 245, 255, 0.15);
          backdrop-filter: blur(12px);
          transition: transform 0.25s ease, box-shadow 0.25s ease;
          overflow: hidden;
        }
        .center-node:hover {
          transform: scale(1.05);
          box-shadow: 0 0 45px rgba(0, 245, 255, 0.45), inset 0 0 25px rgba(0, 245, 255, 0.25);
        }
        .center-logo-watermark {
          position: absolute;
          inset: 0;
          background-image: url('/local/brainstorm-logo.svg'), url('/local/brainstorm-logo.png');
          background-size: 78%;
          background-position: center;
          background-repeat: no-repeat;
          opacity: 0.22;
          pointer-events: none;
          filter: drop-shadow(0 0 8px rgba(0, 245, 255, 0.5));
        }
        .center-content {
          position: relative;
          z-index: 2;
          padding: 8px;
        }
        .center-title {
          font-size: 1.15rem;
          font-weight: 800;
          color: #ffffff;
          letter-spacing: 0.5px;
          text-transform: uppercase;
          text-shadow: 0 0 10px rgba(0, 245, 255, 0.7);
        }
        .center-badge {
          margin-top: 4px;
          font-size: 0.75rem;
          font-weight: 700;
          color: #00f5ff;
          background: rgba(0, 245, 255, 0.18);
          border: 1px solid rgba(0, 245, 255, 0.4);
          padding: 2px 8px;
          border-radius: 12px;
          display: inline-block;
        }

        /* Note Cloud Nodes */
        .note-cloud {
          position: absolute;
          min-width: 170px;
          max-width: 250px;
          margin-left: -90px;
          margin-top: -45px;
          z-index: 10;
          background: var(--ha-card-background, var(--card-background-color, rgba(22, 27, 34, 0.92)));
          border: 2px dashed rgba(0, 245, 255, 0.45);
          border-radius: 20px;
          padding: 12px 14px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.35);
          backdrop-filter: blur(10px);
          cursor: move;
          transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
        }
        .note-cloud:hover {
          border-style: solid;
          border-color: #00f5ff;
          box-shadow: 0 10px 28px rgba(0, 245, 255, 0.28);
          transform: translateY(-2px);
          z-index: 15;
        }
        .note-cloud.dragging {
          transform: scale(1.04);
          box-shadow: 0 15px 35px rgba(0, 245, 255, 0.4);
          z-index: 20;
          border-color: #00f5ff;
        }

        /* Cloud Top Meta */
        .cloud-meta {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 0.72rem;
          color: var(--secondary-text-color, #8b949e);
          margin-bottom: 6px;
        }
        .cat-tag {
          font-weight: 700;
          font-size: 0.68rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          padding: 1px 6px;
          border-radius: 6px;
          background: rgba(255,255,255,0.08);
          border: 1px solid rgba(255,255,255,0.15);
        }
        .cloud-source {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        /* Cloud Text */
        .cloud-text {
          font-size: 0.88rem;
          line-height: 1.35;
          color: var(--primary-text-color, #f0f6fc);
          word-break: break-word;
          margin-bottom: 8px;
          user-select: text;
        }

        /* Cloud Actions */
        .cloud-actions {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 6px;
          opacity: 0.45;
          transition: opacity 0.2s ease;
        }
        .note-cloud:hover .cloud-actions {
          opacity: 1;
        }
        .action-btn {
          background: rgba(255,255,255,0.08);
          border: 1px solid rgba(255,255,255,0.12);
          color: var(--secondary-text-color, #c9d1d9);
          width: 24px;
          height: 24px;
          border-radius: 6px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.75rem;
          cursor: pointer;
          transition: all 0.15s ease;
        }
        .action-btn:hover {
          background: rgba(255,255,255,0.22);
          color: #fff;
          transform: scale(1.1);
        }
        .action-btn.done-btn:hover {
          background: #10b981;
          border-color: #10b981;
          color: #fff;
        }
        .action-btn.del-btn:hover {
          background: #ef4444;
          border-color: #ef4444;
          color: #fff;
        }

        /* Controls Panel (Bottom Right) */
        .controls-panel {
          position: absolute;
          bottom: 16px;
          right: 16px;
          z-index: 25;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .control-btn {
          width: 34px;
          height: 34px;
          border-radius: 9px;
          background: rgba(18, 24, 38, 0.85);
          border: 1px solid rgba(255,255,255,0.15);
          color: var(--primary-text-color, #c9d1d9);
          font-size: 1.1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
          backdrop-filter: blur(8px);
          transition: all 0.15s ease;
        }
        .control-btn:hover {
          background: rgba(0, 245, 255, 0.25);
          border-color: #00f5ff;
          color: #fff;
          transform: scale(1.08);
        }

        /* Quick Add Button (Bottom Left) */
        .add-note-btn {
          position: absolute;
          bottom: 16px;
          left: 16px;
          z-index: 25;
          background: linear-gradient(135deg, #00f5ff, #9d4edd);
          color: #07070e;
          font-weight: 700;
          font-size: 0.85rem;
          padding: 8px 16px;
          border-radius: 20px;
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 6px;
          box-shadow: 0 4px 18px rgba(0, 245, 255, 0.4);
          transition: all 0.2s ease;
        }
        .add-note-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 24px rgba(0, 245, 255, 0.6);
        }

        /* Empty State */
        .empty-state {
          position: absolute;
          top: 60%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 0.85rem;
          color: var(--secondary-text-color, #8b949e);
          text-align: center;
          pointer-events: none;
        }
      </style>

      <ha-card id="cardRoot">
        <!-- Top Bar -->
        <div class="top-bar">
          <div class="top-left">
            <div class="brand-logo">
              <img src="/local/brainstorm-logo.svg" onerror="this.src='/local/brainstorm-logo.png'" alt="Logo" />
            </div>
            <div class="title" id="cardTitle">${this._config.title || "Brainstorm Mindmap"}</div>
          </div>
          <div class="pills-container" id="pillsBar"></div>
          <div class="top-right">
            <button class="fullscreen-btn" id="fullscreenToggleBtn" title="Vollbild umschalten (ESC zum Beenden)">⛶</button>
          </div>
        </div>

        <!-- Interactive Canvas Area -->
        <div class="canvas-area" id="canvasArea">
          <div class="grid-bg"></div>
          <div class="viewport" id="viewport">
            <svg class="connectors" id="connectorsLayer"></svg>
            <div class="center-node" id="centerNode">
              <div class="center-logo-watermark"></div>
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
        <button class="add-note-btn" id="addNoteBtn">
          <span>➕</span>
          <span>Neue Idee</span>
        </button>

        <!-- Bottom Right: Zoom & Reset Controls -->
        <div class="controls-panel">
          <button class="control-btn" id="zoomInBtn" title="Vergrößern">+</button>
          <button class="control-btn" id="zoomOutBtn" title="Verkleinern">−</button>
          <button class="control-btn" id="resetViewBtn" title="Zentrieren / Anordnen">⟲</button>
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

    // Canvas Pan (Drag background)
    canvasArea.addEventListener("mousedown", (e) => {
      if (e.target.closest(".note-cloud") || e.target.closest(".center-node") || e.target.closest(".action-btn")) {
        return;
      }
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
      if (e.touches.length === 1 && !e.target.closest(".note-cloud")) {
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
    });

    // Fullscreen Toggle
    const fullscreenBtn = this.shadowRoot.getElementById("fullscreenToggleBtn");
    const cardRoot = this.shadowRoot.getElementById("cardRoot");
    const toggleFullscreen = () => {
      const isFs = cardRoot.classList.toggle("is-fullscreen");
      fullscreenBtn.innerHTML = isFs ? "✕" : "⛶";
      fullscreenBtn.title = isFs ? "Vollbild beenden" : "Vollbild umschalten (ESC)";
      setTimeout(() => {
        this._centerLayout(false);
      }, 50);
    };

    if (fullscreenBtn) {
      fullscreenBtn.addEventListener("click", toggleFullscreen);
    }

    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && cardRoot && cardRoot.classList.contains("is-fullscreen")) {
        toggleFullscreen();
      }
    });

    // Control Buttons
    zoomInBtn.addEventListener("click", () => this._zoomAtPoint(1.2));
    zoomOutBtn.addEventListener("click", () => this._zoomAtPoint(0.8));
    resetViewBtn.addEventListener("click", () => {
      this._centerLayout(true);
    });

    // Quick Add
    addNoteBtn.addEventListener("click", () => this._promptAddIdea());

    // Center Node Click -> Cycle category
    centerNode.addEventListener("click", () => {
      const sensor = this._getSensorEntity();
      if (!sensor) return;
      const categories = ["all", ...(sensor.attributes.categories || ["Inbox"])];
      const idx = categories.indexOf(this._selectedCategory);
      const nextIdx = (idx + 1) % categories.length;
      this._selectedCategory = categories[nextIdx];
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
      return i.category === this._selectedCategory;
    });

    const count = ideas.length;
    if (count === 0) {
      this._drawConnections();
      return;
    }

    // Determine radius based on count
    const baseRadius = count <= 6 ? 210 : count <= 12 ? 260 : 310;
    const angleStep = (2 * Math.PI) / count;

    ideas.forEach((idea, i) => {
      // Add slight organic offset to give an organic thought cloud feel
      const radiusJitter = (i % 2 === 0 ? 1 : 0.88) * baseRadius;
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
        return i.category === this._selectedCategory;
      });

      // 1. Update Top Category Pills
      const pillsBar = this.shadowRoot.getElementById("pillsBar");
      if (pillsBar) {
        const counts = attributes.category_counts || {};
        pillsBar.innerHTML = `
          <div class="cat-pill ${this._selectedCategory === "all" ? "active" : ""}" data-cat="all">
            Alle (${activeIdeas.length})
          </div>
          ${categories
            .map((cat) => {
              const c = counts[cat] || 0;
              return `
                <div class="cat-pill ${this._selectedCategory === cat ? "active" : ""}" data-cat="${cat}">
                  ${cat} (${c})
                </div>
              `;
            })
            .join("")}
        `;

        pillsBar.querySelectorAll(".cat-pill").forEach((pill) => {
          pill.addEventListener("click", () => {
            this._selectedCategory = pill.getAttribute("data-cat");
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
        centerNode.style.borderColor = catColor;
        centerNode.style.boxShadow = `0 0 35px ${catColor}40, inset 0 0 20px ${catColor}20`;
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
          <div class="note-cloud" id="cloud_${idea.id}" data-id="${idea.id}" style="border-color: ${color}90;">
            <div class="cloud-meta">
              <span class="cat-tag" style="border-color: ${color}60; color: ${color};">${idea.category}</span>
              <span class="cloud-source" title="${idea.source || 'Dashboard'}">
                <span>${sourceIcon}</span>
                <span>${timeAgo}</span>
              </span>
            </div>
            <div class="cloud-text">${this._escapeHtml(idea.text)}</div>
            <div class="cloud-actions">
              <button class="action-btn done-btn" data-act="done" data-id="${idea.id}" title="Als erledigt markieren">✓</button>
              <button class="action-btn" data-act="edit" data-id="${idea.id}" data-text="${this._escapeHtml(idea.text)}" title="Bearbeiten">✏️</button>
              <button class="action-btn" data-act="move" data-id="${idea.id}" data-cat="${idea.category}" title="Kategorie ändern">📁</button>
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

        // Drag start on cloud
        cloud.addEventListener("mousedown", (e) => {
          if (e.target.closest(".action-btn")) return;
          e.stopPropagation();
          cloud.classList.add("dragging");
          const pos = this._nodePositions.get(id) || { x: 0, y: 0 };
          this._activeDrag = {
            id: id,
            startMouseX: e.clientX,
            startMouseY: e.clientY,
            startNodeX: pos.x,
            startNodeY: pos.y,
          };
        });

        // Hover highlight connector
        cloud.addEventListener("mouseenter", () => {
          const path = this.shadowRoot.getElementById(`path_${id}`);
          if (path) path.classList.add("highlight");
        });
        cloud.addEventListener("mouseleave", () => {
          const path = this.shadowRoot.getElementById(`path_${id}`);
          if (path) path.classList.remove("highlight");
        });

        // Action buttons
        cloud.querySelectorAll(".action-btn").forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const act = btn.getAttribute("data-act");
            const noteId = btn.getAttribute("data-id");
            if (act === "done") this._completeIdea(noteId);
            else if (act === "edit") this._editIdea(noteId, btn.getAttribute("data-text"));
            else if (act === "move") this._changeCategory(noteId, btn.getAttribute("data-cat"), categories);
            else if (act === "delete") this._deleteIdea(noteId);
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

  // --- Backend Actions ---

  async _promptAddIdea() {
    const text = prompt("Neue Idee für Brainstorm eingeben:");
    if (!text || !text.trim()) return;

    const sensor = this._getSensorEntity();
    const categories = sensor ? sensor.attributes.categories || ["Inbox"] : ["Inbox"];
    const cat = this._selectedCategory && this._selectedCategory !== "all" ? this._selectedCategory : "Inbox";

    try {
      await this._hass.callService("brainstorm", "add_idea", {
        text: text.trim(),
        category: cat,
        source: "dashboard",
      });
    } catch (e) {
      console.error("Failed to add idea via mindmap:", e);
    }
  }

  async _completeIdea(id) {
    try {
      await this._hass.callService("brainstorm", "update_idea", {
        id: id,
        status: "completed",
      });
    } catch (e) {
      console.error("Failed to complete idea:", e);
    }
  }

  async _editIdea(id, currentText) {
    const newText = prompt("Idee bearbeiten:", currentText);
    if (newText !== null && newText.trim() && newText.trim() !== currentText) {
      try {
        await this._hass.callService("brainstorm", "update_idea", {
          id: id,
          text: newText.trim(),
        });
      } catch (e) {
        console.error("Failed to update idea:", e);
      }
    }
  }

  async _changeCategory(id, currentCategory, availableCategories) {
    const newCat = prompt(
      `Kategorie ändern:\nVerfügbar: ${availableCategories.join(", ")}`,
      currentCategory
    );
    if (newCat !== null && newCat.trim() && newCat.trim() !== currentCategory) {
      try {
        await this._hass.callService("brainstorm", "update_idea", {
          id: id,
          category: newCat.trim(),
        });
      } catch (e) {
        console.error("Failed to change category:", e);
      }
    }
  }

  async _deleteIdea(id) {
    if (confirm("Möchtest du diese Notiz wirklich löschen?")) {
      try {
        await this._hass.callService("brainstorm", "delete_idea", {
          id: id,
        });
      } catch (e) {
        console.error("Failed to delete idea:", e);
      }
    }
  }
}

// Register custom element & Lovelace customCard entry
customElements.define("brainstorm-mindmap-card", BrainstormMindmapCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "brainstorm-mindmap-card",
  name: "Brainstorm Mindmap Card",
  description: "Interaktive Mindmap-Darstellung für deine Brainstorm Hub Notizen und Ideen.",
  preview: true,
  documentationURL: "https://github.com/nukleuz80/ha_brainstorm",
});

console.info(
  "%c BRAINSTORM-MINDMAP-CARD %c v1.3.0 ",
  "color: #07070e; background: #00f5ff; font-weight: bold; border-radius: 4px 0 0 4px; padding: 2px 4px;",
  "color: #ffffff; background: #9d4edd; font-weight: bold; border-radius: 0 4px 4px 0; padding: 2px 4px;"
);
