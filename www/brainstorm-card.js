/**
 * Brainstorm Card for Home Assistant
 * Modern, sleek quick capture and idea manager
 * Version 1.4.29 - Drag & Drop Sorting, Subtask Assignment & Apple Reminders Context Menu
 */
const BRAINSTORM_CARD_DEFAULTS = {
  title: "Brainstorm Hub",
  sensor: "sensor.brainstorm_ideen_ubersicht",
  color_mode: "multicolor",
  default_category: "all",
  max_items: 0,
  show_quick_input: true,
  show_categories: true,
  hide_empty_categories: true,
  show_badge: true,
  show_mindmap_button: true,
  show_color_toggle: true,
  show_source_icons: true,
  show_timestamps: true,
  allow_edit: true,
  allow_delete: true,
};

class BrainstormCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._selectedCategory = "all";
    this._viewMode = "list"; // 'list' | 'mindmap'
    this._config = { ...BRAINSTORM_CARD_DEFAULTS };
    let savedColorMode = "multicolor";
    try {
      savedColorMode = localStorage.getItem("brainstorm_color_mode") || "multicolor";
    } catch {}
    this._colorMode = savedColorMode; // 'multicolor' | 'theme'
    this._lastColorMode = null;
    this._initialized = false;
    this._lastUpdated = null;
    this._lastCategory = "all";
    this._isDialogOpen = false;
  }

  static async getConfigElement() {
    return document.createElement("brainstorm-card-editor");
  }

  static getStubConfig(hass) {
    return { ...BRAINSTORM_CARD_DEFAULTS };
  }

  setConfig(config) {
    if (!config) config = {};
    this._rawConfig = config;
    const parsedConfig = { ...BRAINSTORM_CARD_DEFAULTS };
    for (const key of Object.keys(BRAINSTORM_CARD_DEFAULTS)) {
      if (key in config) {
        if (typeof BRAINSTORM_CARD_DEFAULTS[key] === "boolean") {
          parsedConfig[key] = config[key] === true || config[key] === "true";
        } else if (typeof BRAINSTORM_CARD_DEFAULTS[key] === "number") {
          parsedConfig[key] = Number(config[key]) || 0;
        } else {
          parsedConfig[key] = config[key];
        }
      }
    }
    this._config = { ...config, ...parsedConfig };

    if (config.color_mode) {
      this._colorMode = config.color_mode;
    }
    if (this._config.default_category && (!this._initialized || this._selectedCategory === "all")) {
      this._selectedCategory = String(this._config.default_category).trim();
    }
    this._lastUpdated = null; // Force refresh on config change
    this._lastColorMode = null;
    if (this._initialized) {
      this._updateContent();
    }
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._initDom();
    } else {
      if (!this._isDialogOpen) {
        this._updateContent();
      }
      const popupMindmap = this.shadowRoot.getElementById("popupMindmap");
      const mindmapModal = this.shadowRoot.getElementById("mindmapModal");
      if (popupMindmap && mindmapModal && mindmapModal.style.display === "flex") {
        popupMindmap.hass = hass;
      }
    }
  }

  _getSensorEntity() {
    if (!this._hass) return null;
    const configured = (this._config && this._config.sensor) || "sensor.brainstorm_ideen_ubersicht";
    if (
      this._hass.states &&
      this._hass.states[configured] &&
      this._hass.states[configured].attributes &&
      Array.isArray(this._hass.states[configured].attributes.ideas)
    ) {
      return this._hass.states[configured];
    }
    if (this._hass.states && this._hass.states["sensor.brainstorm_hub_brainstorm_ideen_ubersicht"]) {
      return this._hass.states["sensor.brainstorm_hub_brainstorm_ideen_ubersicht"];
    }
    if (this._hass.states && this._hass.states["sensor.brainstorm_ideen_ubersicht"]) {
      return this._hass.states["sensor.brainstorm_ideen_ubersicht"];
    }
    return this._hass.states ? this._hass.states[configured] : null;
  }

  _escapeHtml(text) {
    if (text === null || text === undefined) return "";
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  _getCategoryColor(category) {
    if (this._colorMode === "theme") {
      return "var(--primary-color, #a855f7)";
    }
    if (!category) return "#2563eb";
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

  _getSourceBadge(source, device) {
    const s = (source || "").toLowerCase();
    let icon = "📝";
    let name = "Notiz";
    if (s.includes("alexa") || s === "voice") {
      icon = "🗣️";
      name = "Alexa";
    } else if (s.includes("assist")) {
      icon = "✨";
      name = "Assist";
    } else if (s.includes("companion_voice") || s.includes("mic") || s.includes("speech")) {
      icon = "🎙️";
      name = "Sprache";
    } else if (s.includes("companion") || s.includes("mobile") || s.includes("handy")) {
      icon = "📱";
      name = "Handy";
    } else if (s.includes("dashboard")) {
      icon = "💻";
      name = "Dashboard";
    }

    if (device && String(device).trim()) {
      const cleanDev = String(device).trim();
      return `<span class="source-badge" title="Quelle: ${name} • Gerät: ${this._escapeHtml(cleanDev)}">${icon} ${this._escapeHtml(name)} <span class="source-device">(${this._escapeHtml(cleanDev)})</span></span>`;
    }
    return `<span class="source-badge" title="Quelle: ${name}">${icon} ${this._escapeHtml(name)}</span>`;
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
      if (diffSec < 3600) return `vor ${Math.floor(diffSec / 60)} Min.`;
      if (diffSec < 86400) return `vor ${Math.floor(diffSec / 3600)} Std.`;
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
      console.error("Failed to toggle priority", err);
    }
  }

  async _submitIdea() {
    const inputEl = this.shadowRoot.getElementById("ideaInput");
    const catSelectEl = this.shadowRoot.getElementById("catSelect");
    const prioSelectEl = this.shadowRoot.getElementById("prioSelect");
    if (!inputEl) return;

    const text = inputEl.value.trim();
    if (!text) return;

    const selectedCat = catSelectEl ? catSelectEl.value : "";
    let category = selectedCat && selectedCat !== "auto" ? selectedCat : null;
    if (!category && this._selectedCategory && this._selectedCategory !== "all" && this._selectedCategory !== "__completed__") {
      category = this._selectedCategory;
    }
    const priority = prioSelectEl ? prioSelectEl.value : "medium";

    inputEl.value = "";
    inputEl.disabled = true;

    try {
      const payload = {
        text: text,
        source: "dashboard",
        priority: priority,
      };
      if (category) {
        payload.category = category;
      }
      await this._hass.callService("brainstorm", "add_idea", payload);
    } catch (e) {
      console.error("Failed to add brainstorm idea", e);
    } finally {
      inputEl.disabled = false;
      inputEl.focus();
    }
  }

  async _completeIdea(id) {
    try {
      await this._hass.callService("brainstorm", "update_idea", {
        id: id,
        status: "completed",
      });
    } catch (e) {
      console.error("Failed to complete idea", e);
    }
  }

  async _uncompleteIdea(id) {
    try {
      await this._hass.callService("brainstorm", "update_idea", {
        id: id,
        status: "active",
      });
    } catch (e) {
      console.error("Failed to uncomplete idea", e);
    }
  }

  async _deleteIdea(id) {
    try {
      await this._hass.callService("brainstorm", "delete_idea", {
        id: id,
      });
    } catch (e) {
      console.error("Failed to delete idea", e);
    }
  }

  _openDialog(title, renderFn) {
    const dialog = this.shadowRoot.getElementById("cardDialog");
    const titleEl = this.shadowRoot.getElementById("cardDialogTitle");
    const bodyEl = this.shadowRoot.getElementById("cardDialogBody");
    if (!dialog || !titleEl || !bodyEl) return;

    this._isDialogOpen = true;
    titleEl.innerHTML = title;
    bodyEl.innerHTML = "";
    renderFn(bodyEl);
    dialog.style.display = "flex";
  }

  _closeDialog() {
    const dialog = this.shadowRoot.getElementById("cardDialog");
    if (dialog) dialog.style.display = "none";
    this._isDialogOpen = false;
  }

  _editIdea(id, currentText, currentCategory, currentPriority = "medium", currentParentId = null) {
    const sensor = this._getSensorEntity();
    const categories = sensor ? (sensor.attributes.categories || ["Inbox"]) : ["Inbox"];
    const activeIdeas = sensor ? (sensor.attributes.ideas || []) : [];
    let selectedCat = currentCategory || "Inbox";
    let selectedPrio = (currentPriority || "medium").toLowerCase();
    const candidateParents = activeIdeas.filter((i) => i.id !== id && !i.parent_id);

    this._openDialog("✏️ Notiz bearbeiten", (body) => {
      body.innerHTML = `
        <div class="action-dialog-label">Notiztext:</div>
        <textarea class="action-dialog-textarea" id="editTextarea" rows="3">${this._escapeHtml(currentText)}</textarea>
        <div class="action-dialog-error" id="editTextError" style="display: none;"></div>

        <div class="action-dialog-label">Priorität:</div>
        <div class="action-dialog-prio-grid" id="editPrioGrid">
          <div class="action-dialog-prio-chip ${selectedPrio === "low" ? "selected" : ""}" data-prio="low" style="--chip-prio-color: #10b981;">🟢 Niedrig</div>
          <div class="action-dialog-prio-chip ${selectedPrio === "medium" ? "selected" : ""}" data-prio="medium" style="--chip-prio-color: #eab308;">🟡 Mittel</div>
          <div class="action-dialog-prio-chip ${selectedPrio === "high" ? "selected" : ""}" data-prio="high" style="--chip-prio-color: #f97316;">🔴 Hoch</div>
          <div class="action-dialog-prio-chip ${selectedPrio === "urgent" ? "selected" : ""}" data-prio="urgent" style="--chip-prio-color: #ef4444;">🔥 Dringend</div>
        </div>

        <div class="action-dialog-label">Kategorie:</div>
        <div class="action-dialog-categories-grid" id="editCatGrid">
          ${categories
            .map((cat) => {
              const isSel = cat === selectedCat;
              const color = this._getCategoryColor(cat);
              return `
                <div class="action-dialog-cat-chip ${isSel ? "selected" : ""}" data-cat="${this._escapeHtml(cat)}" style="--chip-color: ${color};">
                  <span class="action-dialog-cat-dot"></span>
                  <span class="action-dialog-cat-name">${this._escapeHtml(cat)}</span>
                </div>
              `;
            })
            .join("")}
        </div>

        <div class="action-dialog-label" style="margin-top: 6px;">Übergeordnete Aufgabe:</div>
        <select class="action-dialog-input" id="editParentSelect" style="cursor: pointer; width: 100%;">
          <option value="">— Keine (Hauptaufgabe) —</option>
          ${candidateParents
            .map(
              (p) => `
            <option value="${p.id}" ${p.id === currentParentId ? "selected" : ""}>
              ↳ ${this._escapeHtml(p.text.length > 50 ? p.text.substring(0, 50) + "..." : p.text)}
            </option>
          `
            )
            .join("")}
        </select>

        <div class="action-dialog-footer">
          <button class="action-dialog-btn action-dialog-btn-cancel" id="cancelEditBtn">Abbrechen</button>
          <button class="action-dialog-btn action-dialog-btn-primary" id="saveEditBtn">Speichern</button>
        </div>
      `;

      const textarea = body.querySelector("#editTextarea");
      const textError = body.querySelector("#editTextError");
      const saveBtn = body.querySelector("#saveEditBtn");
      const cancelBtn = body.querySelector("#cancelEditBtn");
      const catChips = body.querySelectorAll(".action-dialog-cat-chip");
      const prioChips = body.querySelectorAll(".action-dialog-prio-chip");

      setTimeout(() => {
        if (textarea) {
          textarea.focus();
          textarea.setSelectionRange(textarea.value.length, textarea.value.length);
        }
      }, 50);

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

      prioChips.forEach((chip) => {
        chip.addEventListener("click", () => {
          prioChips.forEach((c) => c.classList.remove("selected"));
          chip.classList.add("selected");
          selectedPrio = chip.getAttribute("data-prio");
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
        const parentSelect = body.querySelector("#editParentSelect");
        if (parentSelect) {
          const selectedPid = parentSelect.value || "";
          if (selectedPid !== (currentParentId || "")) {
            payload.parent_id = selectedPid;
          }
        }

        try {
          await this._hass.callService("brainstorm", "update_idea", payload);
        } catch (err) {
          console.error("Failed to update idea", err);
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

  _changeCategory(id, currentCategory, noteText) {
    const sensor = this._getSensorEntity();
    const categories = sensor ? (sensor.attributes.categories || ["Inbox"]) : ["Inbox"];
    const counts = sensor ? (sensor.attributes.category_counts || {}) : {};

    this._openDialog("🏷️ Kategorie auswählen", (body) => {
      let previewHtml = "";
      if (noteText) {
        previewHtml = `<div class="action-dialog-note-preview">"${this._escapeHtml(noteText)}"</div>`;
      }

      body.innerHTML = `
        ${previewHtml}
        <div class="action-dialog-label">Kategorie wählen:</div>
        <div class="action-dialog-categories-grid">
          ${categories
            .map((cat) => {
              const isSel = cat === currentCategory;
              const color = this._getCategoryColor(cat);
              const count = counts[cat] || 0;
              return `
                <div class="action-dialog-cat-chip ${isSel ? "selected" : ""}" data-cat="${this._escapeHtml(cat)}" style="--chip-color: ${color};">
                  <span class="action-dialog-cat-dot"></span>
                  <span class="action-dialog-cat-name">${this._escapeHtml(cat)}</span>
                  <span class="action-dialog-cat-count">${isSel ? "✓" : count}</span>
                </div>
              `;
            })
            .join("")}
        </div>
        <div class="action-dialog-label" style="margin-top: 6px;">Oder neue Kategorie anlegen:</div>
        <div class="action-dialog-new-cat-row">
          <input type="text" class="action-dialog-input" id="newCatInput" placeholder="Kategoriename..." />
          <button class="action-dialog-btn action-dialog-btn-primary" id="addNewCatBtn">➕ Erstellen</button>
        </div>
        <div class="action-dialog-error" id="newCatError" style="display: none;"></div>
      `;

      body.querySelectorAll(".action-dialog-cat-chip").forEach((chip) => {
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
              console.error("Failed to update category", err);
            }
          }
        });
      });

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
          console.error("Failed to add category", err);
        }
      };

      addNewCatBtn.addEventListener("click", handleCreateCat);
      newCatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleCreateCat();
      });
      setTimeout(() => newCatInput && newCatInput.focus(), 60);
    });
  }

  _addCategory() {
    const sensor = this._getSensorEntity();
    const existingCats = (sensor && sensor.attributes && sensor.attributes.categories) || [];

    this._openDialog("➕ Neue Kategorie", (body) => {
      body.innerHTML = `
        <div class="action-dialog-label">Name der neuen Kategorie:</div>
        <div style="width: 100%; display: flex; flex-direction: column;">
          <input type="text" class="action-dialog-input" id="createCatInput" placeholder="z. B. Smart Home, Finanzen, Einkaufen..." style="width: 100%;" />
          <div class="action-dialog-error" id="createCatError" style="display: none;"></div>
        </div>
        <div class="action-dialog-footer">
          <button class="action-dialog-btn action-dialog-btn-cancel" id="cancelAddCatBtn">Abbrechen</button>
          <button class="action-dialog-btn action-dialog-btn-primary" id="saveAddCatBtn">Kategorie erstellen</button>
        </div>
      `;

      const input = body.querySelector("#createCatInput");
      const errDiv = body.querySelector("#createCatError");
      const saveBtn = body.querySelector("#saveAddCatBtn");
      const cancelBtn = body.querySelector("#cancelAddCatBtn");

      const showError = (msg) => {
        if (!errDiv || !input) return;
        errDiv.textContent = msg;
        errDiv.style.display = "flex";
        input.classList.remove("input-error");
        void input.offsetWidth;
        input.classList.add("input-error");
        input.focus();
      };

      const clearError = () => {
        if (errDiv) {
          errDiv.textContent = "";
          errDiv.style.display = "none";
        }
        if (input) input.classList.remove("input-error");
      };

      input.addEventListener("input", clearError);

      const handleAdd = async () => {
        const name = (input.value || "").trim();
        if (!name) {
          showError("⚠️ Bitte gib einen Kategorienamen ein.");
          return;
        }
        if (existingCats.some((c) => c.toLowerCase() === name.toLowerCase())) {
          showError(`⚠️ Die Kategorie "${name}" existiert bereits.`);
          return;
        }
        this._closeDialog();
        try {
          await this._hass.callService("brainstorm", "add_category", { name: name });
        } catch (err) {
          console.error("Failed to add category", err);
        }
      };

      saveBtn.addEventListener("click", handleAdd);
      cancelBtn.addEventListener("click", () => this._closeDialog());
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleAdd();
      });
      setTimeout(() => input && input.focus(), 60);
    });
  }

  _removeCategory(categoryName) {
    if (categoryName === "Inbox") return;
    this._openDialog("🗑️ Kategorie löschen?", (body) => {
      body.innerHTML = `
        <p style="margin: 8px 0; font-size: 0.9rem; line-height: 1.4; color: var(--primary-text-color, #212121);">
          Möchtest du die Kategorie <strong>"${this._escapeHtml(categoryName)}"</strong> wirklich löschen?
        </p>
        <p style="margin: 0 0 12px 0; font-size: 0.8rem; color: var(--secondary-text-color, #64748b);">
          Enthaltene Notizen werden automatisch in die Kategorie <em>Inbox</em> verschoben.
        </p>
        <div class="action-dialog-footer">
          <button class="action-dialog-btn action-dialog-btn-cancel" id="cancelRemoveCatBtn">Abbrechen</button>
          <button class="action-dialog-btn action-dialog-btn-primary" id="confirmRemoveCatBtn" style="background: var(--error-color, #db4437);">Löschen</button>
        </div>
      `;

      body.querySelector("#cancelRemoveCatBtn").addEventListener("click", () => this._closeDialog());
      body.querySelector("#confirmRemoveCatBtn").addEventListener("click", async () => {
        this._closeDialog();
        try {
          await this._hass.callService("brainstorm", "remove_category", {
            name: categoryName,
          });
          if (String(this._selectedCategory).trim() === String(categoryName).trim()) {
            this._selectedCategory = "all";
          }
        } catch (e) {
          console.error("Failed to remove category", e);
        }
      });
    });
  }

  _openContextMenu(item, prevTopLevelItem, nextItem, prevItem, activeIdeas) {
    const backdrop = this.shadowRoot.getElementById("appleContextMenu");
    const titleEl = this.shadowRoot.getElementById("appleMenuTitle");
    const actionsEl = this.shadowRoot.getElementById("appleMenuActions");
    if (!backdrop || !titleEl || !actionsEl) return;

    titleEl.textContent = item.text;
    actionsEl.innerHTML = "";

    const isSub = item.isSubtask === true;
    let actionsHtml = "";

    // Subtask Action: Indent under previous item or outdent to main task
    if (isSub) {
      actionsHtml += `
        <button class="apple-menu-btn action-indent" data-act="outdent">
          <span class="btn-icon">↰</span>
          <div class="btn-content">
            <span>Ausrücken</span>
            <span class="btn-sublabel">Wieder zur Hauptaufgabe machen</span>
          </div>
        </button>
      `;
    } else if (prevTopLevelItem) {
      const prevTitle = prevTopLevelItem.text.length > 30 ? prevTopLevelItem.text.slice(0, 30) + "..." : prevTopLevelItem.text;
      actionsHtml += `
        <button class="apple-menu-btn action-indent" data-act="indent" data-target="${prevTopLevelItem.id}">
          <span class="btn-icon">↳</span>
          <div class="btn-content">
            <span>Unteraufgabe einrücken</span>
            <span class="btn-sublabel">Unter: „${this._escapeHtml(prevTitle)}“</span>
          </div>
        </button>
      `;
    }

    // Move Up / Move Down
    if (prevItem) {
      actionsHtml += `
        <button class="apple-menu-btn" data-act="move-up">
          <span class="btn-icon">⬆️</span>
          <div class="btn-content"><span>Nach oben verschieben</span></div>
        </button>
      `;
    }
    if (nextItem) {
      actionsHtml += `
        <button class="apple-menu-btn" data-act="move-down">
          <span class="btn-icon">⬇️</span>
          <div class="btn-content"><span>Nach unten verschieben</span></div>
        </button>
      `;
    }

    actionsHtml += `<div class="apple-menu-separator"></div>`;

    // Edit
    actionsHtml += `
      <button class="apple-menu-btn" data-act="edit">
        <span class="btn-icon">✏️</span>
        <div class="btn-content"><span>Notiz bearbeiten</span></div>
      </button>
    `;

    // Delete
    actionsHtml += `
      <button class="apple-menu-btn action-danger" data-act="delete">
        <span class="btn-icon">🗑️</span>
        <div class="btn-content"><span>Notiz löschen</span></div>
      </button>
    `;

    actionsEl.innerHTML = actionsHtml;

    // Attach listeners
    actionsEl.querySelectorAll(".apple-menu-btn").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        this._closeContextMenu();
        const act = btn.getAttribute("data-act");

        if (act === "outdent") {
          try {
            await this._hass.callService("brainstorm", "update_idea", {
              id: item.id,
              parent_id: "",
            });
          } catch (err) {
            console.error("Failed to outdent", err);
          }
        } else if (act === "indent") {
          const targetId = btn.getAttribute("data-target");
          try {
            await this._hass.callService("brainstorm", "update_idea", {
              id: item.id,
              parent_id: targetId,
            });
          } catch (err) {
            console.error("Failed to indent", err);
          }
        } else if (act === "move-up" && prevItem) {
          await this._swapIdeasOrder(item.id, prevItem.id);
        } else if (act === "move-down" && nextItem) {
          await this._swapIdeasOrder(item.id, nextItem.id);
        } else if (act === "edit") {
          this._editIdea(item.id, item.text, item.category, item.priority, item.parent_id);
        } else if (act === "delete") {
          await this._deleteIdea(item.id);
        }
      });
    });

    backdrop.style.display = "flex";
  }

  _closeContextMenu() {
    const backdrop = this.shadowRoot.getElementById("appleContextMenu");
    if (backdrop) backdrop.style.display = "none";
  }

  async _swapIdeasOrder(idA, idB) {
    const sensor = this._getSensorEntity();
    if (!sensor || !this._hass) return;
    const activeIdeas = (sensor.attributes && sensor.attributes.ideas) || [];
    const ids = activeIdeas.map((i) => i.id);
    const idxA = ids.indexOf(idA);
    const idxB = ids.indexOf(idB);
    if (idxA === -1 || idxB === -1) return;

    ids[idxA] = idB;
    ids[idxB] = idA;

    try {
      await this._hass.callService("brainstorm", "reorder_ideas", {
        idea_ids: ids,
      });
    } catch (err) {
      console.error("Failed to swap ideas order", err);
    }
  }

  _initDom() {
    if (!this._hass || !this._config) return;
    this._initialized = true;

    this.shadowRoot.innerHTML = `
      <style>
        * {
          box-sizing: border-box;
        }
        :host {
          display: block;
          font-family: var(--ha-font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif);
        }
        ha-card {
          padding: 20px;
          border-radius: var(--ha-card-border-radius, 16px);
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          box-shadow: var(--ha-card-box-shadow, 0 4px 20px rgba(0,0,0,0.06));
          border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color, rgba(0,0,0,0.08)));
          color: var(--primary-text-color, #212121);
          box-sizing: border-box;
          overflow: hidden;
        }
        .header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 10px;
          margin-bottom: 12px;
        }
        .header-main {
          display: flex;
          align-items: center;
          gap: 10px;
          min-width: 0;
          flex: 1 1 auto;
        }
        .logo-wrap {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 34px;
          height: 34px;
          border-radius: 10px;
          overflow: hidden;
          box-shadow: 0 2px 8px rgba(0, 245, 255, 0.22);
          flex-shrink: 0;
          background: #0d1117;
        }
        .brand-logo {
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
        }
        .header-titles {
          display: flex;
          align-items: center;
          gap: 8px;
          min-width: 0;
          flex-wrap: wrap;
        }
        .card-title {
          font-size: 1.15rem;
          font-weight: 700;
          color: var(--primary-text-color, #212121);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          line-height: 1.25;
        }
        .badge {
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
          font-size: 0.72rem;
          font-weight: 600;
          padding: 2px 8px;
          border-radius: 10px;
          white-space: nowrap;
          line-height: 1.35;
          flex-shrink: 0;
        }
        .header-actions {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-shrink: 0;
        }
        .color-mode-btn {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          color: var(--primary-text-color, #212121);
          border-radius: 50%;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 0.95rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          padding: 0;
          line-height: 1;
        }
        .color-mode-btn:hover {
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
          border-color: var(--primary-color, #03a9f4);
          transform: scale(1.08);
        }
        .color-mode-btn:active {
          transform: scale(0.94);
        }
        .view-toggle-btn {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          color: var(--primary-text-color, #212121);
          font-size: 0.76rem;
          font-weight: 600;
          padding: 6px 12px;
          border-radius: 12px;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 5px;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          white-space: nowrap;
          line-height: 1;
        }
        .view-toggle-btn:hover {
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
          border-color: var(--primary-color, #03a9f4);
        }
        .view-toggle-btn:active {
          transform: scale(0.96);
        }
        /* Mindmap Modal Layer (3/4 Screen Popup) */
        .mindmap-modal-backdrop {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          height: 100dvh;
          background: rgba(0, 0, 0, 0.65);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          z-index: 99999;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
          box-sizing: border-box;
          animation: modalFadeIn 0.2s ease-out;
        }
        @keyframes modalFadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .mindmap-modal-content {
          position: relative;
          width: 75vw;
          height: 75vh;
          height: 75dvh;
          min-width: 320px;
          max-width: 1400px;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          border-radius: var(--ha-card-border-radius, 20px);
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
          overflow: hidden;
          display: flex;
          flex-direction: column;
          animation: modalScaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }
        @keyframes modalScaleIn {
          from { transform: scale(0.95); opacity: 0; }
          to { transform: scale(1); opacity: 1; }
        }
        .mindmap-modal-close {
          position: absolute;
          top: 14px;
          right: 14px;
          z-index: 100;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          color: var(--primary-text-color, #212121);
          font-size: 1.1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
          transition: all 0.2s ease;
        }
        .mindmap-modal-close:hover {
          background: var(--error-color, #db4437);
          color: #ffffff;
          border-color: var(--error-color, #db4437);
          transform: scale(1.08);
        }
        /* Action Dialog Modal (Mushroom / Minimalist UI) */
        .action-dialog-backdrop {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          height: 100dvh;
          background: rgba(0, 0, 0, 0.55);
          backdrop-filter: blur(6px);
          -webkit-backdrop-filter: blur(6px);
          z-index: 999999;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px;
          box-sizing: border-box;
          animation: modalFadeIn 0.18s ease-out;
        }
        .action-dialog-box {
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          color: var(--primary-text-color, #212121);
          width: 100%;
          max-width: 440px;
          border-radius: 20px;
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
          box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
          overflow: hidden;
          display: flex;
          flex-direction: column;
          animation: modalScaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .action-dialog-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px 18px;
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
        }
        .action-dialog-title {
          font-size: 1rem;
          font-weight: 700;
          color: var(--primary-text-color, #212121);
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .action-dialog-close {
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
        .action-dialog-close:hover {
          color: var(--primary-text-color, #212121);
          background: var(--divider-color, rgba(127, 127, 127, 0.2));
        }
        .action-dialog-body {
          padding: 18px;
          display: flex;
          flex-direction: column;
          gap: 14px;
          max-height: 70vh;
          overflow-y: auto;
          box-sizing: border-box;
        }
        .action-dialog-note-preview {
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
        .action-dialog-label {
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.6px;
          color: var(--secondary-text-color, #64748b);
        }
        .action-dialog-categories-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(115px, 1fr));
          gap: 8px;
        }
        .action-dialog-cat-chip {
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
        .action-dialog-cat-chip:hover {
          border-color: var(--chip-color, var(--primary-color, #03a9f4));
          background: color-mix(in srgb, var(--chip-color, var(--primary-color, #03a9f4)) 12%, transparent);
          transform: translateY(-1px);
        }
        .action-dialog-cat-chip.selected {
          border-color: var(--chip-color, var(--primary-color, #03a9f4));
          background: color-mix(in srgb, var(--chip-color, var(--primary-color, #03a9f4)) 18%, transparent);
          font-weight: 700;
        }
        .action-dialog-cat-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: var(--chip-color, var(--primary-color, #03a9f4));
          flex-shrink: 0;
        }
        .action-dialog-cat-name {
          flex: 1;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .action-dialog-cat-count {
          font-size: 0.72rem;
          opacity: 0.65;
          font-weight: 600;
        }
        .action-dialog-prio-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 8px;
          margin-bottom: 16px;
        }
        .action-dialog-prio-chip {
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
        .action-dialog-prio-chip:hover {
          border-color: var(--chip-prio-color, var(--primary-color, #03a9f4));
          background: color-mix(in srgb, var(--chip-prio-color, var(--primary-color, #03a9f4)) 10%, transparent);
        }
        .action-dialog-prio-chip.selected {
          border-color: var(--chip-prio-color, var(--primary-color, #03a9f4));
          background: color-mix(in srgb, var(--chip-prio-color, var(--primary-color, #03a9f4)) 18%, transparent);
          color: var(--chip-prio-color, var(--primary-color, #03a9f4));
          font-weight: 700;
          box-shadow: 0 0 0 1px var(--chip-prio-color, var(--primary-color, #03a9f4));
        }
        .action-dialog-new-cat-row {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 4px;
          width: 100%;
        }
        .action-dialog-input {
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
        .action-dialog-new-cat-row .action-dialog-input {
          flex: 1;
          width: auto;
        }
        .action-dialog-input:focus {
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary-color, #03a9f4) 20%, transparent);
        }
        .action-dialog-textarea {
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
        .action-dialog-textarea:focus {
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary-color, #03a9f4) 20%, transparent);
        }
        .action-dialog-footer {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 8px;
          margin-top: 6px;
        }
        .action-dialog-btn {
          padding: 8px 16px;
          border-radius: 12px;
          font-size: 0.85rem;
          font-weight: 600;
          cursor: pointer;
          border: 1px solid transparent;
          transition: all 0.15s ease;
        }
        .action-dialog-btn-cancel {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
          color: var(--secondary-text-color, #64748b);
          border-color: var(--divider-color, rgba(127, 127, 127, 0.2));
        }
        .action-dialog-btn-cancel:hover {
          background: var(--divider-color, rgba(127, 127, 127, 0.2));
          color: var(--primary-text-color, #212121);
        }
        .action-dialog-btn-primary {
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
        }
        .action-dialog-btn-primary:hover {
          filter: brightness(1.08);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
        .action-dialog-error {
          color: var(--error-color, #db4437);
          font-size: 0.8rem;
          margin-top: 6px;
          line-height: 1.3;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 4px;
        }
        .action-dialog-input.input-error,
        .action-dialog-textarea.input-error {
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
        /* Input & Category Section */
        .input-section {
          margin-bottom: 12px;
        }
        .quick-capture-card {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.05));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.12)));
          border-radius: 14px;
          padding: 6px 8px 6px 10px;
          display: flex;
          flex-direction: column;
          gap: 6px;
          box-sizing: border-box;
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        .quick-capture-card:focus-within {
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 0 0 2px var(--primary-color-alpha, rgba(3, 169, 244, 0.15));
        }
        .input-container {
          display: flex;
          align-items: center;
          gap: 8px;
          width: 100%;
          box-sizing: border-box;
        }
        input[type="text"] {
          flex: 1 1 0;
          min-width: 0;
          width: 0;
          border: none;
          background: transparent;
          font-size: 0.95rem;
          color: var(--primary-text-color, #212121);
          outline: none;
          padding: 6px 2px;
          box-sizing: border-box;
        }
        input[type="text"]::placeholder {
          color: var(--secondary-text-color, #757575);
          opacity: 0.85;
        }
        button.send-btn {
          flex: 0 0 auto;
          background: var(--primary-color, #03a9f4);
          color: white;
          border: none;
          border-radius: 10px;
          padding: 0 14px;
          height: 36px;
          cursor: pointer;
          font-weight: 600;
          font-size: 0.86rem;
          display: inline-flex;
          align-items: center;
          gap: 5px;
          justify-content: center;
          white-space: nowrap;
          box-sizing: border-box;
          transition: opacity 0.2s, transform 0.1s;
        }
        button.send-btn:hover {
          opacity: 0.92;
        }
        button.send-btn:active {
          transform: scale(0.96);
        }
        .send-icon {
          font-size: 0.9rem;
          line-height: 1;
        }
        .quick-meta-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 6px;
          padding-top: 4px;
          border-top: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.08)));
        }
        .quick-meta-left {
          display: flex;
          align-items: center;
          gap: 6px;
          flex-wrap: wrap;
          flex: 1 1 auto;
          min-width: 0;
        }
        .quick-select-wrap {
          display: inline-flex;
          align-items: center;
          background: var(--card-background-color, rgba(255, 255, 255, 0.6));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          border-radius: 8px;
          padding: 2px 6px;
          gap: 4px;
          transition: border-color 0.2s;
        }
        .quick-select-wrap:focus-within {
          border-color: var(--primary-color, #03a9f4);
        }
        .quick-select-icon {
          font-size: 0.82rem;
          line-height: 1;
        }
        select.cat-select {
          border: none;
          background: transparent;
          font-size: 0.82rem;
          font-weight: 500;
          color: var(--primary-text-color, #212121);
          outline: none;
          cursor: pointer;
          padding: 3px 2px;
          max-width: 170px;
          box-sizing: border-box;
        }
        select.prio-select {
          border: none;
          background: transparent;
          font-size: 0.82rem;
          font-weight: 500;
          color: var(--primary-text-color, #212121);
          outline: none;
          cursor: pointer;
          padding: 3px 2px;
          box-sizing: border-box;
        }
        @media (max-width: 520px) {
          ha-card {
            padding: 12px 12px 14px 12px;
          }
          .header {
            gap: 8px;
            margin-bottom: 10px;
          }
          .card-title {
            font-size: 1.05rem;
          }
          .badge {
            font-size: 0.68rem;
            padding: 2px 6px;
          }
          .quick-capture-card {
            padding: 6px 8px;
            gap: 5px;
          }
          button.send-btn {
            padding: 0 10px;
            height: 34px;
            font-size: 0.82rem;
          }
          .send-text {
            display: none;
          }
          .send-icon {
            font-size: 1.05rem;
            margin: 0;
          }
          select.cat-select {
            max-width: 130px;
            font-size: 0.78rem;
          }
          select.prio-select {
            font-size: 0.78rem;
          }
          .idea-item.is-subtask {
            margin-left: 16px;
          }
          .idea-item.is-subtask::before {
            left: -11px;
            width: 8px;
          }
          .indent-btn,
          .edit-btn,
          .delete-btn {
            opacity: 0.75 !important;
            min-width: 28px;
            min-height: 28px;
          }
          .drag-handle {
            opacity: 0.65;
            padding: 4px;
            font-size: 1.25rem;
          }
        }
        @media (max-width: 380px) {
          .view-toggle-btn .btn-text {
            display: none;
          }
          .view-toggle-btn {
            padding: 6px 8px;
          }
          select.cat-select {
            max-width: 105px;
          }
        }
        /* Filter Pills */
        .pills {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          padding-bottom: 6px;
          margin-bottom: 12px;
        }
        .completed-pill {
          opacity: 0.8;
          border-style: dashed !important;
        }
        .idea-item.completed {
          opacity: 0.55;
          background: var(--secondary-background-color, rgba(0, 0, 0, 0.03));
        }
        .idea-item.completed .idea-text {
          text-decoration: line-through;
        }
        .check-btn.checked {
          background: var(--success-color, #4caf50);
          border-color: var(--success-color, #4caf50);
          color: white;
          font-size: 11px;
          font-weight: 700;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .pill {
          background: var(--secondary-background-color, rgba(0,0,0,0.05));
          color: var(--secondary-text-color, #616161);
          border: 1px solid var(--divider-color, rgba(0,0,0,0.06));
          border-radius: 20px;
          padding: 5px 12px;
          font-size: 0.82rem;
          font-weight: 500;
          cursor: pointer;
          white-space: nowrap;
          transition: all 0.15s ease;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .pill:hover {
          background: var(--primary-color-alpha, rgba(3, 169, 244, 0.1));
          color: var(--primary-color, #03a9f4);
        }
        .pill.active {
          background: var(--primary-color, #03a9f4);
          color: white;
          border-color: var(--primary-color, #03a9f4);
          font-weight: 600;
        }
        .pill-count {
          font-size: 0.72rem;
          opacity: 0.85;
          padding: 1px 5px;
          background: rgba(0,0,0,0.12);
          border-radius: 10px;
        }
        .pill.active .pill-count {
          background: rgba(255,255,255,0.25);
        }
        /* Ideas List */
        .ideas-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          max-height: 480px;
          overflow-y: auto;
        }
        .empty-state {
          text-align: center;
          padding: 28px 12px;
          color: var(--secondary-text-color, #888);
          font-size: 0.9rem;
        }
        .idea-item {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          background: var(--card-background-color, #ffffff);
          border: 1px solid var(--divider-color, rgba(0,0,0,0.06));
          border-left: 3.5px solid var(--item-cat-color, var(--divider-color));
          border-radius: 10px;
          padding: 12px;
          transition: background 0.15s, border-color 0.15s;
        }
        .idea-item:hover {
          border-color: var(--divider-color, rgba(0,0,0,0.15));
          background: var(--secondary-background-color, rgba(0,0,0,0.02));
        }
        .check-btn {
          background: transparent;
          border: 2px solid var(--divider-color, #bdbdbd);
          width: 20px;
          height: 20px;
          border-radius: 50%;
          cursor: pointer;
          margin-top: 2px;
          flex-shrink: 0;
          transition: all 0.2s ease;
        }
        .check-btn:hover {
          border-color: var(--success-color, #4caf50);
          background: rgba(76, 175, 80, 0.15);
        }
        .idea-content {
          flex: 1;
        }
        .idea-text {
          font-size: 0.95rem;
          line-height: 1.4;
          word-break: break-word;
          color: var(--primary-text-color, #212121);
        }
        .idea-meta {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 6px;
          font-size: 0.75rem;
          color: var(--secondary-text-color, #757575);
        }
        .category-tag {
          background: var(--secondary-background-color, rgba(0,0,0,0.06));
          padding: 2px 7px;
          border-radius: 6px;
          font-weight: 500;
          color: var(--primary-color, #03a9f4);
        }
        .category-tag.clickable {
          cursor: pointer;
          transition: background 0.15s, color 0.15s;
        }
        .category-tag.clickable:hover {
          background: var(--primary-color-alpha, rgba(3, 169, 244, 0.15));
        }
        .prio-tag {
          display: inline-flex;
          align-items: center;
          gap: 3px;
          font-size: 0.72rem;
          font-weight: 600;
          padding: 2px 7px;
          border-radius: 6px;
          cursor: pointer;
          user-select: none;
          transition: transform 0.1s, opacity 0.15s, box-shadow 0.15s;
        }
        .prio-tag:hover {
          opacity: 0.85;
          transform: scale(1.04);
        }
        .prio-tag.urgent {
          color: #ef4444;
          background: color-mix(in srgb, #ef4444 14%, var(--card-background-color, #ffffff));
          border: 1px solid color-mix(in srgb, #ef4444 35%, transparent);
          box-shadow: 0 0 8px rgba(239, 68, 68, 0.2);
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
        .source-badge {
          display: inline-flex;
          align-items: center;
          gap: 3px;
        }
        .source-device {
          opacity: 0.85;
          font-weight: 500;
        }
        .item-actions {
          display: flex;
          align-items: center;
          gap: 2px;
          margin-left: 4px;
        }
        .indent-btn,
        .edit-btn,
        .delete-btn {
          background: transparent;
          border: none;
          color: var(--secondary-text-color, #9e9e9e);
          cursor: pointer;
          font-size: 1rem;
          padding: 2px 5px;
          border-radius: 4px;
          opacity: 0.35;
          transition: opacity 0.2s, color 0.2s, background 0.2s;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          line-height: 1;
        }
        .idea-item:hover .indent-btn,
        .idea-item:hover .edit-btn,
        .idea-item:hover .delete-btn {
          opacity: 0.85;
        }
        .indent-btn:hover {
          color: var(--primary-color, #03a9f4) !important;
          opacity: 1 !important;
          background: var(--secondary-background-color, rgba(0,0,0,0.05));
        }
        .edit-btn:hover {
          color: var(--primary-color, #03a9f4) !important;
          opacity: 1 !important;
          background: var(--secondary-background-color, rgba(0,0,0,0.05));
        }
        .delete-btn:hover {
          color: var(--error-color, #f44336) !important;
          opacity: 1 !important;
          background: rgba(244, 67, 54, 0.1);
        }
        /* Subtasks styling */
        .idea-item.is-subtask {
          margin-left: 24px;
          border-left: 3.5px solid color-mix(in srgb, var(--item-cat-color, var(--primary-color)) 75%, transparent);
          background: color-mix(in srgb, var(--item-cat-color, var(--primary-color)) 4%, var(--card-background-color, #ffffff));
          position: relative;
        }
        .idea-item.is-subtask::before {
          content: "";
          position: absolute;
          left: -15px;
          top: 18px;
          width: 11px;
          height: 2px;
          background: color-mix(in srgb, var(--item-cat-color, var(--primary-color)) 45%, var(--divider-color, rgba(0,0,0,0.15)));
          border-radius: 1px;
        }
        .subtask-indicator {
          display: inline-flex;
          align-items: center;
          font-weight: 700;
          color: var(--secondary-text-color, #757575);
          margin-right: 5px;
          font-size: 0.95rem;
          user-select: none;
        }
        .subtask-badge {
          display: inline-flex;
          align-items: center;
          font-size: 0.72rem;
          padding: 1px 6px;
          border-radius: 6px;
          background: var(--secondary-background-color, rgba(0, 0, 0, 0.06));
          color: var(--secondary-text-color, #666);
          font-weight: 500;
        }
        /* Drag & Drop styling */
        .drag-handle {
          color: var(--secondary-text-color, #9e9e9e);
          cursor: grab;
          font-size: 1.15rem;
          line-height: 1;
          padding: 2px 4px;
          margin-right: -4px;
          margin-top: 1px;
          opacity: 0.28;
          user-select: none;
          -webkit-user-select: none;
          touch-action: none;
          transition: opacity 0.15s, color 0.15s, transform 0.15s;
          flex-shrink: 0;
        }
        .idea-item:hover .drag-handle {
          opacity: 0.85;
          color: var(--primary-color, #03a9f4);
        }
        .drag-handle:active {
          cursor: grabbing;
          transform: scale(1.18);
        }
        .idea-item.is-dragging {
          opacity: 0.42 !important;
          border-style: dashed !important;
          background: var(--secondary-background-color, rgba(0, 0, 0, 0.05)) !important;
          transform: scale(0.99);
        }
        .idea-item.drop-target-above {
          border-top: 3.5px solid var(--primary-color, #03a9f4) !important;
          transform: translateY(2px);
        }
        .idea-item.drop-target-below {
          border-bottom: 3.5px solid var(--primary-color, #03a9f4) !important;
          transform: translateY(-2px);
        }
        .idea-item.drop-target-subtask {
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 15%, var(--card-background-color, #ffffff)) !important;
          border-color: var(--primary-color, #03a9f4) !important;
          box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary-color, #03a9f4) 30%, transparent) !important;
          transform: translateX(10px);
        }
        .idea-item.drop-target-subtask::after {
          content: "↳ Als Unteraufgabe";
          position: absolute;
          right: 12px;
          top: 10px;
          font-size: 0.72rem;
          font-weight: 700;
          color: var(--primary-color, #03a9f4);
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 18%, var(--card-background-color, #ffffff));
          padding: 2px 8px;
          border-radius: 8px;
          pointer-events: none;
        }
        .touch-drag-ghost {
          position: fixed;
          z-index: 99999999;
          pointer-events: none;
          background: var(--card-background-color, #ffffff);
          border: 1.5px solid var(--primary-color, #03a9f4);
          color: var(--primary-text-color, #212121);
          padding: 8px 14px;
          border-radius: 12px;
          box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28);
          font-size: 0.88rem;
          font-weight: 600;
          white-space: nowrap;
          max-width: 250px;
          overflow: hidden;
          text-overflow: ellipsis;
          opacity: 0.95;
          transform: rotate(2deg);
        }
        /* Apple Reminders Style Context Menu */
        .apple-menu-backdrop {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          height: 100dvh;
          background: rgba(0, 0, 0, 0.45);
          backdrop-filter: blur(5px);
          -webkit-backdrop-filter: blur(5px);
          z-index: 9999999;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px;
          box-sizing: border-box;
          animation: modalFadeIn 0.15s ease-out;
        }
        .apple-menu-card {
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          color: var(--primary-text-color, #212121);
          width: 100%;
          max-width: 360px;
          border-radius: 20px;
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
          box-shadow: 0 20px 48px rgba(0, 0, 0, 0.32);
          overflow: hidden;
          display: flex;
          flex-direction: column;
          animation: appleMenuScale 0.18s cubic-bezier(0.16, 1, 0.3, 1);
        }
        @keyframes appleMenuScale {
          from { transform: scale(0.92); opacity: 0; }
          to { transform: scale(1); opacity: 1; }
        }
        .apple-menu-header {
          padding: 12px 16px;
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.06));
          border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
          display: flex;
          flex-direction: column;
          gap: 3px;
        }
        .apple-menu-headline {
          font-size: 0.72rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.6px;
          color: var(--secondary-text-color, #64748b);
        }
        .apple-menu-item-text {
          font-size: 0.88rem;
          font-weight: 600;
          color: var(--primary-text-color, #212121);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .apple-menu-actions {
          display: flex;
          flex-direction: column;
          padding: 6px;
        }
        .apple-menu-btn {
          display: flex;
          align-items: center;
          gap: 12px;
          width: 100%;
          padding: 10px 14px;
          border: none;
          background: transparent;
          color: var(--primary-text-color, #212121);
          font-size: 0.92rem;
          font-family: inherit;
          font-weight: 500;
          border-radius: 12px;
          cursor: pointer;
          transition: background 0.12s, transform 0.1s;
          text-align: left;
          box-sizing: border-box;
        }
        .apple-menu-btn:hover {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
        }
        .apple-menu-btn:active {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.18));
          transform: scale(0.98);
        }
        .apple-menu-btn.action-indent {
          color: var(--primary-color, #03a9f4);
          font-weight: 600;
        }
        .apple-menu-btn.action-danger {
          color: var(--error-color, #ef4444);
        }
        .apple-menu-btn .btn-icon {
          font-size: 1.15rem;
          width: 22px;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }
        .apple-menu-btn .btn-content {
          display: flex;
          flex-direction: column;
          flex: 1;
          min-width: 0;
        }
        .apple-menu-btn .btn-sublabel {
          font-size: 0.72rem;
          color: var(--secondary-text-color, #64748b);
          font-weight: 400;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .apple-menu-separator {
          height: 1px;
          background: var(--divider-color, rgba(127, 127, 127, 0.15));
          margin: 4px 8px;
        }
        .add-cat-pill {
          padding: 5px 12px;
          font-weight: 600;
          border: 1px dashed var(--divider-color, rgba(0,0,0,0.15)) !important;
          opacity: 0.8;
        }
        .add-cat-pill:hover {
          border-color: var(--primary-color, #03a9f4) !important;
          color: var(--primary-color, #03a9f4) !important;
          opacity: 1;
        }
        .remove-cat-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          margin-left: 5px;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          font-size: 0.65rem;
          opacity: 0.75;
          transition: background 0.15s, opacity 0.15s;
        }
        .remove-cat-btn:hover {
          background: rgba(0,0,0,0.25);
          opacity: 1;
        }
      </style>

      <ha-card>
        <div class="header">
          <div class="header-main">
            <div class="logo-wrap" title="Brainstorm Hub">
              <svg viewBox="0 0 512 512" class="brand-logo" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <radialGradient id="cardBgGlow" cx="50%" cy="45%" r="65%">
                    <stop offset="0%" stop-color="#24244a"/>
                    <stop offset="100%" stop-color="#0a0a14"/>
                  </radialGradient>
                  <linearGradient id="cardCyan" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#00f5ff"/>
                    <stop offset="100%" stop-color="#0072ff"/>
                  </linearGradient>
                  <linearGradient id="cardPurple" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#ff2a8d"/>
                    <stop offset="100%" stop-color="#7928ca"/>
                  </linearGradient>
                  <linearGradient id="cardAmber" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#ffe66d"/>
                    <stop offset="100%" stop-color="#fb8500"/>
                  </linearGradient>
                </defs>
                <rect width="512" height="512" rx="110" fill="url(#cardBgGlow)"/>
                <circle cx="256" cy="210" r="80" fill="#00f5ff" opacity="0.25"/>
                <path d="M165 210 C165 145, 200 100, 256 100 C312 100, 347 145, 347 210 C347 252, 320 285, 312 320 L200 320 C192 285, 165 252, 165 210 Z" fill="none" stroke="url(#cardCyan)" stroke-width="16"/>
                <path d="M 242 148 C 210 144, 188 168, 190 192 C 191 210, 210 215, 215 230 C 220 245, 205 260, 215 280 C 223 295, 238 298, 244 308" fill="none" stroke="url(#cardCyan)" stroke-width="14" stroke-linecap="round"/>
                <path d="M 270 148 C 302 144, 324 168, 322 192 C 321 210, 302 215, 297 230 C 292 245, 307 260, 297 280 C 289 295, 274 298, 268 308" fill="none" stroke="url(#cardPurple)" stroke-width="14" stroke-linecap="round"/>
                <path d="M 258 135 L 246 195 L 268 195 L 248 260 L 274 208 L 253 208 Z" fill="url(#cardAmber)"/>
                <circle cx="256" cy="198" r="10" fill="#ffffff"/>
                <rect x="208" y="328" width="96" height="16" rx="8" fill="#718096"/>
                <rect x="216" y="348" width="80" height="14" rx="7" fill="#718096"/>
                <path d="M232 366 C232 366, 238 382, 256 382 C274 382, 280 366, 280 366 Z" fill="#4a5568"/>
              </svg>
            </div>
            <div class="header-titles">
              <span class="card-title" id="cardTitle">${this._config.title !== undefined ? this._config.title : "Brainstorm Hub"}</span>
              <div class="badge" id="badgeCount" style="display: ${this._config.show_badge === true ? "inline-flex" : "none"};">0 Ideen</div>
            </div>
          </div>
          <div class="header-actions">
            <button class="color-mode-btn" id="cardColorModeBtn" style="display: ${this._config.show_color_toggle === true ? "flex" : "none"};" title="${this._colorMode === 'theme' ? 'Farbmodus: Theme-Farben aktiv (Klicken für Bunt)' : 'Farbmodus: Bunt aktiv (Klicken für Theme-Farben)'}">${this._colorMode === 'theme' ? '🎨' : '🌈'}</button>
            <button class="view-toggle-btn" id="viewToggleBtn" style="display: ${this._config.show_mindmap_button === true ? "flex" : "none"};" title="Mindmap als Layer öffnen">
              <span class="btn-icon">🧠</span>
              <span class="btn-text">Mindmap</span>
            </button>
          </div>
        </div>

        <div id="listViewWrap">
          <div class="input-section" style="display: ${this._config.show_quick_input === true ? "block" : "none"};">
            <div class="quick-capture-card">
              <div class="input-container">
                <input 
                  type="text" 
                  id="ideaInput" 
                  placeholder="Blitz-Idee tippen... (z.B. 'Garten: Baum schneiden')" 
                  autocomplete="off"
                />
                <button class="send-btn" id="sendBtn" title="Idee erfassen">
                  <span class="send-icon">➕</span>
                  <span class="send-text">Hinzufügen</span>
                </button>
              </div>
              <div class="quick-meta-bar">
                <div class="quick-meta-left">
                  <div class="quick-select-wrap cat-wrap">
                    <span class="quick-select-icon">🏷️</span>
                    <select class="cat-select" id="catSelect" title="Ziel-Kategorie auswählen">
                      <option value="auto">Auto (Erkennen)</option>
                    </select>
                  </div>
                  <div class="quick-select-wrap prio-wrap">
                    <select class="prio-select" id="prioSelect" title="Priorität festlegen">
                      <option value="medium" selected>🟡 Mittel</option>
                      <option value="high">🔴 Hoch</option>
                      <option value="urgent">🔥 Dringend</option>
                      <option value="low">🟢 Niedrig</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="pills" id="pillsContainer" style="display: ${this._config.show_categories === true ? "flex" : "none"};"></div>

          <div class="ideas-list" id="ideasList"></div>
        </div>

        <!-- Mindmap Modal Layer (3/4 Screen Popup) -->
        <div class="mindmap-modal-backdrop" id="mindmapModal" style="display: none;">
          <div class="mindmap-modal-content">
            <button class="mindmap-modal-close" id="closeMindmapModalBtn" title="Mindmap schließen (ESC)">✕</button>
            <brainstorm-mindmap-card id="popupMindmap" style="width: 100%; height: 100%; display: flex; flex: 1; min-height: 0;"></brainstorm-mindmap-card>
          </div>
        </div>

        <!-- Action Dialog Modal (Mushroom Style) -->
        <div class="action-dialog-backdrop" id="cardDialog" style="display: none;">
          <div class="action-dialog-box" id="cardDialogBox">
            <div class="action-dialog-header">
              <div class="action-dialog-title" id="cardDialogTitle">Titel</div>
              <button class="action-dialog-close" id="cardDialogCloseBtn" title="Schließen (ESC)">✕</button>
            </div>
            <div class="action-dialog-body" id="cardDialogBody"></div>
          </div>
        </div>

        <!-- Apple Reminders Style Context Menu Modal -->
        <div class="apple-menu-backdrop" id="appleContextMenu" style="display: none;">
          <div class="apple-menu-card" id="appleMenuCard">
            <div class="apple-menu-header">
              <span class="apple-menu-headline">Aktionen für Notiz</span>
              <span class="apple-menu-item-text" id="appleMenuTitle"></span>
            </div>
            <div class="apple-menu-actions" id="appleMenuActions"></div>
          </div>
        </div>
      </ha-card>
    `;

    // Static event listeners attached ONCE
    const inputEl = this.shadowRoot.getElementById("ideaInput");
    const sendBtn = this.shadowRoot.getElementById("sendBtn");
    const quickAddCatBtn = this.shadowRoot.getElementById("quickAddCatBtn");
    const viewToggleBtn = this.shadowRoot.getElementById("viewToggleBtn");
    const mindmapModal = this.shadowRoot.getElementById("mindmapModal");
    const closeMindmapModalBtn = this.shadowRoot.getElementById("closeMindmapModalBtn");
    const popupMindmap = this.shadowRoot.getElementById("popupMindmap");
    const cardDialog = this.shadowRoot.getElementById("cardDialog");
    const cardDialogCloseBtn = this.shadowRoot.getElementById("cardDialogCloseBtn");
    const appleContextMenu = this.shadowRoot.getElementById("appleContextMenu");

    if (cardDialogCloseBtn) {
      cardDialogCloseBtn.addEventListener("click", () => this._closeDialog());
    }
    if (cardDialog) {
      cardDialog.addEventListener("click", (e) => {
        if (e.target === cardDialog) this._closeDialog();
      });
    }
    if (appleContextMenu) {
      appleContextMenu.addEventListener("click", (e) => {
        if (e.target === appleContextMenu) this._closeContextMenu();
      });
    }

    const cardColorModeBtn = this.shadowRoot.getElementById("cardColorModeBtn");
    if (cardColorModeBtn) {
      cardColorModeBtn.addEventListener("click", () => {
        this._colorMode = this._colorMode === "theme" ? "multicolor" : "theme";
        try {
          localStorage.setItem("brainstorm_color_mode", this._colorMode);
        } catch {}
        cardColorModeBtn.innerHTML = this._colorMode === "theme" ? "🎨" : "🌈";
        cardColorModeBtn.title = this._colorMode === "theme"
          ? "Farbmodus: Theme-Farben aktiv (Klicken für Bunt)"
          : "Farbmodus: Bunt aktiv (Klicken für Theme-Farben)";
        this._lastColorMode = null; // Force re-render
        this._lastUpdated = null;
        this._updateContent();
      });
    }

    const openMindmapModal = () => {
      if (!mindmapModal) return;
      mindmapModal.style.display = "flex";
      if (popupMindmap && this._hass) {
        if (typeof popupMindmap.setConfig === "function") {
          popupMindmap.setConfig({ height: "100%", is_popup: true, color_mode: this._colorMode });
        }
        popupMindmap.hass = this._hass;
        setTimeout(() => {
          if (typeof popupMindmap._centerLayout === "function") {
            popupMindmap._centerLayout(true);
          }
        }, 80);
      }
    };

    const closeMindmapModal = () => {
      if (mindmapModal) {
        mindmapModal.style.display = "none";
      }
    };

    if (viewToggleBtn) {
      viewToggleBtn.addEventListener("click", openMindmapModal);
    }

    if (closeMindmapModalBtn) {
      closeMindmapModalBtn.addEventListener("click", closeMindmapModal);
    }

    if (mindmapModal) {
      mindmapModal.addEventListener("click", (e) => {
        if (e.target === mindmapModal) {
          closeMindmapModal();
        }
      });
    }

    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        if (this._isDialogOpen) {
          this._closeDialog();
        } else if (appleContextMenu && appleContextMenu.style.display === "flex") {
          this._closeContextMenu();
        } else if (mindmapModal && mindmapModal.style.display === "flex") {
          closeMindmapModal();
        }
      }
    });

    if (quickAddCatBtn) {
      quickAddCatBtn.addEventListener("click", () => this._addCategory());
    }

    if (sendBtn && inputEl) {
      sendBtn.addEventListener("click", () => this._submitIdea());
      inputEl.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          this._submitIdea();
        }
      });
    }

    this._updateContent();
  }

  _updateContent() {
    try {
      if (!this._shadowRootReady()) return;

      const sensorEntity = this._getSensorEntity();
      if (!sensorEntity) return;

      const currentSensorUpdated = sensorEntity.last_updated;
      const catSelectEl = this.shadowRoot.getElementById("catSelect");
      const isSelectActive = catSelectEl && (this.shadowRoot.activeElement === catSelectEl || document.activeElement === catSelectEl);

      // If neither the sensor nor the selected category nor color mode changed, skip DOM re-render entirely
      if (
        this._lastUpdated === currentSensorUpdated &&
        this._lastCategory === this._selectedCategory &&
        this._lastColorMode === this._colorMode
      ) {
        return;
      }

      // If user is currently picking a category from the dropdown, don't interrupt them
      if (isSelectActive && this._lastUpdated !== null) {
        return;
      }

      this._lastUpdated = currentSensorUpdated;
      this._lastCategory = this._selectedCategory;
      this._lastColorMode = this._colorMode;

      const attributes = sensorEntity.attributes || {};
      const categories = attributes.categories || ["Inbox", "Smarthome", "Haus & Garten", "Projekte", "Alltag"];
      const counts = attributes.category_counts || {};
      const activeIdeas = attributes.ideas || [];
      const completedIdeas = attributes.completed_ideas || [];
      const completedCount = attributes.completed_count || completedIdeas.length || 0;
      const isCompletedView = this._selectedCategory === "__completed__";

    // 1. Update Title, Badge and Controls
    const titleEl = this.shadowRoot.getElementById("cardTitle");
    if (titleEl) {
      titleEl.textContent = this._config.title !== undefined ? this._config.title : "Brainstorm Hub";
    }

    const badgeEl = this.shadowRoot.getElementById("badgeCount");
    if (badgeEl) {
      badgeEl.style.display = this._config.show_badge === true ? "inline-flex" : "none";
      if (completedCount > 0) {
        badgeEl.textContent = `${activeIdeas.length} aktiv • ${completedCount} erledigt`;
      } else {
        badgeEl.textContent = `${activeIdeas.length} Ideen`;
      }
    }

    const cardColorModeBtn = this.shadowRoot.getElementById("cardColorModeBtn");
    if (cardColorModeBtn) {
      cardColorModeBtn.style.display = this._config.show_color_toggle === true ? "flex" : "none";
      cardColorModeBtn.innerHTML = this._colorMode === "theme" ? "🎨" : "🌈";
      cardColorModeBtn.title = this._colorMode === "theme"
        ? "Farbmodus: Theme-Farben aktiv (Klicken für Bunt)"
        : "Farbmodus: Bunt aktiv (Klicken für Theme-Farben)";
    }

    const viewToggleBtn = this.shadowRoot.getElementById("viewToggleBtn");
    if (viewToggleBtn) {
      viewToggleBtn.style.display = this._config.show_mindmap_button === true ? "flex" : "none";
    }

    const inputSection = this.shadowRoot.querySelector(".input-section");
    if (inputSection) {
      inputSection.style.display = this._config.show_quick_input === true ? "block" : "none";
    }

    const pillsContainer = this.shadowRoot.getElementById("pillsContainer");
    if (pillsContainer) {
      pillsContainer.style.display = this._config.show_categories === true ? "flex" : "none";
    }

    // 2. Update Select Dropdown and Input Placeholder
    const ideaInput = this.shadowRoot.getElementById("ideaInput");
    if (ideaInput && document.activeElement !== ideaInput) {
      if (this._selectedCategory && this._selectedCategory !== "all" && this._selectedCategory !== "__completed__") {
        ideaInput.placeholder = `Notiz in "${this._selectedCategory}" verfassen...`;
      } else {
        ideaInput.placeholder = "Blitz-Idee tippen... (z.B. 'Garten: Baum schneiden')";
      }
    }

    if (catSelectEl && !isSelectActive) {
      const currentVal = catSelectEl.value || "auto";
      const existingOptions = Array.from(catSelectEl.options).map((o) => o.value);
      const newValues = ["auto", ...categories];

      // Only update options if categories changed
      if (existingOptions.join(",") !== newValues.join(",")) {
        catSelectEl.innerHTML = `
          <option value="auto">Auto (Erkennen)</option>
          ${categories.map((c) => `<option value="${c}">${c}</option>`).join("")}
        `;
        catSelectEl.value = currentVal;
      }

      if (this._selectedCategory && this._selectedCategory !== "all" && this._selectedCategory !== "__completed__") {
        catSelectEl.value = this._selectedCategory;
      } else if (catSelectEl.value !== "auto" && (this._selectedCategory === "all" || this._selectedCategory === "__completed__")) {
        catSelectEl.value = "auto";
      }
    }

    // 3. Update Category Pills
    if (pillsContainer) {
      const hideEmptyCategories = this._rawConfig && this._rawConfig.hide_empty_categories !== undefined
        ? (this._rawConfig.hide_empty_categories === true || this._rawConfig.hide_empty_categories === "true")
        : (attributes.hide_empty_categories !== undefined ? attributes.hide_empty_categories === true : true);

      const visibleCategories = categories.filter((cat) => {
        if (!hideEmptyCategories) return true;
        const count = counts[cat] || 0;
        const isActive = String(this._selectedCategory || "").trim() === String(cat || "").trim();
        return count > 0 || isActive;
      });

      pillsContainer.innerHTML = `
        <div class="pill ${this._selectedCategory === "all" ? "active" : ""}" data-cat="all">
          <span>Alle</span>
          <span class="pill-count">${activeIdeas.length}</span>
        </div>
        ${visibleCategories
          .map((cat) => {
            const count = counts[cat] || 0;
            const isActive = String(this._selectedCategory || "").trim() === String(cat || "").trim();
            const canDelete = cat !== "Inbox" && isActive;
            const catColor = this._getCategoryColor(cat);
            const pillStyle = isActive
              ? `background: ${catColor}; border-color: ${catColor}; color: #ffffff;`
              : "";
            return `
              <div class="pill ${isActive ? "active" : ""}" data-cat="${cat}" style="${pillStyle}">
                <span class="pill-dot" style="display:inline-block; width:7px; height:7px; border-radius:50%; background:${catColor}; margin-right:4px;"></span>
                <span>${cat}</span>
                <span class="pill-count">${count}</span>
                ${canDelete ? `<span class="remove-cat-btn" title="Kategorie '${cat}' löschen" data-delcat="${cat}">✕</span>` : ""}
              </div>
            `;
          })
          .join("")}
        ${
          completedCount > 0
            ? `
          <div class="pill completed-pill ${isCompletedView ? "active" : ""}" data-cat="__completed__" title="Erledigte Ideen anzeigen">
            <span>✓ Erledigt</span>
            <span class="pill-count">${completedCount}</span>
          </div>
        `
            : ""
        }
        <div class="pill add-cat-pill" id="addCatBtn" title="Neue Kategorie erstellen">
          <span>+ Kategorie</span>
        </div>
      `;

      // Re-attach pill click listeners
      pillsContainer.querySelectorAll(".pill[data-cat]").forEach((pill) => {
        pill.addEventListener("click", (e) => {
          if (e.target.closest(".remove-cat-btn")) return;
          this._selectedCategory = String(pill.getAttribute("data-cat") || "").trim();
          const catSelect = this.shadowRoot.getElementById("catSelect");
          if (catSelect) {
            if (this._selectedCategory !== "all" && this._selectedCategory !== "__completed__") {
              catSelect.value = this._selectedCategory;
            } else {
              catSelect.value = "auto";
            }
          }
          this._updateContent();
        });
      });

      pillsContainer.querySelectorAll(".remove-cat-btn").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const cat = btn.getAttribute("data-delcat");
          this._removeCategory(cat);
        });
      });

      const addCatBtn = pillsContainer.querySelector("#addCatBtn");
      if (addCatBtn) {
        addCatBtn.addEventListener("click", () => this._addCategory());
      }
    }

    // 4. Update Filtered Ideas List with Subtask Hierarchy
    let filteredIdeas = isCompletedView
      ? completedIdeas
      : this._selectedCategory === "all"
      ? activeIdeas
      : activeIdeas.filter((i) => String(i.category || "").trim() === String(this._selectedCategory || "").trim());

    if (this._config.max_items && typeof this._config.max_items === "number" && this._config.max_items > 0) {
      filteredIdeas = filteredIdeas.slice(0, this._config.max_items);
    }

    // Build hierarchical tree: parent followed immediately by its subtasks
    const activeItemMap = new Map();
    (isCompletedView ? completedIdeas : activeIdeas).forEach((i) => {
      activeItemMap.set(i.id, i);
    });

    const parentMap = new Map();
    const topLevelIdeas = [];

    filteredIdeas.forEach((item) => {
      if (item.parent_id && activeItemMap.has(item.parent_id)) {
        if (!parentMap.has(item.parent_id)) {
          parentMap.set(item.parent_id, []);
        }
        parentMap.get(item.parent_id).push(item);
      } else {
        topLevelIdeas.push(item);
      }
    });

    const orderedIdeas = [];
    let lastTopLevelId = null;

    topLevelIdeas.forEach((topItem) => {
      orderedIdeas.push({
        ...topItem,
        isSubtask: false,
        candidateParentId: lastTopLevelId,
      });
      lastTopLevelId = topItem.id;

      const children = parentMap.get(topItem.id) || [];
      children.forEach((child) => {
        orderedIdeas.push({
          ...child,
          isSubtask: true,
          parentTask: topItem,
        });
      });
    });

    const ideasList = this.shadowRoot.getElementById("ideasList");
    if (ideasList) {
      if (orderedIdeas.length === 0) {
        ideasList.innerHTML = `
          <div class="empty-state">
            ${
              isCompletedView
                ? "Keine erledigten Ideen vorhanden."
                : this._selectedCategory === "all"
                ? "✨ Noch keine aktiven Ideen. Tippe oben eine Idee ein oder sprich mit Alexa!"
                : `Keine Ideen in der Kategorie "${this._selectedCategory}".`
            }
          </div>
        `;
      } else {
        const canEdit = this._config.allow_edit === true && !isCompletedView;
        const canDelete = this._config.allow_delete === true;
        const showSource = this._config.show_source_icons === true;
        const showTime = this._config.show_timestamps === true;

        ideasList.innerHTML = orderedIdeas
          .map((item, idx) => {
            const isSub = item.isSubtask === true;
            return `
            <div class="idea-item ${isSub ? "is-subtask" : ""} ${isCompletedView ? "completed" : ""}" data-id="${item.id}" data-idx="${idx}" style="--item-cat-color: ${this._getCategoryColor(item.category)};">
              ${!isCompletedView && canEdit ? `<span class="drag-handle" title="Halten & Ziehen zum Sortieren oder Unteraufgabe zuordnen" data-id="${item.id}">⠿</span>` : ""}
              <button 
                class="check-btn ${isCompletedView ? "checked" : ""}" 
                title="${isCompletedView ? "Wieder als aktiv markieren" : "Als erledigt markieren"}" 
                data-id="${item.id}"
                data-completed="${isCompletedView ? "true" : "false"}"
              >${isCompletedView ? "✓" : ""}</button>
              <div class="idea-content">
                <div class="idea-text" title="${canEdit ? "Klicken zum Bearbeiten (Lange drücken für Kontextmenü)" : ""}" data-id="${item.id}" style="${canEdit ? "" : "cursor: default;"}">
                  ${isSub ? `<span class="subtask-indicator" title="Unteraufgabe">↳</span>` : ""}${this._escapeHtml(item.text)}
                </div>
                <div class="idea-meta">
                  ${isSub ? `<span class="subtask-badge" title="Unteraufgabe">Unteraufgabe</span>` : ""}
                  <span class="category-tag ${canEdit ? "clickable" : ""}" title="${canEdit ? "Kategorie ändern" : "Kategorie"}" data-id="${item.id}" data-cat="${item.category}" style="color: ${this._getCategoryColor(item.category)}; background: color-mix(in srgb, ${this._getCategoryColor(item.category)} 12%, var(--secondary-background-color, rgba(0,0,0,0.06))); border: 1px solid color-mix(in srgb, ${this._getCategoryColor(item.category)} 25%, transparent);">${this._escapeHtml(item.category)}</span>
                  ${this._getPriorityBadge(item.priority, item.id)}
                  ${showSource ? `${this._getSourceBadge(item.source, item.device)}` : ""}
                  ${showSource && showTime ? `<span>•</span>` : ""}
                  ${showTime ? `<span>${this._formatTime(item.created_at)}</span>` : ""}
                </div>
              </div>
              <div class="item-actions">
                ${
                  canEdit
                    ? isSub
                      ? `<button class="indent-btn outdent-btn" title="Ausrücken (zu Hauptaufgabe)" data-id="${item.id}" data-action="outdent">↰</button>`
                      : item.candidateParentId
                      ? `<button class="indent-btn do-indent-btn" title="Unter vorherige Aufgabe einrücken" data-id="${item.id}" data-parent-id="${item.candidateParentId}" data-action="indent">↳</button>`
                      : ""
                    : ""
                }
                ${canEdit ? `<button class="edit-btn" title="Bearbeiten" data-id="${item.id}">✎</button>` : ""}
                ${canDelete ? `<button class="delete-btn" title="Löschen" data-id="${item.id}">✕</button>` : ""}
              </div>
            </div>
          `;
          })
          .join("");

        // Attach item button listeners
        ideasList.querySelectorAll(".check-btn").forEach((btn) => {
          btn.addEventListener("click", () => {
            const id = btn.getAttribute("data-id");
            const wasCompleted = btn.getAttribute("data-completed") === "true";
            if (wasCompleted) {
              this._uncompleteIdea(id);
            } else {
              this._completeIdea(id);
            }
          });
        });

        ideasList.querySelectorAll(".indent-btn").forEach((btn) => {
          btn.addEventListener("click", async (e) => {
            e.stopPropagation();
            if (!canEdit) return;
            const id = btn.getAttribute("data-id");
            const action = btn.getAttribute("data-action");
            const parentId = btn.getAttribute("data-parent-id") || "";
            try {
              await this._hass.callService("brainstorm", "update_idea", {
                id: id,
                parent_id: action === "indent" ? parentId : "",
              });
            } catch (err) {
              console.error("Failed to indent/outdent idea", err);
            }
          });
        });

        ideasList.querySelectorAll(".edit-btn").forEach((btn) => {
          btn.addEventListener("click", () => {
            if (!canEdit) return;
            const id = btn.getAttribute("data-id");
            const item = activeIdeas.find((i) => i.id === id);
            if (item) this._editIdea(id, item.text, item.category, item.priority, item.parent_id);
          });
        });

        ideasList.querySelectorAll(".idea-text").forEach((el) => {
          el.addEventListener("click", () => {
            if (!canEdit) return;
            const id = el.getAttribute("data-id");
            if (isCompletedView) return;
            const item = activeIdeas.find((i) => i.id === id);
            if (item) this._editIdea(id, item.text, item.category, item.priority, item.parent_id);
          });
        });

        ideasList.querySelectorAll(".prio-tag").forEach((el) => {
          el.addEventListener("click", (e) => {
            e.stopPropagation();
            const id = el.getAttribute("data-id");
            const currentPrio = el.getAttribute("data-prio") || "medium";
            if (id && canEdit) this._toggleItemPriority(id, currentPrio);
          });
        });

        ideasList.querySelectorAll(".category-tag.clickable").forEach((el) => {
          el.addEventListener("click", () => {
            if (!canEdit) return;
            const id = el.getAttribute("data-id");
            const currentCat = el.getAttribute("data-cat");
            const item = activeIdeas.find((i) => i.id === id);
            this._changeCategory(id, currentCat, item ? item.text : "");
          });
        });

        ideasList.querySelectorAll(".delete-btn").forEach((btn) => {
          btn.addEventListener("click", () => {
            const id = btn.getAttribute("data-id");
            this._deleteIdea(id);
          });
        });

        // 5. Context Menu (Long-press on Touch / Right-click on Desktop)
        if (canEdit && !isCompletedView) {
          ideasList.querySelectorAll(".idea-item").forEach((el) => {
            const id = el.getAttribute("data-id");
            const idx = parseInt(el.getAttribute("data-idx"), 10);
            const item = orderedIdeas[idx];
            if (!item) return;

            let prevTop = null;
            if (item.candidateParentId) {
              prevTop = orderedIdeas.find((i) => i.id === item.candidateParentId);
            } else if (item.isSubtask && item.parentTask) {
              prevTop = item.parentTask;
            }
            const prevItem = idx > 0 ? orderedIdeas[idx - 1] : null;
            const nextItem = idx < orderedIdeas.length - 1 ? orderedIdeas[idx + 1] : null;

            // Desktop Right-Click
            el.addEventListener("contextmenu", (e) => {
              e.preventDefault();
              this._openContextMenu(item, prevTop, nextItem, prevItem, activeIdeas);
            });

            // Mobile Long-Press (~420ms)
            let longPressTimer = null;
            let touchStartX = 0;
            let touchStartY = 0;
            let touchMoved = false;

            el.addEventListener(
              "touchstart",
              (e) => {
                if (e.target.closest("button") || e.target.closest(".drag-handle") || e.target.closest(".category-tag") || e.target.closest(".prio-tag")) return;
                touchMoved = false;
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                longPressTimer = setTimeout(() => {
                  if (!touchMoved) {
                    if (navigator.vibrate) navigator.vibrate(35);
                    this._openContextMenu(item, prevTop, nextItem, prevItem, activeIdeas);
                  }
                }, 420);
              },
              { passive: true }
            );

            el.addEventListener(
              "touchmove",
              (e) => {
                if (!longPressTimer) return;
                const dx = Math.abs(e.touches[0].clientX - touchStartX);
                const dy = Math.abs(e.touches[0].clientY - touchStartY);
                if (dx > 8 || dy > 8) {
                  touchMoved = true;
                  clearTimeout(longPressTimer);
                }
              },
              { passive: true }
            );

            el.addEventListener("touchend", () => {
              if (longPressTimer) clearTimeout(longPressTimer);
            });
            el.addEventListener("touchcancel", () => {
              if (longPressTimer) clearTimeout(longPressTimer);
            });
          });

          // 6. Desktop HTML5 Drag & Drop
          ideasList.querySelectorAll(".drag-handle").forEach((handle) => {
            const itemEl = handle.closest(".idea-item");
            if (!itemEl) return;
            handle.addEventListener("mousedown", () => {
              itemEl.setAttribute("draggable", "true");
            });
            handle.addEventListener("mouseup", () => {
              itemEl.removeAttribute("draggable");
            });
          });

          ideasList.querySelectorAll(".idea-item").forEach((itemEl) => {
            itemEl.addEventListener("dragstart", (e) => {
              const id = itemEl.getAttribute("data-id");
              itemEl.classList.add("is-dragging");
              e.dataTransfer.effectAllowed = "move";
              e.dataTransfer.setData("text/plain", id);
            });

            itemEl.addEventListener("dragend", () => {
              itemEl.removeAttribute("draggable");
              itemEl.classList.remove("is-dragging");
              ideasList.querySelectorAll(".idea-item").forEach((el) => {
                el.classList.remove("drop-target-above", "drop-target-below", "drop-target-subtask");
              });
            });

            itemEl.addEventListener("dragover", (e) => {
              e.preventDefault();
              const draggingEl = ideasList.querySelector(".idea-item.is-dragging");
              if (!draggingEl || draggingEl === itemEl) return;

              const rect = itemEl.getBoundingClientRect();
              const offsetY = e.clientY - rect.top;
              const offsetX = e.clientX - rect.left;

              itemEl.classList.remove("drop-target-above", "drop-target-below", "drop-target-subtask");

              // Subtask drag: dragged towards the right on a top-level item
              if (offsetX > rect.width * 0.35 && !itemEl.classList.contains("is-subtask")) {
                itemEl.classList.add("drop-target-subtask");
                e.dataTransfer.dropEffect = "copy";
              } else if (offsetY < rect.height / 2) {
                itemEl.classList.add("drop-target-above");
                e.dataTransfer.dropEffect = "move";
              } else {
                itemEl.classList.add("drop-target-below");
                e.dataTransfer.dropEffect = "move";
              }
            });

            itemEl.addEventListener("dragleave", () => {
              itemEl.classList.remove("drop-target-above", "drop-target-below", "drop-target-subtask");
            });

            itemEl.addEventListener("drop", async (e) => {
              e.preventDefault();
              const draggedId = e.dataTransfer.getData("text/plain");
              const targetId = itemEl.getAttribute("data-id");
              if (!draggedId || draggedId === targetId) return;

              const isSubtask = itemEl.classList.contains("drop-target-subtask");
              const isAbove = itemEl.classList.contains("drop-target-above");

              itemEl.classList.remove("drop-target-above", "drop-target-below", "drop-target-subtask");

              if (isSubtask) {
                try {
                  await this._hass.callService("brainstorm", "update_idea", {
                    id: draggedId,
                    parent_id: targetId,
                  });
                } catch (err) {
                  console.error("Failed to assign subtask via drop", err);
                }
              } else {
                const currentIds = orderedIdeas.map((i) => i.id);
                const fromIndex = currentIds.indexOf(draggedId);
                let toIndex = currentIds.indexOf(targetId);
                if (fromIndex !== -1 && toIndex !== -1) {
                  if (!isAbove) toIndex += 1;
                  if (fromIndex < toIndex) toIndex -= 1;
                  currentIds.splice(fromIndex, 1);
                  currentIds.splice(toIndex, 0, draggedId);
                  try {
                    await this._hass.callService("brainstorm", "reorder_ideas", {
                      idea_ids: currentIds,
                    });
                  } catch (err) {
                    console.error("Failed to reorder ideas via drop", err);
                  }
                }
              }
            });
          });

          // 7. Mobile Touch Drag & Drop on Handle
          let activeTouch = null;
          let ghostEl = null;
          let currentTargetEl = null;
          let currentMode = null;

          ideasList.querySelectorAll(".drag-handle").forEach((handle) => {
            handle.addEventListener(
              "touchstart",
              (e) => {
                const touch = e.touches[0];
                const itemEl = handle.closest(".idea-item");
                if (!itemEl) return;
                const id = handle.getAttribute("data-id");

                activeTouch = {
                  id: id,
                  itemEl: itemEl,
                  startX: touch.clientX,
                  startY: touch.clientY,
                };
                itemEl.classList.add("is-dragging");
                if (navigator.vibrate) navigator.vibrate(25);
              },
              { passive: false }
            );
          });

          ideasList.addEventListener(
            "touchmove",
            (e) => {
              if (!activeTouch) return;
              e.preventDefault();
              const touch = e.touches[0];

              if (!ghostEl) {
                ghostEl = document.createElement("div");
                ghostEl.className = "touch-drag-ghost";
                ghostEl.textContent = `⠿ ${activeTouch.itemEl.querySelector(".idea-text")?.textContent?.trim() || "Notiz"}`;
                this.shadowRoot.appendChild(ghostEl);
              }
              ghostEl.style.left = `${touch.clientX + 10}px`;
              ghostEl.style.top = `${touch.clientY - 25}px`;

              ghostEl.style.display = "none";
              const targetNode = this.shadowRoot.elementFromPoint(touch.clientX, touch.clientY);
              ghostEl.style.display = "flex";

              const hitItem = targetNode ? targetNode.closest(".idea-item") : null;

              ideasList.querySelectorAll(".idea-item").forEach((el) => {
                el.classList.remove("drop-target-above", "drop-target-below", "drop-target-subtask");
              });

              if (hitItem && hitItem !== activeTouch.itemEl) {
                currentTargetEl = hitItem;
                const rect = hitItem.getBoundingClientRect();
                const offsetX = touch.clientX - rect.left;
                const offsetY = touch.clientY - rect.top;

                if (offsetX > rect.width * 0.35 && !hitItem.classList.contains("is-subtask")) {
                  hitItem.classList.add("drop-target-subtask");
                  currentMode = "subtask";
                } else if (offsetY < rect.height / 2) {
                  hitItem.classList.add("drop-target-above");
                  currentMode = "above";
                } else {
                  hitItem.classList.add("drop-target-below");
                  currentMode = "below";
                }
              } else {
                currentTargetEl = null;
                currentMode = null;
              }
            },
            { passive: false }
          );

          const endTouchDrag = async () => {
            if (!activeTouch) return;

            if (ghostEl) {
              ghostEl.remove();
              ghostEl = null;
            }

            activeTouch.itemEl.classList.remove("is-dragging");

            if (currentTargetEl && currentMode) {
              const targetId = currentTargetEl.getAttribute("data-id");
              const draggedId = activeTouch.id;

              if (currentMode === "subtask" && targetId) {
                if (navigator.vibrate) navigator.vibrate(35);
                try {
                  await this._hass.callService("brainstorm", "update_idea", {
                    id: draggedId,
                    parent_id: targetId,
                  });
                } catch (err) {
                  console.error("Touch drop subtask error:", err);
                }
              } else if ((currentMode === "above" || currentMode === "below") && targetId) {
                if (navigator.vibrate) navigator.vibrate(25);
                const currentIds = orderedIdeas.map((i) => i.id);
                const fromIndex = currentIds.indexOf(draggedId);
                let toIndex = currentIds.indexOf(targetId);
                if (fromIndex !== -1 && toIndex !== -1) {
                  if (currentMode === "below") toIndex += 1;
                  if (fromIndex < toIndex) toIndex -= 1;
                  currentIds.splice(fromIndex, 1);
                  currentIds.splice(toIndex, 0, draggedId);
                  try {
                    await this._hass.callService("brainstorm", "reorder_ideas", {
                      idea_ids: currentIds,
                    });
                  } catch (err) {
                    console.error("Touch drop reorder error:", err);
                  }
                }
              }
            }

            ideasList.querySelectorAll(".idea-item").forEach((el) => {
              el.classList.remove("drop-target-above", "drop-target-below", "drop-target-subtask");
            });

            activeTouch = null;
            currentTargetEl = null;
            currentMode = null;
          };

          ideasList.addEventListener("touchend", endTouchDrag);
          ideasList.addEventListener("touchcancel", endTouchDrag);
        }
      }
    }
  } catch (err) {
    console.error("Brainstorm card _updateContent error:", err);
  }
}

  _shadowRootReady() {
    return this.shadowRoot && this.shadowRoot.getElementById("ideaInput") !== null;
  }

  getCardSize() {
    return 4;
  }
}

class BrainstormCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = { ...BRAINSTORM_CARD_DEFAULTS };
    this._hass = null;
    this._form = null;
  }

  setConfig(config) {
    this._config = {
      ...BRAINSTORM_CARD_DEFAULTS,
      ...(config || {}),
    };
    if (this._form) {
      this._form.schema = this._getSchema();
      this._form.data = this._config;
    }
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._form) {
      this._form.hass = hass;
      this._form.schema = this._getSchema();
    }
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
      { value: "all", label: "🌟 Alle Kategorien (Standard)" },
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
        label: "Kartentitel",
        default: "Brainstorm Hub",
        selector: { text: {} },
      },
      {
        name: "sensor",
        label: "Sensor-Entität",
        default: "sensor.brainstorm_ideen_ubersicht",
        selector: { entity: { domain: ["sensor"] } },
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
        name: "default_category",
        label: "Standard-Filterkategorie beim Öffnen",
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
        name: "max_items",
        label: "Maximale Notizenanzahl (0 = Unbegrenzt)",
        default: 0,
        selector: { number: { min: 0, max: 200, mode: "box" } },
      },
      {
        name: "show_quick_input",
        label: "Schnelleingabe-Feld für neue Notizen anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_categories",
        label: "Kategorie-Leiste (Filter-Pills) anzeigen",
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
        name: "show_badge",
        label: "Zähler-Badge im Header anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_mindmap_button",
        label: "Mindmap-Schaltfläche (🧠) im Header anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_color_toggle",
        label: "Farbmodus-Umschalter (🎨/🌈) im Header anzeigen",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_source_icons",
        label: "Quellen-Icons anzeigen (Alexa, Assist, Handy, Dashboard)",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "show_timestamps",
        label: "Relative Zeitangaben anzeigen (z.B. 'vor 5 Min.')",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "allow_edit",
        label: "Bearbeiten von Notizen erlauben (Klick & Stift-Icon)",
        default: true,
        selector: { boolean: {} },
      },
      {
        name: "allow_delete",
        label: "Löschen von Notizen erlauben (✕-Schaltfläche)",
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
          <span>Brainstorm Hub – Visuelle Kartenkonfiguration</span>
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
        const val = ev.detail.value;
        const newConfig = {
          type: "custom:brainstorm-card",
          ...this._config,
          ...val,
        };
        for (const [key, defVal] of Object.entries(BRAINSTORM_CARD_DEFAULTS)) {
          if (typeof defVal === "boolean") {
            if (key in val) {
              newConfig[key] = Boolean(val[key]);
            } else {
              newConfig[key] = false;
            }
          }
        }
        this._config = newConfig;
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
          <label class="fallback-label">Kartentitel</label>
          <input class="fallback-input" id="fbTitle" type="text" value="${this._config.title || 'Brainstorm Hub'}" />
        </div>
        <div class="fallback-row">
          <label class="fallback-label">Sensor-Entität</label>
          <input class="fallback-input" id="fbSensor" type="text" value="${this._config.sensor || 'sensor.brainstorm_ideen_ubersicht'}" />
        </div>
        <div class="fallback-row">
          <label class="fallback-label">Standard-Filterkategorie beim Öffnen</label>
          <select class="fallback-select" id="fbDefaultCat">
            ${this._getCategoryOptions().map(o => `<option value="${o.value}" ${(this._config.default_category || 'all') === o.value ? 'selected' : ''}>${o.label}</option>`).join("")}
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
            <input type="checkbox" id="fbHideEmpty" ${this._config.hide_empty_categories ? 'checked' : ''} />
            <span>Kategorien ohne Notizen (0) ausblenden</span>
          </label>
        </div>
      </div>
    `;
    const fbTitle = container.querySelector("#fbTitle");
    const fbSensor = container.querySelector("#fbSensor");
    const fbDefaultCat = container.querySelector("#fbDefaultCat");
    const fbColorMode = container.querySelector("#fbColorMode");
    const fbHideEmpty = container.querySelector("#fbHideEmpty");

    const emitChange = () => {
      this._config = {
        ...this._config,
        title: fbTitle ? fbTitle.value : this._config.title,
        sensor: fbSensor ? fbSensor.value : this._config.sensor,
        default_category: fbDefaultCat ? fbDefaultCat.value : this._config.default_category,
        color_mode: fbColorMode ? fbColorMode.value : this._config.color_mode,
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
    if (fbDefaultCat) fbDefaultCat.addEventListener("change", emitChange);
    if (fbColorMode) fbColorMode.addEventListener("change", emitChange);
    if (fbHideEmpty) fbHideEmpty.addEventListener("change", emitChange);
  }
}

if (!customElements.get("brainstorm-card-editor")) {
  customElements.define("brainstorm-card-editor", BrainstormCardEditor);
}

if (!customElements.get("brainstorm-card")) {
  customElements.define("brainstorm-card", BrainstormCard);
}
window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "brainstorm-card")) {
  window.customCards.push({
    type: "brainstorm-card",
    name: "Brainstorm Card",
    preview: true,
    description: "Moderne Schnellerfassung und Themen-Filter für Brainstorm Hub",
    documentationURL: "https://github.com/nukleuz80/ha_brainstorm",
  });
}

console.info(
  "%c BRAINSTORM-CARD %c v1.4.29 ",
  "color: #07070e; background: #00f5ff; font-weight: bold; border-radius: 4px 0 0 4px; padding: 2px 4px;",
  "color: #ffffff; background: #9d4edd; font-weight: bold; border-radius: 0 4px 4px 0; padding: 2px 4px;"
);
