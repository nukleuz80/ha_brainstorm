import { LEVEL_CSS, SOCIAL_CSS, commentBadge, renderComments, needsPersonalData, reactionBadges, voteBadge, voteTotal, addMoreFields, levelAllows, levelLabel, uiLevel, BOARDS, MARKERS, NODE_SHAPES, NUMBERING, parentOptions, shapeLabel, sortChoices, repeatBadge, repeatOptions, attachmentUrl, coverAttachment, RULE_COLORS, filterToRule, loadRules, ruleFor, ruleSummary, saveRules, boardColumnOf, boardColumns, boardDrop, contentTemplates, alexaEchos, attachmentBadge, blockedBadge, dateLocale, dueFromInputValues, dueInputFormat, dueInputValues, emptyFilter, filterActive, formatDueInput, formatText, ideaMarkers, ideaMatches, ideaTags, inProgressBadge, markerBadges, markerIcon, markerLabel, nextProgress, numberingLabel, numberLabels, outlineFreemind, outlineMarkdown, outlineOpml, outlinePdf, minimapFrame, minimapToMap, parseDueInput, progressBadge, renderAttachments, setLanguage, shortDate, t } from "./brainstorm-i18n.js?v=1.11.10";

/**
 * Brainstorm Hub - Interactive Mindmap Card
 * Version: 1.11.10 - Aufgaben aus Sensoren
 * 
 * An interactive, visual mindmap for Home Assistant ideas and brainstorm notes.
 * Minimalist UI / Mushroom-inspired theme styling.
 */

// Folded branches of the mind map, kept per device
const COLLAPSED_KEY = "brainstorm_mindmap_collapsed";
const LAYOUT_KEY = "brainstorm_mindmap_layout";
const LAYOUTS = ["radial", "tree", "org", "outline", "pin", "kanban", "timeline", "matrix"];
// Pen colours and widths for drawing on the map
const DRAW_COLORS = { red: "#e53935", orange: "#fb8c00", green: "#43a047", blue: "#1e88e5", purple: "#8e24aa", gray: "#78909c" };
const DRAW_WIDTHS = [2, 4, 8];
const DRAW_MAX_POINTS = 400;

// Fewer points along a pen stroke, its shape stays (Ramer-Douglas-Peucker)
function simplifyStroke(points, tolerance = 1.5) {
  if (points.length < 3) return points;
  const keep = new Array(points.length).fill(false);
  keep[0] = keep[points.length - 1] = true;
  const stack = [[0, points.length - 1]];
  while (stack.length) {
    const [first, last] = stack.pop();
    const [ax, ay] = points[first];
    const [bx, by] = points[last];
    const len = Math.hypot(bx - ax, by - ay) || 1;
    let worst = 0;
    let index = -1;
    for (let i = first + 1; i < last; i++) {
      const [x, y] = points[i];
      const dist = Math.abs((bx - ax) * (ay - y) - (ax - x) * (by - ay)) / len;
      if (dist > worst) {
        worst = dist;
        index = i;
      }
    }
    if (index > 0 && worst > tolerance) {
      keep[index] = true;
      stack.push([first, index], [index, last]);
    }
  }
  let result = points.filter((_, i) => keep[i]);
  if (result.length > DRAW_MAX_POINTS) {
    const step = result.length / DRAW_MAX_POINTS;
    result = Array.from({ length: DRAW_MAX_POINTS - 1 }, (_, i) => result[Math.floor(i * step)]).concat([result[result.length - 1]]);
  }
  return result;
}

// How far a point is from a drawn stroke, arrow or ellipse
function strokeDistance(points, kind, x, y) {
  if (kind === "ellipse") {
    const [[x1, y1], [x2, y2]] = points;
    const rx = Math.max(Math.abs(x2 - x1) / 2, 1);
    const ry = Math.max(Math.abs(y2 - y1) / 2, 1);
    const nx = (x - (x1 + x2) / 2) / rx;
    const ny = (y - (y1 + y2) / 2) / ry;
    return Math.abs(Math.hypot(nx, ny) - 1) * Math.min(rx, ry);
  }
  let best = Infinity;
  for (let i = 0; i < points.length - 1; i++) {
    const [ax, ay] = points[i];
    const [bx, by] = points[i + 1];
    const dx = bx - ax;
    const dy = by - ay;
    const t = dx || dy ? Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy))) : 0;
    best = Math.min(best, Math.hypot(x - (ax + t * dx), y - (ay + t * dy)));
  }
  return best;
}
// Sticky note colours of the pinboard; a note without one is yellow
const PIN_COLORS = { yellow: "#fff59d", pink: "#f8bbd0", green: "#c5e1a5", blue: "#b3e5fc", orange: "#ffcc80", purple: "#d1c4e9" };
// The level a view needs; the round map is there for everyone
const LAYOUT_LEVELS = { tree: "normal", outline: "normal", pin: "normal", kanban: "normal", org: "pro", timeline: "pro", matrix: "pro" };
const UNDO_LIMIT = 30;

