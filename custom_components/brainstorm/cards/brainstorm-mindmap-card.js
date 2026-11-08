import { alexaEchos, attachmentBadge, dateLocale, dueFromInputValues, dueInputFormat, dueInputValues, formatDueInput, formatText, inProgressBadge, parseDueInput, renderAttachments, setLanguage, shortDate, t } from "./brainstorm-i18n.js?v=1.7.22";

/**
 * Brainstorm Hub - Interactive Mindmap Card
 * Version: 1.7.22 - Skill, Reminders, Privacy and Sharing
 * 
 * An interactive, visual mindmap for Home Assistant ideas and brainstorm notes.
 * Minimalist UI / Mushroom-inspired theme styling.
 */

// Folded branches of the mind map, kept per device
const COLLAPSED_KEY = "brainstorm_mindmap_collapsed";
const UNDO_LIMIT = 30;

// The bulb lies next to this file, wherever Home Assistant serves it from
const BULB_URL = new URL("./brainstorm-bulb.svg", import.meta.url).href;

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
  show_export_btn: true,
  hide_empty_categories: true,
  map_template: "standard",
  node_shape: "template",
  voice_bubbles: true,
  line_style: "template",
  color_scheme: "template",
};

// Ready-made looks; shape, lines and colors can each be chosen on their own
const MAP_TEMPLATES = {
  standard: { shape: "card", lines: "curve", scheme: "category" },
  clean: { shape: "rect", lines: "angled", scheme: "category" },
  sketch: { shape: "pill", lines: "dashed", scheme: "pastel" },
  neon: { shape: "pill", lines: "curve", scheme: "neon" },
};
const NODE_SHAPES = ["card", "cloud", "bubble", "thought", "pill", "rect", "ellipse", "hexagon", "note", "underline"];
// Shapes CSS cannot draw get an SVG outline behind the note
const SVG_SHAPES = ["cloud", "bubble", "thought", "ellipse", "hexagon", "note"];
// Shapes that point to their parent and need a new outline when it moves
const POINTING_SHAPES = ["bubble", "thought"];
// The name of a shape in the language of the user
function shapeLabel(shape) {
  return {
    card: t("Karte"),
    cloud: t("Wolke"),
    bubble: t("Sprechblase"),
    thought: t("Gedankenblase"),
    pill: t("Kapsel"),
    rect: t("Rechteck"),
    ellipse: t("Ellipse"),
    hexagon: t("Sechseck"),
    note: t("Notizzettel"),
    underline: t("Unterstrichen"),
  }[shape];
}

// Where a ray from the middle of a w × h box leaves it along `angle`
function boxExit(w, h, angle) {
  const c = Math.cos(angle);
  const s = Math.sin(angle);
  if (Math.abs(c) * h > Math.abs(s) * w) {
    return { side: "x", x: c > 0 ? w : 0, y: h / 2 + ((w / 2) * s) / Math.abs(c) };
  }
  return { side: "y", x: w / 2 + ((h / 2) * c) / Math.abs(s), y: s > 0 ? h : 0 };
}

// Said aloud to Alexa, Siri or Assist, so it can show as a speech bubble
export function isVoiceSource(source) {
  return /alexa|siri|assist|voice|speech/.test(String(source || "").toLowerCase());
}