// The bulb lies next to this file, wherever Home Assistant serves it from
const MINIMAP_KEY = "brainstorm_minimap";
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
  show_filter: true,
  show_images: true,
  show_minimap: true,
  hide_empty_categories: true,
  layout: "radial",
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
// Shapes CSS cannot draw get an SVG outline behind the note
const SVG_SHAPES = ["cloud", "bubble", "thought", "ellipse", "hexagon", "note"];
// Shapes that point to their parent and need a new outline when it moves
const POINTING_SHAPES = ["bubble", "thought"];

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
    let savedLayout = null;
    try {
      savedLayout = localStorage.getItem(LAYOUT_KEY);
    } catch {}
    this._savedLayout = LAYOUTS.includes(savedLayout) ? savedLayout : null;
    // Minimap open or closed, remembered per browser; null until chosen
    this._minimapOpen = null;
    try {
      const savedMinimap = localStorage.getItem(MINIMAP_KEY);
      if (savedMinimap === "1" || savedMinimap === "0") this._minimapOpen = savedMinimap === "1";
    } catch {}
    this._minimapRects = [];
    this._scale = 1;
    this._panX = 0;
    this._panY = 0;
    this._isPanning = false;
    this._startPan = { x: 0, y: 0 };
    this._nodePositions = new Map(); // id -> {x, y}
    this._userMovedNodes = new Set();
    // Positions just placed by hand, until Home Assistant sends them back
    this._mapPosOverrides = new Map(); // id -> {x, y} relative to the center, or null
    this._pinOverrides = new Map(); // id -> pinboard place just set here, or null
    this._strokes = []; // drawn on the map of the shown category
    // Who else has a map open; this card is one of them under its token
    this._presenceToken = Math.random().toString(36).slice(2, 12).padEnd(8, "0");
    this._presenceSub = null;
    this._present = [];
    this._presenceEditing = null;
    this._presenceSent = "";
    this._strokesKey = null;
    this._drawMode = false;
    this._drawTool = "pen";
    this._drawColor = "red";
    this._drawWidth = 4;
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
    // Search and filter: hits stay bright, the rest of the map fades
    this._filter = emptyFilter();
    this._filterOpen = false;
    this._filterHits = null; // Set of ids while a filter is on
    this._filterContext = new Set(); // parents of hits, half faded
    this._hitIndex = -1;
    // Rules paint fitting notes with a color and a sign, like SmartRules
    this._rules = [];
    this._rulesLoaded = false;
    this._onRulesChanged = (e) => {
      this._rules = (e.detail && e.detail.rules) || [];
      this._applyRules();
    };
  }

  connectedCallback() {
    window.addEventListener("brainstorm-rules-changed", this._onRulesChanged);
    if (this._hass) this._joinPresence();
  }

  disconnectedCallback() {
    window.removeEventListener("brainstorm-rules-changed", this._onRulesChanged);
    this._leavePresence();
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

    const filterBtn = this.shadowRoot.getElementById("filterBtn");
    if (filterBtn) filterBtn.style.display = this._config.show_filter === true ? "inline-flex" : "none";
    if (this._config.show_filter !== true && this._filterOpen) this._setFilterOpen(false);

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
    this._joinPresence();
    if (!this._rulesLoaded) {
      this._rulesLoaded = true;
      loadRules(hass).then((rules) => {
        this._rules = rules;
        this._applyRules();
      });
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
    if (!state || !needsPersonalData(state.attributes)) return state;
    // With private ideas or a running vote, the sensor holds no ideas and the user's own come separately
    return {
      ...state,
      last_updated: `${state.last_updated}_${this._privateVersion || 0}`,
      attributes: { ...state.attributes, ...(this._privateData || {}) },
    };
  }

  _refreshPrivateData() {
    const state = this._getRawSensorEntity();
    if (!state || !needsPersonalData(state.attributes)) return;
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
        ${LEVEL_CSS}
        ${SOCIAL_CSS}
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
          /* Categories get their own row, so many of them never cover the
             title or the buttons on the right */
          flex-wrap: wrap;
          row-gap: 8px;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
        }
        .top-left {
          display: flex;
          align-items: center;
          gap: 8px;
          flex: 1 1 0;
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
        ha-card.is-fullscreen ~ .dialog-backdrop {
          padding-top: max(8px, env(safe-area-inset-top)) !important;
          padding-bottom: max(8px, env(safe-area-inset-bottom)) !important;
        }
        ha-card.is-fullscreen ~ .dialog-backdrop .dialog-box {
          max-height: calc(100dvh - max(8px, env(safe-area-inset-top)) - max(8px, env(safe-area-inset-bottom))) !important;
        }
        .pills-container {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 6px;
          order: 3;
          flex: 1 0 100%;
          min-width: 0;
          max-width: none;
          padding: 2px 0;
        }
        .pills-container .cat-pill {
          flex-shrink: 0;
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
            flex-wrap: nowrap;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
          }
          .pills-container::-webkit-scrollbar {
            display: none;
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
        .map-preview .suggest-row[data-depth="0"] .suggest-text {
          font-weight: 600;
        }
        .map-preview .suggest-row.off .suggest-text {
          opacity: 0.45;
        }
        .map-preview {
          /* The dialog body holds 70vh, so the buttons below stay in view */
          max-height: max(140px, calc(70vh - 220px));
          overflow-y: auto;
        }
        .empty-ai-btn {
          pointer-events: auto;
          margin-top: 12px;
          min-height: 40px;
          padding: 8px 16px;
          border-radius: 20px;
          border: 1px solid var(--primary-color, #03a9f4);
          background: transparent;
          color: var(--primary-color, #03a9f4);
          font: inherit;
          font-weight: 600;
          cursor: pointer;
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
        .presence-bar {
          display: none;
          position: absolute;
          top: 10px;
          left: 12px;
          z-index: 25;
          pointer-events: auto;
        }
        .presence-bar.open {
          display: flex;
        }
        .presence-avatar {
          width: 32px;
          height: 32px;
          margin-left: -6px;
          border-radius: 50%;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: 700;
          color: #fff;
          background: var(--person-color, #607d8b);
          border: 2px solid var(--ha-card-background, var(--card-background-color, #fff));
          box-sizing: border-box;
          cursor: default;
        }
        .presence-avatar:first-child {
          margin-left: 0;
        }
        .presence-avatar.editing {
          box-shadow: 0 0 0 2px var(--person-color, #607d8b);
        }
        .presence-more {
          background: var(--secondary-background-color, #e0e0e0);
          color: var(--primary-text-color);
        }
        .presence-tag {
          position: absolute;
          bottom: -10px;
          left: 10px;
          max-width: 70%;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          padding: 1px 8px;
          border-radius: 10px;
          font-size: 11px;
          font-weight: 600;
          color: #fff;
          background: var(--person-color, #607d8b);
          pointer-events: none;
          z-index: 2;
        }
        svg.sketch-layer {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          overflow: visible;
          pointer-events: none;
          z-index: 30;
        }
        .sketch-capture {
          display: none;
          position: absolute;
          inset: 0;
          z-index: 40;
          cursor: crosshair;
          touch-action: none;
        }
        .canvas-area.draw-mode .sketch-capture {
          display: block;
        }
        .sketch-bar {
          display: none;
          position: absolute;
          top: 10px;
          left: 50%;
          transform: translateX(-50%);
          z-index: 45;
          max-width: calc(100% - 24px);
          box-sizing: border-box;
          flex-wrap: wrap;
          justify-content: center;
          align-items: center;
          gap: 6px 10px;
          padding: 6px 10px;
          border-radius: 14px;
          background: var(--ha-card-background, var(--card-background-color, #fff));
          border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.2));
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        }
        .canvas-area.draw-mode .sketch-bar {
          display: flex;
        }
        .sketch-group {
          display: flex;
          align-items: center;
          gap: 4px;
        }
        .sketch-btn {
          min-width: 36px;
          height: 36px;
          border-radius: 10px;
          border: 1px solid transparent;
          background: transparent;
          color: var(--primary-text-color);
          font-size: 17px;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 0 6px;
        }
        .sketch-btn.active {
          border-color: var(--primary-color, #03a9f4);
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 15%, transparent);
        }
        .sketch-width span {
          display: block;
          width: 20px;
          border-radius: 4px;
          background: var(--primary-text-color);
        }
        .sketch-done {
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #fff);
        }
        .sketch-color {
          width: 26px;
          height: 26px;
          border-radius: 50%;
          border: 2px solid transparent;
          background: var(--sketch-color);
          cursor: pointer;
          padding: 0;
        }
        .sketch-color.active {
          border-color: var(--primary-text-color);
          box-shadow: 0 0 0 2px var(--ha-card-background, var(--card-background-color, #fff)) inset;
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
        .bs-tag {
          display: inline-block;
          padding: 0 6px;
          border-radius: 9px;
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 14%, transparent);
          color: var(--primary-color, #03a9f4);
          font-size: 0.88em;
          font-weight: 600;
          line-height: 1.5;
          cursor: pointer;
          white-space: nowrap;
        }
        .bs-tag:hover {
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 26%, transparent);
        }
        /* Search and filter */
        .filter-bar {
          flex: 0 0 auto;
          display: none;
          align-items: center;
          gap: 8px;
          padding: 6px 12px;
          z-index: 19;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
        }
        .filter-bar.open {
          display: flex;
        }
        .focus-bar {
          flex: 0 0 auto;
          display: none;
          align-items: center;
          flex-wrap: wrap;
          gap: 4px;
          padding: 4px 12px;
          z-index: 18;
          font-size: 0.82rem;
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 8%, var(--ha-card-background, var(--card-background-color, #ffffff)));
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
        }
        .focus-bar.open {
          display: flex;
        }
        .focus-crumb {
          min-height: 32px;
          padding: 0 8px;
          border: none;
          border-radius: 8px;
          background: transparent;
          color: var(--primary-color, #03a9f4);
          font: inherit;
          cursor: pointer;
        }
        .focus-crumb:hover {
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 12%, transparent);
        }
        .focus-crumb.current {
          display: inline-flex;
          align-items: center;
          color: var(--primary-text-color, #212121);
          font-weight: 600;
          cursor: default;
        }
        .focus-sep {
          color: var(--secondary-text-color, #727272);
        }
        .focus-close {
          margin-left: auto;
          min-width: 32px;
          min-height: 32px;
          border: none;
          border-radius: 50%;
          background: transparent;
          color: var(--secondary-text-color, #727272);
          cursor: pointer;
        }
        .center-node.focused {
          cursor: zoom-out;
        }
        .filter-search {
          flex: 0 1 260px;
          min-width: 140px;
          display: flex;
          align-items: center;
          gap: 6px;
          height: 34px;
          padding: 0 10px;
          border-radius: 17px;
          border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.25));
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.06));
          font-size: 0.85rem;
        }
        .filter-search:focus-within {
          border-color: var(--primary-color, #03a9f4);
        }
        .filter-search input {
          flex: 1 1 auto;
          min-width: 0;
          border: none;
          outline: none;
          background: transparent;
          color: var(--primary-text-color, #212121);
          font: inherit;
          font-size: 16px;
        }
        .filter-chips {
          flex: 1 1 auto;
          min-width: 0;
          display: flex;
          align-items: center;
          gap: 6px;
          overflow-x: auto;
          scrollbar-width: none;
        }
        .filter-chips::-webkit-scrollbar {
          display: none;
        }
        .filter-chip {
          flex: 0 0 auto;
          height: 30px;
          padding: 0 10px;
          border-radius: 15px;
          border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.25));
          background: transparent;
          color: var(--primary-text-color, #212121);
          font-size: 0.8rem;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 4px;
          white-space: nowrap;
        }
        .filter-chip.on {
          background: var(--primary-color, #03a9f4);
          border-color: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
        }
        .filter-chip-count {
          opacity: 0.65;
          font-size: 0.72rem;
        }
        .filter-sep {
          flex: 0 0 1px;
          height: 18px;
          background: var(--divider-color, rgba(127, 127, 127, 0.25));
        }
        .filter-count {
          flex: 0 0 auto;
          font-size: 0.78rem;
          color: var(--secondary-text-color, #727272);
          white-space: nowrap;
        }
        .filter-close {
          flex: 0 0 auto;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          border: none;
          background: transparent;
          color: var(--secondary-text-color, #727272);
          cursor: pointer;
          font-size: 0.95rem;
        }
        .filter-close:hover {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
        }
        .top-tool-btn.filter-on {
          background: var(--primary-color, #03a9f4);
          border-color: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
        }
        .note-cloud.filter-out {
          opacity: 0.16;
          filter: grayscale(0.7);
        }
        .note-cloud.filter-context {
          opacity: 0.55;
        }
        .note-cloud.rule-hit {
          --cat-color: var(--rule-color);
          border-color: color-mix(in srgb, var(--rule-color) 55%, transparent);
          border-left-color: var(--rule-color);
          background: color-mix(in srgb, var(--rule-color) 12%, var(--ha-card-background, var(--card-background-color, #ffffff)));
        }
        #notesContainer .note-cloud.rule-hit {
          border-left-color: var(--rule-color) !important;
        }
        .repeat-badge {
          display: inline-flex;
          align-items: center;
          font-size: 0.7rem;
        }
        .dialog-original-row {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 8px;
        }
        .dialog-original-text {
          flex: 1 1 180px;
          color: var(--secondary-text-color);
        }
        .dialog-original-row .dialog-btn {
          min-height: 44px;
        }
        .cloud-image {
          height: 110px;
          margin: 6px 0 4px;
          border-radius: 10px;
          overflow: hidden;
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
          cursor: zoom-in;
        }
        .cloud-image img {
          display: block;
          width: 100%;
          height: 100%;
          object-fit: cover;
          pointer-events: none;
        }
        .cloud-image.broken {
          display: none;
        }
        .rule-badge {
          position: absolute;
          top: -11px;
          left: -9px;
          min-width: 22px;
          height: 22px;
          padding: 0 3px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border-radius: 11px;
          font-size: 0.8rem;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border: 1px solid var(--rule-color, var(--divider-color));
          box-shadow: 0 1px 4px rgba(0, 0, 0, 0.18);
          pointer-events: none;
          z-index: 2;
        }
        .filter-rules {
          flex: 0 0 auto;
          min-width: 36px;
          min-height: 36px;
          border: none;
          border-radius: 50%;
          background: transparent;
          font-size: 1rem;
          cursor: pointer;
        }
        .filter-rules:hover {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.15));
        }
        .rule-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 12px;
        }
        .rule-row {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 10px;
          border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.25));
          border-left: 5px solid var(--rule-color, var(--divider-color));
          border-radius: 10px;
        }
        .rule-row.off {
          opacity: 0.5;
        }
        .rule-main {
          flex: 1;
          min-width: 0;
        }
        .rule-name {
          font-weight: 600;
        }
        .rule-when {
          font-size: 0.8rem;
          color: var(--secondary-text-color);
          overflow-wrap: anywhere;
        }
        .rule-row button {
          min-width: 34px;
          min-height: 34px;
          border: none;
          border-radius: 8px;
          background: transparent;
          color: var(--primary-text-color);
          cursor: pointer;
          font-size: 0.95rem;
        }
        .rule-row button:hover {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.15));
        }
        .rule-swatches {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin: 6px 0 12px;
        }
        .rule-swatch {
          width: 34px;
          height: 34px;
          border-radius: 50%;
          border: 2px solid transparent;
          background: var(--swatch);
          cursor: pointer;
          font-size: 0.9rem;
          color: var(--primary-text-color);
        }
        .rule-swatch.none {
          background: transparent;
          border-color: var(--divider-color);
        }
        .rule-swatch.icon {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
        }
        .rule-swatch.active {
          border-color: var(--primary-text-color);
          box-shadow: 0 0 0 2px var(--primary-color);
        }
        .note-cloud.filter-hit {
          filter: drop-shadow(0 0 6px color-mix(in srgb, var(--primary-color, #03a9f4) 70%, transparent));
        }
        .note-cloud.filter-hidden-hits .branch-toggle {
          background: var(--primary-color, #03a9f4);
          border-color: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
        }
        .synapse-path.filter-out {
          stroke-opacity: 0.08;
        }
        @media (max-width: 600px) {
          .filter-bar {
            flex-wrap: wrap;
            row-gap: 6px;
          }
          .filter-search {
            flex: 1 1 0;
          }
          .filter-chips {
            order: 3;
            flex: 1 0 100%;
          }
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
        .storm-head {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 10px;
          flex-wrap: wrap;
          margin-bottom: 6px;
        }
        .storm-times {
          flex: 1 1 220px;
          grid-template-columns: repeat(5, minmax(0, 1fr));
        }
        .storm-clock {
          font-size: 1.9rem;
          font-weight: 800;
          font-variant-numeric: tabular-nums;
          color: var(--primary-color, #03a9f4);
          min-width: 88px;
          text-align: right;
        }
        .storm-clock.storm-late {
          color: var(--warning-color, #ffa600);
        }
        .storm-clock.storm-over {
          color: var(--error-color, #db4437);
          animation: storm-pulse 0.9s ease-in-out 3;
        }
        @keyframes storm-pulse {
          50% { transform: scale(1.12); }
        }
        .storm-input-row {
          display: flex;
          gap: 8px;
          margin: 10px 0 6px;
        }
        .storm-input {
          flex: 1;
          min-height: 46px;
          font-size: 1.05rem;
        }
        .storm-count {
          font-size: 0.8rem;
          font-weight: 600;
          color: var(--secondary-text-color, #727272);
          min-height: 1em;
        }
        .storm-notes {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          padding: 8px 2px 4px;
          max-height: 260px;
          overflow-y: auto;
        }
        .storm-note {
          position: relative;
          width: 132px;
          min-height: 64px;
          padding: 10px 22px 10px 10px;
          box-sizing: border-box;
          font-size: 0.82rem;
          line-height: 1.3;
          color: #212121;
          background: var(--storm-color);
          border-radius: 3px 3px 12px 3px;
          box-shadow: 0 3px 8px rgba(0, 0, 0, 0.25);
          transform: rotate(var(--storm-tilt));
          overflow-wrap: break-word;
          hyphens: auto;
          animation: storm-in 0.25s ease-out;
        }
        @keyframes storm-in {
          from { transform: scale(0.6) rotate(0deg); opacity: 0; }
        }
        .storm-remove {
          position: absolute;
          top: 2px;
          right: 2px;
          width: 22px;
          height: 22px;
          border: none;
          background: transparent;
          color: rgba(0, 0, 0, 0.5);
          cursor: pointer;
          font-size: 0.75rem;
        }
        .export-row {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 8px;
          margin: 6px 0 12px;
        }
        .export-row .dialog-btn {
          min-height: 40px;
        }
        .outline-file {
          position: relative;
          overflow: hidden;
          display: inline-flex;
          align-items: center;
          gap: 6px;
        }
        .outline-file input {
          position: absolute;
          inset: 0;
          opacity: 0;
          cursor: pointer;
        }
        .export-row .outline-target {
          flex: 1 1 160px;
          margin: 0;
        }
        .dialog-textarea {
          width: 100%;
          box-sizing: border-box;
          resize: vertical;
          font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
          font-size: 0.8rem;
        }
        .cloud-number {
          font-weight: 700;
          color: var(--primary-color, #03a9f4);
          margin-right: 2px;
          font-variant-numeric: tabular-nums;
        }
        .note-cloud.is-blocked {
          filter: grayscale(0.7);
          opacity: 0.62;
        }
        .blocked-badge {
          display: inline-flex;
          align-items: center;
          gap: 3px;
          padding: 1px 5px;
          border-radius: 6px;
          font-size: 0.68rem;
          font-weight: 600;
          color: var(--error-color, #db4437);
          background: color-mix(in srgb, var(--error-color, #db4437) 12%, transparent);
        }
        .cloud-callout {
          position: absolute;
          bottom: calc(100% + 8px);
          right: -6px;
          max-width: 200px;
          padding: 5px 9px;
          border-radius: 10px;
          font-size: 0.74rem;
          line-height: 1.3;
          color: var(--primary-text-color, #212121);
          background: color-mix(in srgb, var(--warning-color, #ffa600) 18%, var(--ha-card-background, var(--card-background-color, #ffffff)));
          border: 1px solid color-mix(in srgb, var(--warning-color, #ffa600) 45%, transparent);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18);
          word-break: break-word;
          pointer-events: auto;
          z-index: 3;
        }
        .cloud-callout::after {
          content: "";
          position: absolute;
          top: 100%;
          right: 18px;
          border: 6px solid transparent;
          border-top-color: color-mix(in srgb, var(--warning-color, #ffa600) 45%, transparent);
        }
        .link-path {
          fill: none;
          stroke: var(--primary-color, #03a9f4);
          stroke-width: 1.8;
          stroke-dasharray: 6 4;
          stroke-opacity: 0.8;
        }
        .link-path.link-blocks {
          stroke: var(--error-color, #db4437);
        }
        .link-arrow {
          fill: var(--primary-color, #03a9f4);
        }
        .link-arrow.link-blocks {
          fill: var(--error-color, #db4437);
        }
        .link-hit {
          fill: none;
          stroke: transparent;
          stroke-width: 16;
          pointer-events: stroke;
          cursor: pointer;
        }
        .link-label {
          pointer-events: auto;
          cursor: pointer;
        }
        .link-label rect {
          fill: var(--ha-card-background, var(--card-background-color, #ffffff));
          stroke: var(--primary-color, #03a9f4);
          stroke-width: 1;
        }
        .link-label.link-blocks rect {
          stroke: var(--error-color, #db4437);
        }
        .link-label text {
          font-size: 11px;
          font-weight: 600;
          fill: var(--primary-text-color, #212121);
        }
        .board-rect {
          fill: var(--board-color);
          fill-opacity: 0.06;
          stroke: var(--board-color);
          stroke-opacity: 0.35;
          stroke-width: 1.5;
        }
        .board-label {
          font-size: 14px;
          font-weight: 700;
          fill: var(--primary-text-color, #212121);
        }
        .board-count {
          font-weight: 600;
          fill: var(--secondary-text-color, #727272);
        }
        .board-hint {
          font-size: 12px;
          fill: var(--secondary-text-color, #727272);
        }
        .canvas-area.board-mode .center-node,
        .canvas-area.board-mode .branch-toggle,
        .canvas-area.pin-mode .center-node,
        .canvas-area.pin-mode .branch-toggle {
          display: none;
        }
        .canvas-area.pin-mode .note-cloud {
          --primary-text-color: #2b2b2b;
          --secondary-text-color: #5f5f5f;
          color: #2b2b2b;
          background: var(--pin-bg, #fff59d) !important;
          border: none !important;
          border-radius: 3px !important;
          min-width: 150px;
          max-width: 210px;
          min-height: 84px;
          box-shadow: 0 8px 16px -6px rgba(0, 0, 0, 0.35) !important;
          rotate: var(--pin-tilt, 0deg);
        }
        .canvas-area.pin-mode .note-cloud.selected,
        .canvas-area.pin-mode .note-cloud.multi-selected {
          outline: 3px solid var(--primary-color, #03a9f4);
          outline-offset: 2px;
          rotate: 0deg;
        }
        .canvas-area.pin-mode .note-cloud .action-btn:not(.menu-item) {
          background: rgba(0, 0, 0, 0.07);
          border-color: rgba(0, 0, 0, 0.12);
          color: #2b2b2b;
        }
        .canvas-area.pin-mode .note-cloud .node-shape {
          display: none;
        }
        .canvas-area.pin-mode .note-cloud .cloud-menu {
          --primary-text-color: initial;
          --secondary-text-color: initial;
          color: var(--primary-text-color);
        }
        .menu-pins {
          display: flex;
          justify-content: space-between;
          gap: 6px;
          padding: 4px 6px 8px;
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
          margin-bottom: 4px;
        }
        .pin-swatch {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          border: 2px solid rgba(0, 0, 0, 0.15);
          background: var(--pin-bg);
          cursor: pointer;
          padding: 0;
        }
        .pin-swatch.active {
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 0 0 2px var(--primary-color, #03a9f4);
        }
        .present-bar {
          position: absolute;
          left: 50%;
          bottom: 16px;
          transform: translateX(-50%);
          width: min(760px, calc(100% - 32px));
          box-sizing: border-box;
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 12px;
          border-radius: 18px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color, #212121);
          box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
          z-index: 30;
        }
        .present-info {
          flex: 1;
          min-width: 0;
        }
        .present-step {
          font-size: 12px;
          color: var(--secondary-text-color, #727272);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .present-text {
          font-size: 18px;
          font-weight: 700;
          line-height: 1.3;
        }
        .present-desc {
          font-size: 14px;
          line-height: 1.4;
          color: var(--secondary-text-color, #727272);
          max-height: 4.2em;
          overflow: auto;
        }
        .present-btn {
          flex: none;
          width: 44px;
          height: 44px;
          border-radius: 50%;
          border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
          color: var(--primary-text-color, #212121);
          font-size: 22px;
          cursor: pointer;
        }
        .present-end {
          font-size: 16px;
        }
        ha-card.presenting .top-bar,
        ha-card.presenting .controls-panel,
        ha-card.presenting .add-note-btn,
        ha-card.presenting .minimap,
        ha-card.presenting .fullscreen-btn,
        ha-card.presenting .filter-bar,
        ha-card.presenting .selection-bar,
        ha-card.presenting .cloud-actions,
        ha-card.presenting .branch-toggle {
          display: none !important;
        }
        ha-card.presenting .viewport {
          transition: transform 0.45s ease;
        }
        ha-card.present-spot .note-cloud {
          opacity: 0.22;
          transition: opacity 0.3s ease;
        }
        ha-card.present-spot .note-cloud.present-near {
          opacity: 0.6;
        }
        ha-card.present-spot .note-cloud.present-current {
          opacity: 1;
          box-shadow: 0 0 0 3px var(--primary-color, #03a9f4), 0 10px 30px rgba(0, 0, 0, 0.35);
        }
        .sortin-text {
          flex: 1;
          font-size: 14px;
          line-height: 1.4;
        }
        .sortin-arrow {
          color: var(--secondary-text-color, #727272);
        }
        .template-chips {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-bottom: 8px;
        }
        .template-chip {
          min-height: 36px;
          padding: 6px 12px;
          border-radius: 18px;
          border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
          color: var(--primary-text-color, #212121);
          font: inherit;
          font-size: 13px;
          cursor: pointer;
        }
        .template-chip:hover {
          border-color: var(--primary-color, #03a9f4);
        }
        .layout-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 8px;
          margin-bottom: 12px;
        }
        .layout-choice {
          display: flex;
          align-items: center;
          gap: 10px;
          min-height: 48px;
          padding: 8px 12px;
          border-radius: 12px;
          border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
          color: var(--primary-text-color, #212121);
          font: inherit;
          font-size: 13px;
          text-align: left;
          cursor: pointer;
        }
        .layout-choice.active {
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 0 0 1px var(--primary-color, #03a9f4) inset;
        }
        .layout-icon {
          font-size: 20px;
          width: 24px;
          text-align: center;
        }
        .frame-rect {
          fill: var(--frame-color, var(--primary-color, #03a9f4));
          fill-opacity: 0.06;
          stroke: var(--frame-color, var(--primary-color, #03a9f4));
          stroke-width: 1.5;
          stroke-dasharray: 8 5;
        }
        .frame-label {
          font-size: 12px;
          font-weight: 700;
          fill: var(--frame-color, var(--primary-color, #03a9f4));
          pointer-events: auto;
          cursor: pointer;
        }
        .frame.filter-out,
        .link-path.filter-out,
        .link-label.filter-out {
          opacity: 0.2;
        }
        .canvas-area.linking,
        .canvas-area.linking .note-cloud {
          cursor: crosshair;
        }
        .note-cloud.link-source {
          outline: 2px dashed var(--primary-color, #03a9f4);
          outline-offset: 4px;
        }
        .dialog-check {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          margin: 12px 0 4px;
          font-size: 0.85rem;
          line-height: 1.35;
          color: var(--primary-text-color, #212121);
          cursor: pointer;
        }
        .dialog-check input {
          width: 18px;
          height: 18px;
          flex: none;
          margin-top: 1px;
        }
        .cloud-social {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 4px;
          margin: 2px 0 4px;
        }
        .menu-reactions {
          display: flex;
          justify-content: space-between;
          gap: 4px;
          padding: 4px 6px 6px;
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
          margin-bottom: 4px;
        }
        .vote-bar {
          flex: 0 0 auto;
          display: none;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
          padding: 4px 12px;
          z-index: 18;
          font-size: 0.82rem;
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 12%, var(--ha-card-background, var(--card-background-color, #ffffff)));
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
        }
        .vote-bar.open {
          display: flex;
        }
        .vote-bar .vote-info {
          flex: 1 1 auto;
        }
        .vote-bar button {
          min-height: 32px;
          padding: 0 12px;
          border-radius: 16px;
          border: 1px solid var(--primary-color, #03a9f4);
          background: transparent;
          color: var(--primary-color, #03a9f4);
          font: inherit;
          font-weight: 600;
          cursor: pointer;
        }
        .vote-rank {
          list-style: none;
          margin: 0 0 8px;
          padding: 0;
        }
        .vote-rank li {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 4px;
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
        }
        .vote-rank .rank-place {
          width: 28px;
          text-align: center;
          font-weight: 700;
        }
        .vote-rank .rank-text {
          flex: 1 1 auto;
        }
        .vote-rank .rank-points {
          font-weight: 700;
          color: var(--primary-color, #03a9f4);
          white-space: nowrap;
        }
        .vote-choices {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin: 6px 0 4px;
        }
        .cloud-marks {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 4px;
          margin-bottom: 4px;
        }
        .marker-badges {
          display: inline-flex;
          flex-wrap: wrap;
          gap: 2px;
        }
        .marker-badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-width: 22px;
          height: 22px;
          font-size: 0.9rem;
          line-height: 1;
          border-radius: 6px;
          cursor: pointer;
        }
        .marker-badge:hover {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
        }
        .progress-badge {
          display: inline-flex;
          align-items: center;
          gap: 3px;
          min-height: 22px;
          padding: 0 6px 0 3px;
          border-radius: 11px;
          font-size: 0.7rem;
          font-weight: 600;
          color: var(--secondary-text-color, #727272);
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
          cursor: pointer;
          font-variant-numeric: tabular-nums;
        }
        .progress-badge.progress-auto {
          cursor: default;
        }
        .progress-badge svg {
          flex: none;
        }
        .progress-track {
          fill: none;
          stroke: color-mix(in srgb, var(--secondary-text-color, #727272) 25%, transparent);
          stroke-width: 2.5;
        }
        .progress-fill {
          fill: none;
          stroke: var(--cat-color, var(--primary-color, #03a9f4));
          stroke-width: 2.5;
          stroke-linecap: round;
        }
        .progress-badge.progress-full {
          color: var(--success-color, #4caf50);
        }
        .progress-full .progress-fill {
          stroke: var(--success-color, #4caf50);
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
        /* Done, subidea, edit and ⋯; the rest waits in the menu */
        .cloud-actions {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          justify-content: flex-end;
          gap: 6px;
          max-width: 100%;
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
        .action-btn.more-btn {
          font-size: 1rem;
          font-weight: 700;
          line-height: 1;
        }
        .note-cloud.menu-open {
          z-index: 40 !important;
        }
        .note-cloud.menu-open .cloud-actions {
          opacity: 1;
        }
        .note-cloud.menu-open .more-btn {
          background: var(--primary-color, #03a9f4);
          border-color: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
        }
        .cloud-menu {
          display: none;
          position: absolute;
          top: calc(100% + 6px);
          right: 0;
          z-index: 41;
          min-width: 200px;
          max-width: 260px;
          padding: 4px;
          flex-direction: column;
          gap: 2px;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
          border-radius: 12px;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
          cursor: default;
        }
        .note-cloud.menu-open .cloud-menu {
          display: flex;
        }
        .note-cloud.menu-up .cloud-menu {
          top: auto;
          bottom: calc(100% + 6px);
        }
        .note-cloud.menu-left .cloud-menu {
          right: auto;
          left: 0;
        }
        .cloud-menu .action-btn.menu-item {
          width: 100%;
          height: auto;
          min-height: 40px;
          padding: 6px 10px;
          gap: 10px;
          justify-content: flex-start;
          text-align: left;
          border: none;
          border-radius: 8px;
          background: transparent;
          color: var(--primary-text-color, #212121);
          font-size: 0.85rem;
          box-shadow: none;
        }
        .cloud-menu .action-btn.menu-item > span {
          flex: none;
          width: 20px;
          text-align: center;
        }
        .cloud-menu .action-btn.menu-item:hover {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
          color: var(--primary-text-color, #212121);
          box-shadow: none;
        }
        .cloud-menu .action-btn.menu-item.del-btn {
          color: var(--error-color, #db4437);
        }
        .cloud-menu .action-btn.menu-item.del-btn:hover {
          background: color-mix(in srgb, var(--error-color, #db4437) 14%, transparent);
          color: var(--error-color, #db4437);
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

        /* Minimap (Bottom Left, above the add button) */
        .minimap {
          position: absolute;
          left: 16px;
          bottom: 64px;
          z-index: 24;
          width: 168px;
          height: 112px;
          display: none;
          border-radius: 10px;
          overflow: hidden;
          cursor: pointer;
          touch-action: none;
          background: color-mix(in srgb, var(--ha-card-background, var(--card-background-color, #ffffff)) 90%, transparent);
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.25)));
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }
        .minimap.open {
          display: block;
        }
        .minimap.no-add {
          bottom: 16px;
        }
        .minimap canvas {
          display: block;
          width: 100%;
          height: 100%;
        }
        @container (max-width: 600px) {
          .minimap {
            left: 10px;
            bottom: 52px;
            width: 120px;
            height: 80px;
          }
          .minimap.no-add {
            bottom: 10px;
          }
        }
        ha-card.is-fullscreen .minimap {
          left: max(10px, env(safe-area-inset-left));
          bottom: calc(58px + env(safe-area-inset-bottom));
        }
        ha-card.is-fullscreen .minimap.no-add {
          bottom: calc(10px + env(safe-area-inset-bottom));
        }
        #minimapBtn[aria-pressed="true"] {
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
        /* Fixed to the window like the list card, so a tall map never pushes
           the dialog or its buttons out of sight */
        .dialog-backdrop {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          height: 100dvh;
          z-index: 999999;
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
          max-height: calc(100dvh - 32px);
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
          min-height: 0;
          flex: 1 1 auto;
          overflow-y: auto;
          overscroll-behavior: contain;
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
          flex-wrap: wrap;
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
        .dialog-btn-danger {
          margin-right: auto;
          background: transparent;
          color: var(--error-color, #db4437);
          border-color: color-mix(in srgb, var(--error-color, #db4437) 45%, transparent);
        }
        .dialog-btn-danger:hover {
          background: color-mix(in srgb, var(--error-color, #db4437) 10%, transparent);
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
            <div class="title" id="cardTitle">${this._escapeHtml(this._config.title !== undefined ? this._config.title : "Brainstorm Mindmap")}</div>
            <div id="mindmapLastAlexaWrap" class="last-alexa-wrap" style="display: none;"></div>
          </div>
          <div class="pills-container" id="pillsBar"></div>
          <div class="top-right">
            <button class="top-tool-btn" id="colorModeBtn" style="display: ${this._config.show_color_toggle === true ? 'inline-flex' : 'none'};" title="${this._colorMode === 'theme' ? t("Farbmodus: Theme-Farben aktiv (Klicken für Bunt)") : t("Farbmodus: Bunt aktiv (Klicken für Theme-Farben)")}">
              ${this._colorMode === 'theme' ? '🎨' : '🌈'}
            </button>
            <button class="top-tool-btn" id="filterBtn" data-lvl="normal" style="display: ${this._config.show_filter === true ? 'inline-flex' : 'none'};" title="${t("Suchen und filtern (/)")}" aria-pressed="false">🔍</button>
            <button class="top-tool-btn" id="exportBtn" data-lvl="normal" style="display: ${this._config.show_export_btn === true ? 'inline-flex' : 'none'};" title="${t("Map speichern oder Gliederung einfügen")}">🖼️</button>
            <button class="fullscreen-btn" id="fullscreenToggleBtn" style="display: ${this._config.show_fullscreen_btn === true ? 'inline-flex' : 'none'};" title="${t("Vollbild umschalten (ESC zum Beenden)")}">⛶</button>
          </div>
        </div>

        <!-- Search and filter -->
        <div class="filter-bar" id="filterBar" role="search">
          <label class="filter-search">
            <span aria-hidden="true">🔍</span>
            <input id="filterInput" type="search" autocomplete="off" enterkeyhint="search" placeholder="${t("Suchen … (#tag)")}" aria-label="${t("Suchen")}" />
          </label>
          <div class="filter-chips" id="filterChips"></div>
          <span class="filter-count" id="filterCount" aria-live="polite"></span>
          <button class="filter-rules" id="filterRules" data-lvl="pro" title="${t("Regeln: passende Notizen färben (R)")}">🎨</button>
          <button class="filter-close" id="filterClose" title="${t("Filter zurücksetzen und schließen (ESC)")}">✕</button>
        </div>

        <!-- Path of a focused branch -->
        <nav class="focus-bar" id="focusBar" aria-label="${t("Fokus")}"></nav>
        <div class="vote-bar" id="voteBar" role="status" aria-live="polite"></div>

        <!-- Interactive Canvas Area -->
        <div class="canvas-area${this._isBoard() ? " board-mode" : ""}${this._isPinboard() ? " pin-mode" : ""}" id="canvasArea" tabindex="0">
          <div class="lasso-rect" id="lassoRect"></div>
          <div class="selection-bar" id="selectionBar" role="toolbar" aria-label="${t("Auswahl")}">
            <span class="selection-count" id="selectionCount"></span>
            <button class="selection-btn" data-multi="done" title="${t("Alle abhaken")}">✓<span class="selection-label">${t("Abhaken")}</span></button>
            <button class="selection-btn" data-multi="move" title="${t("Kategorie ändern")}">📁<span class="selection-label">${t("Kategorie")}</span></button>
            <button class="selection-btn" data-multi="frame" data-lvl="pro" title="${t("Rahmen um die Auswahl legen")}">▢<span class="selection-label">${t("Rahmen")}</span></button>
            <button class="selection-btn" data-multi="link" data-lvl="pro" title="${t("Die zwei ausgewählten Notizen verbinden")}">🔗<span class="selection-label">${t("Verbinden")}</span></button>
            <button class="selection-btn danger" data-multi="delete" title="${t("Löschen")}">🗑️<span class="selection-label">${t("Löschen")}</span></button>
            <button class="selection-btn" data-multi="clear" title="${t("Auswahl aufheben (ESC)")}">✕</button>
          </div>
          <div class="presence-bar" id="presenceBar" aria-live="polite"></div>
          <div class="sketch-capture" id="sketchCapture"></div>
          <div class="sketch-bar" id="sketchBar" role="toolbar" aria-label="${t("Zeichnen")}">
            <div class="sketch-group">
              <button class="sketch-btn" data-tool="pen" title="${t("Stift")}">🖊️</button>
              <button class="sketch-btn" data-tool="arrow" title="${t("Pfeil")}">➚</button>
              <button class="sketch-btn" data-tool="ellipse" title="${t("Kreis")}">◯</button>
              <button class="sketch-btn" data-tool="erase" title="${t("Radierer: Striche antippen")}">🧽</button>
            </div>
            <div class="sketch-group">
              ${Object.entries(DRAW_COLORS).map(([name, color]) => `<button class="sketch-color" data-color="${name}" style="--sketch-color: ${color};" aria-label="${t("Farbe")} ${name}"></button>`).join("")}
            </div>
            <div class="sketch-group">
              ${DRAW_WIDTHS.map((width) => `<button class="sketch-btn sketch-width" data-width="${width}" title="${t("Strichstärke")} ${width}"><span style="height: ${width}px;"></span></button>`).join("")}
            </div>
            <div class="sketch-group">
              <button class="sketch-btn" data-sketch="undo" title="${t("Rückgängig")}">↶</button>
              <button class="sketch-btn" data-sketch="clear" title="${t("Alles löschen")}">🗑️</button>
              <button class="sketch-btn sketch-done" data-sketch="done" title="${t("Fertig (Esc)")}">✓</button>
            </div>
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
            <svg class="sketch-layer" id="sketchLayer" aria-hidden="true"></svg>
            <div class="empty-state" id="emptyState" style="display: none;">
              ${t('Keine aktiven Notizen in dieser Kategorie.<br>Klicke unten links auf "+ Idee", um eine hinzuzufügen.')}
              <div><button class="empty-ai-btn" id="emptyAiBtn" data-lvl="normal" style="display: none;">✨ ${t("Map aus Thema erzeugen")}</button></div>
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
          <button class="control-btn" id="minimapBtn" data-lvl="normal" title="${t("Übersicht ein- oder ausblenden (M)")}" aria-pressed="false">🗺️</button>
          <button class="control-btn" id="lassoBtn" data-lvl="normal" title="${t("Auswählen: Rahmen um mehrere Notizen ziehen (oder Umschalt+Ziehen)")}" aria-pressed="false">⬚</button>
          <button class="control-btn" id="drawBtn" data-lvl="normal" title="${t("Zeichnen: Pfeile, Kreise und Skizzen auf der Map (D)")}" aria-pressed="false">🖍️</button>
          <button class="control-btn" id="layoutBtn" data-lvl="normal" title="${t("Ansicht wählen")}">${this._layoutIcon()}</button>
          <button class="control-btn" id="voteBtn" data-lvl="normal" title="${t("Abstimmen: Stimmen pro Person verteilen (V)")}">🗳️</button>
          <button class="control-btn" id="stormBtn" data-lvl="pro" title="${t("Brainstorm: schnell viele Ideen sammeln (B)")}">⚡</button>
          <button class="control-btn" id="levelsBtn" data-lvl="normal" title="${t("Ebenen zeigen: 1, 2, 3 oder alle (Tasten 1–9, 0 = alle)")}">∞</button>
          <button class="control-btn" id="arrangeBtn" data-lvl="normal" title="${t("Neu ordnen: von Hand verschobene Notizen wieder automatisch platzieren")}">🪄</button>
          <button class="control-btn" id="undoBtn" title="${t("Rückgängig (Strg+Z)")}" disabled>↶</button>
        </div>

        <!-- Bottom Left, above the add button: overview of the whole map -->
        <div class="minimap" id="minimap" role="button" aria-label="${t("Übersicht: tippen oder ziehen, um dorthin zu springen")}" title="${t("Übersicht: tippen oder ziehen, um dorthin zu springen")}">
          <canvas id="minimapCanvas"></canvas>
        </div>

        <div class="map-toast" id="mapToast" role="status" aria-live="polite"></div>

        <div class="present-bar" id="presentBar" style="display: none;">
          <button class="present-btn" id="presentPrev" title="${t("Zurück (←)")}">‹</button>
          <div class="present-info">
            <div class="present-step" id="presentStep"></div>
            <div class="present-text" id="presentText"></div>
            <div class="present-desc" id="presentDesc"></div>
          </div>
          <button class="present-btn" id="presentNext" title="${t("Weiter (→ oder Leertaste)")}">›</button>
          <button class="present-btn present-end" id="presentEnd" title="${t("Präsentation beenden (Esc)")}">✕</button>
        </div>

      </ha-card>

      <!-- Dialog outside the card: the card's containment would trap a fixed box -->
      <div class="dialog-backdrop" id="mindmapDialog" style="display: none;">
        <div class="dialog-box" id="dialogBox">
          <div class="dialog-header">
            <div class="dialog-title" id="dialogTitle">${t("Titel")}</div>
            <button class="dialog-close" id="dialogCloseBtn" title="${t("Schließen (ESC)")}">✕</button>
          </div>
          <div class="dialog-body" id="dialogBody"></div>
        </div>
      </div>
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
      if (!cardRoot || !fullscreenBtn) return;
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
    this._toggleFullscreen = toggleFullscreen;
    const presentBar = this.shadowRoot.getElementById("presentBar");
    if (presentBar) {
      this.shadowRoot.getElementById("presentPrev").addEventListener("click", () => this._presentStep(-1));
      this.shadowRoot.getElementById("presentNext").addEventListener("click", () => this._presentStep(1));
      this.shadowRoot.getElementById("presentEnd").addEventListener("click", () => this._endPresentation());
    }

    canvasArea.addEventListener("keydown", (e) => this._onMapKey(e));

    // A tap outside the open ⋯ menu closes it
    this.shadowRoot.addEventListener(
      "pointerdown",
      (e) => {
        if (!this._menuId) return;
        const inside = e.composedPath().some((el) => el.classList && (el.classList.contains("cloud-menu") || el.classList.contains("more-btn")));
        if (!inside) this._closeNodeMenu();
      },
      true
    );

    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        if (this._menuId) {
          this._closeNodeMenu();
        } else if (this._presentation && !this._isModalOpen) {
          this._endPresentation();
        } else if (this._isModalOpen) {
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
    const drawBtn = this.shadowRoot.getElementById("drawBtn");
    if (drawBtn) drawBtn.addEventListener("click", () => this._setDrawMode(!this._drawMode));
    this._bindSketch();
    this.shadowRoot.querySelectorAll(".selection-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const act = btn.getAttribute("data-multi");
        if (act === "done") this._completeSelected();
        else if (act === "move") this._showCategoryPicker([...this._multi]);
        else if (act === "frame") this._showFrameDialog(null, [...this._multi]);
        else if (act === "link") {
          const [from, to] = [...this._multi];
          this._clearMulti();
          if (from && to) {
            this._linkFrom = from;
            this._finishLink(to);
          }
        }
        else if (act === "delete") this._confirmDeleteSelected();
        else if (act === "clear") this._clearMulti();
      });
    });
    const arrangeBtn = this.shadowRoot.getElementById("arrangeBtn");
    if (arrangeBtn) arrangeBtn.addEventListener("click", () => this._arrangeAgain());
    const undoBtn = this.shadowRoot.getElementById("undoBtn");
    if (undoBtn) undoBtn.addEventListener("click", () => this._undo());
    // Links and frames are drawn on the line layer, a tap on them opens their dialog
    const connectors = this.shadowRoot.getElementById("connectorsLayer");
    if (connectors) {
      const hit = (e) => e.target.closest && e.target.closest("[data-link-from], [data-frame]");
      ["mousedown", "touchstart"].forEach((type) =>
        connectors.addEventListener(type, (e) => {
          if (hit(e)) e.stopPropagation();
        }, { passive: true }),
      );
      connectors.addEventListener("click", (e) => {
        const el = hit(e);
        if (!el) return;
        e.stopPropagation();
        if (el.hasAttribute("data-link-from")) this._showLinkDialog(el.getAttribute("data-link-from"), el.getAttribute("data-link-to"));
        else this._showFrameDialog(el.getAttribute("data-frame"), null);
      });
    }
    const stormBtn = this.shadowRoot.getElementById("stormBtn");
    if (stormBtn) stormBtn.addEventListener("click", () => this._showBrainstorm());
    const layoutBtn = this.shadowRoot.getElementById("layoutBtn");
    if (layoutBtn) {
      layoutBtn.addEventListener("click", () => {
        this._showLayoutDialog();
      });
    }
    const voteBtn = this.shadowRoot.getElementById("voteBtn");
    if (voteBtn) voteBtn.addEventListener("click", () => this._showVotingDialog());
    const emptyAiBtn = this.shadowRoot.getElementById("emptyAiBtn");
    if (emptyAiBtn) emptyAiBtn.addEventListener("click", () => this._showGenerateMapDialog());
    const voteBar = this.shadowRoot.getElementById("voteBar");
    if (voteBar) {
      voteBar.addEventListener("click", (e) => {
        const end = e.target.closest("[data-end-vote]");
        if (end) this._endVoting(end.getAttribute("data-end-vote"));
        const join = e.target.closest("[data-join-round]");
        if (join) {
          const category = join.getAttribute("data-join-round");
          if (this._selectedCategory !== category) {
            this._selectedCategory = category;
            this._focusId = null;
            this._saveSelectedCategory();
            this._nodePositions.clear();
            this._lastDataSignature = "";
            this._centerLayout(true);
            this._updateContent();
          }
          this._showBrainstorm();
        }
        const reveal = e.target.closest("[data-end-round]");
        if (reveal) this._endRound(reveal.getAttribute("data-end-round"));
      });
    }
    const minimapBtn = this.shadowRoot.getElementById("minimapBtn");
    if (minimapBtn) minimapBtn.addEventListener("click", () => this._toggleMinimap());
    const minimap = this.shadowRoot.getElementById("minimap");
    if (minimap) {
      minimap.addEventListener("pointerdown", (e) => {
        e.preventDefault();
        e.stopPropagation();
        try {
          minimap.setPointerCapture(e.pointerId);
        } catch {}
        this._minimapDrag = true;
        this._minimapJump(e);
      });
      minimap.addEventListener("pointermove", (e) => {
        if (this._minimapDrag) this._minimapJump(e);
      });
      const endDrag = () => {
        if (!this._minimapDrag) return;
        this._minimapDrag = false;
        this._drawMinimapSoon();
      };
      minimap.addEventListener("pointerup", endDrag);
      minimap.addEventListener("pointercancel", endDrag);
    }
    const levelsBtn = this.shadowRoot.getElementById("levelsBtn");
    if (levelsBtn) {
      levelsBtn.addEventListener("click", () => {
        const steps = [1, 2, 3, 0];
        const index = steps.indexOf(this._levels === undefined ? 0 : this._levels);
        this._showLevels(steps[(index + 1) % steps.length]);
      });
    }
    const exportBtn = this.shadowRoot.getElementById("exportBtn");
    if (exportBtn) exportBtn.addEventListener("click", () => this._showExportDialog());
    this._bindFilterEvents();
    this._updateUndoButton();

    // Quick Add -> Show Dialog Modal
    addNoteBtn.addEventListener("click", () => this._showAddDialog());

    // Center Node Click -> Cycle category
    centerNode.addEventListener("click", () => {
      // In a focused branch the center goes one level up
      if (this._focusId) {
        this._focusUp();
        return;
      }
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
      this._focusId = null;
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
    this._drawMinimapSoon();
  }

  // ---- Minimap: the whole map small, with the visible part as a frame ----

  _minimapWanted() {
    if (this._config.show_minimap === false) return false;
    if (this._minimapOpen !== null) return this._minimapOpen;
    // Not chosen yet: open on wide cards, closed on phones
    const canvasArea = this.shadowRoot && this.shadowRoot.getElementById("canvasArea");
    return Boolean(canvasArea && canvasArea.clientWidth >= 700);
  }

  _toggleMinimap() {
    this._minimapOpen = !this._minimapWanted();
    try {
      localStorage.setItem(MINIMAP_KEY, this._minimapOpen ? "1" : "0");
    } catch {}
    this._refreshMinimap();
  }

  // Measure the notes again, then draw (after a change of notes or filter)
  _refreshMinimap() {
    this._minimapMeasure = true;
    this._drawMinimapSoon();
  }

  _drawMinimapSoon() {
    if (this._minimapRaf || !this.shadowRoot) return;
    this._minimapRaf = requestAnimationFrame(() => {
      this._minimapRaf = null;
      if (this._minimapMeasure) {
        this._minimapMeasure = false;
        this._measureMinimap();
      }
      this._drawMinimap();
    });
  }

  // Boxes of the notes in map coordinates, with their colors
  _measureMinimap() {
    const sr = this.shadowRoot;
    const canvasArea = sr.getElementById("canvasArea");
    this._minimapRects = [];
    if (!canvasArea || !this._minimapWanted()) return;
    const base = canvasArea.getBoundingClientRect();
    const s = this._scale || 1;
    const toMap = (r) => ({
      x: (r.left - base.left - this._panX) / s,
      y: (r.top - base.top - this._panY) / s,
      w: r.width / s,
      h: r.height / s,
    });
    const color = (el, prop) => getComputedStyle(el).getPropertyValue(prop).trim();
    sr.querySelectorAll(".board-rect").forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.width) this._minimapRects.push({ ...toMap(r), color: color(el, "--board-color"), kind: "board" });
    });
    const centerNode = sr.getElementById("centerNode");
    if (centerNode && centerNode.offsetParent) {
      const r = centerNode.getBoundingClientRect();
      if (r.width) this._minimapRects.push({ ...toMap(r), color: color(centerNode, "--cat-color"), kind: "center" });
    }
    sr.querySelectorAll("#notesContainer .note-cloud:not(.draft)").forEach((el) => {
      const r = el.getBoundingClientRect();
      if (!r.width) return;
      this._minimapRects.push({
        ...toMap(r),
        color: color(el, "--cat-color"),
        kind: el.classList.contains("filter-out") ? "faded" : "note",
      });
    });
  }

  _drawMinimap() {
    const sr = this.shadowRoot;
    const box = sr.getElementById("minimap");
    const canvas = sr.getElementById("minimapCanvas");
    const canvasArea = sr.getElementById("canvasArea");
    const btn = sr.getElementById("minimapBtn");
    if (!box || !canvas || !canvasArea) return;
    const wanted = this._minimapWanted();
    if (btn) {
      btn.setAttribute("aria-pressed", wanted ? "true" : "false");
      btn.style.display = this._config.show_minimap === false ? "none" : "";
    }
    // Opened before anything was measured
    if (wanted && !this._minimapRects.length) this._measureMinimap();
    const rects = this._minimapRects;
    const show = wanted && rects.some((r) => r.kind === "note" || r.kind === "faded");
    box.classList.toggle("open", show);
    box.classList.toggle("no-add", this._config.show_add_btn !== true);
    if (!show) return;

    const w = box.clientWidth;
    const h = box.clientHeight;
    if (!w || !h) return;
    const dpr = window.devicePixelRatio || 1;
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
    }
    const s = this._scale || 1;
    const view = { x: -this._panX / s, y: -this._panY / s, w: canvasArea.clientWidth / s, h: canvasArea.clientHeight / s };
    // While dragging inside the minimap its scale stays put, so it does not run away
    const frame = this._minimapDrag && this._minimapFrame ? this._minimapFrame : minimapFrame(rects, view, w, h);
    this._minimapFrame = frame;

    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const primary = getComputedStyle(this).getPropertyValue("--primary-color").trim() || "#03a9f4";
    const box2d = (r) => {
      const x = frame.ox + r.x * frame.scale;
      const y = frame.oy + r.y * frame.scale;
      return [x, y, Math.max(2, r.w * frame.scale), Math.max(2, r.h * frame.scale)];
    };
    const alpha = { board: 0.14, faded: 0.22, center: 0.95, note: 0.85 };
    ["board", "faded", "note", "center"].forEach((kind) => {
      rects.forEach((r) => {
        if (r.kind !== kind) return;
        ctx.globalAlpha = alpha[kind];
        ctx.fillStyle = primary;
        if (r.color) ctx.fillStyle = r.color;
        const [x, y, bw, bh] = box2d(r);
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(x, y, bw, bh, Math.min(3, bw / 2, bh / 2));
        else ctx.rect(x, y, bw, bh);
        ctx.fill();
      });
    });
    const [vx, vy, vw, vh] = box2d(view);
    ctx.globalAlpha = 0.1;
    ctx.fillStyle = primary;
    ctx.fillRect(vx, vy, vw, vh);
    ctx.globalAlpha = 1;
    ctx.strokeStyle = primary;
    ctx.lineWidth = 1.5;
    ctx.strokeRect(vx + 0.75, vy + 0.75, Math.max(1, vw - 1.5), Math.max(1, vh - 1.5));
  }

  // Tap or drag on the minimap: that spot becomes the middle of the view
  _minimapJump(e) {
    const box = this.shadowRoot.getElementById("minimap");
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    if (!box || !canvasArea || !this._minimapFrame) return;
    const r = box.getBoundingClientRect();
    const p = minimapToMap(this._minimapFrame, e.clientX - r.left, e.clientY - r.top);
    this._panX = canvasArea.clientWidth / 2 - p.x * this._scale;
    this._panY = canvasArea.clientHeight / 2 - p.y * this._scale;
    this._applyTransform();
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
    return Boolean(this._selectedCategory) && this._selectedCategory !== "all" && !this._focusId && this._layout() === "radial";
  }

  // Radial around the center, a tree to the right, or an org chart downwards
  _layout() {
    const layout = this._savedLayout || (LAYOUTS.includes(this._config.layout) ? this._config.layout : "radial");
    // A view of a higher level falls back to the round map, the choice stays saved
    return levelAllows(this._currentLevel(), LAYOUT_LEVELS[layout] || "beginner") ? layout : "radial";
  }

  _currentLevel() {
    return uiLevel(this._config, this._getRawSensorEntity());
  }

  // Beginners and normal users see fewer controls; CSS hides them by data-lvl
  _applyLevel() {
    const level = this._currentLevel();
    if (this.getAttribute("data-level") !== level) {
      this.setAttribute("data-level", level);
      const canvas = this.shadowRoot && this.shadowRoot.getElementById("canvasArea");
      if (canvas) this._syncCanvasMode(canvas);
      const btn = this.shadowRoot && this.shadowRoot.getElementById("layoutBtn");
      if (btn) btn.textContent = this._layoutIcon();
    }
    return level;
  }

  _layoutIcon(layout = this._layout()) {
    return { radial: "◎", tree: "⇶", org: "⊤", outline: "☰", pin: "📌", kanban: "▥", timeline: "📅", matrix: "⊞" }[layout];
  }

  _layoutName(layout) {
    return {
      radial: t("Rund um die Mitte"),
      tree: t("Baum nach rechts"),
      org: t("Organigramm nach unten"),
      outline: t("Gliederung"),
      pin: t("Pinnwand mit Haftzetteln"),
      kanban: t("Kanban nach Status"),
      timeline: t("Zeitleiste nach Fälligkeit"),
      matrix: t("Eisenhower-Matrix"),
    }[layout];
  }

  // A note shared only for viewing stays where its owner put it
  _canEditIdea(idea) {
    return !idea.access || idea.access !== "view";
  }

  _pinColorName(name) {
    return { yellow: t("Gelb"), pink: t("Rosa"), green: t("Grün"), blue: t("Blau"), orange: t("Orange"), purple: t("Lila") }[name];
  }

  _isBoard() {
    return BOARDS.includes(this._layout());
  }

  // Notes as sticky notes, placed freely, without the tree
  _isPinboard() {
    return this._layout() === "pin";
  }

  _syncCanvasMode(canvas) {
    canvas.classList.toggle("board-mode", this._isBoard());
    canvas.classList.toggle("pin-mode", this._isPinboard());
  }

  // Where a note sits on the pinboard: what was just set here, until Home Assistant has it
  _pinOf(idea) {
    if (!idea) return null;
    const saved = idea.pin || null;
    if (!this._pinOverrides.has(idea.id)) return saved;
    const local = this._pinOverrides.get(idea.id);
    const same = (a, b) => (!a && !b) || (a && b && a.x === b.x && a.y === b.y && (a.color || "") === (b.color || ""));
    if (same(local, saved)) {
      this._pinOverrides.delete(idea.id);
      return saved;
    }
    return local;
  }

  // Pinned notes keep their place, the others line up in rows below them
  _arrangePinLayout(ideas, w, h) {
    const gap = 16;
    const size = (id) => {
      const el = this.shadowRoot.getElementById(`cloud_${id}`);
      return { w: (el && el.offsetWidth) || 180, h: (el && el.offsetHeight) || 100 };
    };
    const places = new Map();
    let bottom = 0;
    ideas.forEach((idea) => {
      const pin = this._pinOf(idea);
      if (!pin) return;
      places.set(idea.id, { x: pin.x, y: pin.y });
      bottom = Math.max(bottom, pin.y + size(idea.id).h / 2);
    });
    const rowWidth = Math.max(w - 40, 420);
    let x = 20;
    let top = places.size ? bottom + 40 : 20;
    let rowH = 0;
    ideas.forEach((idea) => {
      if (places.has(idea.id)) return;
      const box = size(idea.id);
      if (x > 20 && x + box.w > 20 + rowWidth) {
        x = 20;
        top += rowH + gap;
        rowH = 0;
      }
      places.set(idea.id, { x: x + box.w / 2, y: top + box.h / 2 });
      x += box.w + gap;
      rowH = Math.max(rowH, box.h);
    });
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    ideas.forEach((idea) => {
      const pos = places.get(idea.id);
      this._nodePositions.set(idea.id, pos);
      const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
      if (!el) return;
      el.style.left = `${pos.x}px`;
      el.style.top = `${pos.y}px`;
      const pin = this._pinOf(idea);
      el.style.setProperty("--pin-bg", PIN_COLORS[(pin && pin.color) || "yellow"] || PIN_COLORS.yellow);
      // A slight, steady tilt per note, as on a real board
      const seed = [...idea.id].reduce((sum, ch) => sum + ch.charCodeAt(0), 0);
      el.style.setProperty("--pin-tilt", `${(seed % 5) - 2}deg`);
      const box = size(idea.id);
      minX = Math.min(minX, pos.x - box.w / 2);
      minY = Math.min(minY, pos.y - box.h / 2);
      maxX = Math.max(maxX, pos.x + box.w / 2);
      maxY = Math.max(maxY, pos.y + box.h / 2);
    });
    if (!this._pinFitted && ideas.length) {
      this._pinFitted = true;
      // Room above for frame names and callouts
      this._fitBox(minX - 12, minY - 48, maxX + 12, maxY + 12, w, h);
    }
    this._drawConnections();
  }

  _savePins(pins) {
    if (!this._hass) return Promise.resolve();
    return this._hass.callWS({ type: "brainstorm/pins", pins }).catch((err) => {
      console.error("[BrainstormMindmap] Failed to save pinboard places:", err);
      this._showToast(t("Der Zettel konnte nicht gespeichert werden."));
    });
  }

  // Pin the dropped notes where they are; undo puts them back
  async _dropOnPinboard(moved) {
    const pins = {};
    const before = {};
    moved.forEach((id) => {
      const idea = this._ideaById(id);
      const pos = this._nodePositions.get(id);
      if (!idea || !pos || !this._canEditIdea(idea)) return;
      const old = this._pinOf(idea);
      before[id] = old ? { ...old } : null;
      const place = { x: Math.round(pos.x * 10) / 10, y: Math.round(pos.y * 10) / 10 };
      if (old && old.color) place.color = old.color;
      pins[id] = { x: place.x, y: place.y };
      this._pinOverrides.set(id, place);
    });
    this._lastLayoutKey = "";
    this._arrangeNodesRadially();
    if (!Object.keys(pins).length) return;
    await this._savePins(pins);
    this._pushUndo(moved.length === 1 ? this._ideaText(moved[0]) : t("{count} Notizen", { count: moved.length }), async () => {
      const back = {};
      Object.entries(before).forEach(([id, pin]) => {
        this._pinOverrides.set(id, pin);
        back[id] = pin ? { x: pin.x, y: pin.y, color: pin.color || "" } : null;
      });
      this._lastLayoutKey = "";
      this._arrangeNodesRadially();
      await this._savePins(back);
    });
  }

  async _setPinColor(idea, color) {
    const pos = this._pinOf(idea) || this._nodePositions.get(idea.id);
    if (!pos) return;
    const old = this._pinOf(idea);
    const place = { x: Math.round(pos.x * 10) / 10, y: Math.round(pos.y * 10) / 10 };
    if (color !== "yellow") place.color = color;
    this._pinOverrides.set(idea.id, place);
    const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
    if (el) el.style.setProperty("--pin-bg", PIN_COLORS[color]);
    await this._savePins({ [idea.id]: { x: place.x, y: place.y, color: place.color || "" } });
    this._pushUndo(idea.text, async () => {
      this._pinOverrides.set(idea.id, old ? { ...old } : null);
      this._lastLayoutKey = "";
      this._arrangeNodesRadially();
      await this._savePins({ [idea.id]: old ? { x: old.x, y: old.y, color: old.color || "" } : null });
    });
  }

  _showLayoutDialog() {
    this._openDialog(t("Ansicht wählen"), (body) => {
      body.innerHTML = `
        <div class="layout-grid">
          ${LAYOUTS.map((layout) => `
            <button class="layout-choice${layout === this._layout() ? " active" : ""}" data-layout="${layout}"${LAYOUT_LEVELS[layout] ? ` data-lvl="${LAYOUT_LEVELS[layout]}"` : ""}>
              <span class="layout-icon">${this._layoutIcon(layout)}</span>
              <span>${this._layoutName(layout)}</span>
            </button>`).join("")}
        </div>
        <div class="dialog-hint">${t("In Kanban, Zeitleiste und Matrix ändert das Ziehen in eine andere Spalte Status, Fälligkeit oder Priorität.")}</div>
        <div class="dialog-hint">${t("Auf der Pinnwand bleibt jeder Zettel, wo du ihn hinziehst. Die Farbe wählst du unter ⋯, Gruppen bekommen einen Rahmen.")}</div>
        <div class="dialog-footer" data-lvl="pro">
          <button class="dialog-btn dialog-btn-primary" id="presentStart">▶ ${t("Präsentieren (P)")}</button>
        </div>`;
      body.querySelector("#presentStart").addEventListener("click", () => {
        this._closeDialog();
        this._startPresentation();
      });
      body.querySelectorAll(".layout-choice").forEach((btn) => {
        btn.addEventListener("click", () => {
          this._closeDialog();
          this._setLayout(btn.dataset.layout);
        });
      });
    });
  }

  _setLayout(layout) {
    this._savedLayout = layout;
    try {
      localStorage.setItem(LAYOUT_KEY, layout);
    } catch {}
    this._userMovedNodes.clear();
    this._scale = 1;
    this._panX = 0;
    this._panY = 0;
    this._applyTransform();
    const btn = this.shadowRoot.getElementById("layoutBtn");
    if (btn) btn.textContent = this._layoutIcon(layout);
    const canvas = this.shadowRoot.getElementById("canvasArea");
    if (canvas) this._syncCanvasMode(canvas);
    this._pinFitted = false;
    this._lastLayoutKey = "";
    this._updateContent();
    this._arrangeNodesRadially();
    this._showToast(`${this._layoutIcon(layout)} ${this._layoutName(layout)}`);
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
    return this._focusIdeas((sensor.attributes.ideas || []).filter((i) => {
      if (this._selectedCategory === "all") return true;
      return String(i.category || "").trim() === String(this._selectedCategory || "").trim();
    }));
  }

  // In a focused branch only what hangs below it is on the map, the branch itself is the center
  _focusIdeas(ideas) {
    if (!this._focusId) return ideas;
    if (!ideas.some((i) => i.id === this._focusId)) {
      this._focusId = null;
      return ideas;
    }
    const inside = new Set(this._descendantIds(this._focusId, ideas));
    return ideas.filter((i) => inside.has(i.id));
  }

  _focusIdea() {
    const sensor = this._getSensorEntity();
    if (!sensor || !this._focusId) return null;
    return (sensor.attributes.ideas || []).find((i) => i.id === this._focusId) || null;
  }

  // Open a branch as if it were the whole map, null goes back to the list
  _setFocus(id) {
    const sensor = this._getSensorEntity();
    const ideas = (sensor && sensor.attributes.ideas) || [];
    const idea = id ? ideas.find((i) => i.id === id) : null;
    const previous = this._focusId;
    this._focusId = idea ? idea.id : null;
    if (previous === this._focusId) return;
    this._selectedId = previous && !this._focusId ? previous : null;
    this._nodePositions.clear();
    if (this._userMovedNodes) this._userMovedNodes.clear();
    this._lastLayoutKey = "";
    this._lastDataSignature = "";
    this._centerLayout(true);
    this._updateContent();
    this._focusMap();
  }

  // One level up: to the parent of the focused branch, or back to the whole list
  _focusUp() {
    const focus = this._focusIdea();
    if (!focus) {
      this._setFocus(null);
      return;
    }
    const sensor = this._getSensorEntity();
    const ideas = (sensor && sensor.attributes.ideas) || [];
    const parent = focus.parent_id && ideas.find((i) => i.id === focus.parent_id && i.category === focus.category);
    const left = focus.id;
    this._setFocus(parent ? parent.id : null);
    if (this._shadowRootHas(left)) this._selectIdea(left);
  }

  // ---- Reactions and voting rounds ----

  _currentUserId() {
    const sensor = this._getSensorEntity();
    return (sensor && sensor.attributes.current_user) || (this._hass && this._hass.user && this._hass.user.id) || "";
  }

  _voting() {
    const sensor = this._getSensorEntity();
    return (sensor && sensor.attributes.voting) || {};
  }

  // Running hidden brainstorm rounds by category
  _rounds() {
    const sensor = this._getSensorEntity();
    return (sensor && sensor.attributes.rounds) || {};
  }

  _roundEnd(round) {
    const end = round && round.ends_at ? Date.parse(round.ends_at) : 0;
    return Number.isFinite(end) ? end : 0;
  }

  async _endRound(category) {
    try {
      const result = await this._hass.callWS({
        type: "call_service",
        domain: "brainstorm",
        service: "end_round",
        service_data: { category },
        return_response: true,
      });
      const revealed = (result && result.response && result.response.revealed) || 0;
      this._showToast(t("Aufgedeckt: {count} Ideen", { count: revealed }));
    } catch (err) {
      console.error("[BrainstormMindmap] Ending the round failed:", err);
      this._showToast((err && err.message) || t("Das ging nicht."));
    }
  }

  async _react(id, reaction) {
    try {
      await this._hass.callService("brainstorm", "react", { id, reaction });
    } catch (err) {
      console.error("[BrainstormMindmap] Reaction failed:", err);
      this._showToast((err && err.message) || t("Das ging nicht."));
    }
  }

  async _vote(id, delta) {
    try {
      await this._hass.callService("brainstorm", "vote", { id, delta });
    } catch (err) {
      console.error("[BrainstormMindmap] Vote failed:", err);
      this._showToast((err && err.message) || t("Das ging nicht."));
    }
  }

  // The bar over the map while the shown list votes
  _renderVoteBar() {
    const bar = this.shadowRoot && this.shadowRoot.getElementById("voteBar");
    if (!bar) return;
    const voting = this._voting();
    const rounds = this._rounds();
    const shown = (all) => (this._selectedCategory === "all" ? Object.keys(all) : [this._selectedCategory].filter((c) => all[c]));
    const categories = shown(voting);
    const roundCategories = shown(rounds);
    if (!categories.length && !roundCategories.length) {
      bar.classList.remove("open");
      bar.innerHTML = "";
      return;
    }
    const roundHtml = roundCategories
      .map((category) => {
        const round = rounds[category];
        const end = this._roundEnd(round);
        const until = end ? ` · ${t("bis {time}", { time: new Date(end).toLocaleTimeString(this._hass && this._hass.language ? this._hass.language : undefined, { hour: "2-digit", minute: "2-digit" }) })}` : "";
        const hidden = round.hidden_count ? ` · ${t("{count} Ideen anderer verdeckt", { count: round.hidden_count })}` : "";
        return `<span class="vote-info">🙈 ${t("Verdeckte Runde in {category}", { category: this._escapeHtml(category) })}${hidden}${until}</span>
          <button type="button" data-join-round="${this._escapeHtml(category)}">${t("Mitmachen")}</button>
          <button type="button" data-end-round="${this._escapeHtml(category)}">${t("Aufdecken")}</button>`;
      })
      .join("");
    bar.innerHTML = roundHtml + categories
      .map((category) => {
        const round = voting[category];
        const left = Math.max(0, (round.votes || 0) - (round.used || 0));
        return `<span class="vote-info">🗳️ ${t("Abstimmung in {category}: noch {left} von {total} Stimmen", { category: this._escapeHtml(category), left, total: round.votes || 0 })}${round.hidden ? ` · 🙈 ${t("verdeckt")}` : ""}</span>
          <button type="button" data-end-vote="${this._escapeHtml(category)}">${t("Beenden")}</button>`;
      })
      .join("");
    bar.classList.add("open");
  }

  _showVotingDialog() {
    const sensor = this._getSensorEntity();
    if (!sensor) return;
    const voting = this._voting();
    const categories = (sensor.attributes.categories || []).filter((c) => c !== "__completed__");
    const current = this._selectedCategory !== "all" && categories.includes(this._selectedCategory) ? this._selectedCategory : null;
    if (current && voting[current]) {
      this._endVoting(current);
      return;
    }
    this._openDialog(t("🗳️ Abstimmung starten"), (body) => {
      const counts = [3, 5, 10];
      body.innerHTML = `
        <div class="dialog-label">${t("Kategorie")}</div>
        <select class="dialog-input" id="voteCategory">
          ${categories.map((c) => `<option value="${this._escapeHtml(c)}"${c === current ? " selected" : ""}${voting[c] ? " disabled" : ""}>${this._escapeHtml(c)}${voting[c] ? ` (${t("läuft")})` : ""}</option>`).join("")}
        </select>
        <div class="dialog-label">${t("Stimmen pro Person")}</div>
        <div class="vote-choices">
          ${counts.map((n) => `<div class="dialog-prio-chip${n === 5 ? " selected" : ""}" data-votes="${n}">${n}</div>`).join("")}
        </div>
        <label class="dialog-check"><input type="checkbox" id="voteHidden"> ${t("Verdeckt: jede Person sieht bis zum Ende nur ihre eigenen Stimmen")}</label>
        <label class="dialog-check"><input type="checkbox" id="voteClear" checked> ${t("Stimmen früherer Runden löschen")}</label>
        <div class="dialog-hint">${t("Jede Person setzt ihre Stimmen mit + an den Notizen, auch mehrere auf eine. Wer die Liste sieht, darf mitstimmen.")}</div>
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="voteCancel">${t("Abbrechen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="voteStart">${t("Starten")}</button>
        </div>`;
      let votes = 5;
      body.querySelectorAll("[data-votes]").forEach((chip) => {
        chip.addEventListener("click", () => {
          votes = Number(chip.getAttribute("data-votes"));
          body.querySelectorAll("[data-votes]").forEach((c) => c.classList.toggle("selected", c === chip));
        });
      });
      body.querySelector("#voteCancel").addEventListener("click", () => this._closeDialog());
      body.querySelector("#voteStart").addEventListener("click", async () => {
        const category = body.querySelector("#voteCategory").value;
        if (!category || voting[category]) return;
        try {
          await this._hass.callService("brainstorm", "start_voting", {
            category,
            votes,
            hidden: body.querySelector("#voteHidden").checked,
            clear: body.querySelector("#voteClear").checked,
          });
          this._closeDialog();
          if (this._selectedCategory !== category && this._selectedCategory !== "all") {
            this._selectedCategory = category;
            this._saveSelectedCategory();
            this._lastDataSignature = "";
          }
          this._showToast(t("Abstimmung läuft: {votes} Stimmen pro Person", { votes }));
        } catch (err) {
          console.error("[BrainstormMindmap] Starting the vote failed:", err);
          this._showToast((err && err.message) || t("Das ging nicht."));
        }
      });
    });
  }

  // Ask first, the round cannot be taken back
  _endVoting(category) {
    this._openDialog(t("🗳️ Abstimmung beenden"), (body) => {
      body.innerHTML = `
        <div class="dialog-hint">${t("Abstimmung in „{category}“ beenden? Danach zeigt Brainstorm das Ergebnis, die Stimmen bleiben an den Notizen.", { category: this._escapeHtml(category) })}</div>
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="endVoteCancel">${t("Abbrechen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="endVoteOk">${t("Beenden")}</button>
        </div>`;
      body.querySelector("#endVoteCancel").addEventListener("click", () => this._closeDialog());
      body.querySelector("#endVoteOk").addEventListener("click", () => this._finishVoting(category));
    });
  }

  async _finishVoting(category) {
    let ranking = [];
    try {
      const response = await this._hass.callWS({
        type: "call_service",
        domain: "brainstorm",
        service: "end_voting",
        service_data: { category },
        return_response: true,
      });
      ranking = (response && response.response && response.response.ranking) || [];
    } catch (err) {
      console.error("[BrainstormMindmap] Ending the vote failed:", err);
      this._showToast((err && err.message) || t("Das ging nicht."));
      return;
    }
    this._openDialog(t("🏆 Ergebnis: {category}", { category: this._escapeHtml(category) }), (body) => {
      body.innerHTML = ranking.length
        ? `<ol class="vote-rank">${ranking
            .map((item, index) => `<li><span class="rank-place">${index < 3 ? ["🥇", "🥈", "🥉"][index] : index + 1}</span><span class="rank-text">${formatText(item.text || "")}</span><span class="rank-points">● ${item.points}</span></li>`)
            .join("")}</ol>`
        : `<div class="dialog-hint">${t("Niemand hat abgestimmt.")}</div>`;
      body.innerHTML += `
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="rankClose">${t("Schließen")}</button>
          ${ranking.length ? `<button class="dialog-btn dialog-btn-primary" id="rankSort">${t("Nach Stimmen sortieren")}</button>` : ""}
        </div>`;
      body.querySelector("#rankClose").addEventListener("click", () => this._closeDialog());
      const sortBtn = body.querySelector("#rankSort");
      if (sortBtn) {
        sortBtn.addEventListener("click", async () => {
          this._closeDialog();
          try {
            await this._hass.callService("brainstorm", "sort_children", { category, by: "votes" });
          } catch (err) {
            this._showToast((err && err.message) || t("Das ging nicht."));
          }
        });
      }
    });
  }

  _shadowRootHas(id) {
    return Boolean(id && this.shadowRoot && this.shadowRoot.getElementById(`cloud_${id}`));
  }

  // The path to the focused branch: list, its parents, the branch
  _renderFocusBar() {
    const bar = this.shadowRoot && this.shadowRoot.getElementById("focusBar");
    if (!bar) return;
    const focus = this._focusIdea();
    if (!focus) {
      bar.classList.remove("open");
      bar.innerHTML = "";
      return;
    }
    const sensor = this._getSensorEntity();
    const ideas = (sensor && sensor.attributes.ideas) || [];
    const path = [];
    const seen = new Set([focus.id]);
    let parent = ideas.find((i) => i.id === focus.parent_id);
    while (parent && !seen.has(parent.id) && parent.category === focus.category) {
      path.unshift(parent);
      seen.add(parent.id);
      parent = ideas.find((i) => i.id === parent.parent_id);
    }
    const label = this._selectedCategory === "all" ? t("Alle") : this._selectedCategory;
    const short = (text) => {
      const plain = String(text || "").replace(/\s+/g, " ").trim();
      return plain.length > 32 ? `${plain.slice(0, 31)}…` : plain;
    };
    bar.innerHTML = `
      <span class="focus-icon" aria-hidden="true">🎯</span>
      <button class="focus-crumb" data-focus="">${this._escapeHtml(label)}</button>
      ${path.map((p) => `<span class="focus-sep">›</span><button class="focus-crumb" data-focus="${this._escapeHtml(p.id)}">${this._escapeHtml(short(p.text))}</button>`).join("")}
      <span class="focus-sep">›</span><span class="focus-crumb current">${this._escapeHtml(short(focus.text))}</span>
      <button class="focus-close" data-focus="" title="${t("Ganze Map zeigen (Umschalt+F4)")}">✕</button>
    `;
    bar.classList.add("open");
    bar.onclick = (e) => {
      const crumb = e.target.closest("[data-focus]");
      if (crumb) this._setFocus(crumb.getAttribute("data-focus") || null);
    };
  }

  // Fold every branch below a level, 0 opens them all
  _showLevels(level) {
    const ideas = this._categoryIdeas();
    const ids = new Set(ideas.map((i) => i.id));
    const byId = new Map(ideas.map((i) => [i.id, i]));
    const depth = (idea) => {
      let d = 1;
      const seen = new Set([idea.id]);
      let parent = this._branchParent(idea, ids);
      while (parent && !seen.has(parent)) {
        seen.add(parent);
        d += 1;
        parent = this._branchParent(byId.get(parent), ids);
      }
      return d;
    };
    const parents = new Set(ideas.map((i) => this._branchParent(i, ids)).filter(Boolean));
    ideas.forEach((idea) => this._collapsed.delete(idea.id));
    if (level > 0) {
      ideas.forEach((idea) => {
        if (parents.has(idea.id) && depth(idea) >= level) this._collapsed.add(idea.id);
      });
    }
    this._levels = level;
    this._saveCollapsed();
    this._lastLayoutKey = "";
    this._updateContent();
    const levelsBtn = this.shadowRoot.getElementById("levelsBtn");
    if (levelsBtn) levelsBtn.textContent = level > 0 ? String(level) : "∞";
    this._showToast(level > 0 ? t("Ebenen bis {level}", { level }) : t("Alle Ebenen"));
  }

  // The ideas on the map, without those inside a folded branch
  _mapIdeas(ideas = this._categoryIdeas()) {
    // The pinboard has no branches to fold
    if (this._isPinboard()) return ideas;
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

  // Presentation: the map goes through its notes one by one, branch by branch
  _presentationOrder() {
    const ideas = this._categoryIdeas();
    const ids = new Set(ideas.map((i) => i.id));
    const kids = new Map();
    const roots = [];
    ideas.forEach((idea) => {
      const parent = this._branchParent(idea, ids);
      if (parent) {
        if (!kids.has(parent)) kids.set(parent, []);
        kids.get(parent).push(idea);
      } else {
        roots.push(idea);
      }
    });
    const order = [];
    const seen = new Set();
    const walk = (idea) => {
      if (seen.has(idea.id)) return;
      seen.add(idea.id);
      order.push(idea.id);
      (kids.get(idea.id) || []).forEach(walk);
    };
    roots.forEach(walk);
    ideas.forEach(walk);
    return order;
  }

  _startPresentation() {
    const order = this._presentationOrder();
    if (!order.length) {
      this._showToast(t("Keine Notizen zum Präsentieren."));
      return;
    }
    const cardRoot = this.shadowRoot.getElementById("cardRoot");
    const wasFullscreen = Boolean(cardRoot && cardRoot.classList.contains("is-fullscreen"));
    this._presentation = { order, index: -1, wasFullscreen, collapsed: new Set(this._collapsed) };
    this._clearMulti();
    if (cardRoot) cardRoot.classList.add("presenting");
    if (!wasFullscreen && this._toggleFullscreen) this._toggleFullscreen();
    const bar = this.shadowRoot.getElementById("presentBar");
    if (bar) bar.style.display = "flex";
    // The fullscreen layout settles first, then the overview shows
    setTimeout(() => this._presentGo(-1), 120);
    this._focusMap();
  }

  _endPresentation() {
    const presentation = this._presentation;
    if (!presentation) return;
    this._presentation = null;
    const cardRoot = this.shadowRoot.getElementById("cardRoot");
    if (cardRoot) cardRoot.classList.remove("presenting");
    this.shadowRoot.querySelectorAll(".present-current, .present-near").forEach((el) => el.classList.remove("present-current", "present-near"));
    const bar = this.shadowRoot.getElementById("presentBar");
    if (bar) bar.style.display = "none";
    // Branches folded before the presentation fold again
    const refold = [...presentation.collapsed].some((id) => !this._collapsed.has(id));
    this._collapsed = new Set(presentation.collapsed);
    if (refold) {
      this._saveCollapsed();
      this._lastLayoutKey = "";
      this._updateContent();
    }
    if (!presentation.wasFullscreen && this._toggleFullscreen) this._toggleFullscreen();
    else this._centerLayout(this._usesSavedPositions() || this._userMovedNodes.size === 0);
  }

  _presentStep(direction) {
    const presentation = this._presentation;
    if (!presentation) return;
    const next = presentation.index + direction;
    if (next >= presentation.order.length) {
      this._endPresentation();
      return;
    }
    this._presentGo(Math.max(-1, next));
  }

  // -1 is the overview of the whole map
  _presentGo(index) {
    const presentation = this._presentation;
    if (!presentation) return;
    presentation.index = index;
    const total = presentation.order.length;
    const stepEl = this.shadowRoot.getElementById("presentStep");
    const textEl = this.shadowRoot.getElementById("presentText");
    const descEl = this.shadowRoot.getElementById("presentDesc");
    this.shadowRoot.querySelectorAll(".present-current, .present-near").forEach((el) => el.classList.remove("present-current", "present-near"));
    const cardRoot = this.shadowRoot.getElementById("cardRoot");
    if (index < 0) {
      if (cardRoot) cardRoot.classList.remove("present-spot");
      this._centerLayout(this._usesSavedPositions() || this._userMovedNodes.size === 0);
      const focus = this._focusIdea();
      if (stepEl) stepEl.textContent = t("Überblick · {total} Notizen", { total });
      if (textEl) textEl.innerHTML = this._escapeHtml(focus ? focus.text : this._selectedCategory === "all" ? t("Alle") : this._selectedCategory);
      if (descEl) descEl.textContent = t("→ oder Leertaste: weiter · Esc: beenden");
      return;
    }
    const id = presentation.order[index];
    const ideas = this._categoryIdeas();
    const ids = new Set(ideas.map((i) => i.id));
    const byId = new Map(ideas.map((i) => [i.id, i]));
    const idea = byId.get(id);
    if (!idea) return;
    // A note inside a folded branch unfolds it, as the search does
    let unfolded = false;
    const seen = new Set([id]);
    let parent = this._branchParent(idea, ids);
    const path = [];
    while (parent && !seen.has(parent)) {
      seen.add(parent);
      path.unshift(byId.get(parent));
      if (this._collapsed.delete(parent)) unfolded = true;
      parent = this._branchParent(byId.get(parent), ids);
    }
    if (unfolded) {
      this._lastLayoutKey = "";
      this._updateContent();
    }
    if (cardRoot) cardRoot.classList.add("present-spot");
    const el = this.shadowRoot.getElementById(`cloud_${id}`);
    if (el) el.classList.add("present-current");
    ideas.forEach((other) => {
      if (other.id !== id && (this._branchParent(other, ids) === id || other.id === this._branchParent(idea, ids))) {
        const near = this.shadowRoot.getElementById(`cloud_${other.id}`);
        if (near) near.classList.add("present-near");
      }
    });
    const pos = this._nodePositions.get(id);
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    if (pos && canvasArea) {
      const width = (el && el.offsetWidth) || 230;
      this._scale = Math.max(0.6, Math.min(1.4, (canvasArea.clientWidth * 0.5) / width));
      this._panX = canvasArea.clientWidth / 2 - pos.x * this._scale;
      this._panY = (canvasArea.clientHeight - 110) / 2 - pos.y * this._scale;
      this._applyTransform();
    }
    if (stepEl) stepEl.textContent = `${index + 1} / ${total}${path.length ? ` · ${path.map((p) => p.text).join(" › ")}` : ""}`;
    if (textEl) textEl.innerHTML = formatText(idea.text);
    if (descEl) descEl.innerHTML = idea.description ? formatText(idea.description) : "";
  }

  _aiAvailable() {
    const sensor = this._getSensorEntity();
    return Boolean(sensor && sensor.attributes && sensor.attributes.ai_subtasks);
  }

  // The category whose loose notes the AI may sort in, null under "All"
  _sortInCategory() {
    const focus = this._focusIdea();
    if (focus) return focus.category;
    return this._selectedCategory && this._selectedCategory !== "all" ? this._selectedCategory : null;
  }

  _aiErrorText(err, fallback) {
    const code = err && err.code;
    if (code === "ai_not_configured") return t("Wähle zuerst eine KI-Aufgaben-Entität unter Brainstorm Hub ➔ Konfigurieren ➔ KI.");
    if (code === "ai_unavailable") return t("Die KI ist gerade nicht erreichbar. Versuch es gleich nochmal.");
    return fallback;
  }

  // ✨ on a note with subtasks offers more than new subtasks
  _showAiChooser(idea) {
    const sensor = this._getSensorEntity();
    const ideas = (sensor && sensor.attributes.ideas) || [];
    const hasChildren = ideas.some((i) => i.parent_id === idea.id);
    // Summing up a branch is for pros
    if (!hasChildren || !levelAllows(this._currentLevel(), "pro")) {
      this._showSubtaskSuggestions(idea);
      return;
    }
    this._openDialog(t("✨ KI-Hilfe"), (body) => {
      body.innerHTML = `
        <div class="dialog-note-preview">${formatText(idea.text)}</div>
        <div class="layout-grid">
          <button class="layout-choice" data-ai="subtasks"><span class="layout-icon">🌿</span><span>${t("Unteraufgaben vorschlagen")}</span></button>
          <button class="layout-choice" data-ai="summary"><span class="layout-icon">🧾</span><span>${t("Ast zusammenfassen")}</span></button>
        </div>`;
      body.querySelectorAll("[data-ai]").forEach((btn) => {
        btn.addEventListener("click", () => {
          this._closeDialog();
          if (btn.dataset.ai === "summary") this._showBranchSummary(idea);
          else this._showSubtaskSuggestions(idea);
        });
      });
    });
  }

  // The AI sums up a branch; it becomes the description only if the person wants
  _showBranchSummary(idea) {
    if (!this._hass) return;
    this._openDialog(t("🧾 Ast zusammenfassen"), (body) => {
      const preview = `<div class="dialog-note-preview">${formatText(idea.text)}</div>`;
      const load = async () => {
        body.innerHTML = `${preview}<div class="dialog-label suggest-status">${t("Die KI denkt nach …")}</div>`;
        let result;
        try {
          result = await this._hass.callWS({
            type: "brainstorm/summarize_branch",
            idea_id: idea.id,
            ...(this._hass.language ? { language: this._hass.language } : {}),
          });
        } catch (err) {
          if (!this._isModalOpen) return;
          body.innerHTML = `
            ${preview}
            <div class="dialog-error" style="display: flex;">${this._aiErrorText(err, t("Die KI hat keine Zusammenfassung geliefert."))}</div>
            <div class="dialog-footer">
              <button class="dialog-btn dialog-btn-cancel" id="summaryCancel">${t("Abbrechen")}</button>
              <button class="dialog-btn dialog-btn-primary" id="summaryRetry">${t("Nochmal versuchen")}</button>
            </div>`;
          body.querySelector("#summaryCancel").addEventListener("click", () => this._closeDialog());
          body.querySelector("#summaryRetry").addEventListener("click", load);
          return;
        }
        if (!this._isModalOpen) return;
        const summary = (result && result.summary) || "";
        body.innerHTML = `
          ${preview}
          <div class="dialog-label">${t("Du kannst den Text noch ändern.")}</div>
          <textarea class="dialog-input dialog-textarea" id="summaryText" rows="6">${this._escapeHtml(summary)}</textarea>
          <div class="dialog-footer">
            <button class="dialog-btn dialog-btn-cancel" id="summaryCopy">${t("Kopieren")}</button>
            <button class="dialog-btn dialog-btn-cancel" id="summaryRetry">${t("Neu schreiben")}</button>
            ${result.can_edit ? `<button class="dialog-btn dialog-btn-primary" id="summarySave">${t("Als Beschreibung übernehmen")}</button>` : ""}
          </div>`;
        const text = body.querySelector("#summaryText");
        body.querySelector("#summaryRetry").addEventListener("click", load);
        body.querySelector("#summaryCopy").addEventListener("click", async () => {
          try {
            await navigator.clipboard.writeText(text.value);
            this._showToast(t("Kopiert"));
          } catch (err) {
            text.select();
          }
        });
        const save = body.querySelector("#summarySave");
        if (save) {
          save.addEventListener("click", async () => {
            const value = text.value.trim();
            const current = this._ideaById(idea.id) || idea;
            const before = current.description || "";
            const next = before ? `${value}\n\n${before}` : value;
            this._closeDialog();
            try {
              await this._hass.callService("brainstorm", "update_idea", { id: idea.id, description: next });
              this._showToast(t("Zusammenfassung gespeichert"));
              this._pushUndo(idea.text, () => this._hass.callService("brainstorm", "update_idea", { id: idea.id, description: before }));
            } catch (err) {
              console.error("[BrainstormMindmap] Failed to save the summary:", err);
            }
          });
        }
      };
      load();
    });
  }

  // The AI suggests where loose notes belong; nothing moves until the person picks
  _showSortInDialog() {
    if (!this._hass) return;
    const category = this._sortInCategory();
    if (!category) {
      this._showToast(t("Wähle zuerst eine Kategorie."));
      return;
    }
    this._openDialog(t("✨ Lose Ideen zuordnen"), (body) => {
      const load = async () => {
        body.innerHTML = `<div class="dialog-label suggest-status">${t("Die KI denkt nach …")}</div>`;
        let suggestions;
        try {
          const result = await this._hass.callWS({
            type: "brainstorm/suggest_parents",
            category,
            ...(this._hass.language ? { language: this._hass.language } : {}),
          });
          suggestions = (result && result.suggestions) || [];
        } catch (err) {
          if (!this._isModalOpen) return;
          const message = err && err.code === "ai_failed"
            ? t("In dieser Kategorie gibt es keine losen Notizen.")
            : this._aiErrorText(err, t("Die KI hat keine Zuordnung geliefert."));
          body.innerHTML = `
            <div class="dialog-error" style="display: flex;">${message}</div>
            <div class="dialog-footer">
              <button class="dialog-btn dialog-btn-cancel" id="sortInCancel">${t("Schließen")}</button>
              <button class="dialog-btn dialog-btn-primary" id="sortInRetry">${t("Nochmal versuchen")}</button>
            </div>`;
          body.querySelector("#sortInCancel").addEventListener("click", () => this._closeDialog());
          body.querySelector("#sortInRetry").addEventListener("click", load);
          return;
        }
        if (!this._isModalOpen) return;
        if (!suggestions.length) {
          body.innerHTML = `
            <div class="dialog-hint">${t("Die KI hat für keine lose Notiz einen passenden Platz gefunden.")}</div>
            <div class="dialog-footer">
              <button class="dialog-btn dialog-btn-cancel" id="sortInRetry">${t("Nochmal versuchen")}</button>
              <button class="dialog-btn dialog-btn-cancel" id="sortInCluster">${t("✨ Nach Themen gruppieren")}</button>
              <button class="dialog-btn dialog-btn-primary" id="sortInCancel">${t("Schließen")}</button>
            </div>`;
          body.querySelector("#sortInCancel").addEventListener("click", () => this._closeDialog());
          body.querySelector("#sortInRetry").addEventListener("click", load);
          body.querySelector("#sortInCluster").addEventListener("click", () => this._showClusterDialog());
          return;
        }
        body.innerHTML = `
          <div class="dialog-label">${t("Haken weg bei allem, was bleiben soll, wo es ist.")}</div>
          <div class="suggest-list">
            ${suggestions.map((item, index) => `
              <label class="suggest-row sortin-row">
                <input type="checkbox" class="suggest-check" data-index="${index}" checked />
                <span class="sortin-text">${formatText(item.text)} <span class="sortin-arrow">→</span> <b>${formatText(item.parent_text)}</b></span>
              </label>`).join("")}
          </div>
          <div class="dialog-footer">
            <button class="dialog-btn dialog-btn-cancel" id="sortInRetry">${t("Neue Vorschläge")}</button>
            <button class="dialog-btn dialog-btn-primary" id="sortInSave"></button>
          </div>`;
        const saveBtn = body.querySelector("#sortInSave");
        const picked = () => [...body.querySelectorAll(".suggest-check")].filter((box) => box.checked).map((box) => suggestions[Number(box.dataset.index)]);
        const update = () => {
          const count = picked().length;
          saveBtn.textContent = t("{count} übernehmen", { count });
          saveBtn.disabled = count === 0;
        };
        body.querySelectorAll(".suggest-check").forEach((box) => box.addEventListener("input", update));
        update();
        body.querySelector("#sortInRetry").addEventListener("click", load);
        saveBtn.addEventListener("click", async () => {
          const moves = picked();
          this._closeDialog();
          const done = [];
          for (const move of moves) {
            try {
              await this._hass.callService("brainstorm", "update_idea", { id: move.idea_id, parent_id: move.parent_id });
              done.push(move.idea_id);
            } catch (err) {
              console.error("[BrainstormMindmap] Failed to sort in a note:", err);
            }
          }
          if (!done.length) return;
          this._showToast(t("{count} Notizen zugeordnet", { count: done.length }));
          this._pushUndo(t("{count} Notizen", { count: done.length }), async () => {
            for (const id of done) await this._hass.callService("brainstorm", "update_idea", { id, parent_id: null });
          });
        });
      };
      load();
    });
  }

  // The AI groups loose notes into themes; nothing moves until the person picks
  _showClusterDialog() {
    if (!this._hass) return;
    const category = this._sortInCategory();
    if (!category) {
      this._showToast(t("Wähle zuerst eine Kategorie."));
      return;
    }
    this._openDialog(t("✨ Nach Themen gruppieren"), (body) => {
      const showMessage = (message, isError) => {
        if (!this._isModalOpen) return;
        body.innerHTML = `
          <div class="${isError ? "dialog-error" : "dialog-hint"}" style="display: flex;">${message}</div>
          <div class="dialog-footer">
            <button class="dialog-btn dialog-btn-cancel" id="clusterCancel">${t("Schließen")}</button>
            <button class="dialog-btn dialog-btn-primary" id="clusterRetry">${t("Nochmal versuchen")}</button>
          </div>`;
        body.querySelector("#clusterCancel").addEventListener("click", () => this._closeDialog());
        body.querySelector("#clusterRetry").addEventListener("click", load);
      };
      const load = async () => {
        body.innerHTML = `<div class="dialog-label suggest-status">${t("Die KI denkt nach …")}</div>`;
        let themes;
        try {
          const result = await this._hass.callWS({
            type: "brainstorm/cluster_ideas",
            category,
            ...(this._hass.language ? { language: this._hass.language } : {}),
          });
          themes = (result && result.themes) || [];
        } catch (err) {
          showMessage(
            err && err.code === "too_few_notes"
              ? t("Zum Gruppieren braucht es mindestens vier lose Notizen ohne Unterpunkte.")
              : this._aiErrorText(err, t("Die KI hat keine Themen geliefert.")),
            true,
          );
          return;
        }
        if (!this._isModalOpen) return;
        if (!themes.length) {
          showMessage(t("Die KI hat keine Themen gefunden, in die mehrere Notizen passen."), false);
          return;
        }
        body.innerHTML = `
          <div class="dialog-label">${t("Jedes Thema wird ein Oberpunkt, die Notizen kommen darunter. Haken weg bei allem, was bleiben soll, wo es ist. Die Titel kannst du ändern.")}</div>
          <div class="suggest-list map-preview cluster-preview">
            ${themes.map((theme, index) => `
              <label class="suggest-row" data-depth="0" data-theme="${index}">
                <input type="checkbox" class="suggest-check cluster-theme" data-theme="${index}" checked />
                <input type="text" class="dialog-input suggest-text" data-theme="${index}" maxlength="200" value="${this._escapeHtml(theme.title)}" />
              </label>
              ${theme.ideas.map((idea, member) => `
                <label class="suggest-row cluster-member" data-depth="1" style="padding-left: 18px;">
                  <input type="checkbox" class="suggest-check cluster-note" data-theme="${index}" data-member="${member}" checked />
                  <span class="sortin-text">${formatText(idea.text)}</span>
                </label>`).join("")}`).join("")}
          </div>
          <div class="dialog-error" id="clusterError"></div>
          <div class="dialog-footer">
            <button class="dialog-btn dialog-btn-cancel" id="clusterRetry">${t("Neue Vorschläge")}</button>
            <button class="dialog-btn dialog-btn-primary" id="clusterSave"></button>
          </div>`;
        const saveBtn = body.querySelector("#clusterSave");
        const picked = () =>
          themes
            .map((theme, index) => {
              const on = body.querySelector(`.cluster-theme[data-theme="${index}"]`).checked;
              const title = body.querySelector(`.suggest-text[data-theme="${index}"]`).value.replace(/\s+/g, " ").trim();
              const ids = theme.ideas
                .filter((_, member) => body.querySelector(`.cluster-note[data-theme="${index}"][data-member="${member}"]`).checked)
                .map((idea) => idea.idea_id);
              const kept = on && Boolean(title);
              body.querySelector(`.suggest-row[data-theme="${index}"]`).classList.toggle("off", !kept);
              body.querySelectorAll(`.cluster-note[data-theme="${index}"]`).forEach((box) => {
                box.closest(".suggest-row").classList.toggle("off", !kept || !box.checked);
              });
              return { title, ids, on };
            })
            .filter((theme) => theme.on && theme.title && theme.ids.length);
        const update = () => {
          const count = picked().length;
          saveBtn.textContent = t("{count} Themen anlegen", { count });
          saveBtn.disabled = count === 0;
        };
        body.querySelectorAll(".suggest-check, .suggest-text").forEach((el) => el.addEventListener("input", update));
        update();
        body.querySelector("#clusterRetry").addEventListener("click", load);
        saveBtn.addEventListener("click", async () => {
          const groups = picked();
          if (!groups.length) return;
          saveBtn.disabled = true;
          const created = [];
          for (const group of groups) {
            try {
              const result = await this._hass.callWS({
                type: "call_service",
                domain: "brainstorm",
                service: "group_ideas",
                service_data: { title: group.title, ids: group.ids },
                return_response: true,
              });
              const id = result && result.response && result.response.id;
              if (id) created.push(id);
            } catch (err) {
              console.error("[BrainstormMindmap] Failed to group notes:", err);
              const error = body.querySelector("#clusterError");
              if (error) {
                error.textContent = err && err.message ? err.message : t("Gruppieren hat nicht geklappt.");
                error.style.display = "flex";
              }
            }
          }
          if (created.length) {
            this._showToast(t("{count} Themen angelegt", { count: created.length }));
            // Deleting the new notes makes their notes main notes again
            this._pushUndo(t("{count} Themen", { count: created.length }), () =>
              Promise.all(created.map((id) => this._hass.callService("brainstorm", "delete_idea", { id }))),
            );
          }
          if (created.length === groups.length) this._closeDialog();
          else saveBtn.disabled = false;
        });
      };
      load();
    });
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

  // The comments of a note: read, write, delete your own
  _showComments(idea) {
    if (!this._hass || !idea) return;
    this._openDialog(t("💬 Kommentare"), (body) => renderComments(body, { hass: this._hass, idea, close: () => this._closeDialog() }));
  }

  // Let the AI turn a topic or a pasted text into notes, picked in a preview
  _showGenerateMapDialog(prefill = "") {
    if (!this._hass) return;
    const focus = this._focusIdea();
    const target = focus
      ? t("Landet unter „{text}“.", { text: this._escapeHtml(focus.text) })
      : this._selectedCategory === "all"
        ? t("Landet in der Standardkategorie.")
        : t("Landet als Hauptnotizen in „{category}“.", { category: this._escapeHtml(this._selectedCategory) });
    let input = String(prefill || "");
    this._openDialog(t("✨ Map aus Thema erzeugen"), (body) => {
      const showInput = (error = "") => {
        if (!this._isModalOpen) return;
        body.innerHTML = `
          <div class="dialog-hint">${t("Ein Thema wie „Sommerfest planen“ oder einen längeren Text einfügen. Die KI macht daraus eine Map mit bis zu drei Ebenen, du wählst vor dem Übernehmen aus.")}</div>
          <textarea class="dialog-input dialog-textarea" id="mapTopic" rows="5" maxlength="6000" placeholder="${t("Thema oder Text")}"></textarea>
          <div class="dialog-hint outline-target">${target}</div>
          <div class="dialog-error" id="mapError" style="display: ${error ? "flex" : "none"};">${error}</div>
          <div class="dialog-footer">
            <button class="dialog-btn dialog-btn-cancel" id="mapCancel">${t("Abbrechen")}</button>
            <button class="dialog-btn dialog-btn-primary" id="mapGenerate">✨ ${t("Erzeugen")}</button>
          </div>
        `;
        const area = body.querySelector("#mapTopic");
        const go = body.querySelector("#mapGenerate");
        area.value = input;
        go.disabled = !input.trim();
        area.addEventListener("input", () => {
          input = area.value;
          go.disabled = !input.trim();
        });
        area.addEventListener("keydown", (e) => {
          if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && input.trim()) {
            e.preventDefault();
            load();
          }
        });
        body.querySelector("#mapCancel").addEventListener("click", () => this._closeDialog());
        go.addEventListener("click", load);
        setTimeout(() => area.focus(), 50);
      };
      const showPreview = (nodes) => {
        if (!this._isModalOpen) return;
        body.innerHTML = `
          <div class="dialog-label">${t("Haken weg bei allem, was du nicht willst. Unterpunkte rücken dann nach oben. Du kannst die Texte noch ändern.")}</div>
          <div class="suggest-list map-preview">
            ${nodes
              .map(
                (node, index) => `
              <label class="suggest-row" data-depth="${node.depth}" style="padding-left: ${node.depth * 18}px;">
                <input type="checkbox" class="suggest-check" data-index="${index}" checked />
                <input type="text" class="dialog-input suggest-text" data-index="${index}" maxlength="200" value="${this._escapeHtml(node.text)}" />
              </label>`
              )
              .join("")}
          </div>
          <div class="dialog-hint outline-target">${target}</div>
          <div class="dialog-error" id="mapError"></div>
          <div class="dialog-footer">
            <button class="dialog-btn dialog-btn-cancel" id="mapBack">${t("Zurück")}</button>
            <button class="dialog-btn dialog-btn-cancel" id="mapRetry">${t("Neue Vorschläge")}</button>
            <button class="dialog-btn dialog-btn-primary" id="mapSave"></button>
          </div>
        `;
        const saveBtn = body.querySelector("#mapSave");
        const outline = () => {
          // A note below one that is left out moves up to the next one kept
          const kept = [];
          const lines = [];
          nodes.forEach((node, index) => {
            const box = body.querySelector(`.suggest-check[data-index="${index}"]`);
            const text = body.querySelector(`.suggest-text[data-index="${index}"]`).value.trim();
            const on = box.checked && Boolean(text);
            box.closest(".suggest-row").classList.toggle("off", !on);
            kept.length = node.depth;
            const depth = kept.filter(Boolean).length;
            kept[node.depth] = on;
            if (on) lines.push(`${"  ".repeat(depth)}- ${text.replace(/\s+/g, " ")}`);
          });
          return lines;
        };
        const update = () => {
          const count = outline().length;
          saveBtn.textContent = t("{count} übernehmen", { count });
          saveBtn.disabled = count === 0;
        };
        body.querySelectorAll(".suggest-check, .suggest-text").forEach((el) => el.addEventListener("input", update));
        update();
        body.querySelector("#mapBack").addEventListener("click", () => showInput());
        body.querySelector("#mapRetry").addEventListener("click", load);
        saveBtn.addEventListener("click", async () => {
          const lines = outline();
          if (!lines.length) return;
          saveBtn.disabled = true;
          const error = body.querySelector("#mapError");
          const ok = await this._importOutline(lines.join("\n"), (message) => {
            error.textContent = message;
            error.style.display = "flex";
          });
          if (ok) this._closeDialog();
          else saveBtn.disabled = false;
        });
      };
      const load = async () => {
        if (!input.trim()) return;
        body.innerHTML = `<div class="dialog-label suggest-status">${t("Die KI denkt nach …")}</div>`;
        try {
          const result = await this._hass.callWS({
            type: "brainstorm/generate_map",
            text: input.trim(),
            ...(this._hass.language ? { language: this._hass.language } : {}),
          });
          const nodes = (result && result.nodes) || [];
          if (!nodes.length) showInput(t("Die KI hat keine Map geliefert."));
          else showPreview(nodes);
        } catch (err) {
          const code = err && err.code;
          showInput(
            code === "ai_not_configured"
              ? t("Wähle zuerst eine KI-Aufgaben-Entität unter Brainstorm Hub ➔ Konfigurieren ➔ KI.")
              : code === "ai_unavailable"
                ? t("Die KI ist gerade nicht erreichbar. Versuch es gleich nochmal.")
                : t("Die KI hat keine Map geliefert.")
          );
        }
      };
      showInput();
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
    const focus = this._focusIdea();
    const inAll = this._selectedCategory === "all";
    const target = focus
      ? t("Landet unter „{text}“.", { text: this._escapeHtml(focus.text) })
      : inAll
        ? t("Landet in der Standardkategorie.")
        : t("Landet als Hauptnotizen in „{category}“.", { category: this._escapeHtml(this._selectedCategory) });
    this._openDialog(t("🖼️ Map speichern und einfügen"), (body) => {
      body.innerHTML = `
        <div class="dialog-label">${t("Als Bild:")}</div>
        <div class="dialog-hint">${t("Gespeichert wird, was gerade auf der Map steht, ohne eingeklappte Zweige.")}</div>
        <div class="export-row">
          <button class="dialog-btn dialog-btn-cancel" data-export="svg">${t("SVG (Vektor)")}</button>
          <button class="dialog-btn dialog-btn-cancel" data-export="png">${t("PNG (Bild)")}</button>
        </div>
        <div class="dialog-label">${t("Als PDF:")}</div>
        <div class="dialog-hint">${t("Zum Drucken oder Weitergeben: das Bild der Map und danach alle Notizen als Gliederung mit Beschreibung.")}</div>
        <div class="export-row">
          <button class="dialog-btn dialog-btn-cancel" data-export="pdf">📄 ${t("PDF (Map und Gliederung)")}</button>
          <button class="dialog-btn dialog-btn-cancel" data-export="pdf-outline">${t("PDF (nur Gliederung)")}</button>
        </div>
        <div class="dialog-label">${t("Als Gliederung:")}</div>
        <div class="dialog-hint">${t("Alle Notizen dieser Map, auch eingeklappte, für andere Mindmap- und Gliederungsprogramme.")}</div>
        <div class="export-row">
          <button class="dialog-btn dialog-btn-cancel" data-export="md">${t("Markdown")}</button>
          <button class="dialog-btn dialog-btn-cancel" data-export="opml" data-lvl="pro">${t("OPML")}</button>
          <button class="dialog-btn dialog-btn-cancel" data-export="mm" data-lvl="pro">${t("FreeMind (.mm)")}</button>
        </div>
        <div class="dialog-label">${t("Gliederung einfügen:")}</div>
        <div class="dialog-hint">${t("Vorlage wählen, anpassen und einfügen:")}</div>
        <div class="template-chips">
          ${contentTemplates().map((tpl) => `<button class="template-chip" data-template="${tpl.key}">${tpl.icon} ${this._escapeHtml(tpl.name)}</button>`).join("")}
          ${this._aiAvailable() ? `<button class="template-chip" id="outlineAi" data-lvl="normal">✨ ${t("Mit KI erzeugen")}</button>` : ""}
        </div>
        <textarea class="dialog-input dialog-textarea" id="outlineText" rows="5" placeholder="${t("Eine Zeile pro Notiz, Unterpunkte eingerückt oder als Markdown-Liste. Oder eine Datei wählen.")}"></textarea>
        <div class="export-row">
          <label class="dialog-btn dialog-btn-cancel outline-file">📂 ${t("Datei wählen")}<input type="file" id="outlineFile" accept=".md,.markdown,.txt,.opml,.mm,.xml,text/plain,text/markdown,text/xml"></label>
          <span class="dialog-hint outline-target">${target}</span>
        </div>
        <div class="dialog-error" id="outlineError"></div>
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="outlineCancel">${t("Schließen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="outlineImport" disabled>${t("Einfügen")}</button>
        </div>
      `;
      body.querySelectorAll("[data-export]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const kind = btn.getAttribute("data-export");
          this._closeDialog();
          if (kind === "svg" || kind === "png") this._exportMap(kind);
          else if (kind === "pdf" || kind === "pdf-outline") this._exportPdf(kind === "pdf");
          else this._exportOutline(kind);
        });
      });
      const text = body.querySelector("#outlineText");
      const importBtn = body.querySelector("#outlineImport");
      const error = body.querySelector("#outlineError");
      text.addEventListener("input", () => {
        importBtn.disabled = !text.value.trim();
      });
      body.querySelectorAll("[data-template]").forEach((chip) => {
        chip.addEventListener("click", () => {
          const tpl = contentTemplates().find((item) => item.key === chip.dataset.template);
          if (!tpl) return;
          text.value = tpl.outline;
          importBtn.disabled = false;
          error.textContent = "";
          text.focus();
        });
      });
      body.querySelector("#outlineFile").addEventListener("change", (e) => {
        const file = e.target.files && e.target.files[0];
        if (!file) return;
        if (file.size > 200000) {
          error.textContent = t("Die Datei ist zu groß (höchstens 200 KB).");
          return;
        }
        const reader = new FileReader();
        reader.onload = () => {
          text.value = String(reader.result || "");
          importBtn.disabled = !text.value.trim();
          error.textContent = "";
        };
        reader.readAsText(file);
      });
      body.querySelector("#outlineCancel").addEventListener("click", () => this._closeDialog());
      const outlineAi = body.querySelector("#outlineAi");
      if (outlineAi) outlineAi.addEventListener("click", () => this._showGenerateMapDialog(text.value));
      importBtn.addEventListener("click", async () => {
        importBtn.disabled = true;
        error.textContent = "";
        const ok = await this._importOutline(text.value, (message) => {
          error.textContent = message;
        });
        if (ok) this._closeDialog();
        else importBtn.disabled = false;
      });
    });
  }

  // Download the notes of this map, or of the focused branch, as an outline
  _exportOutline(kind) {
    const sensor = this._getSensorEntity();
    const focus = this._focusIdea();
    const ideas = this._categoryIdeas();
    if (!sensor || !ideas.length) {
      this._showToast(t("Auf der Map ist nichts zum Speichern"));
      return;
    }
    const title = focus ? focus.text : this._selectedCategory === "all" ? t("Alle") : this._selectedCategory;
    const files = {
      md: [outlineMarkdown, "text/markdown"],
      opml: [outlineOpml, "text/x-opml"],
      mm: [outlineFreemind, "application/x-freemind"],
    };
    const [build, type] = files[kind];
    this._downloadBlob(new Blob([build(ideas, title)], { type: `${type};charset=utf-8` }), this._exportFileName(kind));
  }

  async _importOutline(text, onError) {
    const data = { text };
    if (this._focusId) data.parent_id = this._focusId;
    else if (this._selectedCategory !== "all") data.category = this._selectedCategory;
    try {
      const result = await this._hass.callWS({
        type: "call_service",
        domain: "brainstorm",
        service: "import_outline",
        service_data: data,
        return_response: true,
      });
      const response = (result && result.response) || {};
      const ids = response.ids || [];
      this._pushUndo(t("{count} Notizen", { count: ids.length }), () =>
        Promise.all(ids.map((id) => this._hass.callService("brainstorm", "delete_idea", { id }))),
      );
      this._showToast(t("{count} Notizen eingefügt.", { count: ids.length }));
      return true;
    } catch (err) {
      console.error("[BrainstormMindmap] Import failed:", err);
      onError(err && err.message ? err.message : t("Einfügen hat nicht geklappt."));
      return false;
    }
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

  // A PDF with the picture of the map and the outline of all its notes
  async _exportPdf(withMap) {
    const focus = this._focusIdea();
    const ideas = this._categoryIdeas();
    if (!ideas.length) {
      this._showToast(t("Auf der Map ist nichts zum Speichern"));
      return;
    }
    const title = focus ? focus.text : this._selectedCategory === "all" ? t("Alle") : this._selectedCategory;
    try {
      let map = null;
      const image = withMap ? this._buildMapSvg() : null;
      if (image) {
        // At most 3000 pixels on the long side keeps the file small enough
        const scale = Math.min(2, 3000 / Math.max(image.width, image.height));
        const blob = await this._svgToPng(image, scale, "image/jpeg");
        map = {
          jpeg: new Uint8Array(await blob.arrayBuffer()),
          width: image.width,
          height: image.height,
          pixelWidth: Math.ceil(image.width * scale),
          pixelHeight: Math.ceil(image.height * scale),
        };
      }
      const pdf = outlinePdf(ideas, title, map);
      this._downloadBlob(new Blob([pdf], { type: "application/pdf" }), this._exportFileName("pdf"));
    } catch (err) {
      console.error("[BrainstormMindmap] PDF export failed:", err);
      this._showToast(t("Speichern als PDF ging nicht"));
    }
  }

  // Draws the SVG onto a canvas at twice the size, for sharp pictures
  _svgToPng(image, scale = 2, type = "image/png") {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(new Blob([image.markup], { type: "image/svg+xml" }));
      const img = new Image();
      img.onload = () => {
        try {
          const canvas = document.createElement("canvas");
          canvas.width = Math.ceil(image.width * scale);
          canvas.height = Math.ceil(image.height * scale);
          const ctx = canvas.getContext("2d");
          if (type === "image/jpeg") {
            // JPEG has no transparency, so the page gets a white ground first
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
          }
          ctx.scale(scale, scale);
          ctx.drawImage(img, 0, 0, image.width, image.height);
          URL.revokeObjectURL(url);
          canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error("empty canvas"))), type, 0.9);
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
      // Markers and progress go in front of the text, as signs
      const marksEl = el.querySelector(".cloud-marks");
      const marks = marksEl ? marksEl.textContent.replace(/\s+/g, " ").trim() : "";
      const text = textEl ? textEl.textContent.trim() : "";
      const lines = wrap(marks ? `${marks}  ${text}` : text, font, width - padX * 2);
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

    const sketch = this._sketchMarkup(true);
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
    if (sketch.box) {
      minX = Math.min(minX, sketch.box.minX);
      minY = Math.min(minY, sketch.box.minY);
      maxX = Math.max(maxX, sketch.box.maxX);
      maxY = Math.max(maxY, sketch.box.maxY);
    }
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
    sr.querySelectorAll("#connectorsLayer rect").forEach((rect) => {
      const style = getComputedStyle(rect);
      body += `<rect x="${xml(rect.getAttribute("x"))}" y="${xml(rect.getAttribute("y"))}" width="${xml(rect.getAttribute("width"))}" height="${xml(rect.getAttribute("height"))}" rx="${xml(rect.getAttribute("rx") || 0)}" fill="${xml(style.fill)}" fill-opacity="${xml(style.fillOpacity)}" stroke="${xml(style.stroke)}" stroke-width="${xml(px(style.strokeWidth) || 1)}"${style.strokeDasharray && style.strokeDasharray !== "none" ? ` stroke-dasharray="${xml(style.strokeDasharray)}"` : ""}/>`;
    });
    sr.querySelectorAll("#connectorsLayer text").forEach((text) => {
      const style = getComputedStyle(text);
      body += `<text x="${xml(text.getAttribute("x"))}" y="${xml(text.getAttribute("y"))}" text-anchor="${xml(text.getAttribute("text-anchor") || "start")}" font-family="sans-serif" font-size="${xml(px(style.fontSize) || 11)}" font-weight="${xml(style.fontWeight)}" fill="${xml(style.fill)}">${xml(text.firstChild ? text.firstChild.textContent : "")}</text>`;
    });
    sr.querySelectorAll("#connectorsLayer path:not(.link-hit):not(.link-arrow)").forEach((path) => {
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
      sketch.markup +
      `</svg>`;
    return { markup, width, height };
  }

  // --- Search and filter: hits stay bright, the rest of the map fades ---

  _bindFilterEvents() {
    const filterBtn = this.shadowRoot.getElementById("filterBtn");
    const input = this.shadowRoot.getElementById("filterInput");
    const close = this.shadowRoot.getElementById("filterClose");
    const chips = this.shadowRoot.getElementById("filterChips");
    if (filterBtn) filterBtn.addEventListener("click", () => this._setFilterOpen(!this._filterOpen));
    const rulesBtn = this.shadowRoot.getElementById("filterRules");
    if (rulesBtn) rulesBtn.addEventListener("click", () => this._showRulesDialog());
    if (close) close.addEventListener("click", () => this._setFilterOpen(false));
    if (input) {
      input.addEventListener("input", () => {
        this._filter.query = input.value;
        this._hitIndex = -1;
        this._applyFilter();
      });
      input.addEventListener("keydown", (e) => {
        e.stopPropagation();
        if (e.key === "Enter") {
          e.preventDefault();
          this._jumpToHit(e.shiftKey ? -1 : 1);
        } else if (e.key === "Escape") {
          e.preventDefault();
          if (input.value) {
            input.value = "";
            this._filter.query = "";
            this._applyFilter();
          } else {
            this._setFilterOpen(false);
          }
        }
      });
    }
    if (chips) {
      chips.addEventListener("click", (e) => {
        const chip = e.target.closest(".filter-chip");
        if (!chip) return;
        const kind = chip.getAttribute("data-kind");
        const value = chip.getAttribute("data-value");
        if (kind === "prio") {
          if (this._filter.prios.has(value)) this._filter.prios.delete(value);
          else this._filter.prios.add(value);
        } else if (kind === "tag") {
          this._toggleFilterTag(value);
          return;
        } else if (kind === "marker") {
          this._toggleFilterMarker(value);
          return;
        } else if (kind === "flag") {
          this._filter[value] = !this._filter[value];
        }
        this._hitIndex = -1;
        this._renderFilterChips();
        this._applyFilter();
      });
    }
  }

  // Closing the bar also drops the filter, so nothing stays hidden unseen
  _setFilterOpen(open) {
    this._filterOpen = Boolean(open);
    const bar = this.shadowRoot.getElementById("filterBar");
    const input = this.shadowRoot.getElementById("filterInput");
    const filterBtn = this.shadowRoot.getElementById("filterBtn");
    if (bar) bar.classList.toggle("open", this._filterOpen);
    if (filterBtn) filterBtn.setAttribute("aria-pressed", String(this._filterOpen));
    if (this._filterOpen) {
      this._renderFilterChips();
      if (input) setTimeout(() => input.focus({ preventScroll: true }), 0);
    } else {
      this._filter = emptyFilter();
      this._hitIndex = -1;
      if (input) input.value = "";
      this._focusMap();
    }
    this._applyFilter();
  }

  _toggleFilterTag(tag) {
    if (!tag) return;
    if (this._filter.tags.has(tag)) this._filter.tags.delete(tag);
    else this._filter.tags.add(tag);
    this._hitIndex = -1;
    if (!this._filterOpen) {
      this._setFilterOpen(true);
      return;
    }
    this._renderFilterChips();
    this._applyFilter();
  }

  _toggleFilterMarker(marker) {
    if (!MARKERS.includes(marker)) return;
    if (this._filter.markers.has(marker)) this._filter.markers.delete(marker);
    else this._filter.markers.add(marker);
    this._hitIndex = -1;
    if (!this._filterOpen) {
      this._setFilterOpen(true);
      return;
    }
    this._renderFilterChips();
    this._applyFilter();
  }

  // A note without subtasks moves on by a quarter, 100 % goes back to 0
  async _cycleProgress(idea) {
    if (!idea || (idea.subtasks && idea.subtasks.total)) return;
    const before = Number(idea.progress) || 0;
    const next = nextProgress(before);
    try {
      await this._hass.callService("brainstorm", "update_idea", { id: idea.id, progress: next });
      this._pushUndo(idea.text, () => this._hass.callService("brainstorm", "update_idea", { id: idea.id, progress: before }));
    } catch (err) {
      console.error("[BrainstormMindmap] Failed to set the progress:", err);
    }
  }

  // --- Pictures: the first image attachment shows inside its note ---

  _loadNodeImages(container) {
    container.querySelectorAll(".cloud-image").forEach((box) => {
      const img = box.querySelector("img");
      attachmentUrl(this._hass, box.dataset.id, box.dataset.att)
        .then((url) => {
          if (img) img.src = url;
        })
        .catch((err) => {
          console.warn("[BrainstormMindmap] Picture could not be loaded:", err);
          box.remove();
        });
      if (img) img.addEventListener("error", () => box.classList.add("broken"));
      box.addEventListener("click", async (e) => {
        // Linking and picking several notes work on the picture as well
        if (e.shiftKey || e.ctrlKey || e.metaKey || this._lassoMode || this._linkFrom) return;
        e.stopPropagation();
        if (Date.now() - (this._dragEndedAt || 0) < 300) return;
        // Open the window first, so pop-up blockers see the tap
        const win = window.open("", "_blank");
        try {
          const url = await attachmentUrl(this._hass, box.dataset.id, box.dataset.att);
          if (win) win.location.href = url;
          else window.location.href = url;
        } catch (err) {
          if (win) win.close();
          console.error("[BrainstormMindmap] Picture could not be opened:", err);
        }
      });
    });
  }

  // --- Rules: notes that fit a saved filter get its color and sign ---

  _applyRules() {
    if (!this.shadowRoot) return;
    const clouds = this.shadowRoot.querySelectorAll(".note-cloud");
    if (!clouds.length) return;
    const byId = new Map(this._categoryIdeas().map((idea) => [idea.id, idea]));
    const now = new Date();
    clouds.forEach((el) => {
      const idea = byId.get(el.getAttribute("data-id"));
      const rule = idea && this._rules.length ? ruleFor(idea, this._rules, now) : null;
      const old = el.querySelector(":scope > .rule-badge");
      if (old) old.remove();
      el.classList.toggle("rule-hit", Boolean(rule && rule.color));
      if (rule && rule.color) el.style.setProperty("--rule-color", rule.color);
      else el.style.removeProperty("--rule-color");
      if (rule && rule.icon) {
        const badge = document.createElement("span");
        badge.className = "rule-badge";
        badge.textContent = rule.icon;
        badge.title = rule.name || ruleSummary(rule);
        el.appendChild(badge);
      }
    });
  }

  async _storeRules(rules) {
    try {
      this._rules = await saveRules(this._hass, rules);
    } catch (err) {
      console.error("[BrainstormMindmap] Failed to save the rules:", err);
      this._showToast(t("Die Regeln konnten nicht gespeichert werden."));
    }
    this._applyRules();
  }

  _showRulesDialog() {
    this._openDialog(t("🎨 Regeln"), (body) => {
      const canAdd = filterActive(this._filter);
      const rules = this._rules;
      body.innerHTML = `
        <div class="dialog-hint">${t("Regeln färben jede Notiz, die zu einem gespeicherten Filter passt, und setzen ein Zeichen daran. Die erste passende Regel gilt. Sie gelten für dich auf allen Geräten.")}</div>
        <div class="rule-list">
          ${rules.length ? rules.map((rule, index) => `
            <div class="rule-row${rule.enabled ? "" : " off"}" style="--rule-color: ${rule.color || "var(--divider-color)"};">
              <input type="checkbox" class="rule-on" data-index="${index}" ${rule.enabled ? "checked" : ""} title="${t("Regel an oder aus")}" />
              <div class="rule-main">
                <div class="rule-name">${rule.icon ? `${this._escapeHtml(rule.icon)} ` : ""}${this._escapeHtml(rule.name || t("Regel {number}", { number: index + 1 }))}</div>
                <div class="rule-when">${this._escapeHtml(ruleSummary(rule))}</div>
              </div>
              <button class="rule-up" data-index="${index}" title="${t("Nach oben")}" ${index ? "" : "disabled"}>↑</button>
              <button class="rule-edit" data-index="${index}" title="${t("Bearbeiten")}">✎</button>
              <button class="rule-delete" data-index="${index}" title="${t("Löschen")}">🗑️</button>
            </div>`).join("") : `<div class="dialog-label">${t("Noch keine Regeln.")}</div>`}
        </div>
        ${canAdd ? "" : `<div class="dialog-hint">${t("Für eine neue Regel stelle zuerst in der Suche 🔍 einen Filter ein, z. B. 🔥 Dringend oder #garten, und tippe dann hier auf ＋.")}</div>`}
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="rulesClose">${t("Schließen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="rulesAdd" ${canAdd ? "" : "disabled"}>＋ ${t("Aktuellen Filter als Regel")}</button>
        </div>`;
      body.querySelector("#rulesClose").addEventListener("click", () => this._closeDialog());
      body.querySelector("#rulesAdd").addEventListener("click", () => {
        if (!canAdd) return;
        this._showRuleEditor(null, { when: filterToRule(this._filter), color: RULE_COLORS[0], icon: "", name: "", enabled: true });
      });
      const at = (btn) => Number(btn.getAttribute("data-index"));
      body.querySelectorAll(".rule-on").forEach((box) => {
        box.addEventListener("change", async () => {
          const next = rules.map((rule, index) => (index === at(box) ? { ...rule, enabled: box.checked } : rule));
          await this._storeRules(next);
          this._showRulesDialog();
        });
      });
      body.querySelectorAll(".rule-up").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const index = at(btn);
          if (!index) return;
          const next = [...rules];
          [next[index - 1], next[index]] = [next[index], next[index - 1]];
          await this._storeRules(next);
          this._showRulesDialog();
        });
      });
      body.querySelectorAll(".rule-edit").forEach((btn) => {
        btn.addEventListener("click", () => this._showRuleEditor(at(btn), rules[at(btn)]));
      });
      body.querySelectorAll(".rule-delete").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const removed = rules[at(btn)];
          await this._storeRules(rules.filter((_, index) => index !== at(btn)));
          this._pushUndo(removed.name || ruleSummary(removed), () => this._storeRules([...this._rules, removed]));
          this._showRulesDialog();
        });
      });
    });
  }

  _showRuleEditor(index, rule) {
    const icons = ["", "🔥", "⚠️", "⭐", "❗", "🚩", "💰", "⏰", "✅", "💤"];
    let color = rule.color || "";
    let icon = rule.icon || "";
    this._openDialog(index === null ? t("🎨 Neue Regel") : t("🎨 Regel bearbeiten"), (body) => {
      body.innerHTML = `
        <div class="dialog-label">${t("Wenn")}</div>
        <div class="rule-when" style="margin-bottom: 12px;">${this._escapeHtml(ruleSummary(rule))}</div>
        <label class="dialog-label" for="ruleName">${t("Name")}</label>
        <input class="dialog-input" id="ruleName" maxlength="60" value="${this._escapeHtml(rule.name || "")}" placeholder="${t("z. B. Brennt")}" />
        <div class="dialog-label">${t("Farbe")}</div>
        <div class="rule-swatches" id="ruleColors">
          <button class="rule-swatch none${color ? "" : " active"}" data-color="" title="${t("Keine Farbe")}">∅</button>
          ${RULE_COLORS.map((value) => `<button class="rule-swatch${value === color ? " active" : ""}" data-color="${value}" style="--swatch: ${value};" title="${value}"></button>`).join("")}
        </div>
        <div class="dialog-label">${t("Zeichen")}</div>
        <div class="rule-swatches" id="ruleIcons">
          ${icons.map((value) => `<button class="rule-swatch icon${value === icon ? " active" : ""}" data-icon="${value}" title="${value || t("Kein Zeichen")}">${value || "∅"}</button>`).join("")}
        </div>
        <div class="dialog-error" id="ruleError"></div>
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="ruleBack">${t("Zurück")}</button>
          <button class="dialog-btn dialog-btn-primary" id="ruleSave">${t("Speichern")}</button>
        </div>`;
      const pick = (selector, attr, set) => {
        body.querySelectorAll(selector).forEach((btn) => {
          btn.addEventListener("click", () => {
            body.querySelectorAll(selector).forEach((other) => other.classList.toggle("active", other === btn));
            set(btn.getAttribute(attr));
          });
        });
      };
      pick("#ruleColors .rule-swatch", "data-color", (value) => (color = value));
      pick("#ruleIcons .rule-swatch", "data-icon", (value) => (icon = value));
      body.querySelector("#ruleBack").addEventListener("click", () => this._showRulesDialog());
      body.querySelector("#ruleSave").addEventListener("click", async () => {
        if (!color && !icon) {
          const error = body.querySelector("#ruleError");
          error.textContent = t("Wähle eine Farbe oder ein Zeichen.");
          error.style.display = "flex";
          return;
        }
        const saved = { ...rule, name: body.querySelector("#ruleName").value.trim(), color, icon };
        const next = [...this._rules];
        if (index === null) next.push(saved);
        else next[index] = saved;
        await this._storeRules(next);
        this._showRulesDialog();
      });
    });
  }

  _renderFilterChips() {
    const chips = this.shadowRoot && this.shadowRoot.getElementById("filterChips");
    if (!chips || !this._filterOpen) return;
    const ideas = this._categoryIdeas();
    const counts = new Map();
    ideas.forEach((idea) => ideaTags(idea).forEach((tag) => counts.set(tag, (counts.get(tag) || 0) + 1)));
    // Chosen tags stay even when no note of this list has them any more
    this._filter.tags.forEach((tag) => {
      if (!counts.has(tag)) counts.set(tag, 0);
    });
    const tags = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    const markerCounts = new Map();
    ideas.forEach((idea) => ideaMarkers(idea).forEach((marker) => markerCounts.set(marker, (markerCounts.get(marker) || 0) + 1)));
    const markers = MARKERS.filter((marker) => markerCounts.has(marker) || this._filter.markers.has(marker));
    const chip = (kind, value, label, title, on) =>
      `<button class="filter-chip${on ? " on" : ""}" data-kind="${kind}" data-value="${this._escapeHtml(value)}" title="${this._escapeHtml(title)}" aria-pressed="${on}">${label}</button>`;
    const prios = [
      ["urgent", "🔥", t("🔥 Dringend")],
      ["high", "🔴", t("🔴 Hoch")],
      ["medium", "🟡", t("🟡 Mittel")],
      ["low", "🟢", t("🟢 Niedrig")],
    ];
    chips.innerHTML = [
      ...prios.map(([value, icon, label]) => chip("prio", value, icon, label, this._filter.prios.has(value))),
      '<span class="filter-sep"></span>',
      chip("flag", "overdue", `⏰ ${t("Überfällig")}`, t("Termin ist vorbei"), this._filter.overdue),
      chip("flag", "soon", `📅 ${t("7 Tage")}`, t("Termin in den nächsten 7 Tagen"), this._filter.soon),
      chip("flag", "working", `🔧 ${t("In Arbeit")}`, t("Als „In Arbeit“ markiert"), this._filter.working),
      markers.length ? '<span class="filter-sep"></span>' : "",
      ...markers.map((marker) => chip("marker", marker, `${markerIcon(marker)}<span class="filter-chip-count">${markerCounts.get(marker) || 0}</span>`, t("Nur Notizen mit {marker}", { marker: markerLabel(marker) }), this._filter.markers.has(marker))),
      tags.length ? '<span class="filter-sep"></span>' : "",
      ...tags.map(([tag, count]) => chip("tag", tag, `#${this._escapeHtml(tag)}<span class="filter-chip-count">${count}</span>`, t("Nur Notizen mit #{tag}", { tag }), this._filter.tags.has(tag))),
    ].join("");
  }

  // Mark hits, their parents and the rest; a folded branch with hits says so
  _applyFilter() {
    if (!this.shadowRoot) return;
    const ideas = this._categoryIdeas();
    const active = filterActive(this._filter);
    const filterBtn = this.shadowRoot.getElementById("filterBtn");
    if (filterBtn) filterBtn.classList.toggle("filter-on", active);
    const countEl = this.shadowRoot.getElementById("filterCount");
    const clouds = this.shadowRoot.querySelectorAll(".note-cloud");
    const paths = this.shadowRoot.querySelectorAll(".synapse-path");
    if (!active) {
      this._filterHits = null;
      this._filterContext = new Set();
      clouds.forEach((el) => el.classList.remove("filter-hit", "filter-context", "filter-out", "filter-hidden-hits"));
      paths.forEach((el) => el.classList.remove("filter-out"));
      if (countEl) countEl.textContent = "";
      this._refreshMinimap();
      return;
    }
    const now = new Date();
    const hits = new Set(ideas.filter((idea) => ideaMatches(idea, this._filter, now)).map((i) => i.id));
    const ids = new Set(ideas.map((i) => i.id));
    const byId = new Map(ideas.map((i) => [i.id, i]));
    const context = new Set();
    const hiddenHits = new Set();
    hits.forEach((id) => {
      const seen = new Set([id]);
      let parent = this._branchParent(byId.get(id), ids);
      while (parent && !seen.has(parent)) {
        seen.add(parent);
        if (!hits.has(parent)) context.add(parent);
        if (this._collapsed.has(parent)) hiddenHits.add(parent);
        parent = this._branchParent(byId.get(parent), ids);
      }
    });
    this._filterHits = hits;
    this._filterContext = context;
    clouds.forEach((el) => {
      const id = el.getAttribute("data-id");
      el.classList.toggle("filter-hit", hits.has(id));
      el.classList.toggle("filter-context", context.has(id));
      el.classList.toggle("filter-out", !hits.has(id) && !context.has(id));
      el.classList.toggle("filter-hidden-hits", hiddenHits.has(id));
    });
    paths.forEach((el) => {
      const id = el.id.replace(/^path_/, "");
      el.classList.toggle("filter-out", !hits.has(id));
    });
    if (countEl) countEl.textContent = t("{hits} von {total}", { hits: hits.size, total: ideas.length });
    this._refreshMinimap();
  }

  // Enter walks through the hits, unfolds their branch and brings them into view
  _jumpToHit(direction) {
    if (!this._filterHits || !this._filterHits.size) return;
    const ideas = this._categoryIdeas();
    const order = ideas.filter((idea) => this._filterHits.has(idea.id));
    this._hitIndex = (this._hitIndex + direction + order.length) % order.length;
    const target = order[this._hitIndex];
    const ids = new Set(ideas.map((i) => i.id));
    const byId = new Map(ideas.map((i) => [i.id, i]));
    let unfolded = false;
    const seen = new Set([target.id]);
    let parent = this._branchParent(target, ids);
    while (parent && !seen.has(parent)) {
      seen.add(parent);
      if (this._collapsed.delete(parent)) unfolded = true;
      parent = this._branchParent(byId.get(parent), ids);
    }
    if (unfolded) {
      this._saveCollapsed();
      this._lastLayoutKey = "";
      this._updateContent();
    }
    const pos = this._nodePositions.get(target.id);
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    if (pos && canvasArea) {
      this._panX = canvasArea.clientWidth / 2 - pos.x * this._scale;
      this._panY = canvasArea.clientHeight / 2 - pos.y * this._scale;
      this._applyTransform();
    }
    this._selectedId = target.id;
    this.shadowRoot.querySelectorAll(".note-cloud.selected").forEach((el) => el.classList.remove("selected"));
    const el = this.shadowRoot.getElementById(`cloud_${target.id}`);
    if (el) el.classList.add("selected");
    const countEl = this.shadowRoot.getElementById("filterCount");
    if (countEl) countEl.textContent = t("{index}/{hits} von {total}", { index: this._hitIndex + 1, hits: order.length, total: ideas.length });
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

  // ---- Live presence: who else has the map open, and what they edit ----

  _joinPresence() {
    if (this._presenceSub || !this.isConnected || !this._hass || !this._hass.connection) return;
    if (this._presenceFailed) return;
    const connection = this._hass.connection;
    this._presenceSent = "";
    this._presenceSub = connection
      .subscribeMessage((event) => this._onPresence(event), {
        type: "brainstorm/presence/subscribe",
        token: this._presenceToken,
        category: this._selectedCategory || null,
      })
      .catch((err) => {
        // An older Brainstorm or too many open maps: just no avatars
        console.debug("[BrainstormMindmap] Presence unavailable:", err);
        this._presenceFailed = true;
        this._presenceSub = null;
        return null;
      });
  }

  _leavePresence() {
    const sub = this._presenceSub;
    this._presenceSub = null;
    this._present = [];
    if (sub) sub.then((unsub) => unsub && unsub()).catch(() => {});
  }

  _sendPresence() {
    if (!this._presenceSub || !this._hass) return;
    const state = { category: this._selectedCategory || null, editing: this._presenceEditing };
    const key = JSON.stringify(state);
    if (key === this._presenceSent) return;
    this._presenceSent = key;
    this._presenceSub
      .then((unsub) => unsub && this._hass.callWS({ type: "brainstorm/presence/update", token: this._presenceToken, ...state }))
      .catch(() => {
        // Lost while the subscription comes back; the next change tries again
        this._presenceSent = "";
      });
  }

  _setPresenceEditing(id) {
    this._presenceEditing = id || null;
    this._sendPresence();
  }

  _onPresence(event) {
    this._present = ((event && event.present) || []).filter((entry) => entry.key !== this._presenceToken);
    this._renderPresence();
  }

  // Others on the same list, one avatar per person, even with two devices
  _presentPeople() {
    const mine = this._selectedCategory;
    const people = new Map();
    this._present.forEach((entry) => {
      if (mine && mine !== "all" && entry.category !== mine && entry.category !== "all") return;
      const person = people.get(entry.user_id) || { user_id: entry.user_id, name: entry.name || "?", editing: [] };
      if (entry.editing) person.editing.push(entry.editing);
      people.set(entry.user_id, person);
    });
    return [...people.values()];
  }

  _personColor(userId) {
    const seed = [...String(userId)].reduce((sum, ch) => (sum * 31 + ch.charCodeAt(0)) % 360, 7);
    return `hsl(${seed}, 62%, 45%)`;
  }

  _initials(name) {
    const parts = String(name).trim().split(/\s+/).filter(Boolean);
    return ((parts[0] || "?")[0] + (parts.length > 1 ? parts[parts.length - 1][0] : "")).toUpperCase();
  }

  _renderPresence() {
    const sr = this.shadowRoot;
    const bar = sr && sr.getElementById("presenceBar");
    if (!bar) return;
    const people = this._presentPeople();
    const ideaText = (id) => {
      const idea = this._ideaById(id);
      return idea ? idea.text : null;
    };
    bar.innerHTML = people.slice(0, 6).map((person) => {
      const texts = person.editing.map(ideaText).filter(Boolean);
      const title = texts.length
        ? t("{name} bearbeitet „{text}“", { name: person.name, text: texts[0] })
        : t("{name} schaut sich die Map an", { name: person.name });
      return `<span class="presence-avatar${texts.length ? " editing" : ""}" style="--person-color: ${this._personColor(person.user_id)};" title="${this._escapeHtml(title)}" aria-label="${this._escapeHtml(title)}">${this._escapeHtml(this._initials(person.name))}</span>`;
    }).join("") + (people.length > 6 ? `<span class="presence-avatar presence-more">+${people.length - 6}</span>` : "");
    bar.classList.toggle("open", people.length > 0);
    // A name tag on the notes somebody is editing right now
    sr.querySelectorAll(".presence-tag").forEach((tag) => tag.remove());
    people.forEach((person) => {
      person.editing.forEach((id) => {
        const cloud = sr.getElementById(`cloud_${id}`);
        if (!cloud) return;
        const tag = document.createElement("span");
        tag.className = "presence-tag";
        tag.style.setProperty("--person-color", this._personColor(person.user_id));
        tag.textContent = `✏️ ${person.name}`;
        tag.title = t("{name} bearbeitet diese Notiz gerade", { name: person.name });
        cloud.appendChild(tag);
      });
    });
  }

  // ---- Drawing: pen, arrows and circles above the map of one category ----

  _syncDrawing(attributes) {
    if (!this._hass || !this._usesSavedPositions()) {
      this._strokes = [];
      this._strokesKey = null;
      if (this._drawMode) this._setDrawMode(false);
      return;
    }
    const category = this._selectedCategory;
    const revs = attributes.drawing_revs || {};
    const key = `${category}:${revs[category] || 0}`;
    if (key === this._strokesKey) return;
    this._strokesKey = key;
    if (!(category in revs)) {
      this._strokes = [];
      this._renderSketch();
      return;
    }
    this._hass
      .callWS({ type: "brainstorm/drawing", category })
      .then((reply) => {
        if (this._selectedCategory !== category) return;
        this._strokes = reply.strokes || [];
        this._renderSketch();
      })
      .catch((err) => console.error("[BrainstormMindmap] Failed to load the drawing:", err));
  }

  // Points of a stroke on the map, from their place relative to the center
  _strokePoints(stroke) {
    const c = this._centerPos || { x: 0, y: 0 };
    return stroke.points.map(([x, y]) => [c.x + x, c.y + y]);
  }

  _strokeShape(stroke, color) {
    const pts = this._strokePoints(stroke);
    const w = stroke.width;
    const attrs = `fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"`;
    const f = (n) => n.toFixed(1);
    if (stroke.kind === "ellipse") {
      const [[x1, y1], [x2, y2]] = pts;
      return `<ellipse cx="${f((x1 + x2) / 2)}" cy="${f((y1 + y2) / 2)}" rx="${f(Math.abs(x2 - x1) / 2)}" ry="${f(Math.abs(y2 - y1) / 2)}" ${attrs}/>`;
    }
    if (stroke.kind === "arrow") {
      const [[x1, y1], [x2, y2]] = pts;
      const angle = Math.atan2(y2 - y1, x2 - x1);
      const head = 10 + w * 2;
      const side = (turn) => `L ${f(x2 - head * Math.cos(angle + turn))} ${f(y2 - head * Math.sin(angle + turn))}`;
      return `<path d="M ${f(x1)} ${f(y1)} L ${f(x2)} ${f(y2)} M ${f(x2)} ${f(y2)} ${side(0.45)} M ${f(x2)} ${f(y2)} ${side(-0.45)}" ${attrs}/>`;
    }
    // A smooth line through the middles between the points
    let d = `M ${f(pts[0][0])} ${f(pts[0][1])}`;
    for (let i = 1; i < pts.length - 1; i++) {
      const [x, y] = pts[i];
      const [nx, ny] = pts[i + 1];
      d += ` Q ${f(x)} ${f(y)} ${f((x + nx) / 2)} ${f((y + ny) / 2)}`;
    }
    const last = pts[pts.length - 1];
    d += ` L ${f(last[0])} ${f(last[1])}`;
    return `<path d="${d}" ${attrs}/>`;
  }

  _sketchMarkup(forImage = false) {
    if (!this._usesSavedPositions() || !this._strokes.length) return { markup: "", box: null };
    let box = null;
    const markup = this._strokes.map((stroke) => {
      this._strokePoints(stroke).forEach(([x, y]) => {
        const pad = stroke.width + 14;
        box = box
          ? { minX: Math.min(box.minX, x - pad), minY: Math.min(box.minY, y - pad), maxX: Math.max(box.maxX, x + pad), maxY: Math.max(box.maxY, y + pad) }
          : { minX: x - pad, minY: y - pad, maxX: x + pad, maxY: y + pad };
      });
      const shape = this._strokeShape(stroke, DRAW_COLORS[stroke.color] || DRAW_COLORS.gray);
      return forImage ? shape : `<g data-stroke="${this._escapeHtml(stroke.id)}">${shape}</g>`;
    }).join("");
    return { markup, box };
  }

  _renderSketch() {
    const layer = this.shadowRoot && this.shadowRoot.getElementById("sketchLayer");
    if (!layer) return;
    const preview = this._sketchDraft ? this._strokeShape(this._sketchDraft, DRAW_COLORS[this._sketchDraft.color]) : "";
    layer.innerHTML = this._sketchMarkup().markup + preview;
  }

  _setDrawMode(on) {
    if (on && !this._usesSavedPositions()) {
      this._showToast(t("Zeichnen geht auf der runden Map einer einzelnen Kategorie."));
      return;
    }
    this._drawMode = Boolean(on);
    if (this._drawMode && this._lassoMode) this._setLassoMode(false);
    const sr = this.shadowRoot;
    const canvasArea = sr.getElementById("canvasArea");
    if (canvasArea) canvasArea.classList.toggle("draw-mode", this._drawMode);
    const btn = sr.getElementById("drawBtn");
    if (btn) {
      btn.classList.toggle("active", this._drawMode);
      btn.setAttribute("aria-pressed", String(this._drawMode));
    }
    this._sketchDraft = null;
    this._syncSketchBar();
  }

  _syncSketchBar() {
    const bar = this.shadowRoot.getElementById("sketchBar");
    if (!bar) return;
    bar.querySelectorAll("[data-tool]").forEach((b) => b.classList.toggle("active", b.dataset.tool === this._drawTool));
    bar.querySelectorAll("[data-color]").forEach((b) => b.classList.toggle("active", b.dataset.color === this._drawColor));
    bar.querySelectorAll("[data-width]").forEach((b) => b.classList.toggle("active", Number(b.dataset.width) === this._drawWidth));
  }

  _sketchPoint(e) {
    const canvasArea = this.shadowRoot.getElementById("canvasArea");
    const rect = canvasArea.getBoundingClientRect();
    const c = this._centerPos || { x: 0, y: 0 };
    return [
      Math.round(((e.clientX - rect.left - this._panX) / this._scale - c.x) * 10) / 10,
      Math.round(((e.clientY - rect.top - this._panY) / this._scale - c.y) * 10) / 10,
    ];
  }

  _bindSketch() {
    const sr = this.shadowRoot;
    const capture = sr.getElementById("sketchCapture");
    const bar = sr.getElementById("sketchBar");
    if (!capture || !bar) return;
    bar.addEventListener("click", (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      e.stopPropagation();
      if (btn.dataset.tool) this._drawTool = btn.dataset.tool;
      if (btn.dataset.color) {
        this._drawColor = btn.dataset.color;
        if (this._drawTool === "erase") this._drawTool = "pen";
      }
      if (btn.dataset.width) {
        this._drawWidth = Number(btn.dataset.width);
        if (this._drawTool === "erase") this._drawTool = "pen";
      }
      if (btn.dataset.sketch === "undo") this._undo();
      else if (btn.dataset.sketch === "clear") this._clearDrawing();
      else if (btn.dataset.sketch === "done") this._setDrawMode(false);
      this._syncSketchBar();
    });
    capture.addEventListener("wheel", (e) => {
      e.preventDefault();
      this._zoomAtPoint(e.deltaY < 0 ? 1.1 : 0.9, e.clientX, e.clientY);
    }, { passive: false });
    capture.addEventListener("pointerdown", (e) => {
      if (!this._drawMode || e.button > 0) return;
      e.preventDefault();
      try {
        capture.setPointerCapture(e.pointerId);
      } catch {}
      const point = this._sketchPoint(e);
      if (this._drawTool === "erase") {
        this._erasing = [];
        this._eraseAt(point);
        return;
      }
      this._sketchDraft = { kind: this._drawTool, color: this._drawColor, width: this._drawWidth, points: [point, point] };
      this._renderSketch();
    });
    capture.addEventListener("pointermove", (e) => {
      if (!this._drawMode) return;
      const point = this._sketchPoint(e);
      if (this._erasing) {
        this._eraseAt(point);
        return;
      }
      const draft = this._sketchDraft;
      if (!draft) return;
      if (draft.kind === "pen") {
        const [lx, ly] = draft.points[draft.points.length - 1];
        if (Math.hypot(point[0] - lx, point[1] - ly) < 2 / this._scale) return;
        if (draft.points.length === 2 && draft.points[0] === draft.points[1]) draft.points[1] = point;
        else draft.points.push(point);
      } else {
        draft.points[1] = point;
      }
      this._renderSketch();
    });
    const finish = () => {
      if (this._erasing) {
        const erased = this._erasing;
        this._erasing = null;
        if (erased.length) {
          this._pushUndo(t("Zeichnung"), async () => {
            for (const stroke of erased) await this._addStroke(stroke);
          });
        }
        return;
      }
      const draft = this._sketchDraft;
      this._sketchDraft = null;
      if (!draft) return;
      const [a, b] = [draft.points[0], draft.points[draft.points.length - 1]];
      if (Math.hypot(b[0] - a[0], b[1] - a[1]) < 4 && draft.points.length < 4) {
        this._renderSketch();
        return;
      }
      if (draft.kind === "pen") draft.points = simplifyStroke(draft.points);
      this._addStroke(draft).then((stroke) => {
        if (!stroke) return;
        this._pushUndo(t("Zeichnung"), () => this._deleteStrokes([stroke.id]));
      });
    };
    capture.addEventListener("pointerup", finish);
    capture.addEventListener("pointercancel", finish);
  }

  async _addStroke(stroke) {
    const category = this._selectedCategory;
    try {
      const reply = await this._hass.callWS({
        type: "brainstorm/add_stroke",
        category,
        kind: stroke.kind,
        points: stroke.points,
        color: stroke.color,
        width: stroke.width,
      });
      if (this._selectedCategory === category) this._strokes = [...this._strokes, reply.stroke];
      this._renderSketch();
      return reply.stroke;
    } catch (err) {
      console.error("[BrainstormMindmap] Failed to save the drawing:", err);
      this._showToast(err && err.code === "drawing_full"
        ? t("Die Map hat schon sehr viele Zeichnungen. Lösche zuerst welche.")
        : t("Die Zeichnung konnte nicht gespeichert werden."));
      this._renderSketch();
      return null;
    }
  }

  async _deleteStrokes(ids) {
    const category = this._selectedCategory;
    const gone = new Set(ids || this._strokes.map((stroke) => stroke.id));
    this._strokes = this._strokes.filter((stroke) => !gone.has(stroke.id));
    this._renderSketch();
    try {
      await this._hass.callWS({ type: "brainstorm/delete_strokes", category, ...(ids ? { ids } : {}) });
    } catch (err) {
      console.error("[BrainstormMindmap] Failed to delete the drawing:", err);
    }
  }

  // The stroke under the eraser goes at once, undo brings back all of one wipe
  _eraseAt(point) {
    const c = this._centerPos || { x: 0, y: 0 };
    const [px, py] = [point[0] + c.x, point[1] + c.y];
    const hit = [...this._strokes].reverse().find((stroke) => strokeDistance(this._strokePoints(stroke), stroke.kind, px, py) <= 8 / this._scale + stroke.width / 2);
    if (!hit) return;
    this._erasing.push(hit);
    this._deleteStrokes([hit.id]);
  }

  async _clearDrawing() {
    const all = [...this._strokes];
    if (!all.length) return;
    await this._deleteStrokes(null);
    this._showToast(t("Zeichnung gelöscht. ↶ holt sie zurück."));
    this._pushUndo(t("Zeichnung"), async () => {
      for (const stroke of all) await this._addStroke(stroke);
    });
  }

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
    // Picking several notes starts at the normal level
    if (!levelAllows(this._currentLevel(), "normal")) return;
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
    // Picking several notes starts at the normal level
    if (!levelAllows(this._currentLevel(), "normal")) return;
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
    const linkBtn = bar.querySelector('[data-multi="link"]');
    if (linkBtn) linkBtn.style.display = this._multi.size === 2 ? "" : "none";
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
    if (this._presentation) {
      // While presenting only the keys of a slide show count
      if (["ArrowRight", "ArrowDown", "PageDown", " ", "Enter"].includes(e.key)) {
        e.preventDefault();
        this._presentStep(1);
      } else if (["ArrowLeft", "ArrowUp", "PageUp", "Backspace"].includes(e.key)) {
        e.preventDefault();
        this._presentStep(-1);
      } else if (e.key === "Home") {
        e.preventDefault();
        this._presentGo(-1);
      }
      return;
    }
    const target = e.composedPath()[0];
    if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) return;
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey && e.key.toLowerCase() === "z") {
      e.preventDefault();
      this._undo();
      return;
    }
    // Slash or Ctrl+F opens the search, like in most programs
    if (this._config.show_filter === true && levelAllows(this._currentLevel(), "normal") && ((e.key === "/" && !e.ctrlKey && !e.metaKey && !e.altKey) || ((e.ctrlKey || e.metaKey) && !e.altKey && e.key.toLowerCase() === "f"))) {
      e.preventDefault();
      this._setFilterOpen(true);
      return;
    }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const level = this._currentLevel();
    const pro = levelAllows(level, "pro");
    const normal = levelAllows(level, "normal");
    if (this._linkFrom && e.key === "Escape") {
      e.preventDefault();
      e.stopPropagation();
      this._cancelLink();
      return;
    }
    if (this._drawMode && e.key === "Escape") {
      e.preventDefault();
      e.stopPropagation();
      this._setDrawMode(false);
      return;
    }
    if (normal && (e.key === "d" || e.key === "D")) {
      e.preventDefault();
      this._setDrawMode(!this._drawMode);
      return;
    }
    if (normal && (e.key === "v" || e.key === "V")) {
      e.preventDefault();
      this._showVotingDialog();
      return;
    }
    if (normal && (e.key === "m" || e.key === "M") && this._config.show_minimap !== false) {
      e.preventDefault();
      this._toggleMinimap();
      return;
    }
    if (pro && (e.key === "p" || e.key === "P")) {
      e.preventDefault();
      this._startPresentation();
      return;
    }
    if (normal && (e.key === "g" || e.key === "G") && this._aiAvailable()) {
      e.preventDefault();
      this._showGenerateMapDialog();
      return;
    }
    if (pro && (e.key === "z" || e.key === "Z") && this._aiAvailable()) {
      e.preventDefault();
      this._showSortInDialog();
      return;
    }
    if (pro && (e.key === "k" || e.key === "K") && this._aiAvailable()) {
      e.preventDefault();
      this._showClusterDialog();
      return;
    }
    if (pro && (e.key === "r" || e.key === "R")) {
      e.preventDefault();
      this._showRulesDialog();
      return;
    }
    if (pro && (e.key === "b" || e.key === "B") && !e.shiftKey) {
      e.preventDefault();
      this._showBrainstorm();
      return;
    }
    if (pro && (e.key === "s" || e.key === "S")) {
      const hasChildren = this._selectedId && this._categoryIdeas().some((i) => i.parent_id === this._selectedId);
      if (hasChildren || (!this._selectedId && this._selectedCategory !== "all" && !this._focusId)) {
        e.preventDefault();
        this._showSortDialog(hasChildren ? this._selectedId : null);
        return;
      }
    }
    if (pro && (e.key === "l" || e.key === "L") && this._selectedId) {
      e.preventDefault();
      this._startLink(this._selectedId);
      return;
    }
    // Digits fold the map to that many levels, 0 opens everything
    if (normal && /^[0-9]$/.test(e.key) && !e.shiftKey) {
      e.preventDefault();
      this._showLevels(Number(e.key));
      return;
    }
    // F4 opens the chosen branch on its own, Shift+F4 goes back up
    if (normal && e.key === "F4") {
      e.preventDefault();
      if (e.shiftKey) this._focusUp();
      else if (this._selectedId) this._setFocus(this._selectedId);
      return;
    }
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
      if (key === "Escape" && this._focusId) {
        e.preventDefault();
        this._focusUp();
      } else if (key === "Enter") {
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
    this._setPresenceEditing(id);
    const close = () => {
      textarea.remove();
      textEl.style.display = "";
      cloud.classList.remove("editing");
      this._setPresenceEditing(null);
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
    if (this._isBoard()) {
      this._dropOnBoard(moved, drag);
      return;
    }
    if (this._isPinboard()) {
      this._dropOnPinboard(moved);
      return;
    }
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
    if (this._isPinboard()) {
      this._arrangePinLayout(ideas, w, h);
      return;
    }
    if (this._isBoard()) {
      this._arrangeBoardLayout(ideas, w, h);
      return;
    }
    if (this._layout() === "outline") {
      this._arrangeOutlineLayout(ideas, childrenOf, roots, w, h, centerNode);
      return;
    }
    if (this._layout() !== "radial") {
      this._arrangeTreeLayout(ideas, childrenOf, roots, w, h, centerNode, this._layout() === "org");
      return;
    }

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

  // Columns side by side, or the four fields of the Eisenhower matrix
  _arrangeBoardLayout(ideas, w, h) {
    const kind = this._layout();
    const size = new Map();
    ideas.forEach((idea) => {
      const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
      size.set(idea.id, { w: (el && el.offsetWidth) || 230, h: (el && el.offsetHeight) || 120 });
    });
    const order = new Map(ideas.map((idea, index) => [idea.id, index]));
    const columns = boardColumns(kind, ideas);
    const pad = 14;
    const gap = 12;
    const head = 44;
    const noteW = Math.max(200, ...[...size.values()].map((box) => box.w));
    const items = [];
    const stack = (ids, x, y, perRow) => {
      // Notes fill the field row by row, perRow side by side
      let bottom = y;
      const rowHeights = [];
      ids.sort((a, b) => order.get(a) - order.get(b)).forEach((id, index) => {
        const row = Math.floor(index / perRow);
        rowHeights[row] = Math.max(rowHeights[row] || 0, size.get(id).h);
      });
      const rowTops = [];
      rowHeights.reduce((top, height, row) => {
        rowTops[row] = top;
        return top + height + gap;
      }, y);
      ids.forEach((id, index) => {
        const row = Math.floor(index / perRow);
        const col = index % perRow;
        const box = size.get(id);
        const item = { id, x: x + col * (noteW + gap) + noteW / 2, y: rowTops[row] + box.h / 2, ...box };
        items.push(item);
        bottom = Math.max(bottom, rowTops[row] + box.h);
      });
      return bottom;
    };
    const fields = [];
    if (kind === "matrix") {
      const perRow = 2;
      const fieldW = perRow * noteW + (perRow - 1) * gap + pad * 2;
      const bottoms = columns.map((column, index) => {
        const x = 20 + (index % 2) * (fieldW + gap);
        return stack(column.ids, x + pad, 20 + head, perRow) - 20;
      });
      // Both fields of a row get the height of the taller one
      const rowH = [0, 1].map((row) => Math.max(160, bottoms[row * 2], bottoms[row * 2 + 1]) + pad);
      items.length = 0;
      columns.forEach((column, index) => {
        const row = Math.floor(index / 2);
        const x = 20 + (index % 2) * (fieldW + gap);
        const y = 20 + (row ? rowH[0] + gap : 0);
        stack(column.ids, x + pad, y + head, perRow);
        fields.push({ key: column.key, label: column.label, count: column.ids.length, x, y, w: fieldW, h: rowH[row] });
      });
    } else {
      const colW = noteW + pad * 2;
      let tallest = 200;
      columns.forEach((column, index) => {
        const x = 20 + index * (colW + gap);
        tallest = Math.max(tallest, stack(column.ids, x + pad, 20 + head, 1) - 20 + pad);
        fields.push({ key: column.key, label: column.label, count: column.ids.length, x, y: 20, w: colW, h: 0 });
      });
      fields.forEach((field) => { field.h = Math.max(tallest, h - 96); });
    }
    this._board = { kind, fields };
    items.forEach((item) => {
      this._nodePositions.set(item.id, { x: item.x, y: item.y });
      const el = this.shadowRoot.getElementById(`cloud_${item.id}`);
      if (el) {
        el.style.left = `${item.x}px`;
        el.style.top = `${item.y}px`;
      }
    });
    if (this._scale >= 0.95 && this._scale <= 1.05) {
      const maxX = Math.max(...fields.map((field) => field.x + field.w));
      const maxY = Math.max(...fields.map((field) => field.y + field.h));
      this._fitBox(8, 8, maxX + 12, maxY + 12, w, h, true);
    }
    this._drawConnections();
  }

  // Fit a box into the card, never below 45 %; a box too big stays at its start
  _fitBox(minX, minY, maxX, maxY, w, h, alwaysFitWidth = false) {
    const bottomInset = 56;
    const availW = w - 24;
    const availH = h - 12 - bottomInset;
    const tooBig = minX < 12 || maxX > w - 12 || minY < 12 || maxY > h - bottomInset;
    if (!tooBig && !alwaysFitWidth) return;
    const fit = Math.min(availW / (maxX - minX), alwaysFitWidth ? Infinity : availH / (maxY - minY));
    this._scale = Math.max(0.45, Math.min(1, fit));
    this._panX = 12 - this._scale * minX + Math.max(0, (availW - this._scale * (maxX - minX)) / 2);
    this._panY = 12 - this._scale * minY + Math.max(0, (availH - this._scale * (maxY - minY)) / 2);
    this._applyTransform();
  }

  _boardSvg() {
    const board = this._board;
    if (!board || board.kind !== this._layout()) return "";
    const tint = { do: "#e53935", plan: "#1e88e5", delegate: "#fb8c00", drop: "#9e9e9e", overdue: "#e53935", done: "#43a047" };
    return board.fields.map((field) => {
      const color = tint[field.key] || "var(--primary-color, #03a9f4)";
      const empty = !field.count && field.key === "done"
        ? `<text class="board-hint" x="${field.x + field.w / 2}" y="${field.y + 80}" text-anchor="middle">${this._escapeHtml(t("Hierher ziehen zum Abhaken"))}</text>`
        : "";
      return `
        <g class="board-field" data-board="${field.key}">
          <rect class="board-rect" x="${field.x}" y="${field.y}" width="${field.w}" height="${field.h}" rx="14" style="--board-color: ${color};" />
          <text class="board-label" x="${field.x + 16}" y="${field.y + 28}" style="--board-color: ${color};">${this._escapeHtml(field.label)}<tspan class="board-count" dx="8">${field.count || ""}</tspan></text>
          ${empty}
        </g>`;
    }).join("");
  }

  // The field under the middle of a dropped note
  _boardFieldAt(x, y) {
    const board = this._board;
    if (!board) return null;
    return board.fields.find((field) => x >= field.x - 6 && x <= field.x + field.w + 6 && y >= field.y - 40 && y <= field.y + field.h + 40) || null;
  }

  async _dropOnBoard(moved, drag) {
    const kind = this._layout();
    const pos = this._nodePositions.get(drag.id);
    const field = pos && this._boardFieldAt(pos.x, pos.y);
    const rearrange = () => {
      this._lastLayoutKey = "";
      this._arrangeNodesRadially();
    };
    if (!field || !this._hass) {
      rearrange();
      return;
    }
    const changes = [];
    let refused = false;
    moved.forEach((id) => {
      const idea = this._ideaById(id);
      if (!idea) return;
      const change = boardDrop(kind, field.key, idea);
      if (change === null) refused = true;
      else if (Object.keys(change).length) changes.push({ idea, change });
    });
    if (refused) {
      this._showToast(kind === "kanban"
        ? t("„Wartet“ ergibt sich aus blockierenden Verbindungen")
        : kind === "matrix"
          ? t("Fällig in den nächsten drei Tagen bleibt dringend, ändere dafür das Datum")
          : t("Überfällig ergibt sich aus dem Datum"));
    }
    if (!changes.length) {
      rearrange();
      return;
    }
    const undo = [];
    for (const { idea, change } of changes) {
      const before = { id: idea.id };
      if ("status" in change) before.status = "active";
      if ("in_progress" in change) before.in_progress = Boolean(idea.in_progress);
      if ("due" in change) before.due = idea.due || null;
      if ("priority" in change) before.priority = idea.priority || "medium";
      try {
        await this._hass.callService("brainstorm", "update_idea", { id: idea.id, ...change });
        undo.push(before);
      } catch (err) {
        console.error("[BrainstormMindmap] Failed to move note on the board:", err);
      }
    }
    rearrange();
    if (!undo.length) return;
    this._showToast(`${field.label}: ${undo.length === 1 ? changes[0].idea.text : t("{count} Notizen", { count: undo.length })}`);
    this._pushUndo(undo.length === 1 ? changes[0].idea.text : t("{count} Notizen", { count: undo.length }), async () => {
      for (const before of undo) await this._hass.callService("brainstorm", "update_idea", before);
    });
  }

  // One note per row, subtasks indented below their parent, as in an outliner
  _arrangeOutlineLayout(ideas, childrenOf, roots, w, h, centerNode) {
    const indent = 44;
    const gap = 10;
    const centerW = (centerNode && centerNode.offsetWidth) || 154;
    const centerH = (centerNode && centerNode.offsetHeight) || 154;
    this._centerPos = { x: 20 + centerW / 2, y: 20 + centerH / 2 };
    if (centerNode) {
      centerNode.style.left = `${this._centerPos.x}px`;
      centerNode.style.top = `${this._centerPos.y}px`;
    }
    const left = 20 + centerW / 2 + 30;
    let top = 20 + centerH + 16;
    let maxX = 20 + centerW;
    const seen = new Set();
    const place = (idea, depth) => {
      if (seen.has(idea.id)) return;
      seen.add(idea.id);
      const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
      const width = (el && el.offsetWidth) || 230;
      const height = (el && el.offsetHeight) || 120;
      const x = left + depth * indent + width / 2;
      const y = top + height / 2;
      top += height + gap;
      maxX = Math.max(maxX, x + width / 2);
      this._nodePositions.set(idea.id, { x, y });
      if (el) {
        el.style.left = `${x}px`;
        el.style.top = `${y}px`;
      }
      (childrenOf.get(idea.id) || []).forEach((kid) => place(kid, depth + 1));
    };
    roots.forEach((root) => place(root, 0));
    ideas.forEach((idea) => place(idea, 0));
    // The width fits the card, the list scrolls down by panning
    if (this._scale >= 0.95 && this._scale <= 1.05) {
      this._scale = Math.max(0.45, Math.min(1, (w - 24) / (maxX + 4)));
      this._panX = 12 - this._scale * 8;
      this._panY = 12 - this._scale * 8;
      this._applyTransform();
    }
    this._drawConnections();
  }

  // Tidy tree: every leaf gets its own row (or column), parents sit in the middle of theirs
  _arrangeTreeLayout(ideas, childrenOf, roots, w, h, centerNode, vertical) {
    const size = new Map();
    ideas.forEach((idea) => {
      const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
      size.set(idea.id, { w: (el && el.offsetWidth) || 230, h: (el && el.offsetHeight) || 120 });
    });
    const centerW = (centerNode && centerNode.offsetWidth) || 154;
    const centerH = (centerNode && centerNode.offsetHeight) || 154;
    const levelGap = vertical ? 46 : 70;
    const siblingGap = vertical ? 18 : 22;
    // How far each level reaches along the main direction
    const depthOf = new Map();
    const extent = [];
    const seen = new Set();
    const measure = (idea, depth) => {
      if (seen.has(idea.id)) return;
      seen.add(idea.id);
      depthOf.set(idea.id, depth);
      const box = size.get(idea.id);
      extent[depth] = Math.max(extent[depth] || 0, vertical ? box.h : box.w);
      (childrenOf.get(idea.id) || []).forEach((kid) => measure(kid, depth + 1));
    };
    roots.forEach((root) => measure(root, 0));
    ideas.forEach((idea) => measure(idea, 0));
    const main = [];
    let cursorMain = (vertical ? centerH : centerW) / 2 + levelGap;
    extent.forEach((reach, depth) => {
      main[depth] = cursorMain + reach / 2;
      cursorMain += reach + levelGap;
    });
    // Across the main direction leaves line up one after the other
    const cross = new Map();
    let cursorCross = 0;
    const placed = new Set();
    const place = (idea) => {
      if (placed.has(idea.id)) return null;
      placed.add(idea.id);
      const kids = (childrenOf.get(idea.id) || []).map(place).filter((value) => value !== null);
      const box = size.get(idea.id);
      const span = vertical ? box.w : box.h;
      let middle;
      if (kids.length) {
        middle = (kids[0] + kids[kids.length - 1]) / 2;
        cursorCross = Math.max(cursorCross, middle + span / 2 + siblingGap);
      } else {
        middle = cursorCross + span / 2;
        cursorCross += span + siblingGap;
      }
      cross.set(idea.id, middle);
      return middle;
    };
    roots.forEach(place);
    ideas.forEach(place);
    const total = Math.max(0, cursorCross - siblingGap);
    // The center sits at the start, in the middle of everything across
    const margin = 20;
    this._centerPos = vertical
      ? { x: Math.max(w / 2, total / 2 + margin), y: margin + centerH / 2 }
      : { x: margin + centerW / 2, y: Math.max(h / 2, total / 2 + margin) };
    if (centerNode) {
      centerNode.style.left = `${this._centerPos.x}px`;
      centerNode.style.top = `${this._centerPos.y}px`;
    }
    const items = ideas.map((idea) => {
      const along = main[depthOf.get(idea.id) || 0];
      const across = cross.get(idea.id) - total / 2;
      const box = size.get(idea.id);
      return vertical
        ? { idea, x: this._centerPos.x + across, y: this._centerPos.y + along, ...box }
        : { idea, x: this._centerPos.x + along, y: this._centerPos.y + across, ...box };
    });
    items.forEach((item) => {
      this._nodePositions.set(item.idea.id, { x: item.x, y: item.y });
      const el = this.shadowRoot.getElementById(`cloud_${item.idea.id}`);
      if (el) {
        el.style.left = `${item.x}px`;
        el.style.top = `${item.y}px`;
      }
    });
    // Fit the whole tree into the card, the start of the tree in view
    if (items.length && this._scale >= 0.95 && this._scale <= 1.05) {
      let minX = this._centerPos.x - centerW / 2;
      let minY = this._centerPos.y - centerH / 2;
      let maxX = this._centerPos.x + centerW / 2;
      let maxY = this._centerPos.y + centerH / 2;
      items.forEach((item) => {
        minX = Math.min(minX, item.x - item.w / 2);
        maxX = Math.max(maxX, item.x + item.w / 2);
        minY = Math.min(minY, item.y - item.h / 2);
        maxY = Math.max(maxY, item.y + item.h / 2);
      });
      const bottomInset = 56;
      const availW = w - 24;
      const availH = h - 12 - bottomInset;
      if (minX < 12 || maxX > w - 12 || minY < 12 || maxY > h - bottomInset) {
        const fit = Math.min(availW / (maxX - minX), availH / (maxY - minY));
        this._scale = Math.max(0.45, Math.min(1, fit));
        this._panX = 12 - this._scale * minX + Math.max(0, (availW - this._scale * (maxX - minX)) / 2);
        this._panY = 12 - this._scale * minY + Math.max(0, (availH - this._scale * (maxY - minY)) / 2);
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
    if (lines === "angled-down") {
      const midY = y1 + dy / 2;
      return `M ${x1} ${y1} V ${midY} H ${x2} V ${y2}`;
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
    this._renderSketch();
    this._renderPresence();

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
    if (this._isBoard()) {
      // A board has columns instead of lines
      activeIdeas.forEach((idea) => {
        const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
        if (el) this._drawNodeShape(el, -Math.PI / 2);
      });
      svg.innerHTML = this._boardSvg();
      return;
    }
    if (this._isPinboard()) {
      // Sticky notes need no lines, frames and own links stay
      activeIdeas.forEach((idea) => {
        const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
        if (el) this._drawNodeShape(el, -Math.PI / 2);
      });
      svg.innerHTML = `${this._framesSvg(activeIdeas)}${this._linksSvg(activeIdeas)}`;
      this._refreshMinimap();
      return;
    }
    // A tree or an org chart reads best with lines at right angles
    const layout = this._layout();
    const lines = { tree: "angled", org: "angled-down" }[layout] || this._mapStyle().lines;
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

      let pathData;
      if (layout === "outline") {
        // Down from the left side of the parent, then across to the note
        const fromEl = from ? this.shadowRoot.getElementById(`cloud_${parentId}`) : this.shadowRoot.getElementById("centerNode");
        const spine = x1 - ((fromEl && fromEl.offsetWidth) || 0) / 2 + 22;
        pathData = `M ${spine} ${y1} V ${y2} H ${x2 - el.offsetWidth / 2}`;
      } else {
        pathData = this._linePath(lines, x1, y1, x2, y2);
      }
      const faded = this._filterHits && !this._filterHits.has(idea.id) ? " filter-out" : "";
      svgHtml += `
        <path id="path_${this._escapeHtml(idea.id)}" class="synapse-path${from ? " branch-path" : ""}${faded}" d="${pathData}" style="--path-color: ${catColor};" />
      `;
    });

    svg.innerHTML = `${this._framesSvg(activeIdeas)}${svgHtml}${this._linksSvg(activeIdeas)}`;
    this._refreshMinimap();
  }

  // Where the line from the middle of a note towards a point leaves the note
  _nodeEdge(id, toward) {
    const pos = this._nodePositions.get(id);
    const el = this.shadowRoot.getElementById(`cloud_${id}`);
    if (!pos || !el) return pos;
    const dx = toward.x - pos.x;
    const dy = toward.y - pos.y;
    const halfW = el.offsetWidth / 2 + 4;
    const halfH = el.offsetHeight / 2 + 4;
    if (!dx && !dy) return pos;
    const scale = Math.min(dx ? halfW / Math.abs(dx) : Infinity, dy ? halfH / Math.abs(dy) : Infinity);
    return scale >= 1 ? pos : { x: pos.x + dx * scale, y: pos.y + dy * scale };
  }

  // Curved arrows between notes of different branches, with their label
  _linksSvg(ideas) {
    const shown = new Map(ideas.map((i) => [i.id, i]));
    let html = "";
    ideas.forEach((idea) => {
      (idea.links || []).forEach((link) => {
        if (!shown.has(link.to)) return;
        const a = this._nodePositions.get(idea.id);
        const b = this._nodePositions.get(link.to);
        if (!a || !b) return;
        const mx = (a.x + b.x) / 2;
        const my = (a.y + b.y) / 2;
        const len = Math.hypot(b.x - a.x, b.y - a.y) || 1;
        // The line bows to one side, so it does not hide the tree lines
        const bow = Math.min(80, len * 0.22);
        const control = { x: mx - ((b.y - a.y) / len) * bow, y: my + ((b.x - a.x) / len) * bow };
        const start = this._nodeEdge(idea.id, control);
        const end = this._nodeEdge(link.to, control);
        const d = `M ${start.x.toFixed(1)} ${start.y.toFixed(1)} Q ${control.x.toFixed(1)} ${control.y.toFixed(1)} ${end.x.toFixed(1)} ${end.y.toFixed(1)}`;
        const labelX = 0.25 * start.x + 0.5 * control.x + 0.25 * end.x;
        const labelY = 0.25 * start.y + 0.5 * control.y + 0.25 * end.y;
        const faded = this._filterHits && !this._filterHits.has(idea.id) && !this._filterHits.has(link.to) ? " filter-out" : "";
        const kind = link.blocks ? " link-blocks" : "";
        const label = `${link.blocks ? "⛔ " : ""}${link.label || ""}`.trim();
        const ids = `data-link-from="${this._escapeHtml(idea.id)}" data-link-to="${this._escapeHtml(link.to)}"`;
        html += `<path class="link-path${kind}${faded}" d="${d}" marker-end="url(#bsLinkArrow${link.blocks ? "Blocks" : ""})" />`;
        html += `<path class="link-hit" ${ids} d="${d}"><title>${this._escapeHtml(t("Verbindung bearbeiten"))}</title></path>`;
        if (label) {
          const width = Math.max(24, [...label].length * 6.4 + 14);
          html += `<g class="link-label${kind}${faded}" ${ids}><rect x="${(labelX - width / 2).toFixed(1)}" y="${(labelY - 10).toFixed(1)}" width="${width.toFixed(1)}" height="20" rx="10" /><text x="${labelX.toFixed(1)}" y="${(labelY + 4).toFixed(1)}" text-anchor="middle">${this._escapeHtml(label)}</text></g>`;
        }
      });
    });
    if (!html) return "";
    const arrow = (id) => `<marker id="${id}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" class="${id === "bsLinkArrow" ? "link-arrow" : "link-arrow link-blocks"}" /></marker>`;
    return `<defs>${arrow("bsLinkArrow")}${arrow("bsLinkArrowBlocks")}</defs>${html}`;
  }

  // A rounded frame around the notes with the same frame name
  _framesSvg(ideas) {
    const groups = new Map();
    ideas.forEach((idea) => {
      if (!idea.frame) return;
      if (!groups.has(idea.frame)) groups.set(idea.frame, []);
      groups.get(idea.frame).push(idea);
    });
    let html = "";
    groups.forEach((members, name) => {
      let minX = Infinity;
      let minY = Infinity;
      let maxX = -Infinity;
      let maxY = -Infinity;
      members.forEach((idea) => {
        const pos = this._nodePositions.get(idea.id);
        const el = this.shadowRoot.getElementById(`cloud_${idea.id}`);
        if (!pos || !el) return;
        minX = Math.min(minX, pos.x - el.offsetWidth / 2);
        maxX = Math.max(maxX, pos.x + el.offsetWidth / 2);
        minY = Math.min(minY, pos.y - el.offsetHeight / 2);
        maxY = Math.max(maxY, pos.y + el.offsetHeight / 2);
      });
      if (!Number.isFinite(minX)) return;
      const pad = 16;
      const x = minX - pad;
      const y = minY - pad - 18;
      const width = maxX - minX + pad * 2;
      const height = maxY - minY + pad * 2 + 18;
      const color = this._getCategoryColor(members[0].category);
      const faded = this._filterHits && !members.some((m) => this._filterHits.has(m.id)) ? " filter-out" : "";
      html += `<g class="frame${faded}" style="--frame-color: ${color};"><rect class="frame-rect" x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${width.toFixed(1)}" height="${height.toFixed(1)}" rx="18" />`;
      html += `<text class="frame-label" data-frame="${this._escapeHtml(name)}" x="${(x + 14).toFixed(1)}" y="${(y + 17).toFixed(1)}">▢ ${this._escapeHtml(name)}<title>${this._escapeHtml(t("Rahmen bearbeiten"))}</title></text></g>`;
    });
    return html;
  }

  // Brainstorm mode: type idea after idea against a timer, each one a note at once
  _showBrainstorm() {
    const focus = this._focusIdea();
    const category = focus ? focus.category : this._selectedCategory === "all" ? null : this._selectedCategory;
    const where = focus
      ? t("Ideen landen unter „{text}“.", { text: this._escapeHtml(focus.text) })
      : category
        ? t("Ideen landen in „{category}“.", { category: this._escapeHtml(category) })
        : t("Ideen landen in der passenden Kategorie.");
    const state = { minutes: 5, endsAt: 0, timer: null, added: [] };
    const running = category ? this._rounds()[category] : null;
    if (running) {
      // Join the round: its time limit counts for everyone
      const end = this._roundEnd(running);
      state.minutes = end ? Math.max(1, Math.ceil((end - Date.now()) / 60000)) : 0;
      state.endsAt = end;
    }
    this._openDialog(t("⚡ Brainstorm"), (body) => {
      const roundRow = !category
        ? ""
        : running
          ? `<div class="dialog-hint storm-round">🙈 ${t("Verdeckte Runde läuft: Deine Ideen sieht bis zum Aufdecken nur du.")}</div>`
          : `<label class="dialog-check storm-round"><input type="checkbox" id="stormHidden"> 🙈 ${t("Verdeckt: Jeder sieht bis zum Ende nur die eigenen Ideen")}</label>`;
      body.innerHTML = `
        <div class="storm-head">
          <div class="dialog-prio-grid storm-times" id="stormTimes"${running ? ' style="display: none;"' : ""}>
            ${[3, 5, 10, 15, 0].map((m) => `<div class="dialog-prio-chip ${m === state.minutes ? "selected" : ""}" data-minutes="${m}">${m ? t("{minutes} Min.", { minutes: m }) : "∞"}</div>`).join("")}
          </div>
          <div class="storm-clock" id="stormClock" aria-live="polite">5:00</div>
        </div>
        <div class="dialog-hint">${where} ${t("Nicht bewerten, nur sammeln: Enter speichert und das Feld ist sofort wieder frei.")}</div>
        ${roundRow}
        <div class="storm-input-row">
          <input class="dialog-input storm-input" id="stormInput" maxlength="300" autocomplete="off" placeholder="${t("Idee eintippen und Enter …")}">
          <button class="dialog-btn dialog-btn-primary" id="stormAdd">${t("Sammeln")}</button>
        </div>
        <div class="storm-count" id="stormCount"></div>
        <div class="storm-notes" id="stormNotes"></div>
        <div class="dialog-footer">
          ${this._aiAvailable() && this._sortInCategory() ? `<button class="dialog-btn dialog-btn-cancel" id="stormSortIn" title="${t("✨ Lose Ideen zuordnen")}">${t("✨ Zuordnen")}</button>` : ""}
          ${this._aiAvailable() && this._sortInCategory() ? `<button class="dialog-btn dialog-btn-cancel" id="stormCluster" title="${t("✨ Nach Themen gruppieren")}">${t("✨ Themen")}</button>` : ""}
          ${running ? `<button class="dialog-btn dialog-btn-cancel" id="stormReveal">🙈 ${t("Aufdecken")}</button>` : ""}
          <button class="dialog-btn dialog-btn-primary" id="stormDone">${t("Fertig")}</button>
        </div>
      `;
      const input = body.querySelector("#stormInput");
      const clock = body.querySelector("#stormClock");
      const notes = body.querySelector("#stormNotes");
      const count = body.querySelector("#stormCount");
      const colors = ["#fff59d", "#ffcc80", "#a5d6a7", "#90caf9", "#f48fb1", "#ce93d8"];
      const fmt = (ms) => {
        const total = Math.max(0, Math.ceil(ms / 1000));
        return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
      };
      const showClock = () => {
        if (!state.minutes) {
          clock.textContent = "∞";
          return;
        }
        if (!state.endsAt) {
          clock.textContent = fmt(state.minutes * 60000);
          return;
        }
        const left = state.endsAt - Date.now();
        clock.textContent = fmt(left);
        clock.classList.toggle("storm-late", left <= 30000);
        if (left <= 0) {
          clearInterval(state.timer);
          state.timer = null;
          clock.textContent = t("Zeit!");
          clock.classList.add("storm-over");
          if (navigator.vibrate) navigator.vibrate([120, 80, 120]);
        }
      };
      const start = async () => {
        const hiddenBox = body.querySelector("#stormHidden");
        if (hiddenBox && hiddenBox.checked && !state.round) {
          state.round = true;
          hiddenBox.disabled = true;
          body.querySelectorAll("#stormTimes [data-minutes]").forEach((chip) => chip.classList.add("disabled"));
          try {
            const result = await this._hass.callWS({
              type: "call_service",
              domain: "brainstorm",
              service: "start_round",
              service_data: { category, minutes: state.minutes },
              return_response: true,
            });
            const end = this._roundEnd(result && result.response && result.response.round);
            if (end) state.endsAt = end;
          } catch (err) {
            console.error("[BrainstormMindmap] Starting the hidden round failed:", err);
            this._showToast((err && err.message) || t("Das ging nicht."));
          }
        }
        if (state.timer || !state.minutes) return;
        if (!state.endsAt) state.endsAt = Date.now() + state.minutes * 60000;
        state.timer = setInterval(showClock, 250);
      };
      const render = () => {
        count.textContent = state.added.length ? t("{count} Ideen gesammelt", { count: state.added.length }) : "";
        notes.innerHTML = state.added
          .map((item, index) => `<div class="storm-note" style="--storm-color: ${colors[index % colors.length]}; --storm-tilt: ${((index * 37) % 7) - 3}deg;">${formatText(item.text)}<button class="storm-remove" data-index="${index}" title="${t("Wieder löschen")}">✕</button></div>`)
          .reverse()
          .join("");
        notes.querySelectorAll(".storm-remove").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const item = state.added[Number(btn.getAttribute("data-index"))];
            if (!item) return;
            state.added = state.added.filter((x) => x !== item);
            render();
            if (item.id) await this._hass.callService("brainstorm", "delete_idea", { id: item.id }).catch(() => {});
          });
        });
      };
      const add = async () => {
        const text = input.value.trim();
        if (!text) return;
        input.value = "";
        input.focus();
        await start();
        const item = { text, id: null };
        state.added.push(item);
        render();
        try {
          item.id = await this._addIdea(
            { text, ...(category ? { category } : {}), ...(focus ? { parent_id: focus.id } : {}) },
            { undo: false },
          );
        } catch (err) {
          console.error("[BrainstormMindmap] Brainstorm note failed:", err);
          state.added = state.added.filter((x) => x !== item);
          render();
          this._showToast(t("Die Idee konnte nicht gespeichert werden."));
        }
      };
      body.querySelectorAll("#stormTimes [data-minutes]").forEach((chip) => {
        chip.addEventListener("click", () => {
          if (state.round) return;
          body.querySelectorAll("#stormTimes [data-minutes]").forEach((c) => c.classList.remove("selected"));
          chip.classList.add("selected");
          state.minutes = Number(chip.getAttribute("data-minutes")) || 0;
          clearInterval(state.timer);
          state.timer = null;
          state.endsAt = 0;
          clock.classList.remove("storm-late", "storm-over");
          showClock();
          input.focus();
        });
      });
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.isComposing) {
          e.preventDefault();
          add();
        }
      });
      body.querySelector("#stormAdd").addEventListener("click", add);
      body.querySelector("#stormDone").addEventListener("click", () => this._closeDialog());
      const reveal = body.querySelector("#stormReveal");
      if (reveal) {
        reveal.addEventListener("click", () => {
          this._closeDialog();
          this._endRound(category);
        });
      }
      const sortIn = body.querySelector("#stormSortIn");
      if (sortIn) {
        sortIn.addEventListener("click", () => {
          this._closeDialog();
          this._showSortInDialog();
        });
      }
      const cluster = body.querySelector("#stormCluster");
      if (cluster) {
        cluster.addEventListener("click", () => {
          this._closeDialog();
          this._showClusterDialog();
        });
      }
      this._dialogCleanup = () => {
        clearInterval(state.timer);
        const ids = state.added.map((item) => item.id).filter(Boolean);
        if (!ids.length) return;
        this._pushUndo(t("{count} Ideen", { count: ids.length }), () =>
          Promise.all(ids.map((id) => this._hass.callService("brainstorm", "delete_idea", { id }))),
        );
        this._showToast(t("{count} Ideen gesammelt. 🪄 ordnet die Map neu, ↶ nimmt alle heraus.", { count: ids.length }));
      };
      showClock();
      if (running && state.endsAt) state.timer = setInterval(showClock, 250);
      setTimeout(() => input.focus(), 60);
    });
  }

  // The sort choices, as chips for the edit and the sort dialog
  _sortChips() {
    return sortChoices()
      .map(([by, reverse, label]) => `<div class="dialog-prio-chip" data-sort="${by}"${reverse ? " data-reverse" : ""}>${label}</div>`)
      .join("");
  }

  // Sort the subtasks of a note, or the main notes of the category, with undo
  async _sortChildren(parentId, by, reverse) {
    const sensor = this._getSensorEntity();
    const ideas = (sensor && sensor.attributes.ideas) || [];
    const category = this._selectedCategory;
    const ids = new Set(ideas.map((i) => i.id));
    const before = ideas
      .filter((i) => (parentId ? i.parent_id === parentId : i.category === category && !(i.parent_id && ids.has(i.parent_id))))
      .map((i) => i.id);
    if (before.length < 2) {
      this._showToast(t("Nichts zu sortieren."));
      return;
    }
    const target = parentId ? { parent_id: parentId } : { category };
    try {
      await this._hass.callService("brainstorm", "sort_children", { ...target, by, reverse });
      const parent = parentId ? ideas.find((i) => i.id === parentId) : null;
      this._pushUndo(parent ? parent.text : category, () => this._hass.callService("brainstorm", "sort_children", { ...target, ids: before }));
      this._showToast(this._usesSavedPositions() ? t("Sortiert. 🪄 ordnet die Map passend neu.") : t("Sortiert."));
    } catch (err) {
      console.error("[BrainstormMindmap] Failed to sort:", err);
      this._showToast(t("Sortieren hat nicht geklappt."));
    }
  }

  // Sort dialog for the S key: subtasks of the picked note, else the main notes
  _showSortDialog(parentId) {
    const parent = parentId ? this._ideaById(parentId) : null;
    const title = parent ? t("↕ Unterpunkte von „{text}“ sortieren", { text: this._escapeHtml(parent.text) }) : t("↕ Hauptnotizen sortieren");
    this._openDialog(title, (body) => {
      body.innerHTML = `
        <div class="dialog-prio-grid dialog-sort-grid">${this._sortChips()}</div>
        <div class="dialog-hint">${t("Die Reihenfolge gilt in beiden Karten. ↶ macht es rückgängig.")}</div>
      `;
      body.querySelectorAll("[data-sort]").forEach((chip) => {
        chip.addEventListener("click", () => {
          this._closeDialog();
          this._sortChildren(parentId, chip.getAttribute("data-sort"), chip.hasAttribute("data-reverse"));
        });
      });
    });
  }

  _startLink(id) {
    if (this._linkFrom === id) {
      this._cancelLink();
      return;
    }
    this._linkFrom = id;
    const area = this.shadowRoot.getElementById("canvasArea");
    if (area) area.classList.add("linking");
    this.shadowRoot.querySelectorAll(".note-cloud").forEach((el) => el.classList.toggle("link-source", el.getAttribute("data-id") === id));
    this._showToast(t("Ziel-Notiz antippen … (Esc bricht ab)"));
  }

  _cancelLink() {
    this._linkFrom = null;
    const area = this.shadowRoot.getElementById("canvasArea");
    if (area) area.classList.remove("linking");
    this.shadowRoot.querySelectorAll(".note-cloud.link-source").forEach((el) => el.classList.remove("link-source"));
  }

  _ideaById(id) {
    const sensor = this._getSensorEntity();
    return ((sensor && sensor.attributes.ideas) || []).find((i) => i.id === id) || null;
  }

  async _saveLinks(fromId, links, before) {
    try {
      await this._hass.callService("brainstorm", "update_idea", { id: fromId, links });
      const from = this._ideaById(fromId);
      this._pushUndo(from ? from.text : "", () => this._hass.callService("brainstorm", "update_idea", { id: fromId, links: before }));
    } catch (err) {
      console.error("[BrainstormMindmap] Failed to save the links:", err);
      this._showToast(t("Die Verbindung konnte nicht gespeichert werden."));
    }
  }

  async _finishLink(toId) {
    const fromId = this._linkFrom;
    this._cancelLink();
    if (!fromId || fromId === toId) return;
    const from = this._ideaById(fromId);
    if (!from) return;
    const before = (from.links || []).map((link) => ({ ...link }));
    if (before.some((link) => link.to === toId)) {
      this._showLinkDialog(fromId, toId);
      return;
    }
    // A line back between the same two notes would only double the first
    const to = this._ideaById(toId);
    if (to && (to.links || []).some((link) => link.to === fromId)) {
      this._showLinkDialog(toId, fromId);
      return;
    }
    if (before.length >= 20) {
      this._showToast(t("Höchstens 20 Verbindungen pro Notiz."));
      return;
    }
    await this._saveLinks(fromId, [...before, { to: toId }], before);
    this._showToast(t("Verbunden. Die Linie antippen, um sie zu beschriften."));
  }

  _showLinkDialog(fromId, toId) {
    const from = this._ideaById(fromId);
    const to = this._ideaById(toId);
    if (!from || !to) return;
    const before = (from.links || []).map((link) => ({ ...link }));
    const link = before.find((l) => l.to === toId) || { to: toId };
    this._openDialog(t("🔗 Verbindung"), (body) => {
      body.innerHTML = `
        <div class="dialog-label">${this._escapeHtml(from.text)} → ${this._escapeHtml(to.text)}</div>
        <div class="dialog-label">${t("Beschriftung:")}</div>
        <input class="dialog-input" id="linkLabel" maxlength="40" placeholder="${t("z. B. gehört zu, braucht, siehe auch")}" value="${this._escapeHtml(link.label || "")}">
        <label class="dialog-check"><input type="checkbox" id="linkBlocks" ${link.blocks ? "checked" : ""}> ${t("„{from}“ blockiert „{to}“: das Ziel wartet, bis die erste Notiz erledigt ist", { from: this._escapeHtml(from.text), to: this._escapeHtml(to.text) })}</label>
        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-danger" id="linkDelete">${t("Verbindung löschen")}</button>
          <button class="dialog-btn dialog-btn-cancel" id="linkCancel">${t("Abbrechen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="linkSave">${t("Speichern")}</button>
        </div>
      `;
      const input = body.querySelector("#linkLabel");
      const save = () => {
        const label = input.value.trim();
        const blocks = body.querySelector("#linkBlocks").checked;
        const next = before.filter((l) => l.to !== toId);
        const item = { to: toId };
        if (label) item.label = label;
        if (blocks) item.blocks = true;
        const index = before.findIndex((l) => l.to === toId);
        next.splice(index < 0 ? next.length : index, 0, item);
        this._closeDialog();
        this._saveLinks(fromId, next, before);
      };
      body.querySelector("#linkSave").addEventListener("click", save);
      body.querySelector("#linkCancel").addEventListener("click", () => this._closeDialog());
      body.querySelector("#linkDelete").addEventListener("click", () => {
        this._closeDialog();
        this._saveLinks(fromId, before.filter((l) => l.to !== toId), before);
      });
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          save();
        }
      });
      setTimeout(() => input.focus(), 50);
    });
  }

  // Name, rename or remove a frame; with ids it frames those notes
  _showFrameDialog(name, ids) {
    const sensor = this._getSensorEntity();
    const ideas = (sensor && sensor.attributes.ideas) || [];
    const members = ids
      ? ideas.filter((i) => ids.includes(i.id))
      : this._categoryIdeas().filter((i) => i.frame === name);
    if (!members.length) return;
    const existing = [...new Set(this._categoryIdeas().map((i) => i.frame).filter(Boolean))];
    this._openDialog(ids ? t("▢ Rahmen um {count} Notizen", { count: members.length }) : t("▢ Rahmen bearbeiten"), (body) => {
      body.innerHTML = `
        <div class="dialog-label">${t("Name des Rahmens:")}</div>
        <input class="dialog-input" id="frameName" maxlength="40" list="frameNames" placeholder="${t("z. B. Phase 1, Später, Erdgeschoss")}" value="${this._escapeHtml(name || "")}">
        <datalist id="frameNames">${existing.map((f) => `<option value="${this._escapeHtml(f)}"></option>`).join("")}</datalist>
        <div class="dialog-hint">${t("Notizen mit demselben Namen teilen sich einen Rahmen.")}</div>
        <div class="dialog-footer">
          ${name ? `<button class="dialog-btn dialog-btn-danger" id="frameRemove">${t("Rahmen entfernen")}</button>` : ""}
          <button class="dialog-btn dialog-btn-cancel" id="frameCancel">${t("Abbrechen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="frameSave">${t("Speichern")}</button>
        </div>
      `;
      const input = body.querySelector("#frameName");
      const apply = async (value) => {
        this._closeDialog();
        const previous = members.map((m) => ({ id: m.id, frame: m.frame || null }));
        try {
          await Promise.all(members.map((m) => this._hass.callService("brainstorm", "update_idea", { id: m.id, frame: value })));
          this._pushUndo(value || name || "", () => Promise.all(previous.map((p) => this._hass.callService("brainstorm", "update_idea", p))));
          if (ids) this._clearMulti();
        } catch (err) {
          console.error("[BrainstormMindmap] Failed to save the frame:", err);
        }
      };
      body.querySelector("#frameSave").addEventListener("click", () => apply(input.value.trim() || null));
      body.querySelector("#frameCancel").addEventListener("click", () => this._closeDialog());
      const remove = body.querySelector("#frameRemove");
      if (remove) remove.addEventListener("click", () => apply(null));
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          apply(input.value.trim() || null);
        }
      });
      setTimeout(() => input.focus(), 50);
    });
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
      this._applyLevel();

      const attributes = sensor.attributes || {};
      const categories = attributes.categories || ["Inbox"];
      const activeIdeas = attributes.ideas || [];

      // Filter ideas by selected category
      const listIdeas = activeIdeas.filter((i) => {
        if (this._selectedCategory === "all") return true;
        return String(i.category || "").trim() === String(this._selectedCategory || "").trim();
      });
      // Numbers come from the whole list, so they stay the same in a focused branch
      const numbers = numberLabels(listIdeas);
      const filteredIdeas = this._focusIdeas(listIdeas);
      this._renderFocusBar();
      this._renderVoteBar();
      this._syncDrawing(attributes);
      this._sendPresence();

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
                  <ha-icon icon="${this._escapeHtml(catIcon)}" style="--mdc-icon-size: 14px; width: 14px; height: 14px; margin-right: 4px; display: inline-flex; align-items: center; vertical-align: middle; color: ${isActive ? '#ffffff' : catColor};"></ha-icon>
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
            if (this._selectedCategory !== newCat || this._focusId) {
              this._selectedCategory = newCat;
              this._focusId = null;
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
        const focusIdea = this._focusIdea();
        const focusText = focusIdea ? String(focusIdea.text || "").replace(/\s+/g, " ").trim() : "";
        centerTitle.textContent = focusIdea ? (focusText.length > 40 ? `${focusText.slice(0, 39)}…` : focusText) : displayCat;
        centerNode.classList.toggle("focused", Boolean(focusIdea));
        centerNode.title = focusIdea ? t("Eine Ebene zurück (Umschalt+F4)") : "";
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
        const emptyAi = this.shadowRoot.getElementById("emptyAiBtn");
        if (emptyAi) emptyAi.style.display = this._aiAvailable() ? "" : "none";
        container.innerHTML = "";
        this._nodePositions.clear();
        this._drawConnections();
        this._renderFilterChips();
        this._applyFilter();
        return;
      }

      emptyState.style.display = "none";

      // Render notes HTML, without those inside a folded branch
      const shownIdeas = this._mapIdeas(filteredIdeas);
      const listIds = new Set(filteredIdeas.map((i) => i.id));
      let html = "";
      const aiSubtasks = Boolean(sensor && sensor.attributes && sensor.attributes.ai_subtasks);
      const voting = (sensor && sensor.attributes && sensor.attributes.voting) || {};
      const me = this._currentUserId();
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
        const cover = this._config.show_images !== false ? coverAttachment(idea) : null;
        const branchToggle = hasBranch
          ? `<button class="branch-toggle" data-id="${this._escapeHtml(idea.id)}" title="${folded ? t("Zweig aufklappen") : t("Zweig einklappen")}">${folded ? `+${hiddenCount}` : "−"}</button>`
          : "";

        html += `
          <div class="note-cloud ${prioClass}${idea.blocked_by && idea.blocked_by.length ? " is-blocked" : ""}${idea.id === this._linkFrom ? " link-source" : ""} nshape-${shape}${svgShape ? " has-shape" : ""}${idea.id === this._selectedId ? " selected" : ""}${this._multi.has(idea.id) ? " multi-selected" : ""}${idea.id === this._menuId ? " menu-open" : ""}" id="cloud_${this._escapeHtml(idea.id)}" data-id="${this._escapeHtml(idea.id)}" data-shape="${shape}" style="--cat-color: ${color};">
            ${svgShape ? '<svg class="node-shape" aria-hidden="true"></svg>' : ""}
            ${branchToggle}
            ${idea.callout ? `<div class="cloud-callout" title="${t("Callout")}">💬 ${formatText(idea.callout)}</div>` : ""}
            <div class="cloud-meta">
              <span class="cat-tag" data-cat="${this._escapeHtml(idea.category)}" title="${t("Kategorie ändern")}">
                <ha-icon icon="${this._getCategoryIcon(idea.category)}" style="--mdc-icon-size: 12px; width: 12px; height: 12px; display: inline-flex; align-items: center; vertical-align: middle;"></ha-icon> ${this._escapeHtml(idea.category)}
              </span>
              ${prioBadge}
              ${this._getReminderBadges(idea)}${repeatBadge(idea)}
              ${inProgressBadge(idea)}
              ${blockedBadge(idea)}
              ${attachmentBadge(idea)}
              <span class="cloud-source" title="${t("Quelle")}: ${this._escapeHtml(idea.source || 'Dashboard')}${idea.device ? ` • ${t("Gerät")}: ` + this._escapeHtml(idea.device) : ''}">
                <span>${sourceBadge}</span>
                <span>•</span>
                <span>${timeAgo}</span>
              </span>
            </div>
            ${markerBadges(idea) || progressBadge(idea) ? `<div class="cloud-marks">${progressBadge(idea)}${markerBadges(idea)}</div>` : ""}
            ${(() => {
              const social = `${voteBadge(idea, voting, me)}${reactionBadges(idea, me)}${commentBadge(idea)}`;
              return social ? `<div class="cloud-social">${social}</div>` : "";
            })()}
            ${cover ? `<div class="cloud-image" data-id="${this._escapeHtml(idea.id)}" data-att="${this._escapeHtml(cover.id)}" title="${t("Bild öffnen")}"><img alt="${this._escapeHtml(cover.name || "")}" draggable="false"></div>` : ""}
            <div class="cloud-text" title="${t("Klicken zum Bearbeiten")}">${numbers.has(idea.id) ? `<span class="cloud-number">${numbers.get(idea.id)}</span> ` : ""}${formatText(idea.text)}</div>
            ${idea.result ? `<div class="cloud-result" title="${t("Ergebnis")}">${formatText(idea.result)}</div>` : ""}
            <div class="cloud-actions">
              <button class="action-btn done-btn" data-act="done" data-id="${this._escapeHtml(idea.id)}" title="${t("Als erledigt markieren")}">✓</button>
              <button class="action-btn" data-act="branch" data-lvl="normal" data-id="${this._escapeHtml(idea.id)}" title="${t("Unteridee anlegen")}">🌿</button>
              <button class="action-btn" data-act="edit" data-id="${this._escapeHtml(idea.id)}" title="${t("Bearbeiten")}">✏️</button>
              <button class="action-btn more-btn" data-act="menu" data-id="${this._escapeHtml(idea.id)}" title="${t("Aktionen")}" aria-label="${t("Aktionen")}" aria-haspopup="menu" aria-expanded="${idea.id === this._menuId}">⋯</button>
              <div class="cloud-menu" role="menu">
                <div class="menu-reactions">${reactionBadges(idea, me, true)}</div>
                ${this._isPinboard() && this._canEditIdea(idea) ? `<div class="menu-pins">${Object.entries(PIN_COLORS).map(([name, bg]) => `<button class="pin-swatch${((this._pinOf(idea) || {}).color || "yellow") === name ? " active" : ""}" data-pin-color="${name}" style="--pin-bg: ${bg};" title="${this._escapeHtml(this._pinColorName(name))}" aria-label="${this._escapeHtml(this._pinColorName(name))}"></button>`).join("")}</div>` : ""}
                <button class="action-btn menu-item" role="menuitem" data-act="comments" data-lvl="normal" data-id="${this._escapeHtml(idea.id)}"><span>💬</span>${t("Kommentare")}${idea.comment_count ? ` (${idea.comment_count})` : ""}</button>
                <button class="action-btn menu-item" role="menuitem" data-act="link" data-lvl="pro" data-id="${this._escapeHtml(idea.id)}"><span>🔗</span>${t("Mit einer anderen Notiz verbinden (L)")}</button>
                ${hasBranch ? `<button class="action-btn menu-item" role="menuitem" data-act="focus" data-lvl="normal" data-id="${this._escapeHtml(idea.id)}"><span>🎯</span>${t("Nur diesen Zweig zeigen (F4)")}</button>` : ""}
                ${aiSubtasks ? `<button class="action-btn menu-item" role="menuitem" data-act="suggest" data-lvl="normal" data-id="${this._escapeHtml(idea.id)}"><span>✨</span>${t("Unteraufgaben von der KI vorschlagen lassen")}</button>` : ""}
                <button class="action-btn menu-item" role="menuitem" data-act="move" data-id="${this._escapeHtml(idea.id)}"><span>📁</span>${t("Kategorie ändern")}</button>
                <button class="action-btn menu-item del-btn" role="menuitem" data-act="delete" data-id="${this._escapeHtml(idea.id)}"><span>🗑️</span>${t("Löschen")}</button>
              </div>
            </div>
          </div>
        `;
      });
      // The old notes go, and with them what the observer watched
      if (this._shapeObserver) this._shapeObserver.disconnect();
      container.innerHTML = html;
      this._loadNodeImages(container);
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
      const board = this._isBoard() ? this._layout() : null;
      const layoutKey = shownIdeas
        .map((i) => {
          const pos = this._usesSavedPositions() && i.map_pos ? `${i.map_pos.x},${i.map_pos.y}` : "";
          const pinPlace = this._isPinboard() ? this._pinOf(i) : null;
          const column = board ? boardColumnOf(board, i) : pinPlace ? `${pinPlace.x},${pinPlace.y}` : "";
          return `${i.id}:${i.parent_id || ""}:${pos}:${this._collapsed.has(i.id) ? "folded" : ""}:${column}`;
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
          // On the pinboard every note moves on its own
          if (!this._isPinboard()) roots.forEach((rootId) => this._descendantIds(rootId, filteredIdeas).forEach((d) => ids.add(d)));
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
          if (e.target.closest(".action-btn") || e.target.closest(".cloud-menu") || e.target.closest("a") || e.target.closest(".bs-tag") || e.target.closest(".marker-badge") || e.target.closest(".bs-social") || e.target.closest(".progress-badge") || e.target.closest(".cat-tag") || e.target.closest(".prio-tag") || e.target.closest(".branch-toggle") || e.target.closest(".cloud-inline-editor")) return;
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
          if (e.target.closest(".action-btn") || e.target.closest(".cloud-menu") || e.target.closest("a") || e.target.closest(".bs-tag") || e.target.closest(".marker-badge") || e.target.closest(".bs-social") || e.target.closest(".progress-badge") || e.target.closest(".cat-tag") || e.target.closest(".prio-tag") || e.target.closest(".branch-toggle") || e.target.closest(".cloud-inline-editor")) return;
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
          // While linking, a tap on another note is the end of the line
          if (this._linkFrom && !e.target.closest(".action-btn")) {
            e.stopPropagation();
            this._finishLink(idea.id);
            return;
          }
          // Shift or Ctrl+click, or a tap while selecting, adds or removes the note
          if (e.shiftKey || e.ctrlKey || e.metaKey || this._lassoMode) {
            if (e.target.closest(".action-btn") || e.target.closest(".cloud-menu") || e.target.closest("a")) return;
            this._toggleMulti(idea.id);
            return;
          }
          this._selectIdea(idea.id);
        });
        cloud.addEventListener("dblclick", (e) => {
          if (e.shiftKey || e.ctrlKey || e.metaKey || this._lassoMode) return;
          if (e.target.closest(".action-btn") || e.target.closest(".cloud-menu") || e.target.closest("a") || e.target.closest(".bs-tag") || e.target.closest(".marker-badge") || e.target.closest(".bs-social") || e.target.closest(".progress-badge") || e.target.closest(".cloud-image") || e.target.closest(".cloud-inline-editor")) return;
          this._startInlineEdit(idea.id);
        });
        const textEl = cloud.querySelector(".cloud-text");
        if (textEl) {
          textEl.addEventListener("click", (e) => {
            if (e.shiftKey || e.ctrlKey || e.metaKey || this._lassoMode || this._linkFrom) return;
            e.stopPropagation();
            if (e.target.closest("a") || e.target.closest(".bs-tag")) return;
            if (Date.now() - this._dragEndedAt < 300) return;
            this._selectIdea(idea.id);
            this._startInlineEdit(idea.id);
          });
        }

        // A #tag in the text filters the map by it
        cloud.querySelectorAll(".bs-tag").forEach((tagEl) => {
          tagEl.addEventListener("click", (e) => {
            if (e.shiftKey || e.ctrlKey || e.metaKey || this._lassoMode) return;
            e.stopPropagation();
            this._toggleFilterTag(tagEl.getAttribute("data-tag"));
          });
        });

        // Reactions switch your own, − and + change your points
        cloud.querySelectorAll("[data-react]").forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            this._react(idea.id, btn.getAttribute("data-react"));
          });
        });
        cloud.querySelectorAll("[data-vote]").forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            this._vote(idea.id, Number(btn.getAttribute("data-vote")));
          });
        });
        cloud.querySelectorAll("[data-comment]").forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            this._showComments(idea);
          });
        });

        // A marker filters the map by it, the ring of a note without subtasks moves on
        cloud.querySelectorAll(".marker-badge").forEach((markerEl) => {
          markerEl.addEventListener("click", (e) => {
            if (e.shiftKey || e.ctrlKey || e.metaKey || this._lassoMode) return;
            e.stopPropagation();
            this._toggleFilterMarker(markerEl.getAttribute("data-marker"));
          });
        });
        const progressEl = cloud.querySelector(".progress-badge:not(.progress-auto)");
        if (progressEl) {
          progressEl.addEventListener("click", (e) => {
            if (e.shiftKey || e.ctrlKey || e.metaKey || this._lassoMode) return;
            e.stopPropagation();
            this._cycleProgress(idea);
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

        cloud.querySelectorAll(".pin-swatch").forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            this._closeNodeMenu();
            this._setPinColor(idea, btn.dataset.pinColor);
          });
        });

        // Action buttons
        cloud.querySelectorAll(".action-btn").forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const act = btn.getAttribute("data-act");
            if (act === "menu") {
              this._toggleNodeMenu(idea.id);
              return;
            }
            this._closeNodeMenu();
            this._selectIdea(idea.id);
            if (act === "done") this._completeIdea(idea.id);
            else if (act === "branch") this._showAddDialog(idea);
            else if (act === "focus") this._setFocus(idea.id);
            else if (act === "link") this._startLink(idea.id);
            else if (act === "comments") this._showComments(idea);
            else if (act === "suggest") this._showAiChooser(idea);
            else if (act === "edit") this._showEditDialog(idea.id, idea.text, idea.category, idea.priority);
            else if (act === "move") this._showCategoryPicker(idea.id, idea.category, idea.text);
            else if (act === "delete") this._showDeleteConfirm(idea.id, idea.text);
          });
        });
      });
      this._renderFilterChips();
      this._applyRules();
      this._applyFilter();
    } catch (e) {
      console.error("[BrainstormMindmapCard] Update error:", e);
    }
  }

  /** Open or close the ⋯ menu of a note; only one is open at a time. */
  _toggleNodeMenu(id) {
    const wasOpen = this._menuId === id;
    this._closeNodeMenu();
    if (wasOpen) return;
    const cloud = this.shadowRoot.getElementById(`cloud_${id}`);
    if (!cloud) return;
    this._menuId = id;
    cloud.classList.add("menu-open");
    const btn = cloud.querySelector(".more-btn");
    if (btn) btn.setAttribute("aria-expanded", "true");
    // Opens upward when there is no room below the note
    const menu = cloud.querySelector(".cloud-menu");
    const area = this.shadowRoot.getElementById("canvasArea");
    if (menu && area) {
      const box = area.getBoundingClientRect();
      const note = cloud.getBoundingClientRect();
      cloud.classList.toggle("menu-up", box.bottom - note.bottom < menu.offsetHeight + 8);
      // Opens to the right when it would leave the map on the left
      cloud.classList.toggle("menu-left", menu.getBoundingClientRect().left < box.left + 4);
    }
  }

  _closeNodeMenu() {
    if (!this._menuId) return;
    const cloud = this.shadowRoot.getElementById(`cloud_${this._menuId}`);
    this._menuId = null;
    if (!cloud) return;
    cloud.classList.remove("menu-open", "menu-up", "menu-left");
    const btn = cloud.querySelector(".more-btn");
    if (btn) btn.setAttribute("aria-expanded", "false");
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

    if (this._dialogCleanup) {
      const cleanup = this._dialogCleanup;
      this._dialogCleanup = null;
      cleanup();
    }
    this._isModalOpen = true;
    titleEl.innerHTML = title;
    if (bodyEl._bsAttachments) bodyEl._bsAttachments.abort();
    bodyEl._bsAttachments = null;
    bodyEl.innerHTML = "";
    renderFn(bodyEl);
    dialog.style.display = "flex";
  }

  _closeDialog() {
    if (this._dialogCleanup) {
      const cleanup = this._dialogCleanup;
      this._dialogCleanup = null;
      cleanup();
    }
    const dialog = this.shadowRoot.getElementById("mindmapDialog");
    if (dialog) dialog.style.display = "none";
    this._isModalOpen = false;
    if (this._presenceEditing && !this._inlineEdit) this._setPresenceEditing(null);
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
    this._setPresenceEditing(id);
    const sensor = this._getSensorEntity();
    const categories = sensor ? (sensor.attributes.categories || ["Inbox"]) : ["Inbox"];
    let selectedCat = currentCategory || "Inbox";
    let selectedPrio = (currentPriority || "medium").toLowerCase();
    const allIdeas = (sensor && sensor.attributes.ideas) || [];
    const idea = allIdeas.find((i) => i.id === id) || {};
    const rawText = idea.raw_text;
    const currentParentId = idea.parent_id || null;
    const dueValues = dueInputValues(idea.due);
    const echos = alexaEchos(this._hass);
    const currentEchos = idea.echos || [];
    let selectedEchos = [...currentEchos];
    const currentShape = NODE_SHAPES.includes(idea.shape) ? idea.shape : "";
    let selectedShape = currentShape;
    const shapeChoices = [["", t("Automatisch")], ...NODE_SHAPES.map((shape) => [shape, shapeLabel(shape)])];
    const currentMarkers = ideaMarkers(idea);
    let selectedMarkers = new Set(currentMarkers);
    const hasSubtasks = Boolean(idea.subtasks && idea.subtasks.total);
    const currentProgress = Number(idea.progress) || 0;
    let selectedProgress = currentProgress;
    const currentNumbering = NUMBERING.includes(idea.numbering) ? idea.numbering : "";
    let selectedNumbering = currentNumbering;

    this._openDialog(t("✏️ Notiz bearbeiten"), (body) => {
      body.innerHTML = `
        <div class="dialog-label">${t("Titel:")}</div>
        <textarea class="dialog-textarea" id="editTextarea" rows="2">${this._escapeHtml(currentText)}</textarea>
        <div class="dialog-error" id="editTextError" style="display: none;"></div>
        <div class="dialog-label">${t("Beschreibung:")}</div>
        <textarea class="dialog-textarea" id="editDescription" rows="4" placeholder="${t("Optional: Details, Links, Notizen …")}">${this._escapeHtml(idea.description || "")}</textarea>
        <div class="lvl" data-lvl="normal"><div class="dialog-label">${t("Anhänge:")}</div>
        <div id="editAttachments"></div></div>
        ${rawText && rawText !== currentText ? `<div class="lvl" data-lvl="pro">
          <div class="dialog-label">${t("Original gesprochen:")}</div>
          <div class="dialog-original-row">
            <span id="editOriginalText" class="dialog-original-text">${this._escapeHtml(rawText)}</span>
            <button class="dialog-btn dialog-btn-cancel" id="editUseOriginal">${t("Übernehmen")}</button>
          </div></div>
        ` : ""}

        <div class="dialog-label">${t("Priorität:")}</div>
        <div class="dialog-prio-grid" id="editPrioGrid">
          <div class="dialog-prio-chip ${selectedPrio === "low" ? "selected" : ""}" data-prio="low">${t("🟢 Niedrig")}</div>
          <div class="dialog-prio-chip ${selectedPrio === "medium" ? "selected" : ""}" data-prio="medium">${t("🟡 Mittel")}</div>
          <div class="dialog-prio-chip ${selectedPrio === "high" ? "selected" : ""}" data-prio="high">${t("🔴 Hoch")}</div>
          <div class="dialog-prio-chip ${selectedPrio === "urgent" ? "selected" : ""}" data-prio="urgent">${t("🔥 Dringend")}</div>
        </div>

        <div class="lvl" data-lvl="normal"><div class="dialog-label">${t("Marker:")}</div>
        <div class="dialog-prio-grid dialog-marker-grid" id="editMarkerGrid">
          ${MARKERS.map((marker) => `<div class="dialog-prio-chip ${selectedMarkers.has(marker) ? "selected" : ""}" data-marker="${marker}" title="${this._escapeHtml(markerLabel(marker))}">${markerIcon(marker)} ${this._escapeHtml(markerLabel(marker))}</div>`).join("")}
        </div></div>

        <div class="lvl" data-lvl="pro"><div class="dialog-label">${t("Fortschritt:")}</div>
        ${hasSubtasks
          ? `<div class="dialog-hint">${t("Kommt aus den Unteraufgaben: {done} von {total} erledigt, {percent} %.", { done: idea.subtasks.done, total: idea.subtasks.total, percent: idea.subtasks.percent })}</div>`
          : `<div class="dialog-prio-grid dialog-progress-grid" id="editProgressGrid">
          ${[0, 25, 50, 75, 100].map((step) => `<div class="dialog-prio-chip ${step === selectedProgress ? "selected" : ""}" data-progress="${step}">${step} %</div>`).join("")}
        </div>`}</div>

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
        <div class="lvl" data-lvl="normal"><div class="dialog-label">${t("Wiederholen:")}</div>
        <select class="dialog-input" id="editRepeat" title="${t("Abgehakt kommt die Notiz mit ihren Unteraufgaben zum nächsten Termin wieder.")}">${repeatOptions(idea.repeat)}</select></div>

        ${echos.length ? `
          <details class="dialog-echo-details" data-lvl="pro">
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

        <div class="lvl" data-lvl="normal"><div class="dialog-label">${t("Übergeordnete Aufgabe:")}</div>
        <select class="dialog-input" id="editParentSelect">${parentOptions(allIdeas, id, currentParentId, idea.category || currentCategory)}</select></div>

        ${hasSubtasks ? `<div class="lvl" data-lvl="pro">
        <div class="dialog-label">${t("Unterpunkte nummerieren:")}</div>
        <div class="dialog-prio-grid dialog-numbering-grid" id="editNumberingGrid">
          ${["", ...NUMBERING].map((style) => `<div class="dialog-prio-chip ${style === selectedNumbering ? "selected" : ""}" data-numbering="${style}">${numberingLabel(style)}</div>`).join("")}
        </div>
        <div class="dialog-label">${t("Unterpunkte sortieren:")}</div>
        <div class="dialog-prio-grid dialog-sort-grid" id="editSortGrid">${this._sortChips()}</div>
        <div class="dialog-hint">${t("Sortiert sofort, ↶ macht es rückgängig.")}</div>
        </div>` : ""}

        <div class="lvl" data-lvl="pro"><div class="dialog-label">${t("Callout:")}</div>
        <input class="dialog-input" id="editCallout" maxlength="200" placeholder="${t("Optional: kurze Anmerkung in einer Sprechblase")}" value="${this._escapeHtml(idea.callout || "")}">
        <div class="dialog-label">${t("Rahmen:")}</div>
        <input class="dialog-input" id="editFrame" maxlength="40" list="editFrameNames" placeholder="${t("Optional: Name eines Rahmens")}" value="${this._escapeHtml(idea.frame || "")}">
        <datalist id="editFrameNames">${[...new Set(((sensor && sensor.attributes.ideas) || []).filter((i) => i.category === (idea.category || currentCategory)).map((i) => i.frame).filter(Boolean))].map((f) => `<option value="${this._escapeHtml(f)}"></option>`).join("")}</datalist>


        <div class="dialog-label">${t("Form auf der Mindmap:")}</div>
        <div class="dialog-prio-grid dialog-shape-grid" id="editShapeGrid">
          ${shapeChoices
            .map(([value, label]) => `<div class="dialog-prio-chip ${value === selectedShape ? "selected" : ""}" data-shape="${value}">${label}</div>`)
            .join("")}
        </div>
        <div class="dialog-hint dialog-shape-hint">${t("Automatisch: Sprachnotizen als Sprechblase, sonst die Form der Map.")}</div></div>

        <div class="dialog-footer">
          <button class="dialog-btn dialog-btn-cancel" id="cancelEditBtn">${t("Abbrechen")}</button>
          <button class="dialog-btn dialog-btn-primary" id="saveEditBtn">${t("Speichern")}</button>
        </div>
      `;

      addMoreFields(body, this._applyLevel(), "dialog-btn dialog-btn-cancel");
      const textarea = body.querySelector("#editTextarea");
      renderAttachments(body.querySelector("#editAttachments"), {
        hass: this._hass,
        idea: { ...idea, id },
        canEdit: true,
        dropTarget: body,
      });
      const useOriginal = body.querySelector("#editUseOriginal");
      if (useOriginal) {
        useOriginal.addEventListener("click", () => {
          textarea.value = rawText;
          textarea.focus();
        });
      }
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
      body.querySelectorAll("#editMarkerGrid .dialog-prio-chip").forEach((chip) => {
        chip.addEventListener("click", () => {
          const marker = chip.getAttribute("data-marker");
          if (selectedMarkers.has(marker)) selectedMarkers.delete(marker);
          else selectedMarkers.add(marker);
          chip.classList.toggle("selected", selectedMarkers.has(marker));
        });
      });
      const numberingChips = body.querySelectorAll("#editNumberingGrid .dialog-prio-chip");
      numberingChips.forEach((chip) => {
        chip.addEventListener("click", () => {
          numberingChips.forEach((c) => c.classList.remove("selected"));
          chip.classList.add("selected");
          selectedNumbering = chip.getAttribute("data-numbering") || "";
        });
      });
      body.querySelectorAll("#editSortGrid [data-sort]").forEach((chip) => {
        chip.addEventListener("click", () => this._sortChildren(id, chip.getAttribute("data-sort"), chip.hasAttribute("data-reverse")));
      });
      const progressChips = body.querySelectorAll("#editProgressGrid .dialog-prio-chip");
      progressChips.forEach((chip) => {
        chip.addEventListener("click", () => {
          progressChips.forEach((c) => c.classList.remove("selected"));
          chip.classList.add("selected");
          selectedProgress = Number(chip.getAttribute("data-progress")) || 0;
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
        const newRepeat = body.querySelector("#editRepeat").value || "";
        if (newRepeat !== (idea.repeat || "")) {
          payload.repeat = newRepeat;
        }
        const newDescription = (body.querySelector("#editDescription").value || "").trim();
        if (newDescription !== (idea.description || "")) {
          payload.description = newDescription;
        }
        if (selectedShape !== currentShape) {
          payload.shape = selectedShape || null;
        }
        const newMarkers = MARKERS.filter((marker) => selectedMarkers.has(marker));
        if (newMarkers.join() !== currentMarkers.join()) {
          payload.markers = newMarkers;
        }
        if (!hasSubtasks && selectedProgress !== currentProgress) {
          payload.progress = selectedProgress;
        }
        if (selectedNumbering !== currentNumbering) payload.numbering = selectedNumbering || null;
        const newCallout = (body.querySelector("#editCallout").value || "").trim();
        if (newCallout !== (idea.callout || "")) payload.callout = newCallout || null;
        const newFrame = (body.querySelector("#editFrame").value || "").trim();
        if (newFrame !== (idea.frame || "")) payload.frame = newFrame || null;
        const newParent = body.querySelector("#editParentSelect").value || "";
        if (newParent !== (currentParentId || "")) payload.parent_id = newParent;

        // Everything this save changes, as it was before
        const before = { id, text: currentText, priority: currentPriority || "medium" };
        if ("category" in payload) before.category = currentCategory;
        if ("due" in payload) before.due = idea.due || null;
        if ("echos" in payload) before.echos = currentEchos.length ? currentEchos : null;
        if ("description" in payload) before.description = idea.description || "";
        if ("shape" in payload) before.shape = currentShape || null;
        if ("markers" in payload) before.markers = currentMarkers;
        if ("progress" in payload) before.progress = currentProgress;
        if ("callout" in payload) before.callout = idea.callout || null;
        if ("numbering" in payload) before.numbering = currentNumbering || null;
        if ("frame" in payload) before.frame = idea.frame || null;
        if ("parent_id" in payload) before.parent_id = currentParentId || "";
        if ("repeat" in payload) before.repeat = idea.repeat || "";
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
    // In a focused branch a new note hangs below it
    if (!parent && this._focusId) parent = this._focusIdea();
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
        name: "level",
        label: t("Bedienstufe dieser Karte"),
        default: "auto",
        selector: {
          select: {
            mode: "dropdown",
            options: ["auto", "beginner", "normal", "pro"].map((value) => ({ value, label: levelLabel(value) })),
          },
        },
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
        name: "layout",
        label: t("Anordnung der Notizen"),
        default: "radial",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "radial", label: t("Rund um die Mitte") },
              { value: "tree", label: t("Baum nach rechts") },
              { value: "org", label: t("Organigramm nach unten") },
              { value: "outline", label: t("Gliederung") },
              { value: "pin", label: t("Pinnwand mit Haftzetteln") },
              { value: "kanban", label: t("Kanban nach Status") },
              { value: "timeline", label: t("Zeitleiste nach Fälligkeit") },
              { value: "matrix", label: t("Eisenhower-Matrix") },
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
        name: "show_minimap",
        label: t("Übersicht (Minimap) anzeigen"),
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
        name: "show_images",
        label: t("Bilder aus den Anhängen in den Notizen zeigen"),
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_filter",
        label: t("Suche und Filter (🔍) anzeigen"),
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
          <input class="fallback-input" id="fbTitle" type="text" value="${this._escapeHtml(this._config.title || 'Brainstorm Mindmap')}" />
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
  "%c BRAINSTORM-MINDMAP-CARD %c v1.11.10 ",
  "color: #07070e; background: #00f5ff; font-weight: bold; border-radius: 4px 0 0 4px; padding: 2px 4px;",
  "color: #ffffff; background: #9d4edd; font-weight: bold; border-radius: 0 4px 4px 0; padding: 2px 4px;"
);