// The same note always gets the same bumps
function seededRandom(seed) {
  let h = 2166136261;
  for (const ch of String(seed)) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return () => {
    h = Math.imul(h ^ (h >>> 15), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  };
}

// SVG pieces of a note outline, w × h is the note box. Drawn twice by the
// caller, stroked and then filled on top, so overlapping pieces show one
// outline. The bubble's tail points along `angle`, towards the parent.
export function shapeParts(shape, w, h, { angle = Math.PI / 2, seed = "" } = {}) {
  const f = (n) => Math.round(n * 10) / 10;
  if (shape === "cloud") {
    const rand = seededRandom(seed);
    const inset = 5;
    const a = Math.max(w / 2 - inset, 8);
    const b = Math.max(h / 2 - inset, 8);
    // Bump centers sit on a squircle inside the box, evenly spaced
    const pts = [];
    const samples = 160;
    for (let i = 0; i < samples; i++) {
      const t = (i / samples) * 2 * Math.PI;
      const c = Math.cos(t);
      const s = Math.sin(t);
      pts.push([w / 2 + a * Math.sign(c) * Math.sqrt(Math.abs(c)), h / 2 + b * Math.sign(s) * Math.sqrt(Math.abs(s))]);
    }
    const lengths = pts.map((p, i) => {
      const q = pts[(i + 1) % samples];
      return Math.hypot(q[0] - p[0], q[1] - p[1]);
    });
    const total = lengths.reduce((sum, l) => sum + l, 0);
    const base = Math.min(15, Math.max(10, Math.min(w, h) / 5));
    const count = Math.max(8, Math.round(total / (base * 1.45)));
    const step = total / count;
    const parts = [`<path d="M ${pts.map((p) => `${f(p[0])} ${f(p[1])}`).join(" L ")} Z"/>`];
    let target = rand() * step;
    let walked = 0;
    for (let i = 0; i < samples && parts.length <= count; i++) {
      while (target <= walked + lengths[i] && parts.length <= count) {
        const k = (target - walked) / lengths[i];
        const p = pts[i];
        const q = pts[(i + 1) % samples];
        const r = base * (0.85 + rand() * 0.3);
        parts.push(`<circle cx="${f(p[0] + (q[0] - p[0]) * k)}" cy="${f(p[1] + (q[1] - p[1]) * k)}" r="${f(r)}"/>`);
        target += step;
      }
      walked += lengths[i];
    }
    return parts;
  }
  if (shape === "thought") {
    // A cloud and two small puffs on the way to the parent
    const parts = shapeParts("cloud", w, h, { seed });
    const exit = boxExit(w, h, angle);
    const c = Math.cos(angle);
    const s = Math.sin(angle);
    [
      [15, 6],
      [29, 3.5],
    ].forEach(([dist, r]) => {
      parts.push(`<circle cx="${f(exit.x + c * dist)}" cy="${f(exit.y + s * dist)}" r="${r}"/>`);
    });
    return parts;
  }
  if (shape === "ellipse") {
    // Big enough that the text corners stay inside
    const rx = Math.max(w / 2 + 2, (w / 2 - 16) * Math.SQRT2);
    const ry = Math.max(h / 2 + 2, (h / 2 - 10) * Math.SQRT2);
    return [`<ellipse cx="${f(w / 2)}" cy="${f(h / 2)}" rx="${f(rx)}" ry="${f(ry)}"/>`];
  }
  if (shape === "hexagon") {
    // The points stick out left and right, the text keeps the full box
    const d = Math.min(h * 0.35, 22);
    const pts = [
      [0, 0],
      [w, 0],
      [w + d, h / 2],
      [w, h],
      [0, h],
      [-d, h / 2],
    ];
    return [`<path d="M ${pts.map((p) => `${f(p[0])} ${f(p[1])}`).join(" L ")} Z"/>`];
  }
  if (shape === "note") {
    // A slip of paper with its lower right corner folded over
    const k = Math.min(16, h / 3, w / 3);
    return [
      `<path d="M 0 0 H ${f(w)} V ${f(h - k)} L ${f(w - k)} ${f(h)} H 0 Z"/>`,
      `<path class="shape-fold" d="M ${f(w - k)} ${f(h)} V ${f(h - k)} H ${f(w)} Z"/>`,
    ];
  }
  if (shape === "bubble") {
    const r = Math.min(16, h / 2, w / 2);
    const half = 9;
    const len = 16;
    const c = Math.cos(angle);
    const s = Math.sin(angle);
    const clamp = (v, lo, hi) => (lo > hi ? (lo + hi) / 2 : Math.max(lo, Math.min(hi, v)));
    const exit = boxExit(w, h, angle);
    let b1;
    let b2;
    let mid;
    if (exit.side === "x") {
      // Leaves through the left or right side
      const x = exit.x;
      const y = clamp(exit.y, r + half, h - r - half);
      const back = c > 0 ? -2 : 2;
      b1 = [x + back, y - half];
      b2 = [x + back, y + half];
      mid = [x, y];
    } else {
      const y = exit.y;
      const x = clamp(exit.x, r + half, w - r - half);
      const back = s > 0 ? -2 : 2;
      b1 = [x - half, y + back];
      b2 = [x + half, y + back];
      mid = [x, y];
    }
    const tip = [mid[0] + c * len, mid[1] + s * len];
    return [
      `<rect x="0" y="0" width="${f(w)}" height="${f(h)}" rx="${f(r)}"/>`,
      `<path d="M ${f(b1[0])} ${f(b1[1])} L ${f(tip[0])} ${f(tip[1])} L ${f(b2[0])} ${f(b2[1])} Z"/>`,
    ];
  }
  return [];
}
const LINE_STYLES = ["curve", "straight", "angled", "dashed"];
const COLOR_SCHEMES = ["category", "pastel", "mono", "neon"];

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
    // Positions just placed by hand, until Home Assistant sends them back
    this._mapPosOverrides = new Map(); // id -> {x, y} relative to the center, or null
    // Folded branches, remembered per device
    this._collapsed = this._loadCollapsed();
    this._centerPos = { x: 400, y: 300 };
    this._activeDrag = null; // { id, startMouseX, startMouseY, startNodeX, startNodeY }
    this._pendingDrag = null; // { id, cloud, startMouseX, startMouseY, startNodeX, startNodeY }
    this._initialized = false;
    this._lastUpdated = null;
    this._lastAlexaKey = null;
    this._lastDataSignature = "";
    this._isModalOpen = false;
    // The note the keyboard works on, and the text field open in a note
    this._selectedId = null;
    this._inlineEdit = null;
    this._dragEndedAt = 0;
    // Several notes picked with the lasso or Shift+click, and the lasso itself
    this._multi = new Set();
    this._lassoMode = false;
    this._lasso = null;
    // Steps of this session that Ctrl+Z takes back, newest last
    this._undoStack = [];
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
    this._restoreSelectedCategory();
    if (this._config.default_category && !this._hasSavedCategory && !this._initialized) {
      this._selectedCategory = String(this._config.default_category).trim();
    }
    if (this._initialized) {
      this._applyConfigUpdates();
    }
  }

  // The look of the map: the template, with single parts chosen differently
  _mapStyle() {
    const config = this._config || {};
    const base = MAP_TEMPLATES[config.map_template] || MAP_TEMPLATES.standard;
    const pick = (value, allowed, fallback) => (allowed.includes(value) ? value : fallback);
    return {
      shape: pick(config.node_shape, NODE_SHAPES, base.shape),
      lines: pick(config.line_style, LINE_STYLES, base.lines),
      scheme: pick(config.color_scheme, COLOR_SCHEMES, base.scheme),
    };
  }

  _applyMapStyle() {
    const cardRoot = this.shadowRoot && this.shadowRoot.getElementById("cardRoot");
    if (!cardRoot) return;
    const style = this._mapStyle();
    const classes = [`shape-${style.shape}`, `lines-${style.lines}`, `scheme-${style.scheme}`];
    [...cardRoot.classList]
      .filter((name) => /^(shape|lines|scheme)-/.test(name) && !classes.includes(name))
      .forEach((name) => cardRoot.classList.remove(name));
    classes.forEach((name) => cardRoot.classList.add(name));
    // Every note carries its own shape, so a new one needs fresh notes
    const shapeKey = `${style.shape}:${this._config.voice_bubbles !== false}`;
    if (this._shownShape && this._shownShape !== shapeKey) {
      this._lastDataSignature = null;
      if (this._hass) this.hass = this._hass;
    }
    this._shownShape = shapeKey;
  }

  // The shape of one note: its own, a speech bubble for voice notes, or the
  // shape of the whole map
  _nodeShape(idea) {
    if (idea && NODE_SHAPES.includes(idea.shape)) return idea.shape;
    if (idea && this._config.voice_bubbles !== false && isVoiceSource(idea.source)) return "bubble";
    return this._mapStyle().shape;
  }

  _applyConfigUpdates() {
    if (!this.shadowRoot) return;
    this._applyMapStyle();
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

    const exportBtn = this.shadowRoot.getElementById("exportBtn");
    if (exportBtn) exportBtn.style.display = this._config.show_export_btn === true ? "inline-flex" : "none";

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

  _onPrivateData() {
    if (this._hass) this.hass = this._hass;
  }

  set hass(hass) {
    setLanguage(hass);
    this._hass = hass;
    this._refreshPrivateData();
    if (!this._initialized) {
      this._initDom();
    }
    const sensor = this._getSensorEntity();
    if (!sensor) return;

    const ideas = sensor.attributes.ideas || [];
    const categories = sensor.attributes.categories || [];
    this._checkSavedCategory(categories);
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
    if (this._inlineEdit) {
      this._inlineEdit.deferred = true;
      return;
    }
    this._lastDataSignature = sig;
    this._updateContent();
  }

  _categoryStorageKey() {
    const title = (this._config && this._config.title) || "default";
    return `brainstorm_selected_category_mindmap_${title}`;
  }

  _restoreSelectedCategory() {
    if (this._categoryRestored) return;
    this._categoryRestored = true;
    try {
      const saved = localStorage.getItem(this._categoryStorageKey());
      if (saved) {
        this._selectedCategory = saved;
        this._hasSavedCategory = true;
        this._savedCategoryUnchecked = true;
      }
    } catch (e) {
      // Without browser storage the card simply starts with its default
    }
  }

  _saveSelectedCategory() {
    try {
      localStorage.setItem(this._categoryStorageKey(), this._selectedCategory);
    } catch (e) {
      // Without browser storage the selection only lasts until the next reload
    }
  }

  // A saved category may have been deleted in the meantime
  _checkSavedCategory(categories) {
    if (!this._savedCategoryUnchecked || !categories.length) return;
    this._savedCategoryUnchecked = false;
    const selected = this._selectedCategory;
    if (selected !== "all" && selected !== "__completed__" && !categories.includes(selected)) {
      this._selectedCategory = "all";
      this._saveSelectedCategory();
    }
  }

  _getSensorEntity() {
    const state = this._getRawSensorEntity();
    if (!state || !state.attributes || !state.attributes.privacy) return state;
    // With private ideas, the sensor holds no ideas and the user's own come separately
    return {
      ...state,
      last_updated: `${state.last_updated}_${this._privateVersion || 0}`,
      attributes: { ...state.attributes, ...(this._privateData || {}) },
    };
  }

  _refreshPrivateData() {
    const state = this._getRawSensorEntity();
    if (!state || !state.attributes || !state.attributes.privacy) return;
    if (this._privateFetchKey === state.last_updated) return;
    const key = state.last_updated;
    this._privateFetchKey = key;
    this._hass
      .callWS({ type: "brainstorm/ideas" })
      .then((data) => {
        if (this._privateFetchKey !== key) return;
        this._privateData = data;
        this._privateVersion = (this._privateVersion || 0) + 1;
        this._onPrivateData();
      })
      .catch((err) => console.error("[Brainstorm] Failed to load ideas:", err));
  }

  _getRawSensorEntity() {
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
    if (s.includes("siri")) icon = '<ha-icon icon="mdi:apple" style="--mdc-icon-size: 14px; width: 14px; height: 14px;"></ha-icon>';
    else if (s.includes("assist")) icon = "✨";
    else if (s.includes("alexa") || s.includes("voice") || s.includes("speech")) icon = "🗣️";
    else if (s.includes("mobile") || s.includes("handy") || s.includes("companion")) icon = "📱";
    else if (s.includes("dashboard")) icon = "💻";

    if (device && String(device).trim()) {
      return `${icon} <span class="cloud-device" title="${t("Gerät: {device}", { device: this._escapeHtml(String(device).trim()) })}">(${this._escapeHtml(String(device).trim())})</span>`;
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
      if (diffSec < 60) return t("gerade eben");
      if (diffSec < 3600) return t("vor {count}m", { count: Math.floor(diffSec / 60) });
      if (diffSec < 86400) return t("vor {count}h", { count: Math.floor(diffSec / 3600) });
      return date.toLocaleDateString(dateLocale(), { day: "2-digit", month: "2-digit" });
    } catch {
      return "";
    }
  }

  _getReminderBadges(idea) {
    const parts = [];
    if (idea.due) {
      const date = new Date(idea.due);
      if (!Number.isNaN(date.getTime())) {
        const pad = (value) => String(value).padStart(2, "0");
        const label = `${shortDate(date)} ${date.getHours()}:${pad(date.getMinutes())}`;
        parts.push(`⏰ ${label}`);
      }
    }
    const name = (entityId) => {
      const state = entityId && this._hass && this._hass.states[entityId];
      return state ? state.attributes.friendly_name || entityId : entityId;
    };
    if (idea.trigger && idea.trigger.zone) {
      parts.push(`📍 ${idea.trigger.zone === "zone.home" ? t("Zuhause") : name(idea.trigger.zone)}`);
    }
    if (idea.assignee) parts.push(`👤 ${name(idea.assignee)}`);
    if (idea.access && idea.access !== "owner") parts.push(`👥 ${idea.owner_name || t("Geteilt")}`);
    if (idea.created_by && idea.author_name) parts.push(`✍️ ${idea.author_name}`);
    if (idea.access === "owner" && Object.keys(idea.shares || {}).length) {
      parts.push(`👥 ${Object.keys(idea.shares).length}`);
    }
    return parts.map((part) => `<span class="reminder-tag">${this._escapeHtml(part)}</span>`).join("");
  }

  _getPriorityBadge(priority, id = "") {
    const p = (priority || "medium").toLowerCase();
    const idAttr = id ? `data-id="${this._escapeHtml(id)}"` : "";
    if (p === "urgent") {
      return `<span class="prio-tag urgent" ${idAttr} data-prio="urgent" title="${t("Priorität: 🔥 Dringend (Klicken zum Umschalten)")}">${t("🔥 Dringend")}</span>`;
    }
    if (p === "high") {
      return `<span class="prio-tag high" ${idAttr} data-prio="high" title="${t("Priorität: 🔴 Hoch (Klicken zum Umschalten)")}">${t("🔴 Hoch")}</span>`;
    }
    if (p === "low") {
      return `<span class="prio-tag low" ${idAttr} data-prio="low" title="${t("Priorität: 🟢 Niedrig (Klicken zum Umschalten)")}">${t("🟢 Niedrig")}</span>`;
    }
    return `<span class="prio-tag medium" ${idAttr} data-prio="medium" title="${t("Priorität: 🟡 Mittel (Klicken zum Umschalten)")}">${t("🟡 Mittel")}</span>`;
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
      this._pushUndo(this._ideaText(id), () =>
        this._hass.callService("brainstorm", "update_idea", { id, priority: currentPrio })
      );
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
          position: relative;
          flex: 0 0 auto;
          z-index: 20;
          padding: 10px 14px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
          flex-wrap: nowrap;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
        }
        .top-left {
          display: flex;
          align-items: center;
          gap: 8px;
          flex: 0 1 auto;
          min-width: 0;
        }
        .top-right {
          display: flex;
          align-items: center;
          gap: 6px;
          flex: 0 0 auto;
          justify-content: flex-end;
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
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .reminder-tag {
          color: var(--primary-color);
          font-size: 0.75em;
          font-weight: 500;
          white-space: nowrap;
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
          flex: 0 0 auto;
          padding: 0;
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
        ha-card.is-fullscreen .top-bar {
          padding-top: max(10px, env(safe-area-inset-top));
          padding-left: max(14px, env(safe-area-inset-left));
          padding-right: max(14px, env(safe-area-inset-right));
        }
        ha-card.is-fullscreen .add-note-btn {
          bottom: calc(10px + env(safe-area-inset-bottom)) !important;
          left: max(10px, env(safe-area-inset-left)) !important;
        }
        ha-card.is-fullscreen .controls-panel {
          bottom: calc(10px + env(safe-area-inset-bottom)) !important;
          right: max(10px, env(safe-area-inset-right)) !important;
        }
        ha-card.is-fullscreen .dialog-backdrop {
          padding-top: max(8px, env(safe-area-inset-top)) !important;
          padding-bottom: max(8px, env(safe-area-inset-bottom)) !important;
        }
        ha-card.is-fullscreen .dialog-box {
          max-height: calc(100dvh - max(8px, env(safe-area-inset-top)) - max(8px, env(safe-area-inset-bottom))) !important;
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
          scrollbar-width: none;
        }
        .pills-container::-webkit-scrollbar {
          display: none;
        }
        @container (max-width: 600px) {
          .top-bar {
            flex-wrap: wrap;
            row-gap: 6px;
          }
          .top-left {
            flex: 1 1 0;
          }
          .pills-container {
            order: 3;
            flex: 1 0 100%;
            padding: 2px 0;
          }
          .cat-pill[data-cat="all"] {
            display: none !important;
          }
          .cat-pill {
            padding: 4px 10px !important;
            min-height: 32px !important;
            font-size: 0.74rem !important;
            border-radius: 14px !important;
          }
          .pill-dot {
            width: 7px !important;
            height: 7px !important;
          }
          .note-cloud {
            padding: 7px 10px !important;
            min-width: 130px !important;
            max-width: min(190px, calc(50cqw - 16px)) !important;
            border-radius: 12px !important;
          }
          #notesContainer .note-cloud.nshape-cloud {
            padding: 12px 16px !important;
          }
          #notesContainer .note-cloud.nshape-bubble {
            padding: 8px 12px !important;
          }
          #notesContainer .note-cloud.nshape-thought {
            padding: 12px 16px !important;
          }
          #notesContainer .note-cloud.nshape-ellipse {
            padding: 9px 18px !important;
          }
          #notesContainer .note-cloud.nshape-underline {
            padding: 5px 3px !important;
          }
          .cloud-device {
            max-width: 72px;
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
            font-size: 1rem !important;
          }
        }
        @container (max-width: 380px) {
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
        .synapse-path.branch-path {
          stroke-opacity: 0.6;
          stroke-width: 2.2;
          stroke-dasharray: none;
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
          width: max-content;
          min-width: 170px;
          max-width: 250px;
          transform: translate(-50%, -50%);
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
        /* Shapes, chosen per note */
        .note-cloud.nshape-pill {
          border-radius: 26px !important;
          border-left-width: 1px;
          border-color: color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 55%, transparent);
          padding-left: 18px !important;
          padding-right: 18px !important;
        }
        .note-cloud.nshape-rect {
          border-radius: 3px !important;
        }
        /* Cloud and bubble: the note box is see-through, an SVG draws the outline */
        #notesContainer .note-cloud.has-shape {
          background: transparent !important;
          border: none !important;
          border-radius: 0 !important;
          box-shadow: none !important;
        }
        .note-cloud.nshape-cloud {
          padding: 16px 22px !important;
        }
        .note-cloud.nshape-bubble {
          padding: 12px 16px !important;
        }
        .note-cloud.nshape-thought {
          padding: 16px 22px !important;
        }
        .note-cloud.nshape-ellipse {
          padding: 12px 26px !important;
        }
        .note-cloud.nshape-hexagon,
        .note-cloud.nshape-note {
          padding: 12px 14px !important;
        }
        /* Underlined: only the text, a line in the category color below it,
           and the lines to and from the note meet at its ends */
        #notesContainer .note-cloud.nshape-underline {
          /* Nearly see-through, but lines behind the text fade away */
          background: color-mix(in srgb, var(--ha-card-background, var(--card-background-color, #ffffff)) 85%, transparent) !important;
          border: none !important;
          border-bottom: 3px solid var(--cat-color, var(--primary-color, #03a9f4)) !important;
          border-radius: 0 !important;
          box-shadow: none !important;
          padding: 6px 4px 6px !important;
        }
        ha-card.scheme-neon #notesContainer .note-cloud.nshape-underline {
          background: color-mix(in srgb, #0b1020 80%, transparent) !important;
          box-shadow: 0 6px 8px -6px var(--cat-color, #22d3ee) !important;
        }
        #notesContainer .note-cloud.nshape-underline.cloud-high {
          border-bottom-color: #f97316 !important;
        }
        #notesContainer .note-cloud.nshape-underline.cloud-urgent {
          border-bottom-color: #ef4444 !important;
        }
        #notesContainer .note-cloud.nshape-underline.selected,
        #notesContainer .note-cloud.nshape-underline.multi-selected {
          background: color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 10%, transparent) !important;
          border-radius: 6px 6px 0 0 !important;
        }
        .node-shape {
          position: absolute;
          left: 0;
          top: 0;
          z-index: -1;
          overflow: visible;
          pointer-events: none;
          --shape-fill: var(--ha-card-background, var(--card-background-color, #ffffff));
          --shape-stroke: color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 60%, var(--card-background-color, #ffffff));
          --shape-width: 1.5px;
          filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.08));
          transition: filter 0.15s ease;
        }
        .node-shape .shape-outline > * {
          fill: none;
          stroke: var(--shape-stroke);
          stroke-width: calc(var(--shape-width) * 2);
          stroke-linejoin: round;
        }
        .node-shape .shape-fill > * {
          fill: var(--shape-fill);
          stroke: none;
        }
        .node-shape .shape-fill > .shape-fold {
          fill: var(--shape-stroke);
          fill-opacity: 0.35;
        }
        /* A note slip is tinted like paper in the category color */
        .note-cloud.nshape-note .node-shape {
          --shape-fill: color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 14%, var(--card-background-color, #ffffff));
        }
        .note-cloud.has-shape:hover .node-shape {
          --shape-stroke: var(--cat-color, var(--primary-color, #03a9f4));
          filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.14));
        }
        .note-cloud.has-shape.dragging .node-shape {
          filter: drop-shadow(0 8px 18px rgba(0, 0, 0, 0.2));
        }
        .note-cloud.has-shape.cloud-high .node-shape {
          --shape-stroke: #f97316;
        }
        .note-cloud.has-shape.cloud-urgent .node-shape {
          --shape-stroke: #ef4444;
          filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.35));
        }
        .note-cloud.has-shape.selected .node-shape {
          --shape-stroke: var(--cat-color, var(--primary-color, #03a9f4));
          --shape-width: 2.5px;
          filter: drop-shadow(0 0 5px color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 55%, transparent));
        }
        .note-cloud.has-shape.multi-selected .node-shape {
          --shape-stroke: var(--primary-color, #03a9f4);
          --shape-width: 2.5px;
        }
        ha-card.scheme-pastel .node-shape {
          --shape-fill: color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 15%, var(--card-background-color, #ffffff));
          --shape-stroke: color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 45%, var(--card-background-color, #ffffff));
          filter: none;
        }
        ha-card.scheme-neon .node-shape {
          --shape-fill: #0f172a;
          --shape-stroke: var(--cat-color, #22d3ee);
          filter: drop-shadow(0 0 8px color-mix(in srgb, var(--cat-color, #22d3ee) 55%, transparent));
        }
        ha-card.shape-rect .center-node {
          border-radius: 14px !important;
        }
        /* Templates: lines */
        ha-card.lines-straight .synapse-path,
        ha-card.lines-angled .synapse-path {
          stroke-dasharray: none;
        }
        ha-card.lines-angled .synapse-path {
          stroke-linejoin: round;
        }
        ha-card.lines-dashed .synapse-path {
          stroke-dasharray: 7, 5;
          stroke-linecap: round;
        }
        /* Templates: colors */
        ha-card.scheme-pastel .note-cloud,
        ha-card.scheme-pastel .center-node {
          background: color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 15%, var(--card-background-color, #ffffff));
        }
        ha-card.scheme-pastel .note-cloud {
          border-color: color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 40%, transparent);
          box-shadow: none;
        }
        ha-card.scheme-pastel .synapse-path {
          stroke-opacity: 0.55;
        }
        ha-card.scheme-mono .note-cloud,
        ha-card.scheme-mono .center-node {
          --cat-color: var(--secondary-text-color, #64748b) !important;
        }
        ha-card.scheme-mono .center-node {
          border-color: var(--primary-text-color, #1e293b) !important;
        }
        ha-card.scheme-mono .synapse-path {
          --path-color: var(--secondary-text-color, #64748b) !important;
        }
        ha-card.scheme-mono .note-cloud.selected {
          --cat-color: var(--primary-color, #03a9f4) !important;
        }
        ha-card.scheme-neon .canvas-area {
          --primary-text-color: #e2e8f0;
          --secondary-text-color: #94a3b8;
          --card-background-color: #0f172a;
          --ha-card-background: #0f172a;
          --divider-color: rgba(148, 163, 184, 0.25);
          background: radial-gradient(circle at 50% 45%, #1e1b4b 0%, #0b1020 70%);
        }
        ha-card.scheme-neon .note-cloud {
          background: rgba(15, 23, 42, 0.92);
          border: 1px solid var(--cat-color, #22d3ee);
          box-shadow: 0 0 14px color-mix(in srgb, var(--cat-color, #22d3ee) 55%, transparent);
        }
        ha-card.scheme-neon .center-node {
          background: #0f172a;
          box-shadow: 0 0 26px color-mix(in srgb, var(--cat-color, #22d3ee) 60%, transparent) !important;
        }
        ha-card.scheme-neon .synapse-path {
          stroke-opacity: 0.85;
          filter: drop-shadow(0 0 3px var(--path-color, #22d3ee));
        }
        .control-btn:disabled {
          opacity: 0.35;
          cursor: default;
        }
        .map-toast {
          position: absolute;
          left: 50%;
          bottom: 16px;
          transform: translate(-50%, 8px);
          max-width: calc(100% - 32px);
          padding: 8px 14px;
          border-radius: 10px;
          background: var(--primary-text-color, #1e293b);
          color: var(--card-background-color, #ffffff);
          font-size: 0.85rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.2s ease, transform 0.2s ease;
          z-index: 40;
        }
        .map-toast.visible {
          opacity: 0.92;
          transform: translate(-50%, 0);
        }
        .canvas-area:focus {
          outline: none;
        }
        .note-cloud.selected {
          border-color: var(--cat-color, var(--primary-color, #03a9f4));
          box-shadow: 0 0 0 3px color-mix(in srgb, var(--cat-color, var(--primary-color, #03a9f4)) 40%, transparent);
          z-index: 12;
        }
        .suggest-list {
          display: flex;
          flex-direction: column;
          gap: 6px;
          margin: 6px 0 4px;
          max-height: 50vh;
          overflow-y: auto;
        }
        .suggest-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .suggest-check {
          width: 22px;
          height: 22px;
          flex: 0 0 auto;
          accent-color: var(--primary-color, #03a9f4);
          cursor: pointer;
        }
        .suggest-text {
          flex: 1 1 auto;
          min-width: 0;
        }
        .suggest-status {
          padding: 14px 0;
          text-align: center;
        }
        .note-cloud.multi-selected {
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary-color, #03a9f4) 45%, transparent);
          z-index: 12;
        }
        .note-cloud.multi-selected::after {
          content: "✓";
          position: absolute;
          top: -9px;
          left: -9px;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
          font-size: 12px;
          line-height: 20px;
          text-align: center;
          pointer-events: none;
        }
        .canvas-area.lasso-mode {
          cursor: crosshair;
          touch-action: none;
        }
        .lasso-rect {
          position: absolute;
          display: none;
          border: 1.5px dashed var(--primary-color, #03a9f4);
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 12%, transparent);
          border-radius: 6px;
          pointer-events: none;
          z-index: 35;
        }
        .control-btn.active {
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
          border-color: var(--primary-color, #03a9f4);
        }
        .selection-bar {
          position: absolute;
          top: 10px;
          left: 12px;
          right: 12px;
          width: fit-content;
          margin: 0 auto;
          display: none;
          align-items: center;
          flex-wrap: wrap;
          justify-content: center;
          gap: 6px;
          box-sizing: border-box;
          padding: 6px 8px 6px 14px;
          border-radius: 22px;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border: 1px solid var(--primary-color, #03a9f4);
          box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
          color: var(--primary-text-color, #212121);
          font-size: 0.85rem;
          z-index: 38;
        }
        .selection-bar.visible {
          display: flex;
        }
        .selection-count {
          font-weight: 600;
          margin-right: 4px;
          white-space: nowrap;
        }
        .selection-btn {
          min-width: 36px;
          height: 36px;
          padding: 0 10px;
          border-radius: 18px;
          border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.2));
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
          color: var(--primary-text-color, #212121);
          font-size: 0.85rem;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
        }
        .selection-btn:hover {
          border-color: var(--primary-color, #03a9f4);
          color: var(--primary-color, #03a9f4);
        }
        .selection-btn.danger:hover {
          border-color: var(--error-color, #db4437);
          color: var(--error-color, #db4437);
        }
        @container (max-width: 480px) {
          .selection-btn .selection-label {
            display: none;
          }
        }
        .note-cloud.draft {
          z-index: 30;
          cursor: text;
        }
        .cloud-inline-editor {
          display: block;
          box-sizing: border-box;
          width: 100%;
          min-width: 140px;
          margin: 0 0 6px;
          padding: 4px 6px;
          border: 1px solid var(--cat-color, var(--primary-color, #03a9f4));
          border-radius: 8px;
          background: var(--card-background-color, #ffffff);
          color: var(--primary-text-color, #1e293b);
          font: inherit;
          font-size: 0.92rem;
          line-height: 1.3;
          resize: none;
          overflow: hidden;
          outline: none;
          user-select: text;
          cursor: text;
        }
        .note-cloud.draft .cloud-inline-editor {
          margin: 0;
        }
        .branch-toggle {
          position: absolute;
          top: -12px;
          right: -12px;
          min-width: 26px;
          height: 26px;
          padding: 0 6px;
          border-radius: 13px;
          border: 2px solid var(--ha-card-background, var(--card-background-color, #ffffff));
          background: var(--cat-color, var(--primary-color, #03a9f4));
          color: #ffffff;
          font-size: 0.8rem;
          font-weight: 700;
          line-height: 1;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        }
        .branch-toggle:hover {
          filter: brightness(1.1);
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
          white-space: nowrap;
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
          flex-wrap: wrap;
          gap: 4px 6px;
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
          white-space: nowrap;
          font-size: 0.72rem;
          color: var(--secondary-text-color, #64748b);
          /* Stay inside the cloud: the device name gives way, the time does not */
          min-width: 0;
          max-width: 100%;
        }
        .cloud-source > span {
          flex-shrink: 0;
        }
        .cloud-source > span:first-child {
          display: inline-flex;
          align-items: center;
          flex-shrink: 1;
          min-width: 0;
          overflow: hidden;
        }
        .cloud-device {
          font-size: 0.68rem;
          opacity: 0.85;
          max-width: 110px;
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          display: inline-block;
          vertical-align: middle;
        }

        .bs-link {
          color: var(--primary-color, #03a9f4);
          text-decoration: underline;
          overflow-wrap: anywhere;
        }
        .idea-text code, .idea-result code, .cloud-text code, .cloud-result code {
          font-family: var(--code-font-family, monospace);
          font-size: 0.9em;
          padding: 0 3px;
          border-radius: 4px;
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.15));
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
        .in-progress-badge,
        .attachment-badge {
          display: inline-flex;
          align-items: center;
          gap: 3px;
          padding: 1px 5px;
          border-radius: 6px;
          font-size: 0.68rem;
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
        }
        .in-progress-badge {
          font-weight: 600;
          color: var(--warning-color, #ff9800);
          background: color-mix(in srgb, var(--warning-color, #ff9800) 14%, transparent);
        }
        .cloud-result {
          margin: -4px 0 8px;
          padding-left: 7px;
          border-left: 2px solid var(--success-color, #4caf50);
          font-size: 0.76rem;
          line-height: 1.3;
          color: var(--secondary-text-color, #727272);
          white-space: pre-line;
          word-break: break-word;
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
        .dialog-body > * {
          flex-shrink: 0;
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
        .dialog-shape-grid {
          grid-template-columns: repeat(3, 1fr);
          margin-bottom: 4px;
        }
        .dialog-shape-hint {
          margin-bottom: 12px;
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
        input[type="date"].dialog-input,
        input[type="time"].dialog-input {
          height: 44px;
          min-height: 44px;
          padding-top: 0;
          padding-bottom: 0;
          line-height: normal;
        }
        .dialog-echo-details[open] .dialog-echo-summary {
          margin-bottom: 10px;
        }
        .dialog-echo-summary {
          display: flex;
          align-items: center;
          gap: 8px;
          min-height: 44px;
          cursor: pointer;
          list-style: none;
        }
        .dialog-echo-summary::-webkit-details-marker {
          display: none;
        }
        .dialog-echo-summary::after {
          content: "▾";
          margin-left: auto;
          color: var(--secondary-text-color, #64748b);
          transition: transform 0.15s ease;
        }
        .dialog-echo-details[open] .dialog-echo-summary::after {
          transform: rotate(180deg);
        }
        .dialog-echo-chosen {
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          font-size: 0.85rem;
          color: var(--primary-text-color, #212121);
        }
        .dialog-echo-details .dialog-hint {
          margin-top: 6px;
        }
        .dialog-echo-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 6px;
        }
        .dialog-due-row {
          display: grid;
          grid-template-columns: minmax(0, 1fr) minmax(0, 7rem) 44px;
          gap: 8px;
          align-items: center;
        }
        .dialog-due-row input::-webkit-date-and-time-value {
          text-align: left;
        }
        .dialog-btn.dialog-due-clear {
          width: 44px;
          height: 44px;
          padding: 0;
        }
        .dialog-hint {
          margin-top: -8px;
          font-size: 0.78rem;
          color: var(--secondary-text-color, #64748b);
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
        .dialog-btn-primary:disabled {
          opacity: 0.45;
          cursor: default;
          filter: none;
          box-shadow: none;
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
            <button class="top-tool-btn" id="colorModeBtn" style="display: ${this._config.show_color_toggle === true ? 'inline-flex' : 'none'};" title="${this._colorMode === 'theme' ? t("Farbmodus: Theme-Farben aktiv (Klicken für Bunt)") : t("Farbmodus: Bunt aktiv (Klicken für Theme-Farben)")}">
              ${this._colorMode === 'theme' ? '🎨' : '🌈'}
            </button>
            <button class="top-tool-btn" id="exportBtn" style="display: ${this._config.show_export_btn === true ? 'inline-flex' : 'none'};" title="${t("Map als Bild speichern")}">🖼️</button>
            <button class="fullscreen-btn" id="fullscreenToggleBtn" style="display: ${this._config.show_fullscreen_btn === true ? 'inline-flex' : 'none'};" title="${t("Vollbild umschalten (ESC zum Beenden)")}">⛶</button>
          </div>
        </div>

        <!-- Interactive Canvas Area -->
        <div class="canvas-area" id="canvasArea" tabindex="0">
          <div class="lasso-rect" id="lassoRect"></div>
          <div class="selection-bar" id="selectionBar" role="toolbar" aria-label="${t("Auswahl")}">
            <span class="selection-count" id="selectionCount"></span>
            <button class="selection-btn" data-multi="done" title="${t("Alle abhaken")}">✓<span class="selection-label">${t("Abhaken")}</span></button>
            <button class="selection-btn" data-multi="move" title="${t("Kategorie ändern")}">📁<span class="selection-label">${t("Kategorie")}</span></button>
            <button class="selection-btn danger" data-multi="delete" title="${t("Löschen")}">🗑️<span class="selection-label">${t("Löschen")}</span></button>
            <button class="selection-btn" data-multi="clear" title="${t("Auswahl aufheben (ESC)")}">✕</button>
          </div>
          <div class="grid-bg" id="gridBg" style="display: ${this._config.show_grid !== false ? 'block' : 'none'};"></div>
          <div class="viewport" id="viewport">
            <svg class="connectors" id="connectorsLayer"></svg>
            <div class="center-node" id="centerNode">
              <div class="center-bulb-wrapper" style="display: ${this._config.show_bulb_watermark === true ? 'block' : 'none'};">
                <img src="${BULB_URL}" class="center-bulb-img" alt="Brainstorm" />
              </div>
              <div class="center-content">
                <div class="center-icon" id="centerIcon" style="display: flex; justify-content: center; margin-bottom: 2px;"></div>
                <div class="center-title" id="centerTitle">Inbox</div>
                <div class="center-badge" id="centerBadge">${t("0 Notizen")}</div>
              </div>
            </div>
            <div id="notesContainer"></div>
            <div class="empty-state" id="emptyState" style="display: none;">
              ${t('Keine aktiven Notizen in dieser Kategorie.<br>Klicke unten links auf "+ Idee", um eine hinzuzufügen.')}
            </div>
          </div>
        </div>

        <!-- Bottom Left: Add Note -->
        <button class="add-note-btn" id="addNoteBtn" style="display: ${this._config.show_add_btn === true ? 'flex' : 'none'};">
          <span>➕</span>
          <span class="btn-text">${t("Neue Idee")}</span>
        </button>

        <!-- Bottom Right: Zoom & Reset Controls -->
        <div class="controls-panel" style="display: ${this._config.show_controls === true ? 'flex' : 'none'};">
          <button class="control-btn" id="zoomInBtn" title="${t("Vergrößern")}">+</button>
          <button class="control-btn" id="zoomOutBtn" title="${t("Verkleinern")}">−</button>
          <button class="control-btn" id="resetViewBtn" title="${t("Zentrieren / Anordnen")}">⟲</button>
          <button class="control-btn" id="lassoBtn" title="${t("Auswählen: Rahmen um mehrere Notizen ziehen (oder Umschalt+Ziehen)")}" aria-pressed="false">⬚</button>
          <button class="control-btn" id="arrangeBtn" title="${t("Neu ordnen: von Hand verschobene Notizen wieder automatisch platzieren")}">🪄</button>
          <button class="control-btn" id="undoBtn" title="${t("Rückgängig (Strg+Z)")}" disabled>↶</button>
        </div>

        <div class="map-toast" id="mapToast" role="status" aria-live="polite"></div>

        <!-- In-Card Modal Dialog (Mushroom Style) -->
        <div class="dialog-backdrop" id="mindmapDialog" style="display: none;">
          <div class="dialog-box" id="dialogBox">
            <div class="dialog-header">
              <div class="dialog-title" id="dialogTitle">${t("Titel")}</div>
              <button class="dialog-close" id="dialogCloseBtn" title="${t("Schließen (ESC)")}">✕</button>
            </div>
            <div class="dialog-body" id="dialogBody"></div>
          </div>
        </div>
      </ha-card>
    `;

    this._applyMapStyle();
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
          ? t("Farbmodus: Theme-Farben aktiv (Klicken für Bunt)")
          : t("Farbmodus: Bunt aktiv (Klicken für Theme-Farben)");
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
            if (this._usesSavedPositions() || this._userMovedNodes.size === 0) {
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
        e.target.closest(".control-btn") ||
        e.target.closest(".selection-bar") ||
        e.target.closest(".dialog-box")
      ) {
        return;
      }
      if (e.button !== 0) return;
      // Shift+drag or the select button draws a frame instead of moving the map
      if (e.shiftKey || this._lassoMode) {
        e.preventDefault();
        this._startLasso(e.clientX, e.clientY, e.shiftKey);
        return;
      }
      this._isPanning = true;
      this._startPan = { x: e.clientX - this._panX, y: e.clientY - this._panY };
    });

    window.addEventListener("mousemove", (e) => {
      if (this._lasso) {
        this._moveLasso(e.clientX, e.clientY);
        return;
      }
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
        this._moveDraggedNodes(dx, dy);
      }
    });

    window.addEventListener("mouseup", () => {
      if (this._lasso) this._finishLasso();
      if (this._isPanning) this._isPanning = false;
      if (this._activeDrag) this._finishDrag();
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
      const onBackground = !e.target.closest(".note-cloud") && !e.target.closest(".dialog-box") &&
        !e.target.closest(".control-btn") && !e.target.closest(".selection-bar");
      if (e.touches.length === 1 && this._lassoMode && onBackground) {
        this._startLasso(e.touches[0].clientX, e.touches[0].clientY, true);
        return;
      }
      if (this._lasso) this._cancelLasso();
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
      if (this._lasso && e.touches.length === 1) {
        e.preventDefault();
        this._moveLasso(e.touches[0].clientX, e.touches[0].clientY);
        return;
      }
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
        this._moveDraggedNodes(dx, dy);
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
      if (this._lasso) this._finishLasso();
      touchStartPan = null;
      lastTouchDist = null;
      if (this._activeDrag) this._finishDrag();
      this._pendingDrag = null;
    });

    // Fullscreen Toggle
    const fullscreenBtn = this.shadowRoot.getElementById("fullscreenToggleBtn");
    const cardRoot = this.shadowRoot.getElementById("cardRoot");
    const toggleFullscreen = () => {
      const isFs = cardRoot.classList.toggle("is-fullscreen");
      fullscreenBtn.innerHTML = isFs ? "✕" : "⛶";
      fullscreenBtn.classList.toggle("is-fullscreen", isFs);
      fullscreenBtn.title = isFs ? t("Vollbild beenden") : t("Vollbild umschalten (ESC zum Beenden)");
      setTimeout(() => {
        this._centerLayout(this._usesSavedPositions() || this._userMovedNodes.size === 0);
      }, 50);
    };

    if (fullscreenBtn) {
      fullscreenBtn.addEventListener("click", toggleFullscreen);
    }

    canvasArea.addEventListener("keydown", (e) => this._onMapKey(e));

    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        if (this._isModalOpen) {
          this._closeDialog();
        } else if (this._lasso || this._multi.size || this._lassoMode) {
          if (this._lasso) this._cancelLasso();
          this._clearMulti();
          this._setLassoMode(false);
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
    const lassoBtn = this.shadowRoot.getElementById("lassoBtn");
    if (lassoBtn) lassoBtn.addEventListener("click", () => this._setLassoMode(!this._lassoMode));
    this.shadowRoot.querySelectorAll(".selection-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const act = btn.getAttribute("data-multi");
        if (act === "done") this._completeSelected();
        else if (act === "move") this._showCategoryPicker([...this._multi]);
        else if (act === "delete") this._confirmDeleteSelected();
        else if (act === "clear") this._clearMulti();
      });
    });
    const arrangeBtn = this.shadowRoot.getElementById("arrangeBtn");
    if (arrangeBtn) arrangeBtn.addEventListener("click", () => this._arrangeAgain());
    const undoBtn = this.shadowRoot.getElementById("undoBtn");
    if (undoBtn) undoBtn.addEventListener("click", () => this._undo());
    const exportBtn = this.shadowRoot.getElementById("exportBtn");
    if (exportBtn) exportBtn.addEventListener("click", () => this._showExportDialog());
    this._updateUndoButton();

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
      this._saveSelectedCategory();
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

  // A single list keeps its map on every device, the overview of all lists does not
  _usesSavedPositions() {
    return Boolean(this._selectedCategory) && this._selectedCategory !== "all";
  }

  _loadCollapsed() {
    try {
      const stored = JSON.parse(window.localStorage.getItem(COLLAPSED_KEY) || "[]");
      return new Set(Array.isArray(stored) ? stored : []);
    } catch (err) {
      return new Set();
    }
  }

  _saveCollapsed() {
    try {
      window.localStorage.setItem(COLLAPSED_KEY, JSON.stringify([...this._collapsed]));
    } catch (err) {
      // Private windows may refuse storage, the branch then folds for this visit only
    }
  }

  _categoryIdeas() {
    const sensor = this._getSensorEntity();
    if (!sensor) return [];
    return (sensor.attributes.ideas || []).filter((i) => {
      if (this._selectedCategory === "all") return true;
      return String(i.category || "").trim() === String(this._selectedCategory || "").trim();
    });
  }

  // The ideas on the map, without those inside a folded branch
  _mapIdeas(ideas = this._categoryIdeas()) {
    const ids = new Set(ideas.map((i) => i.id));
    const byId = new Map(ideas.map((i) => [i.id, i]));
    return ideas.filter((idea) => {
      const seen = new Set();
      let parent = this._branchParent(idea, ids);
      while (parent && !seen.has(parent)) {
        if (this._collapsed.has(parent)) return false;
        seen.add(parent);
        parent = this._branchParent(byId.get(parent), ids);
      }
      return true;
    });
  }

  _toggleBranch(id) {
    if (this._collapsed.has(id)) this._collapsed.delete(id);
    else this._collapsed.add(id);
    this._saveCollapsed();
    this._lastLayoutKey = "";
    this._updateContent();
  }

  _savedPosition(idea) {
    if (!this._usesSavedPositions() || !this._centerPos) return null;
    const saved = idea.map_pos;
    if (this._mapPosOverrides.has(idea.id)) {
      // Home Assistant has caught up with what was just done here
      const override = this._mapPosOverrides.get(idea.id);
      const arrived = override === null
        ? !saved
        : Boolean(saved) && saved.x === override.x && saved.y === override.y;
      if (arrived) this._mapPosOverrides.delete(idea.id);
    }
    const pos = this._mapPosOverrides.has(idea.id) ? this._mapPosOverrides.get(idea.id) : saved;
    if (!pos || !Number.isFinite(pos.x) || !Number.isFinite(pos.y)) return null;
    return { x: this._centerPos.x + pos.x, y: this._centerPos.y + pos.y };
  }

  // A subtask hangs on its parent when that is on the same map
  _branchParent(idea, ids) {
    const parent = idea.parent_id;
    return parent && parent !== idea.id && ids.has(parent) ? parent : null;
  }

  _descendantIds(id, ideas) {
    const ids = new Set(ideas.map((i) => i.id));
    const result = [];
    const seen = new Set([id]);
    const queue = [id];
    while (queue.length) {
      const current = queue.shift();
      ideas.forEach((idea) => {
        if (this._branchParent(idea, ids) === current && !seen.has(idea.id)) {
          seen.add(idea.id);
          result.push(idea.id);
          queue.push(idea.id);
        }
      });
    }
    return result;
  }

  _ideaText(id) {
    const idea = this._categoryIdeas().find((i) => i.id === id);
    return idea ? idea.text || "" : "";
  }

  // Adds a note typed on the dashboard and gives back its ID
  async _addIdea(data, { undo = true } = {}) {
    const result = await this._hass.callWS({
      type: "call_service",
      domain: "brainstorm",
      service: "add_idea",
      service_data: { ...data, source: "dashboard" },
      return_response: true,
    });
    const created = result && result.response && result.response.idea;
    if (!created || !created.id) return null;
    if (undo) this._pushUndo(data.text, () => this._hass.callService("brainstorm", "delete_idea", { id: created.id }));
    return created.id;
  }

  // The AI suggests subtasks; nothing is stored until the person picks and saves
  _showSubtaskSuggestions(idea) {
    if (!this._hass) return;
    this._openDialog(t("✨ Unteraufgaben vorschlagen"), (body) => {
      const render = (state, suggestions = []) => {
        if (!this._isModalOpen) return;
        const preview = `<div class="dialog-note-preview">${formatText(idea.text)}</div>`;
        if (state === "loading") {
          body.innerHTML = `${preview}<div class="dialog-label suggest-status">${t("Die KI denkt nach …")}</div>`;
          return;
        }
        if (state === "error") {
          body.innerHTML = `
            ${preview}
            <div class="dialog-error" style="display: flex;">${suggestions}</div>
            <div class="dialog-footer">
              <button class="dialog-btn dialog-btn-cancel" id="cancelSuggestBtn">${t("Abbrechen")}</button>
              <button class="dialog-btn dialog-btn-primary" id="retrySuggestBtn">${t("Nochmal versuchen")}</button>
            </div>
          `;
          body.querySelector("#cancelSuggestBtn").addEventListener("click", () => this._closeDialog());
          body.querySelector("#retrySuggestBtn").addEventListener("click", load);
          return;
        }
        body.innerHTML = `
          ${preview}
          <div class="dialog-label">${t("Haken weg bei allem, was du nicht willst. Du kannst die Texte noch ändern.")}</div>
          <div class="suggest-list">
            ${suggestions
              .map(
                (text, index) => `
              <label class="suggest-row">
                <input type="checkbox" class="suggest-check" data-index="${index}" checked />
                <input type="text" class="dialog-input suggest-text" data-index="${index}" maxlength="200" value="${this._escapeHtml(text)}" />
              </label>`
              )
              .join("")}
          </div>
          <div class="dialog-footer">
            <button class="dialog-btn dialog-btn-cancel" id="retrySuggestBtn">${t("Neue Vorschläge")}</button>
            <button class="dialog-btn dialog-btn-primary" id="saveSuggestBtn"></button>
          </div>
        `;
        const saveBtn = body.querySelector("#saveSuggestBtn");
        const picked = () =>
          [...body.querySelectorAll(".suggest-check")]
            .filter((box) => box.checked)
            .map((box) => body.querySelector(`.suggest-text[data-index="${box.dataset.index}"]`).value.trim())
            .filter(Boolean);
        const updateSave = () => {
          const count = picked().length;
          saveBtn.textContent = t("{count} übernehmen", { count });
          saveBtn.disabled = count === 0;
        };
        body.querySelectorAll(".suggest-check, .suggest-text").forEach((el) => el.addEventListener("input", updateSave));
        updateSave();
        body.querySelector("#retrySuggestBtn").addEventListener("click", load);
        saveBtn.addEventListener("click", async () => {
          const texts = picked();
          if (!texts.length) return;
          this._closeDialog();
          if (this._collapsed.has(idea.id)) this._toggleBranch(idea.id);
          const created = [];
          for (const text of texts) {
            try {
              const id = await this._addIdea({ text, category: idea.category, parent_id: idea.id }, { undo: false });
              if (id) created.push(id);
            } catch (err) {
              console.error("[BrainstormMindmap] Failed to add subtask:", err);
            }
          }
          if (!created.length) return;
          this._showToast(t("{count} Unteraufgaben angelegt", { count: created.length }));
          this._pushUndo(t("{count} Unteraufgaben", { count: created.length }), async () => {
            for (const id of [...created].reverse()) {
              await this._hass.callService("brainstorm", "delete_idea", { id });
            }
          });
        });
      };
      const load = async () => {
        render("loading");
        try {
          const result = await this._hass.callWS({
            type: "brainstorm/suggest_subtasks",
            idea_id: idea.id,
            ...(this._hass.language ? { language: this._hass.language } : {}),
          });
          const suggestions = (result && result.suggestions) || [];
          if (!suggestions.length) render("error", t("Die KI hat keine Unteraufgaben geliefert."));
          else render("list", suggestions);
        } catch (err) {
          const code = err && err.code;
          render(
            "error",
            code === "ai_not_configured"
              ? t("Wähle zuerst eine KI-Aufgaben-Entität unter Brainstorm Hub ➔ Konfigurieren ➔ KI.")
              : code === "ai_unavailable"
                ? t("Die KI ist gerade nicht erreichbar. Versuch es gleich nochmal.")
                : code === "unauthorized"
                ? t("Du darfst diese Notiz nicht ändern.")
                : t("Die KI hat keine Unteraufgaben geliefert.")
          );
        }
      };
      load();
    });
  }

  _pushUndo(text, run) {
    this._undoStack.push({ text, run });
    if (this._undoStack.length > UNDO_LIMIT) this._undoStack.shift();
    this._updateUndoButton();
  }

  _updateUndoButton() {
    const btn = this.shadowRoot.getElementById("undoBtn");
    if (btn) btn.disabled = this._undoStack.length === 0;
  }

  async _undo() {
    const step = this._undoStack.pop();
    this._updateUndoButton();
    if (!step || !this._hass) return;
    try {
      await step.run();
      this._showToast(step.text ? t("↶ Rückgängig: {text}", { text: step.text }) : t("↶ Rückgängig"));
    } catch (err) {
      console.error("[BrainstormMindmap] Undo failed:", err);
      this._showToast(t("Rückgängig ging nicht"));
    }
  }

  _showToast(text) {
    const toast = this.shadowRoot.getElementById("mapToast");
    if (!toast) return;
    toast.textContent = text;
    toast.classList.add("visible");
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => toast.classList.remove("visible"), 2500);
  }

  _showExportDialog() {
    this._openDialog(t("🖼️ Map als Bild speichern"), (body) => {
      body.innerHTML = `
        <div class="dialog-label">${t("Gespeichert wird, was gerade auf der Map steht, ohne eingeklappte Zweige.")}</div>
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="exportSvgBtn">${t("SVG (Vektor)")}</button>
          <button class="dialog-btn dialog-btn-primary" id="exportPngBtn">${t("PNG (Bild)")}</button>
        </div>
      `;
      body.querySelector("#exportSvgBtn").addEventListener("click", () => {
        this._closeDialog();
        this._exportMap("svg");
      });
      body.querySelector("#exportPngBtn").addEventListener("click", () => {
        this._closeDialog();
        this._exportMap("png");
      });
    });
  }

  _exportFileName(extension) {
    const category = this._selectedCategory === "all" ? t("Alle") : this._selectedCategory || "map";
    const slug = String(category)
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "map";
    const now = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    return `brainstorm-${slug}-${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}.${extension}`;
  }

  _downloadBlob(blob, name) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  async _exportMap(format) {
    try {
      const image = this._buildMapSvg();
      if (!image) {
        this._showToast(t("Auf der Map ist nichts zum Speichern"));
        return;
      }
      if (format === "svg") {
        this._downloadBlob(new Blob([image.markup], { type: "image/svg+xml" }), this._exportFileName("svg"));
        return;
      }
      const blob = await this._svgToPng(image);
      this._downloadBlob(blob, this._exportFileName("png"));
    } catch (err) {
      console.error("[BrainstormMindmap] Export failed:", err);
      this._showToast(t("Speichern als Bild ging nicht"));
    }
  }

  // Draws the SVG onto a canvas at twice the size, for sharp pictures
  _svgToPng(image, scale = 2) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(new Blob([image.markup], { type: "image/svg+xml" }));
      const img = new Image();
      img.onload = () => {
        try {
          const canvas = document.createElement("canvas");
          canvas.width = Math.ceil(image.width * scale);
          canvas.height = Math.ceil(image.height * scale);
          const ctx = canvas.getContext("2d");
          ctx.scale(scale, scale);
          ctx.drawImage(img, 0, 0, image.width, image.height);
          URL.revokeObjectURL(url);
          canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error("empty canvas"))), "image/png");
        } catch (err) {
          URL.revokeObjectURL(url);
          reject(err);
        }
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error("SVG could not be drawn"));
      };
      img.src = url;
    });
  }

  // A picture of the map as plain SVG: lines, notes and the center, in the
  // colors the map shows right now, without buttons and badges
  _buildMapSvg() {
    const sr = this.shadowRoot;
    const clouds = [...sr.querySelectorAll("#notesContainer .note-cloud:not(.draft)")];
    if (!clouds.length) return null;
    const xml = (text) =>
      String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    const px = (value) => parseFloat(value) || 0;
    const measure = document.createElement("canvas").getContext("2d");
    const wrap = (text, font, maxWidth) => {
      measure.font = font;
      const lines = [];
      String(text)
        .split(/\n/)
        .forEach((paragraph) => {
          let line = "";
          paragraph.split(/\s+/).forEach((word) => {
            const next = line ? `${line} ${word}` : word;
            if (line && measure.measureText(next).width > maxWidth) {
              lines.push(line);
              line = word;
            } else {
              line = next;
            }
          });
          lines.push(line);
        });
      return lines;
    };

    const nodes = [];
    clouds.forEach((el, index) => {
      const pos = this._nodePositions.get(el.dataset.id);
      if (!pos) return;
      const style = getComputedStyle(el);
      const textEl = el.querySelector(".cloud-text");
      const tagEl = el.querySelector(".cat-tag");
      const textStyle = getComputedStyle(textEl || el);
      const tagStyle = getComputedStyle(tagEl || el);
      const width = el.offsetWidth;
      const padX = Math.max(px(style.paddingLeft), 10);
      const fontSize = px(textStyle.fontSize) || 14;
      const font = `${textStyle.fontWeight} ${fontSize}px ${textStyle.fontFamily}`;
      const lines = wrap(textEl ? textEl.textContent.trim() : "", font, width - padX * 2);
      const lineHeight = Math.round(fontSize * 1.35);
      const tagSize = 10;
      const height = 12 + tagSize + 6 + lines.length * lineHeight + 10;
      nodes.push({
        index,
        x: pos.x - width / 2,
        y: pos.y - height / 2,
        width,
        height,
        padX,
        lines,
        lineHeight,
        font,
        fontSize,
        tagSize,
        tag: tagEl ? tagEl.textContent.trim().toUpperCase() : "",
        tagColor: tagStyle.color,
        textColor: textStyle.color,
        fill: style.backgroundColor,
        stroke: style.borderTopColor,
        strokeWidth: px(style.borderTopWidth),
        accent: style.borderLeftColor,
        accentWidth: px(style.borderLeftWidth),
        radius: Math.min(px(style.borderTopLeftRadius), height / 2),
        shape: null,
      });
      // Cloud and bubble take their outline and its colors along
      const shapeEl = el.classList.contains("has-shape") && el.querySelector(":scope > .node-shape");
      if (shapeEl) {
        const outline = shapeEl.querySelector(".shape-outline > *");
        const fill = shapeEl.querySelector(".shape-fill > *");
        const node = nodes[nodes.length - 1];
        node.shape = el.dataset.shape;
        node.seed = el.dataset.id;
        node.angle = el._shapeAngle ?? Math.PI / 2;
        node.fill = fill ? getComputedStyle(fill).fill : node.fill;
        node.stroke = outline ? getComputedStyle(outline).stroke : node.stroke;
        node.strokeWidth = outline ? px(getComputedStyle(outline).strokeWidth) : 3;
      }
      // Underlined: just the line, where the lines on the map meet it
      if (el.classList.contains("nshape-underline")) {
        const node = nodes[nodes.length - 1];
        node.underline = { y: pos.y + el.offsetHeight / 2 - 1.5, color: style.borderBottomColor };
        // The picture leaves out the buttons, so the text moves down onto its line
        node.y = node.underline.y - node.height + 1.5;
      }
    });

    const centerNode = sr.getElementById("centerNode");
    const centerStyle = getComputedStyle(centerNode);
    const centerSize = centerNode.offsetWidth || 130;
    const center = {
      x: this._centerPos.x,
      y: this._centerPos.y,
      size: centerSize,
      round: centerStyle.borderTopLeftRadius.includes("%") || px(centerStyle.borderTopLeftRadius) >= centerSize / 2,
      radius: px(centerStyle.borderTopLeftRadius),
      fill: centerStyle.backgroundColor,
      stroke: centerStyle.borderTopColor,
      title: (sr.getElementById("centerTitle") || {}).textContent || "",
      badge: (sr.getElementById("centerBadge") || {}).textContent || "",
      color: getComputedStyle(sr.getElementById("centerTitle") || centerNode).color,
    };

    const pad = 40;
    let minX = center.x - centerSize / 2;
    let minY = center.y - centerSize / 2;
    let maxX = center.x + centerSize / 2;
    let maxY = center.y + centerSize / 2;
    nodes.forEach((node) => {
      minX = Math.min(minX, node.x);
      minY = Math.min(minY, node.y);
      maxX = Math.max(maxX, node.x + node.width);
      maxY = Math.max(maxY, node.y + node.height);
    });
    minX -= pad;
    minY -= pad;
    const width = Math.ceil(maxX + pad - minX);
    const height = Math.ceil(maxY + pad - minY);

    const canvasArea = sr.getElementById("canvasArea");
    const cardRoot = sr.getElementById("cardRoot");
    const transparent = (color) => !color || color === "transparent" || /rgba\(.*,\s*0\)$/.test(color);
    const areaStyle = getComputedStyle(canvasArea);
    const background = !transparent(areaStyle.backgroundColor)
      ? areaStyle.backgroundColor
      : !transparent(getComputedStyle(cardRoot).backgroundColor)
        ? getComputedStyle(cardRoot).backgroundColor
        : "#ffffff";
    // The neon template paints a gradient, the picture takes its dark end
    const gradient = areaStyle.backgroundImage && areaStyle.backgroundImage.startsWith("radial-gradient");

    let body = "";
    sr.querySelectorAll("#connectorsLayer path").forEach((path) => {
      const style = getComputedStyle(path);
      body += `<path d="${xml(path.getAttribute("d"))}" fill="none" stroke="${xml(style.stroke)}" stroke-opacity="${xml(style.strokeOpacity)}" stroke-width="${xml(px(style.strokeWidth) || 1.8)}"${style.strokeDasharray && style.strokeDasharray !== "none" ? ` stroke-dasharray="${xml(style.strokeDasharray)}"` : ""} stroke-linecap="round" stroke-linejoin="round"/>`;
    });

    const c = center;
    body += c.round
      ? `<circle cx="${c.x}" cy="${c.y}" r="${c.size / 2 - 1.25}" fill="${xml(c.fill)}" stroke="${xml(c.stroke)}" stroke-width="2.5"/>`
      : `<rect x="${c.x - c.size / 2}" y="${c.y - c.size / 2}" width="${c.size}" height="${c.size}" rx="${c.radius}" fill="${xml(c.fill)}" stroke="${xml(c.stroke)}" stroke-width="2.5"/>`;
    body += `<text x="${c.x}" y="${c.y - 2}" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="700" fill="${xml(c.color)}">${xml(c.title)}</text>`;
    body += `<text x="${c.x}" y="${c.y + 18}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="${xml(c.stroke)}">${xml(c.badge)}</text>`;

    const pageColor = gradient ? "#0b1020" : background;
    let defs = "";
    nodes.forEach((n) => {
      const clipId = `clip${n.index}`;
      defs += `<clipPath id="${clipId}"><rect x="${n.x}" y="${n.y}" width="${n.width}" height="${n.height}" rx="${n.radius}"/></clipPath>`;
      if (n.shape) {
        const parts = shapeParts(n.shape, n.width, n.height, { angle: n.angle, seed: n.seed }).join("");
        body += `<g transform="translate(${n.x} ${n.y})">`;
        body += `<g fill="none" stroke="${xml(n.stroke)}" stroke-width="${n.strokeWidth}" stroke-linejoin="round">${parts}</g>`;
        // The folded corner of a note slip is a shade of its outline
        const fillParts = parts.replace('class="shape-fold"', `class="shape-fold" fill="${xml(n.stroke)}" fill-opacity="0.35"`);
        body += `<g fill="${xml(pageColor)}">${parts}</g><g fill="${xml(n.fill)}">${fillParts}</g></g>`;
      }
      body += `<g>`;
      // See-through notes would show the lines behind them
      if (n.underline) {
        body += `<rect x="${n.x}" y="${n.y}" width="${n.width}" height="${n.height}" fill="${xml(pageColor)}" fill-opacity="0.85"/>`;
        body += `<line x1="${n.x}" y1="${n.underline.y}" x2="${n.x + n.width}" y2="${n.underline.y}" stroke="${xml(n.underline.color)}" stroke-width="3"/>`;
      } else if (!n.shape) {
        body += `<rect x="${n.x}" y="${n.y}" width="${n.width}" height="${n.height}" rx="${n.radius}" fill="${xml(pageColor)}"/>`;
        body += `<rect x="${n.x}" y="${n.y}" width="${n.width}" height="${n.height}" rx="${n.radius}" fill="${xml(n.fill)}" stroke="${xml(n.stroke)}" stroke-width="${n.strokeWidth || 1}"/>`;
      }
      if (!n.shape && !n.underline && n.accentWidth > n.strokeWidth + 0.5) {
        body += `<rect x="${n.x}" y="${n.y}" width="${n.accentWidth}" height="${n.height}" fill="${xml(n.accent)}" clip-path="url(#${clipId})"/>`;
      }
      const textX = n.x + n.padX;
      let y = n.y + 12 + n.tagSize;
      if (n.tag) {
        body += `<text x="${textX}" y="${y}" font-family="sans-serif" font-size="${n.tagSize}" font-weight="700" letter-spacing="0.5" fill="${xml(n.tagColor)}">${xml(n.tag)}</text>`;
      }
      y += 6;
      n.lines.forEach((line) => {
        y += n.lineHeight;
        body += `<text x="${textX}" y="${y - (n.lineHeight - n.fontSize) / 2 - 2}" style="font: ${xml(n.font)}" fill="${xml(n.textColor)}">${xml(line)}</text>`;
      });
      body += `</g>`;
    });

    const markup =
      `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="${minX} ${minY} ${width} ${height}">` +
      `<defs>${defs}</defs>` +
      `<rect x="${minX}" y="${minY}" width="${width}" height="${height}" fill="${xml(pageColor)}"/>` +
      body +
      `</svg>`;
    return { markup, width, height };
  }

  _focusMap() {
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    if (canvasArea) canvasArea.focus({ preventScroll: true });
  }

  _selectIdea(id) {
    this._selectedId = id;
    this.shadowRoot.querySelectorAll(".note-cloud.selected").forEach((el) => el.classList.remove("selected"));
    const el = id && this.shadowRoot.getElementById(`cloud_${id}`);
    if (el) el.classList.add("selected");
    if (id) this._focusMap();
  }

  // --- Picking several notes: lasso, Shift+click and the bar above the map ---

  _setLassoMode(on) {
    this._lassoMode = Boolean(on);
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    if (canvasArea) canvasArea.classList.toggle("lasso-mode", this._lassoMode);
    const btn = this.shadowRoot.getElementById("lassoBtn");
    if (btn) {
      btn.classList.toggle("active", this._lassoMode);
      btn.setAttribute("aria-pressed", String(this._lassoMode));
    }
    if (this._lassoMode) this._showToast(t("Rahmen ziehen oder Notizen antippen"));
  }

  _startLasso(clientX, clientY, additive) {
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    const rectEl = this.shadowRoot.getElementById("lassoRect");
    if (!canvasArea || !rectEl) return;
    this._lasso = { startX: clientX, startY: clientY, endX: clientX, endY: clientY, additive, rectEl, canvasArea };
    this._drawLasso();
  }

  _moveLasso(clientX, clientY) {
    if (!this._lasso) return;
    this._lasso.endX = clientX;
    this._lasso.endY = clientY;
    this._drawLasso();
  }

  _lassoBox() {
    const l = this._lasso;
    return {
      left: Math.min(l.startX, l.endX),
      top: Math.min(l.startY, l.endY),
      right: Math.max(l.startX, l.endX),
      bottom: Math.max(l.startY, l.endY),
    };
  }

  _drawLasso() {
    const { rectEl, canvasArea } = this._lasso;
    const box = this._lassoBox();
    const area = canvasArea.getBoundingClientRect();
    rectEl.style.display = "block";
    rectEl.style.left = `${box.left - area.left}px`;
    rectEl.style.top = `${box.top - area.top}px`;
    rectEl.style.width = `${box.right - box.left}px`;
    rectEl.style.height = `${box.bottom - box.top}px`;
  }

  _cancelLasso() {
    if (this._lasso) this._lasso.rectEl.style.display = "none";
    this._lasso = null;
  }

  _finishLasso() {
    const lasso = this._lasso;
    if (!lasso) return;
    const box = this._lassoBox();
    this._cancelLasso();
    // A plain click on the empty map lets go of the selection
    if (box.right - box.left < 6 && box.bottom - box.top < 6) {
      if (!lasso.additive) this._clearMulti();
      return;
    }
    const hits = [];
    this.shadowRoot.querySelectorAll("#notesContainer .note-cloud:not(.draft)").forEach((cloud) => {
      const r = cloud.getBoundingClientRect();
      if (r.right >= box.left && r.left <= box.right && r.bottom >= box.top && r.top <= box.bottom) {
        hits.push(cloud.dataset.id);
      }
    });
    if (!lasso.additive) this._multi.clear();
    hits.forEach((id) => this._multi.add(id));
    this._dragEndedAt = Date.now();
    this._refreshMultiClasses();
  }

  _toggleMulti(id) {
    if (this._multi.has(id)) this._multi.delete(id);
    else this._multi.add(id);
    this._refreshMultiClasses();
  }

  _clearMulti() {
    if (!this._multi.size) return;
    this._multi.clear();
    this._refreshMultiClasses();
  }

  _refreshMultiClasses() {
    this.shadowRoot.querySelectorAll("#notesContainer .note-cloud").forEach((cloud) => {
      cloud.classList.toggle("multi-selected", this._multi.has(cloud.dataset.id));
    });
    this._updateSelectionBar();
  }

  _updateSelectionBar() {
    const bar = this.shadowRoot.getElementById("selectionBar");
    if (!bar) return;
    bar.classList.toggle("visible", this._multi.size > 0);
    const count = this.shadowRoot.getElementById("selectionCount");
    if (count) count.textContent = t("{count} ausgewählt", { count: this._multi.size });
  }

  // Deepest notes first, so a subtask still knows its parent when it goes
  _byDepth(ids, deepestFirst) {
    const ideas = new Map(this._categoryIdeas().map((i) => [i.id, i]));
    const depth = (id) => {
      let d = 0;
      let cur = ideas.get(id);
      const seen = new Set();
      while (cur && cur.parent_id && ideas.has(cur.parent_id) && !seen.has(cur.id)) {
        seen.add(cur.id);
        cur = ideas.get(cur.parent_id);
        d += 1;
      }
      return d;
    };
    return [...ids].sort((a, b) => (deepestFirst ? depth(b) - depth(a) : depth(a) - depth(b)));
  }

  async _completeSelected() {
    const ids = [...this._multi];
    if (!ids.length || !this._hass) return;
    const done = [];
    for (const id of ids) {
      try {
        await this._hass.callService("brainstorm", "update_idea", { id, status: "completed" });
        done.push(id);
      } catch (err) {
        console.error("[BrainstormMindmap] Failed to complete idea:", err);
      }
    }
    this._clearMulti();
    if (!done.length) return;
    this._showToast(t("{count} Notizen erledigt", { count: done.length }));
    this._pushUndo(t("{count} Notizen", { count: done.length }), async () => {
      for (const id of done) {
        await this._hass.callService("brainstorm", "update_idea", { id, status: "active" });
      }
    });
  }

  _confirmDeleteSelected() {
    const ids = [...this._multi];
    if (!ids.length) return;
    this._openDialog(t("🗑️ {count} Notizen löschen?", { count: ids.length }), (body) => {
      const preview = ids
        .slice(0, 5)
        .map((id) => `<div class="dialog-note-preview">"${this._escapeHtml(this._ideaText(id))}"</div>`)
        .join("");
      const more = ids.length > 5 ? `<div class="dialog-label">${t("… und {count} weitere", { count: ids.length - 5 })}</div>` : "";
      body.innerHTML = `
        ${preview}${more}
        <p style="margin: 8px 0; font-size: 0.88rem; color: var(--secondary-text-color, #64748b);">
          ${t("Möchtest du diese Notizen wirklich aus Brainstorm entfernen?")}
        </p>
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="cancelDelBtn">${t("Abbrechen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="confirmDelBtn" style="background: var(--error-color, #db4437);">${t("Löschen")}</button>
        </div>
      `;
      body.querySelector("#cancelDelBtn").addEventListener("click", () => this._closeDialog());
      body.querySelector("#confirmDelBtn").addEventListener("click", async () => {
        this._closeDialog();
        const deleted = [];
        for (const id of this._byDepth(ids, true)) {
          try {
            await this._hass.callService("brainstorm", "delete_idea", { id });
            deleted.push(id);
            if (this._selectedId === id) this._selectedId = null;
          } catch (err) {
            console.error("[BrainstormMindmap] Failed to delete idea:", err);
          }
        }
        this._clearMulti();
        if (!deleted.length) return;
        this._showToast(t("{count} Notizen gelöscht", { count: deleted.length }));
        // Parents come back first, so their subtasks hang on them again
        this._pushUndo(t("{count} Notizen", { count: deleted.length }), async () => {
          for (const id of [...deleted].reverse()) {
            await this._hass.callService("brainstorm", "restore_idea", { id });
          }
        });
      });
    });
  }

  // Keys on the map: Tab adds a subtask, Enter a note beside it, Delete removes
  // it after asking, F2 edits it, the arrows walk along the branches
  _onMapKey(e) {
    if (this._isModalOpen || this._inlineEdit) return;
    const target = e.composedPath()[0];
    if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) return;
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey && e.key.toLowerCase() === "z") {
      e.preventDefault();
      this._undo();
      return;
    }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    // With several notes picked, Delete asks once for all of them
    if (this._multi.size && (e.key === "Delete" || e.key === "Backspace")) {
      e.preventDefault();
      this._confirmDeleteSelected();
      return;
    }
    const ideas = this._mapIdeas();
    const ids = new Set(ideas.map((i) => i.id));
    const idea = ideas.find((i) => i.id === this._selectedId);
    const key = e.key;

    if (!idea) {
      if (key === "Enter") {
        e.preventDefault();
        this._showAddDialog();
      } else if (key.startsWith("Arrow") && ideas.length) {
        e.preventDefault();
        const first = ideas.find((i) => !this._branchParent(i, ids)) || ideas[0];
        this._selectIdea(first.id);
      }
      return;
    }

    const parentId = this._branchParent(idea, ids);
    const siblings = ideas.filter((i) => this._branchParent(i, ids) === parentId);
    const children = ideas.filter((i) => this._branchParent(i, ids) === idea.id);
    const step = (offset) => {
      const index = siblings.findIndex((i) => i.id === idea.id);
      const next = siblings[(index + offset + siblings.length) % siblings.length];
      if (next) this._selectIdea(next.id);
    };

    if (key === "Tab" && !e.shiftKey) {
      e.preventDefault();
      this._startDraft(idea, true);
    } else if (key === "Enter") {
      e.preventDefault();
      this._startDraft(idea, false);
    } else if (key === "Delete" || key === "Backspace") {
      e.preventDefault();
      this._showDeleteConfirm(idea.id, idea.text);
    } else if (key === "F2") {
      e.preventDefault();
      this._startInlineEdit(idea.id);
    } else if (key === "Escape") {
      e.preventDefault();
      e.stopPropagation();
      this._selectIdea(null);
    } else if (key === "ArrowLeft") {
      e.preventDefault();
      if (parentId) this._selectIdea(parentId);
    } else if (key === "ArrowRight") {
      e.preventDefault();
      if (this._collapsed.has(idea.id)) this._toggleBranch(idea.id);
      else if (children.length) this._selectIdea(children[0].id);
    } else if (key === "ArrowUp" || key === "ArrowDown") {
      e.preventDefault();
      step(key === "ArrowUp" ? -1 : 1);
    }
  }

  // A text field inside a note: Enter keeps the text, Shift+Enter starts a new
  // line, Escape gives up, leaving the field keeps what was typed
  _openInlineEditor(textarea, onSave, onCancel) {
    let finished = false;
    const grow = () => {
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
    };
    const finish = (save) => {
      if (finished) return;
      finished = true;
      const text = (textarea.value || "").trim();
      const deferred = this._inlineEdit && this._inlineEdit.deferred;
      this._inlineEdit = null;
      if (save && text) onSave(text);
      else onCancel();
      this._focusMap();
      // Show what arrived from Home Assistant while the field was open
      if (deferred && this._hass) this.hass = this._hass;
    };
    textarea.addEventListener("input", grow);
    textarea.addEventListener("keydown", (e) => {
      e.stopPropagation();
      if ((e.key === "Enter" && !e.shiftKey) || e.key === "Tab") {
        e.preventDefault();
        finish(true);
      } else if (e.key === "Escape") {
        e.preventDefault();
        finish(false);
      }
    });
    textarea.addEventListener("blur", () => finish(true));
    ["mousedown", "touchstart", "click", "dblclick", "wheel"].forEach((type) =>
      textarea.addEventListener(type, (e) => e.stopPropagation(), { passive: true })
    );
    this._inlineEdit = { textarea };
    grow();
    textarea.focus({ preventScroll: true });
  }

  _startInlineEdit(id) {
    if (this._inlineEdit || this._isModalOpen) return;
    const idea = this._categoryIdeas().find((i) => i.id === id);
    const cloud = this.shadowRoot.getElementById(`cloud_${id}`);
    const textEl = cloud && cloud.querySelector(".cloud-text");
    if (!idea || !textEl) return;
    const textarea = document.createElement("textarea");
    textarea.className = "cloud-inline-editor";
    textarea.rows = 1;
    textarea.value = idea.text || "";
    textEl.style.display = "none";
    textEl.after(textarea);
    cloud.classList.add("editing");
    const close = () => {
      textarea.remove();
      textEl.style.display = "";
      cloud.classList.remove("editing");
    };
    this._openInlineEditor(
      textarea,
      (text) => {
        close();
        if (text === (idea.text || "").trim()) return;
        textEl.innerHTML = formatText(text);
        const oldText = idea.text || "";
        this._hass
          .callService("brainstorm", "update_idea", { id, text })
          .then(() =>
            this._pushUndo(oldText, () => this._hass.callService("brainstorm", "update_idea", { id, text: oldText }))
          )
          .catch((err) => {
            console.error("[BrainstormMindmap] Failed to update idea:", err);
            textEl.innerHTML = formatText(idea.text);
          });
      },
      close
    );
    textarea.select();
  }

  // An empty note right on the map, as a subtask of the anchor or beside it
  _startDraft(anchor, asChild) {
    if (this._inlineEdit || this._isModalOpen || !this._hass) return;
    const ids = new Set(this._categoryIdeas().map((i) => i.id));
    const parentId = asChild ? anchor.id : this._branchParent(anchor, ids);
    if (asChild && this._collapsed.has(anchor.id)) this._toggleBranch(anchor.id);
    const container = this.shadowRoot.getElementById("notesContainer");
    const pos = this._nodePositions.get(anchor.id);
    if (!container || !pos) return;

    let x = pos.x;
    let y = pos.y + 90;
    if (asChild) {
      // Further out, away from the center
      const dx = pos.x - this._centerPos.x;
      const dy = pos.y - this._centerPos.y;
      const length = Math.hypot(dx, dy) || 1;
      x = pos.x + (dx / length) * 190;
      y = pos.y + (dy / length) * 130;
    }

    const draft = document.createElement("div");
    draft.className = "note-cloud draft selected";
    draft.style.setProperty("--cat-color", this._getCategoryColor(anchor.category));
    draft.style.left = `${x}px`;
    draft.style.top = `${y}px`;
    const textarea = document.createElement("textarea");
    textarea.className = "cloud-inline-editor";
    textarea.rows = 1;
    textarea.placeholder = asChild ? t("Neue Unteridee …") : t("Neue Idee …");
    draft.appendChild(textarea);
    container.appendChild(draft);
    this.shadowRoot.querySelectorAll(".note-cloud.selected").forEach((el) => {
      if (el !== draft) el.classList.remove("selected");
    });

    this._openInlineEditor(
      textarea,
      (text) => {
        draft.remove();
        this._addIdea({
          text,
          category: anchor.category,
          ...(parentId ? { parent_id: parentId } : {}),
        })
          .then((createdId) => {
            // The keyboard goes on from the new note
            if (createdId) this._selectIdea(createdId);
          })
          .catch((err) => console.error("[BrainstormMindmap] Failed to add idea:", err));
      },
      () => {
        draft.remove();
        this._selectIdea(anchor.id);
      }
    );
  }

  _finishDrag() {
    const drag = this._activeDrag;
    const el = this.shadowRoot.getElementById(`cloud_${drag.id}`);
    if (el) el.classList.remove("dragging");
    const moved = [drag.id, ...(drag.group || []).map((g) => g.id)];
    this._activeDrag = null;
    // The click that ends a drag neither selects nor edits
    this._dragEndedAt = Date.now();
    const noteText = this._ideaText(drag.id);
    if (!this._usesSavedPositions()) {
      // Only this device knows these places, so undo puts them back here
      const starts = [{ id: drag.id, x: drag.startNodeX, y: drag.startNodeY }, ...(drag.group || [])];
      const wasMoved = new Set(moved.filter((id) => this._userMovedNodes.has(id)));
      moved.forEach((id) => this._userMovedNodes.add(id));
      this._pushUndo(noteText, async () => {
        starts.forEach((start) => {
          this._nodePositions.set(start.id, { x: start.x, y: start.y });
          const cloud = this.shadowRoot.getElementById(`cloud_${start.id}`);
          if (cloud) {
            cloud.style.left = `${start.x}px`;
            cloud.style.top = `${start.y}px`;
          }
          if (!wasMoved.has(start.id)) this._userMovedNodes.delete(start.id);
        });
        this._drawConnections();
      });
      return;
    }
    const ideasById = new Map(this._categoryIdeas().map((i) => [i.id, i]));
    const previous = {};
    moved.forEach((id) => {
      const idea = ideasById.get(id);
      previous[id] = this._mapPosOverrides.has(id) ? this._mapPosOverrides.get(id) : (idea && idea.map_pos) || null;
    });
    const positions = {};
    moved.forEach((id) => {
      const pos = this._nodePositions.get(id);
      if (!pos) return;
      const rel = {
        x: Math.round((pos.x - this._centerPos.x) * 10) / 10,
        y: Math.round((pos.y - this._centerPos.y) * 10) / 10,
      };
      positions[id] = rel;
      this._mapPosOverrides.set(id, rel);
    });
    if (!Object.keys(positions).length || !this._hass) return;
    this._hass
      .callWS({ type: "brainstorm/map_positions", positions })
      .then(() => this._pushUndo(noteText, () => this._restorePositions(previous)))
      .catch((err) => console.error("[BrainstormMindmap] Failed to save positions:", err));
  }

  // Saved places as they were, null for the automatic place
  async _restorePositions(positions) {
    Object.entries(positions).forEach(([id, pos]) => this._mapPosOverrides.set(id, pos));
    this._lastLayoutKey = "";
    this._updateContent();
    await this._hass.callWS({ type: "brainstorm/map_positions", positions });
  }

  // Puts notes placed by hand back where the map would put them itself
  _arrangeAgain() {
    const placed = this._categoryIdeas().filter((idea) => this._savedPosition(idea));
    if (!placed.length) {
      this._userMovedNodes.clear();
      this._centerLayout(true);
      return;
    }
    this._openDialog(t("🪄 Map neu ordnen?"), (body) => {
      body.innerHTML = `
        <div class="dialog-label">${t("{count} von Hand verschobene Notizen kommen wieder an ihren automatischen Platz, auf allen Geräten.", { count: placed.length })}</div>
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="cancelArrangeBtn">${t("Abbrechen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="confirmArrangeBtn">${t("Ordnen")}</button>
        </div>
      `;
      body.querySelector("#cancelArrangeBtn").addEventListener("click", () => this._closeDialog());
      body.querySelector("#confirmArrangeBtn").addEventListener("click", () => {
        this._closeDialog();
        const positions = {};
        const previous = {};
        placed.forEach((idea) => {
          previous[idea.id] = this._mapPosOverrides.has(idea.id)
            ? this._mapPosOverrides.get(idea.id)
            : idea.map_pos || null;
          positions[idea.id] = null;
          this._mapPosOverrides.set(idea.id, null);
        });
        this._userMovedNodes.clear();
        this._centerLayout(true);
        this._hass
          .callWS({ type: "brainstorm/map_positions", positions })
          .then(() => this._pushUndo("", () => this._restorePositions(previous)))
          .catch((err) => console.error("[BrainstormMindmap] Failed to reset positions:", err));
      });
    });
  }

  _moveDraggedNodes(dx, dy) {
    const drag = this._activeDrag;
    const nodes = [{ id: drag.id, x: drag.startNodeX, y: drag.startNodeY }, ...(drag.group || [])];
    nodes.forEach((node) => {
      const x = node.x + dx;
      const y = node.y + dy;
      this._nodePositions.set(node.id, { x, y });
      const el = this.shadowRoot.getElementById(`cloud_${node.id}`);
      if (el) {
        el.style.left = `${x}px`;
        el.style.top = `${y}px`;
      }
    });
    this._drawConnections();
  }

  _arrangeNodesRadially() {
    if (!this._getSensorEntity()) return;
    const ideas = this._mapIdeas();

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

    // Only ideas without a parent on this map sit around the center
    const ids = new Set(ideas.map((i) => i.id));
    const childrenOf = new Map();
    ideas.forEach((idea) => {
      const parent = this._branchParent(idea, ids);
      if (!parent) return;
      if (!childrenOf.has(parent)) childrenOf.set(parent, []);
      childrenOf.get(parent).push(idea);
    });
    const roots = ideas.filter((idea) => !this._branchParent(idea, ids));
    const ringCount = roots.length;

    // Partition nodes into concentric elliptical rings to prevent clustering
    const rings = [];
    if (ringCount <= 6) {
      rings.push(roots);
    } else if (ringCount <= 12) {
      const nInner = Math.min(5, Math.max(3, Math.floor(ringCount * 0.42)));
      rings.push(roots.slice(0, nInner));
      rings.push(roots.slice(nInner));
    } else if (ringCount <= 20) {
      const n1 = 5;
      const n2 = Math.min(7, Math.floor((ringCount - 5) * 0.55));
      rings.push(roots.slice(0, n1));
      rings.push(roots.slice(n1, n1 + n2));
      rings.push(roots.slice(n1 + n2));
    } else {
      let rem = [...roots];
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
    const rx0 = ringCount <= 6
      ? Math.max(isNarrow ? 125 : 260, Math.min(w * (isNarrow ? 0.35 : 0.30), isNarrow ? 220 : 360))
      : Math.max(isNarrow ? 115 : 250, Math.min(w * (isNarrow ? 0.28 : 0.22), isNarrow ? 190 : 310));
    const ry0 = ringCount <= 6
      ? Math.max(isNarrow ? 90 : 180, Math.min(h * (isNarrow ? 0.32 : 0.30), isNarrow ? h * 0.32 : 220))
      : Math.max(isNarrow ? 85 : 175, Math.min(h * (isNarrow ? 0.2 : 0.24), isNarrow ? h * 0.2 : 185));
    const drx = isNarrow ? Math.max(120, Math.min(w * 0.16, 170)) : Math.max(210, Math.min(w * 0.16, 250));
    const dry = isNarrow ? Math.max(70, h * 0.18) : Math.max(110, Math.min(h * 0.16, 135));

    const positionedItems = [];

    rings.forEach((ringIdeas, r) => {
      const n = ringIdeas.length;
      if (n === 0) return;
      const rx = rx0 + r * drx;
      const ry = ry0 + r * dry;
      const phase = -Math.PI / 2 + (r * Math.PI / (n * 2));
      const angleStep = (2 * Math.PI) / n;

      ringIdeas.forEach((idea, j) => {
        const saved = this._savedPosition(idea);
        if (saved) {
          positionedItems.push({ idea, x: saved.x, y: saved.y, fixed: true });
          return;
        }
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

    const branchDist = isNarrow ? 150 : 230;

    // With branches, each one gets its own slice of the circle so lines do not cross
    if (childrenOf.size > 0 && !isNarrow) {
      positionedItems.length = 0;
      const weight = new Map();
      let maxDepth = 0;
      const weigh = (idea, depth, seen) => {
        if (seen.has(idea.id)) return 0;
        seen.add(idea.id);
        maxDepth = Math.max(maxDepth, depth);
        const kids = childrenOf.get(idea.id) || [];
        const sum = kids.reduce((total, kid) => total + weigh(kid, depth + 1, seen), 0);
        weight.set(idea.id, Math.max(1, sum));
        return Math.max(1, sum);
      };
      const weighed = new Set();
      const total = roots.reduce((sum, root) => sum + weigh(root, 0, weighed), 0) || 1;
      // The outer ring needs room for every leaf
      const grow = Math.max(1, (total * 230) / (2 * Math.PI * (rx0 + maxDepth * drx)));
      const done = new Set();
      const placeTree = (idea, start, end, depth, parent) => {
        if (done.has(idea.id)) return;
        done.add(idea.id);
        const angle = (start + end) / 2;
        const saved = this._savedPosition(idea);
        const moved = this._userMovedNodes.has(idea.id) && this._nodePositions.get(idea.id);
        let item;
        if (saved || moved) {
          const pos = saved || moved;
          item = { idea, x: pos.x, y: pos.y, fixed: true };
        } else if (parent && parent.fixed) {
          // Below a note placed by hand, the branch follows that note
          item = {
            idea,
            x: parent.x + Math.cos(angle) * branchDist,
            y: parent.y + Math.sin(angle) * branchDist * 0.75,
            fixed: false,
          };
        } else {
          item = {
            idea,
            x: this._centerPos.x + Math.cos(angle) * (rx0 + depth * drx) * grow,
            y: this._centerPos.y + Math.sin(angle) * (ry0 + depth * dry) * grow,
            fixed: false,
          };
        }
        positionedItems.push(item);
        let cursor = start;
        (childrenOf.get(idea.id) || []).forEach((kid) => {
          const span = ((end - start) * (weight.get(kid.id) || 1)) / weight.get(idea.id);
          placeTree(kid, cursor, cursor + span, depth + 1, item);
          cursor += span;
        });
      };
      const firstSpan = roots.length ? (2 * Math.PI * weight.get(roots[0].id)) / total : 0;
      let cursor = -Math.PI / 2 - firstSpan / 2;
      roots.forEach((root) => {
        const span = (2 * Math.PI * weight.get(root.id)) / total;
        placeTree(root, cursor, cursor + span, 0, null);
        cursor += span;
      });
    }

    // Subtasks fan out behind their parent, away from the center
    const placed = new Map(positionedItems.map((item) => [item.idea.id, item]));
    const placeAt = (idea, x, y) => {
      const saved = this._savedPosition(idea);
      const moved = this._userMovedNodes.has(idea.id) && this._nodePositions.get(idea.id);
      const pos = saved || moved;
      const item = pos ? { idea, x: pos.x, y: pos.y, fixed: true } : { idea, x, y, fixed: false };
      positionedItems.push(item);
      placed.set(idea.id, item);
      return item;
    };
    const queue = [...positionedItems];
    while (queue.length) {
      const parent = queue.shift();
      const kids = (childrenOf.get(parent.idea.id) || []).filter((kid) => !placed.has(kid.id));
      if (!kids.length) continue;
      const dx = parent.x - this._centerPos.x;
      const dy = parent.y - this._centerPos.y;
      const base = dx || dy ? Math.atan2(dy, dx) : -Math.PI / 2;
      const spread = Math.min(Math.PI * 0.8, 0.5 * (kids.length - 1));
      kids.forEach((kid, k) => {
        const angle = kids.length === 1 ? base : base - spread / 2 + (spread * k) / (kids.length - 1);
        queue.push(placeAt(
          kid,
          parent.x + Math.cos(angle) * branchDist,
          parent.y + Math.sin(angle) * branchDist * 0.75,
        ));
      });
    }
    // Should parents ever point at each other, those ideas still get a place
    ideas.forEach((idea) => {
      if (!placed.has(idea.id)) placeAt(idea, this._centerPos.x, this._centerPos.y + branchDist);
    });

    // In reading order, a parent comes right before its subtasks
    const readingOrder = new Map();
    const visit = (idea) => {
      if (readingOrder.has(idea.id)) return;
      readingOrder.set(idea.id, readingOrder.size);
      (childrenOf.get(idea.id) || []).forEach(visit);
    };
    roots.forEach(visit);
    ideas.forEach(visit);

    // Collision relaxation pass: repel from center bulb and avoid card overlaps
    const gap = isNarrow ? 8 : 14;
    positionedItems.forEach((item) => {
      const el = this.shadowRoot.getElementById(`cloud_${item.idea.id}`);
      item.w = (el && el.offsetWidth) || (isNarrow ? 160 : 230);
      item.h = (el && el.offsetHeight) || (isNarrow ? 110 : 130);
    });
    const centerItem = {
      x: this._centerPos.x,
      y: this._centerPos.y,
      w: (centerNode && centerNode.offsetWidth) || 154,
      h: (centerNode && centerNode.offsetHeight) || 154,
      fixed: true,
    };
    const collisionItems = [centerItem, ...positionedItems];

    // On narrow cards the notes stay within the width and spread vertically
    const margin = isNarrow ? 8 : 12;
    const clampX = (item, x) => {
      if (!isNarrow || item.fixed) return x;
      return Math.max(margin + item.w / 2, Math.min(w - margin - item.w / 2, x));
    };
    if (isNarrow && count > 4) {
      const freeItems = positionedItems
        .filter((item) => !item.fixed)
        .sort((a, b) => readingOrder.get(a.idea.id) - readingOrder.get(b.idea.id));
      const rowCount = Math.ceil(freeItems.length / 2);
      freeItems.forEach((item, i) => {
        const row = Math.floor(i / 2);
        item.x = w * (i % 2 ? 0.75 : 0.25);
        item.y = this._centerPos.y + (row - (rowCount - 1) / 2) * (item.h + gap);
      });
    }
    positionedItems.forEach((item) => {
      item.x = clampX(item, item.x);
    });

    for (let iter = 0; iter < 80; iter++) {
      for (let i = 0; i < collisionItems.length; i++) {
        for (let j = i + 1; j < collisionItems.length; j++) {
          const a = collisionItems[i];
          const b = collisionItems[j];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const minX = (a.w + b.w) / 2 + gap;
          const minY = (a.h + b.h) / 2 + gap;
          const ox = minX - Math.abs(dx);
          const oy = minY - Math.abs(dy);

          if (ox > 0 && oy > 0) {
            const share = a.fixed || b.fixed ? 1 : 0.5;
            const pushX = (dx >= 0 ? 1 : -1) * ox * share;
            const nextAx = a.fixed ? a.x : a.x - pushX;
            const nextBx = b.fixed ? b.x : b.x + pushX;
            const canPushX = clampX(a, nextAx) === nextAx && clampX(b, nextBx) === nextBx;
            if (canPushX && ox / minX < oy / minY) {
              a.x = nextAx;
              b.x = nextBx;
            } else {
              const pushY = (dy >= 0 ? 1 : -1) * oy * share;
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
        minX = Math.min(minX, item.x - item.w / 2);
        maxX = Math.max(maxX, item.x + item.w / 2);
        minY = Math.min(minY, item.y - item.h / 2);
        maxY = Math.max(maxY, item.y + item.h / 2);
      });

      // Keep the cards clear of the buttons along the bottom edge
      const bottomInset = 56;
      const availW = w - margin * 2;
      const availH = h - margin - bottomInset;

      if (minX < margin || maxX > w - margin || minY < margin || maxY > h - bottomInset) {
        const minFitLimit = isNarrow ? 0.5 : 0.65;
        const fitScale = Math.min(availW / (maxX - minX), availH / (maxY - minY));
        this._scale = Math.max(minFitLimit, Math.min(1.0, fitScale));
        this._panX = w / 2 - this._scale * ((minX + maxX) / 2);
        this._panY = margin + availH / 2 - this._scale * ((minY + maxY) / 2);
        this._applyTransform();
      }
    }

    this._drawConnections();
  }

  _linePath(lines, x1, y1, x2, y2) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    if (lines === "straight") return `M ${x1} ${y1} L ${x2} ${y2}`;
    if (lines === "angled") {
      // Out sideways, then up or down, then on to the note
      const midX = x1 + dx / 2;
      return `M ${x1} ${y1} H ${midX} V ${y2} H ${x2}`;
    }
    // Cubic Bézier curve for an organic synapse look
    const cx1 = x1 + dx * 0.35;
    const cy1 = y1 + dy * 0.15;
    const cx2 = x1 + dx * 0.65;
    const cy2 = y1 + dy * 0.85;
    return `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`;
  }

  _drawConnections() {
    const svg = this.shadowRoot.getElementById("connectorsLayer");
    if (!svg) return;

    if (!this._getSensorEntity()) {
      svg.innerHTML = "";
      return;
    }

    const activeIdeas = this._mapIdeas();

    if (!this._centerPos) {
      const canvasArea = this.shadowRoot.getElementById("canvasArea");
      const w = (canvasArea && canvasArea.clientWidth) || 800;
      const h = (canvasArea && canvasArea.clientHeight) || 600;
      this._centerPos = { x: w / 2, y: h / 2 };
    }

    const ids = new Set(activeIdeas.map((i) => i.id));
    const lines = this._mapStyle().lines;
    let svgHtml = "";
    activeIdeas.forEach((idea) => {
      const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
      const pos = this._nodePositions.get(idea.id);
      // ONLY draw connection if node is currently rendered in the DOM and has coordinates
      if (!el || !pos) return;

      const catColor = this._getCategoryColor(idea.category);
      // A subtask's line starts at its parent instead of the center
      const parentId = this._branchParent(idea, ids);
      const from = (parentId && this._nodePositions.get(parentId)) || null;
      let x1 = from ? from.x : this._centerPos.x;
      let y1 = from ? from.y : this._centerPos.y;
      let x2 = pos.x;
      let y2 = pos.y;

      this._drawNodeShape(el, Math.atan2(y1 - y2, x1 - x2));

      // An underlined note takes its lines at the end of its underline
      const parentEl = from && this.shadowRoot.getElementById(`cloud_${parentId}`);
      if (parentEl && parentEl.classList.contains("nshape-underline")) {
        [x1, y1] = this._underlineEnd(parentEl, from, x2);
      }
      if (el.classList.contains("nshape-underline")) {
        [x2, y2] = this._underlineEnd(el, pos, x1);
      }

      const pathData = this._linePath(lines, x1, y1, x2, y2);
      svgHtml += `
        <path id="path_${idea.id}" class="synapse-path${from ? " branch-path" : ""}" d="${pathData}" style="--path-color: ${catColor};" />
      `;
    });

    svg.innerHTML = svgHtml;
  }

  // The end of a note's underline that faces towards x
  _underlineEnd(el, pos, x) {
    const half = el.offsetWidth / 2;
    return [x < pos.x ? pos.x - half : pos.x + half, pos.y + el.offsetHeight / 2];
  }

  // Remembers where a note's parent lies and paints its outline; a size
  // change, like while typing, paints it again
  _drawNodeShape(el, angle) {
    if (!el.classList.contains("has-shape")) return;
    el._shapeAngle = angle;
    if (!this._shapeObserver && window.ResizeObserver) {
      this._shapeObserver = new ResizeObserver((entries) => entries.forEach((entry) => this._paintShape(entry.target)));
    }
    if (this._shapeObserver && !el._shapeObserved) {
      el._shapeObserved = true;
      this._shapeObserver.observe(el);
    }
    this._paintShape(el);
  }

  _paintShape(el) {
    const svg = el.querySelector(":scope > .node-shape");
    const w = el.offsetWidth;
    const h = el.offsetHeight;
    if (!svg || !w || !h || !el.isConnected) return;
    const shape = el.dataset.shape;
    const angle = el._shapeAngle ?? Math.PI / 2;
    // Small turns of the tail are not worth a new outline
    const key = `${w}x${h}:${POINTING_SHAPES.includes(shape) ? Math.round(angle * 20) : ""}`;
    if (svg.dataset.key === key) return;
    svg.dataset.key = key;
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const parts = shapeParts(shape, w, h, { angle, seed: el.dataset.id }).join("");
    svg.innerHTML = `<g class="shape-outline">${parts}</g><g class="shape-fill">${parts}</g>`;
  }

  _updateContent() {
    try {
      const sensor = this._getSensorEntity();
      if (!sensor) return;

      const attributes = sensor.attributes || {};
      const categories = attributes.categories || ["Inbox"];
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
        this._mapPosOverrides.clear();
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
            <div class="last-alexa-badge" title="${t("Zuletzt aktive Alexa: {name} (Klicken für Details)", { name: this._escapeHtml(alexaInfo.name) })}">
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
          ? t("Farbmodus: Theme-Farben aktiv (Klicken für Bunt)")
          : t("Farbmodus: Bunt aktiv (Klicken für Theme-Farben)");
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
            <span>${t("Alle")} (${activeIdeas.length})</span>
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
              this._saveSelectedCategory();
              this._nodePositions.clear();
              if (this._userMovedNodes) this._userMovedNodes.clear();
              this._mapPosOverrides.clear();
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
        const displayCat = this._selectedCategory === "all" ? t("Alle") : this._selectedCategory;
        centerTitle.textContent = displayCat;
        centerBadge.textContent = `${filteredIdeas.length} ${filteredIdeas.length === 1 ? t("Idee") : t("Ideen")}`;

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

      // Render notes HTML, without those inside a folded branch
      const shownIdeas = this._mapIdeas(filteredIdeas);
      const listIds = new Set(filteredIdeas.map((i) => i.id));
      let html = "";
      const aiSubtasks = Boolean(sensor && sensor.attributes && sensor.attributes.ai_subtasks);
      shownIdeas.forEach((idea) => {
        const color = this._getCategoryColor(idea.category);
        const sourceBadge = this._getSourceBadge(idea.source, idea.device);
        const shape = this._nodeShape(idea);
        const svgShape = SVG_SHAPES.includes(shape);
        const timeAgo = this._formatTime(idea.created_at);
        const prio = (idea.priority || "medium").toLowerCase();
        const prioClass = prio === "urgent" ? "cloud-urgent" : prio === "high" ? "cloud-high" : "";
        const prioBadge = this._getPriorityBadge(idea.priority, idea.id);
        const hasBranch = filteredIdeas.some((i) => i.id !== idea.id && i.parent_id === idea.id && listIds.has(i.id));
        const folded = hasBranch && this._collapsed.has(idea.id);
        const hiddenCount = folded ? this._descendantIds(idea.id, filteredIdeas).length : 0;
        const branchToggle = hasBranch
          ? `<button class="branch-toggle" data-id="${idea.id}" title="${folded ? t("Zweig aufklappen") : t("Zweig einklappen")}">${folded ? `+${hiddenCount}` : "−"}</button>`
          : "";

        html += `
          <div class="note-cloud ${prioClass} nshape-${shape}${svgShape ? " has-shape" : ""}${idea.id === this._selectedId ? " selected" : ""}${this._multi.has(idea.id) ? " multi-selected" : ""}" id="cloud_${idea.id}" data-id="${idea.id}" data-shape="${shape}" style="--cat-color: ${color};">
            ${svgShape ? '<svg class="node-shape" aria-hidden="true"></svg>' : ""}
            ${branchToggle}
            <div class="cloud-meta">
              <span class="cat-tag" data-cat="${this._escapeHtml(idea.category)}" title="${t("Kategorie ändern")}">
                <ha-icon icon="${this._getCategoryIcon(idea.category)}" style="--mdc-icon-size: 12px; width: 12px; height: 12px; display: inline-flex; align-items: center; vertical-align: middle;"></ha-icon> ${this._escapeHtml(idea.category)}
              </span>
              ${prioBadge}
              ${this._getReminderBadges(idea)}
              ${inProgressBadge(idea)}
              ${attachmentBadge(idea)}
              <span class="cloud-source" title="${t("Quelle")}: ${this._escapeHtml(idea.source || 'Dashboard')}${idea.device ? ` • ${t("Gerät")}: ` + this._escapeHtml(idea.device) : ''}">
                <span>${sourceBadge}</span>
                <span>•</span>
                <span>${timeAgo}</span>
              </span>
            </div>
            <div class="cloud-text" title="${t("Klicken zum Bearbeiten")}">${formatText(idea.text)}</div>
            ${idea.result ? `<div class="cloud-result" title="${t("Ergebnis")}">${formatText(idea.result)}</div>` : ""}
            <div class="cloud-actions">
              <button class="action-btn done-btn" data-act="done" data-id="${idea.id}" title="${t("Als erledigt markieren")}">✓</button>
              <button class="action-btn" data-act="branch" data-id="${idea.id}" title="${t("Unteridee anlegen")}">🌿</button>
              ${aiSubtasks ? `<button class="action-btn" data-act="suggest" data-id="${idea.id}" title="${t("Unteraufgaben von der KI vorschlagen lassen")}">✨</button>` : ""}
              <button class="action-btn" data-act="edit" data-id="${idea.id}" title="${t("Bearbeiten")}">✏️</button>
              <button class="action-btn" data-act="move" data-id="${idea.id}" title="${t("Kategorie ändern")}">📁</button>
              <button class="action-btn del-btn" data-act="delete" data-id="${idea.id}" title="${t("Löschen")}">🗑️</button>
            </div>
          </div>
        `;
      });
      // The old notes go, and with them what the observer watched
      if (this._shapeObserver) this._shapeObserver.disconnect();
      container.innerHTML = html;
      // Notes that are done, deleted or filtered away leave the selection
      const shownIds = new Set(shownIdeas.map((i) => i.id));
      [...this._multi].forEach((id) => {
        if (!shownIds.has(id)) this._multi.delete(id);
      });
      this._updateSelectionBar();

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
      shownIdeas.forEach((idea) => {
        if (!this._nodePositions.has(idea.id)) {
          needsArrangement = true;
        }
      });

      const activeIds = new Set(shownIdeas.map((i) => i.id));
      for (const id of this._nodePositions.keys()) {
        if (!activeIds.has(id)) {
          this._nodePositions.delete(id);
          needsArrangement = true;
        }
      }

      // Branches or positions changed, maybe on another device
      const layoutKey = shownIdeas
        .map((i) => {
          const pos = this._usesSavedPositions() && i.map_pos ? `${i.map_pos.x},${i.map_pos.y}` : "";
          return `${i.id}:${i.parent_id || ""}:${pos}:${this._collapsed.has(i.id) ? "folded" : ""}`;
        })
        .join("|");
      if (layoutKey !== this._lastLayoutKey) {
        this._lastLayoutKey = layoutKey;
        needsArrangement = true;
      }

      if (needsArrangement || this._nodePositions.size !== shownIdeas.length) {
        this._arrangeNodesRadially();
      } else {
        // Restore existing positions
        shownIdeas.forEach((idea) => {
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
        const idea = shownIdeas.find((i) => i.id === id);
        if (!idea) return;
        // A parent takes its subtasks along, a picked note all other picked ones
        const dragGroup = () => {
          const roots = this._multi.has(id) ? [...this._multi] : [id];
          const ids = new Set(roots);
          roots.forEach((rootId) => this._descendantIds(rootId, filteredIdeas).forEach((d) => ids.add(d)));
          ids.delete(id);
          return [...ids]
            .map((otherId) => {
              // A folded subtask has no note on the map, only its saved place
              const other = filteredIdeas.find((i) => i.id === otherId);
              const pos = this._nodePositions.get(otherId) || (other && this._savedPosition(other));
              return pos ? { id: otherId, x: pos.x, y: pos.y } : null;
            })
            .filter(Boolean);
        };

        // Mouse down records pending drag - only moves if threshold > 5px (prevents click jitter!)
        cloud.addEventListener("mousedown", (e) => {
          if (e.target.closest(".action-btn") || e.target.closest("a") || e.target.closest(".cat-tag") || e.target.closest(".prio-tag") || e.target.closest(".branch-toggle") || e.target.closest(".cloud-inline-editor")) return;
          if (e.button !== 0) return;
          const pos = this._nodePositions.get(id) || { x: 0, y: 0 };
          this._pendingDrag = {
            id: id,
            cloud: cloud,
            startMouseX: e.clientX,
            startMouseY: e.clientY,
            startNodeX: pos.x,
            startNodeY: pos.y,
            group: dragGroup(),
          };
        });

        // Touch start records pending drag
        cloud.addEventListener("touchstart", (e) => {
          if (e.target.closest(".action-btn") || e.target.closest("a") || e.target.closest(".cat-tag") || e.target.closest(".prio-tag") || e.target.closest(".branch-toggle") || e.target.closest(".cloud-inline-editor")) return;
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
              group: dragGroup(),
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

        const toggleEl = cloud.querySelector(".branch-toggle");
        if (toggleEl) {
          toggleEl.addEventListener("click", (e) => {
            e.stopPropagation();
            this._toggleBranch(idea.id);
          });
        }

        // Priority Tag click -> Cycle Priority
        const prioTagEl = cloud.querySelector(".prio-tag");
        if (prioTagEl) {
          prioTagEl.addEventListener("click", (e) => {
            e.stopPropagation();
            this._toggleItemPriority(idea.id, idea.priority || "medium");
          });
        }

        // A click selects the note, a click on its text edits it right there
        cloud.addEventListener("click", (e) => {
          if (Date.now() - this._dragEndedAt < 300 || e.target.closest(".cloud-inline-editor")) return;
          // Shift or Ctrl+click, or a tap while selecting, adds or removes the note
          if (e.shiftKey || e.ctrlKey || e.metaKey || this._lassoMode) {
            if (e.target.closest(".action-btn") || e.target.closest("a")) return;
            this._toggleMulti(idea.id);
            return;
          }
          this._selectIdea(idea.id);
        });
        cloud.addEventListener("dblclick", (e) => {
          if (e.shiftKey || e.ctrlKey || e.metaKey || this._lassoMode) return;
          if (e.target.closest(".action-btn") || e.target.closest("a") || e.target.closest(".cloud-inline-editor")) return;
          this._startInlineEdit(idea.id);
        });
        const textEl = cloud.querySelector(".cloud-text");
        if (textEl) {
          textEl.addEventListener("click", (e) => {
            if (e.shiftKey || e.ctrlKey || e.metaKey || this._lassoMode) return;
            e.stopPropagation();
            if (e.target.closest("a")) return;
            if (Date.now() - this._dragEndedAt < 300) return;
            this._selectIdea(idea.id);
            this._startInlineEdit(idea.id);
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
            this._selectIdea(idea.id);
            if (act === "done") this._completeIdea(idea.id);
            else if (act === "branch") this._showAddDialog(idea);
            else if (act === "suggest") this._showSubtaskSuggestions(idea);
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
    if (bodyEl._bsAttachments) bodyEl._bsAttachments.abort();
    bodyEl._bsAttachments = null;
    bodyEl.innerHTML = "";
    renderFn(bodyEl);
    dialog.style.display = "flex";
  }

  _closeDialog() {
    const dialog = this.shadowRoot.getElementById("mindmapDialog");
    if (dialog) dialog.style.display = "none";
    this._isModalOpen = false;
    // Keys keep working on the map after a dialog
    if (this._selectedId) this._focusMap();
  }

  // One note (id) or several picked ones (an array of ids)
  _showCategoryPicker(id, currentCategory, noteText) {
    const sensor = this._getSensorEntity();
    const categories = sensor ? (sensor.attributes.categories || ["Inbox"]) : ["Inbox"];
    const counts = sensor ? (sensor.attributes.category_counts || {}) : {};
    const ids = Array.isArray(id) ? id : [id];
    if (!ids.length) return;
    const ideasById = new Map(this._categoryIdeas().map((i) => [i.id, i]));
    const previous = {};
    ids.forEach((ideaId) => {
      const idea = ideasById.get(ideaId);
      previous[ideaId] = idea ? idea.category : currentCategory;
    });
    if (Array.isArray(id)) {
      const cats = new Set(Object.values(previous));
      currentCategory = cats.size === 1 ? [...cats][0] : null;
    }
    const undoText = ids.length > 1 ? t("{count} Notizen", { count: ids.length }) : noteText;
    // Moves the notes, and undo puts each back into its own category
    const apply = async (newCat) => {
      const moved = [];
      for (const ideaId of ids) {
        if (previous[ideaId] === newCat) continue;
        await this._hass.callService("brainstorm", "update_idea", { id: ideaId, category: newCat });
        moved.push(ideaId);
      }
      if (Array.isArray(id)) this._clearMulti();
      if (!moved.length) return;
      this._pushUndo(undoText, async () => {
        for (const ideaId of moved) {
          await this._hass.callService("brainstorm", "update_idea", { id: ideaId, category: previous[ideaId] });
        }
      });
    };

    this._openDialog(t("🏷️ Kategorie auswählen"), (body) => {
      let previewHtml = "";
      if (ids.length > 1) {
        previewHtml = `<div class="dialog-note-preview">${this._escapeHtml(t("{count} Notizen", { count: ids.length }))}</div>`;
      } else if (noteText) {
        previewHtml = `<div class="dialog-note-preview">"${this._escapeHtml(noteText)}"</div>`;
      }

      body.innerHTML = `
        ${previewHtml}
        <div class="dialog-label">${t("Kategorie wählen:")}</div>
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
        <div class="dialog-label" style="margin-top: 6px;">${t("Oder neue Kategorie anlegen:")}</div>
        <div class="dialog-new-cat-row">
          <input type="text" class="dialog-input" id="newCatInput" placeholder="${t("Kategoriename...")}" />
          <button class="dialog-btn dialog-btn-primary" id="addNewCatBtn">${t("➕ Erstellen")}</button>
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
              await apply(newCat);
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
          showCatError(t("⚠️ Bitte gib einen Kategorienamen ein."));
          return;
        }
        if (categories.some((c) => c.toLowerCase() === val.toLowerCase())) {
          showCatError(t('⚠️ Die Kategorie "{name}" existiert bereits.', { name: val }));
          return;
        }
        this._closeDialog();
        try {
          await this._hass.callService("brainstorm", "add_category", { name: val });
          await apply(val);
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
    const idea = ((sensor && sensor.attributes.ideas) || []).find((i) => i.id === id) || {};
    const dueValues = dueInputValues(idea.due);
    const echos = alexaEchos(this._hass);
    const currentEchos = idea.echos || [];
    let selectedEchos = [...currentEchos];
    const currentShape = NODE_SHAPES.includes(idea.shape) ? idea.shape : "";
    let selectedShape = currentShape;
    const shapeChoices = [["", t("Automatisch")], ...NODE_SHAPES.map((shape) => [shape, shapeLabel(shape)])];

    this._openDialog(t("✏️ Notiz bearbeiten"), (body) => {
      body.innerHTML = `
        <div class="dialog-label">${t("Titel:")}</div>
        <textarea class="dialog-textarea" id="editTextarea" rows="2">${this._escapeHtml(currentText)}</textarea>
        <div class="dialog-error" id="editTextError" style="display: none;"></div>
        <div class="dialog-label">${t("Beschreibung:")}</div>
        <textarea class="dialog-textarea" id="editDescription" rows="4" placeholder="${t("Optional: Details, Links, Notizen …")}">${this._escapeHtml(idea.description || "")}</textarea>
        <div class="dialog-label">${t("Anhänge:")}</div>
        <div id="editAttachments"></div>

        <div class="dialog-label">${t("Priorität:")}</div>
        <div class="dialog-prio-grid" id="editPrioGrid">
          <div class="dialog-prio-chip ${selectedPrio === "low" ? "selected" : ""}" data-prio="low">${t("🟢 Niedrig")}</div>
          <div class="dialog-prio-chip ${selectedPrio === "medium" ? "selected" : ""}" data-prio="medium">${t("🟡 Mittel")}</div>
          <div class="dialog-prio-chip ${selectedPrio === "high" ? "selected" : ""}" data-prio="high">${t("🔴 Hoch")}</div>
          <div class="dialog-prio-chip ${selectedPrio === "urgent" ? "selected" : ""}" data-prio="urgent">${t("🔥 Dringend")}</div>
        </div>

        <div class="dialog-label">${t("Form auf der Mindmap:")}</div>
        <div class="dialog-prio-grid dialog-shape-grid" id="editShapeGrid">
          ${shapeChoices
            .map(([value, label]) => `<div class="dialog-prio-chip ${value === selectedShape ? "selected" : ""}" data-shape="${value}">${label}</div>`)
            .join("")}
        </div>
        <div class="dialog-hint dialog-shape-hint">${t("Automatisch: Sprachnotizen als Sprechblase, sonst die Form der Map.")}</div>

        <div class="dialog-label" style="margin-top: 10px;">${t("Kategorie:")}</div>
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

        <div class="dialog-label">${t("Termin:")}</div>
        <div class="dialog-due-row">
          <input type="date" class="dialog-input" id="editDueDate" value="${dueValues.date}">
          <input type="time" class="dialog-input" id="editDueTime" value="${dueValues.time}">
          <button class="dialog-btn dialog-btn-cancel dialog-due-clear" id="editDueClear" title="${t("Termin entfernen")}" aria-label="${t("Termin entfernen")}">✕</button>
        </div>
        <div class="dialog-hint">${t("Ohne Uhrzeit erinnert Brainstorm um 9:00.")}</div>

        ${echos.length ? `
          <details class="dialog-echo-details">
          <summary class="dialog-echo-summary">
            <span class="dialog-label">${t("Erinnern auf:")}</span>
            <span class="dialog-echo-chosen" id="editEchoChosen"></span>
          </summary>
          <div class="dialog-echo-grid" id="editEchoGrid">
            ${echos
              .map(
                (echo) => `
              <div class="dialog-cat-chip ${currentEchos.includes(echo.id) ? "selected" : ""}" data-echo="${this._escapeHtml(echo.id)}">
                <span class="dialog-cat-dot"></span>
                <span class="dialog-cat-name">${this._escapeHtml(echo.name)}</span>
              </div>
            `
              )
              .join("")}
          </div>
          <div class="dialog-hint">${t("Ohne Auswahl gelten die Einstellungen der Erinnerungen.")}</div>
          </details>
        ` : ""}

        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="cancelEditBtn">${t("Abbrechen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="saveEditBtn">${t("Speichern")}</button>
        </div>
      `;

      const textarea = body.querySelector("#editTextarea");
      renderAttachments(body.querySelector("#editAttachments"), {
        hass: this._hass,
        idea: { ...idea, id },
        canEdit: true,
        dropTarget: body,
      });
      const textError = body.querySelector("#editTextError");
      const saveBtn = body.querySelector("#saveEditBtn");
      const cancelBtn = body.querySelector("#cancelEditBtn");
      const catChips = body.querySelectorAll("#editCatGrid .dialog-cat-chip");
      const prioChips = body.querySelectorAll("#editPrioGrid .dialog-prio-chip");
      const shapeChips = body.querySelectorAll("#editShapeGrid .dialog-prio-chip");
      shapeChips.forEach((chip) => {
        chip.addEventListener("click", () => {
          shapeChips.forEach((c) => c.classList.remove("selected"));
          chip.classList.add("selected");
          selectedShape = chip.getAttribute("data-shape") || "";
        });
      });
      const dueDate = body.querySelector("#editDueDate");
      const dueTime = body.querySelector("#editDueTime");

      body.querySelector("#editDueClear").addEventListener("click", () => {
        dueDate.value = "";
        dueTime.value = "";
      });
      const echoChosen = body.querySelector("#editEchoChosen");
      const showChosenEchos = () => {
        if (!echoChosen) return;
        const names = echos.filter((echo) => selectedEchos.includes(echo.id)).map((echo) => echo.name);
        echoChosen.textContent = names.length ? names.join(", ") : t("Wie in den Einstellungen");
      };
      showChosenEchos();
      body.querySelectorAll("#editEchoGrid .dialog-cat-chip").forEach((chip) => {
        chip.addEventListener("click", () => {
          const echo = chip.getAttribute("data-echo");
          chip.classList.toggle("selected");
          selectedEchos = chip.classList.contains("selected")
            ? [...selectedEchos, echo]
            : selectedEchos.filter((e) => e !== echo);
          showChosenEchos();
        });
      });

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
          showTextError(t("⚠️ Der Text darf nicht leer sein."));
          return;
        }
        this._closeDialog();

        const payload = { id: id, text: newText, priority: selectedPrio };
        if (selectedCat && selectedCat !== currentCategory) {
          payload.category = selectedCat;
        }
        const newDue = dueFromInputValues(dueDate.value, dueTime.value);
        const oldDue = idea.due ? new Date(idea.due).getTime() : null;
        if ((newDue ? new Date(newDue).getTime() : null) !== oldDue) {
          payload.due = newDue;
        }
        if ([...selectedEchos].sort().join() !== [...currentEchos].sort().join()) {
          payload.echos = selectedEchos.length ? selectedEchos : null;
        }
        const newDescription = (body.querySelector("#editDescription").value || "").trim();
        if (newDescription !== (idea.description || "")) {
          payload.description = newDescription;
        }
        if (selectedShape !== currentShape) {
          payload.shape = selectedShape || null;
        }

        // Everything this save changes, as it was before
        const before = { id, text: currentText, priority: currentPriority || "medium" };
        if ("category" in payload) before.category = currentCategory;
        if ("due" in payload) before.due = idea.due || null;
        if ("echos" in payload) before.echos = currentEchos.length ? currentEchos : null;
        if ("description" in payload) before.description = idea.description || "";
        if ("shape" in payload) before.shape = currentShape || null;
        try {
          await this._hass.callService("brainstorm", "update_idea", payload);
          this._pushUndo(currentText, () => this._hass.callService("brainstorm", "update_idea", before));
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

  _showAddDialog(parent = null) {
    const sensor = this._getSensorEntity();
    const categories = sensor ? (sensor.attributes.categories || ["Inbox"]) : ["Inbox"];
    let selectedCat = this._selectedCategory && this._selectedCategory !== "all" ? this._selectedCategory : "Inbox";
    // A subtask stays in the list of its parent
    if (parent) selectedCat = parent.category;
    let selectedPrio = "medium";

    this._openDialog(parent ? t("🌿 Neue Unteridee") : t("💡 Neue Idee erfassen"), (body) => {
      body.innerHTML = `
        ${parent ? `<div class="dialog-label">${t("Unter: {text}", { text: this._escapeHtml(parent.text) })}</div>` : ""}
        <div class="dialog-label">${t("Idee / Gedanke:")}</div>
        <textarea class="dialog-textarea" id="addTextarea" placeholder="${t("Was möchtest du festhalten?...")}" rows="3"></textarea>
        <div class="dialog-error" id="addTextError" style="display: none;"></div>

        <div class="dialog-label">${t("Priorität:")}</div>
        <div class="dialog-prio-grid" id="addPrioGrid">
          <div class="dialog-prio-chip" data-prio="low">${t("🟢 Niedrig")}</div>
          <div class="dialog-prio-chip selected" data-prio="medium">${t("🟡 Mittel")}</div>
          <div class="dialog-prio-chip" data-prio="high">${t("🔴 Hoch")}</div>
          <div class="dialog-prio-chip" data-prio="urgent">${t("🔥 Dringend")}</div>
        </div>

        <div class="dialog-label" style="margin-top: 10px;${parent ? " display: none;" : ""}">${t("Kategorie:")}</div>
        <div class="dialog-categories-grid" id="addCatGrid"${parent ? ' style="display: none;"' : ""}>
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
          <button class="dialog-btn dialog-btn-cancel" id="cancelAddBtn">${t("Abbrechen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="saveAddBtn">${t("Hinzufügen")}</button>
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
          showTextError(t("⚠️ Der Text darf nicht leer sein."));
          return;
        }
        this._closeDialog();

        try {
          await this._addIdea({
            text: text,
            category: selectedCat,
            priority: selectedPrio,
            ...(parent ? { parent_id: parent.id } : {}),
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
    this._openDialog(t("🗑️ Notiz löschen?"), (body) => {
      body.innerHTML = `
        <div class="dialog-note-preview">"${this._escapeHtml(noteText)}"</div>
        <p style="margin: 8px 0; font-size: 0.88rem; color: var(--secondary-text-color, #64748b);">
          ${t("Möchtest du diese Notiz wirklich unwiderruflich aus Brainstorm entfernen?")}
        </p>
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="cancelDelBtn">${t("Abbrechen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="confirmDelBtn" style="background: var(--error-color, #db4437);">${t("Löschen")}</button>
        </div>
      `;

      body.querySelector("#cancelDelBtn").addEventListener("click", () => this._closeDialog());
      body.querySelector("#confirmDelBtn").addEventListener("click", async () => {
        this._closeDialog();
        try {
          await this._hass.callService("brainstorm", "delete_idea", { id: id });
          // Home Assistant keeps deleted ideas until its next start
          this._pushUndo(noteText, () => this._hass.callService("brainstorm", "restore_idea", { id }));
          if (this._selectedId === id) this._selectedId = null;
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
      this._pushUndo(this._ideaText(id), () =>
        this._hass.callService("brainstorm", "update_idea", { id, status: "active" })
      );
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
    setLanguage(hass);
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
    const defaultList = ["Inbox"];
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
      { value: "all", label: t("🌟 Alle Kategorien (Gesamtübersicht)") },
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
        label: t("Mindmap-Titel"),
        default: "Brainstorm Mindmap",
        selector: { text: {} },
      },
      {
        name: "sensor",
        label: t("Sensor-Entität"),
        default: "sensor.brainstorm_ideen_ubersicht",
        selector: { entity: { domain: ["sensor"] } },
      },
      {
        name: "show_last_alexa",
        label: t("Zuletzt aktive Alexa (Last Alexa) anzeigen"),
        default: false,
        selector: { boolean: {} },
      },
      {
        name: "last_alexa_entity",
        label: t("Last Alexa Entität (Echo / Sensor)"),
        default: "sensor.last_alexa",
        selector: { entity: { domain: ["sensor", "media_player"] } },
      },
      {
        name: "color_mode",
        label: t("Standard-Farbmodus"),
        default: "theme",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "theme", label: t("🎨 Theme-Farben (Dynamisch nach Home Assistant Theme)") },
              { value: "multicolor", label: t("🌈 Bunt (Multicolor-Kategoriefarben)") },
            ],
          },
        },
      },
      {
        name: "map_template",
        label: t("Vorlage für das Aussehen"),
        default: "standard",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "standard", label: t("Standard: Karten, Kurven, Kategoriefarben") },
              { value: "clean", label: t("Klar: Rechtecke, eckige Linien") },
              { value: "sketch", label: t("Skizze: Kapseln, gestrichelt, Pastell") },
              { value: "neon", label: t("Neon: dunkel und leuchtend") },
            ],
          },
        },
      },
      {
        name: "node_shape",
        label: t("Form der Notizen"),
        default: "template",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "template", label: t("Wie die Vorlage") },
              ...NODE_SHAPES.map((shape) => ({ value: shape, label: shapeLabel(shape) })),
            ],
          },
        },
      },
      {
        name: "voice_bubbles",
        label: t("Sprachnotizen als Sprechblase zeigen"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "line_style",
        label: t("Linien"),
        default: "template",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "template", label: t("Wie die Vorlage") },
              { value: "curve", label: t("Kurve") },
              { value: "straight", label: t("Gerade") },
              { value: "angled", label: t("Eckig") },
              { value: "dashed", label: t("Gestrichelt") },
            ],
          },
        },
      },
      {
        name: "color_scheme",
        label: t("Farbschema"),
        default: "template",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "template", label: t("Wie die Vorlage") },
              { value: "category", label: t("Kategoriefarben") },
              { value: "pastel", label: t("Pastell") },
              { value: "mono", label: t("Einfarbig") },
              { value: "neon", label: t("Neon") },
            ],
          },
        },
      },
      {
        name: "height",
        label: t("Höhe der Mindmap (z.B. 600px, 75vh, calc(100vh - 32px))"),
        default: "calc(100vh - 32px)",
        selector: { text: {} },
      },
      {
        name: "default_category",
        label: t("Standard-Kategorie im Fokus"),
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
        label: t("Leuchtende Glühbirne im Zentrum als Wasserzeichen anzeigen"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_grid",
        label: t("Punktraster im Hintergrund anzeigen"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_logo",
        label: t("Brainstorm Logo in Toolbar anzeigen"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_toolbar",
        label: t("Obere Werkzeugleiste (Titel & Filter-Pills) anzeigen"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "hide_empty_categories",
        label: t("Kategorien ohne Notizen (0) ausblenden"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_color_toggle",
        label: t("Farbmodus-Umschalter (🎨/🌈) in Toolbar anzeigen"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_fullscreen_btn",
        label: t("Vollbild-Schaltfläche (⛶) anzeigen"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_controls",
        label: t("Zoom- & Zentrieren-Schaltflächen anzeigen"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_export_btn",
        label: t("Schaltfläche zum Speichern als Bild (🖼️) anzeigen"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_add_btn",
        label: t("Neue Notiz-Schaltfläche (+ Idee) anzeigen"),
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
          <img src="${BULB_URL}" alt="Brainstorm" onerror="this.style.display='none'" />
          <span>${t("Brainstorm Mindmap – Visuelle Kartenkonfiguration")}</span>
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
          <label class="fallback-label">${t("Mindmap-Titel")}</label>
          <input class="fallback-input" id="fbTitle" type="text" value="${this._config.title || 'Brainstorm Mindmap'}" />
        </div>
        <div class="fallback-row">
          <label class="fallback-label">${t("Sensor-Entität")}</label>
          <input class="fallback-input" id="fbSensor" type="text" value="${this._config.sensor || 'sensor.brainstorm_ideen_ubersicht'}" />
        </div>
        <div class="fallback-row">
          <label class="fallback-label" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" id="fbShowLastAlexa" ${this._config.show_last_alexa ? 'checked' : ''} />
            <span>${t("Zuletzt aktive Alexa (Last Alexa) anzeigen")}</span>
          </label>
        </div>
        <div class="fallback-row">
          <label class="fallback-label">${t("Last Alexa Entität")}</label>
          <input class="fallback-input" id="fbLastAlexaEntity" type="text" value="${this._config.last_alexa_entity || 'sensor.last_alexa'}" />
        </div>
        <div class="fallback-row">
          <label class="fallback-label">${t("Standard-Kategorie im Fokus")}</label>
          <select class="fallback-select" id="fbDefaultCat">
            ${this._getCategoryOptions().map(o => `<option value="${this._escapeHtml(o.value)}" ${(this._config.default_category || 'all') === o.value ? 'selected' : ''}>${this._escapeHtml(o.label)}</option>`).join("")}
          </select>
        </div>
        <div class="fallback-row">
          <label class="fallback-label">${t("Farbmodus")}</label>
          <select class="fallback-select" id="fbColorMode">
            <option value="theme" ${(this._config.color_mode || 'theme') === 'theme' ? 'selected' : ''}>${t("🎨 Theme-Farben")}</option>
            <option value="multicolor" ${this._config.color_mode === 'multicolor' ? 'selected' : ''}>${t("🌈 Bunt (Multicolor)")}</option>
          </select>
        </div>
        <div class="fallback-row">
          <label class="fallback-label" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" id="fbShowLogo" ${this._config.show_logo !== false ? 'checked' : ''} />
            <span>${t("Brainstorm Logo in Toolbar anzeigen")}</span>
          </label>
        </div>
        <div class="fallback-row">
          <label class="fallback-label" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" id="fbHideEmpty" ${this._config.hide_empty_categories ? 'checked' : ''} />
            <span>${t("Kategorien ohne Notizen (0) ausblenden")}</span>
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
    description: t("Interaktive Mindmap-Darstellung für deine Brainstorm Hub Notizen und Ideen."),
    preview: true,
    documentationURL: "https://github.com/nukleuz80/ha_brainstorm",
  });
}

console.info(
  "%c BRAINSTORM-MINDMAP-CARD %c v1.7.22 ",
  "color: #07070e; background: #00f5ff; font-weight: bold; border-radius: 4px 0 0 4px; padding: 2px 4px;",
  "color: #ffffff; background: #9d4edd; font-weight: bold; border-radius: 0 4px 4px 0; padding: 2px 4px;"
);
