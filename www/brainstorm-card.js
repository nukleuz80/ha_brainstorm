/**
 * Brainstorm Card for Home Assistant
 * Modern, sleek quick capture and idea manager
 * Version 1.4.5 - Dynamic Home Assistant Theme colors & color mode switcher
 */
class BrainstormCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._selectedCategory = "all";
    this._viewMode = "list"; // 'list' | 'mindmap'
    this._config = {
      title: "Brainstorm Hub",
      sensor: "sensor.brainstorm_ideen_ubersicht",
    };
    let savedColorMode = "theme";
    try {
      savedColorMode = localStorage.getItem("brainstorm_color_mode") || "theme";
    } catch {}
    this._colorMode = savedColorMode; // 'theme' | 'multicolor'
    this._lastColorMode = null;
    this._initialized = false;
    this._lastUpdated = null;
    this._lastCategory = "all";
    this._isDialogOpen = false;
  }

  static getStubConfig() {
    return {
      title: "Brainstorm Hub",
      sensor: "sensor.brainstorm_ideen_ubersicht",
    };
  }

  setConfig(config) {
    if (!config) config = {};
    this._config = Object.assign(
      {
        title: "Brainstorm Hub",
        sensor: "sensor.brainstorm_ideen_ubersicht",
      },
      config
    );
    if (config.color_mode) {
      this._colorMode = config.color_mode;
    }
    this._lastUpdated = null; // Force refresh on config change
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

  _getCategoryColor(category) {
    if (this._colorMode === "theme") {
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
    const s = (source || "").toLowerCase();
    if (s.includes("alexa") || s === "voice") {
      return "🗣️ Alexa";
    }
    if (s.includes("assist")) {
      return "✨ Assist";
    }
    if (s.includes("companion_voice") || s.includes("mic") || s.includes("speech")) {
      return "🎙️ Sprache";
    }
    if (s.includes("companion") || s.includes("mobile") || s.includes("handy")) {
      return "📱 Handy";
    }
    if (s.includes("dashboard")) {
      return "💻 Dashboard";
    }
    return "📝 Notiz";
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

  async _submitIdea() {
    const inputEl = this.shadowRoot.getElementById("ideaInput");
    const catSelectEl = this.shadowRoot.getElementById("catSelect");
    if (!inputEl) return;

    const text = inputEl.value.trim();
    if (!text) return;

    const selectedCat = catSelectEl ? catSelectEl.value : "";
    const category = selectedCat && selectedCat !== "auto" ? selectedCat : null;

    inputEl.value = "";
    inputEl.disabled = true;

    try {
      const payload = {
        text: text,
        source: "dashboard",
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

  _editIdea(id, currentText, currentCategory) {
    const sensor = this._getSensorEntity();
    const categories = sensor ? (sensor.attributes.categories || ["Inbox"]) : ["Inbox"];
    let selectedCat = currentCategory || "Inbox";

    this._openDialog("✏️ Notiz bearbeiten", (body) => {
      body.innerHTML = `
        <div class="action-dialog-label">Notiztext:</div>
        <textarea class="action-dialog-textarea" id="editTextarea" rows="3">${this._escapeHtml(currentText)}</textarea>

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

        <div class="action-dialog-footer">
          <button class="action-dialog-btn action-dialog-btn-cancel" id="cancelEditBtn">Abbrechen</button>
          <button class="action-dialog-btn action-dialog-btn-primary" id="saveEditBtn">Speichern</button>
        </div>
      `;

      const textarea = body.querySelector("#editTextarea");
      const saveBtn = body.querySelector("#saveEditBtn");
      const cancelBtn = body.querySelector("#cancelEditBtn");
      const catChips = body.querySelectorAll(".action-dialog-cat-chip");

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
        if (!newText) return;
        this._closeDialog();

        const payload = { id: id, text: newText };
        if (selectedCat && selectedCat !== currentCategory) {
          payload.category = selectedCat;
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
      const addNewCatBtn = body.querySelector("#addNewCatBtn");
      const handleCreateCat = async () => {
        const val = (newCatInput.value || "").trim();
        if (!val) return;
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
    this._openDialog("➕ Neue Kategorie", (body) => {
      body.innerHTML = `
        <div class="action-dialog-label">Name der neuen Kategorie:</div>
        <input type="text" class="action-dialog-input" id="createCatInput" placeholder="z. B. Smart Home, Finanzen, Einkaufen..." />
        <div class="action-dialog-footer">
          <button class="action-dialog-btn action-dialog-btn-cancel" id="cancelAddCatBtn">Abbrechen</button>
          <button class="action-dialog-btn action-dialog-btn-primary" id="saveAddCatBtn">Kategorie erstellen</button>
        </div>
      `;

      const input = body.querySelector("#createCatInput");
      const saveBtn = body.querySelector("#saveAddCatBtn");
      const cancelBtn = body.querySelector("#cancelAddCatBtn");

      const handleAdd = async () => {
        const name = (input.value || "").trim();
        if (!name) return;
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
          if (this._selectedCategory === categoryName) {
            this._selectedCategory = "all";
          }
        } catch (e) {
          console.error("Failed to remove category", e);
        }
      });
    });
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
          margin-bottom: 16px;
        }
        .title {
          font-size: 1.25rem;
          font-weight: 700;
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .logo-wrap {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          border-radius: 9px;
          overflow: hidden;
          box-shadow: 0 2px 8px rgba(0, 245, 255, 0.25);
          flex-shrink: 0;
          background: #0d1117;
        }
        .brand-logo {
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
        }
        .badge {
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
          font-size: 0.75rem;
          font-weight: 600;
          padding: 3px 9px;
          border-radius: 12px;
        }
        .header-right {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .view-toggle-btn {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          color: var(--primary-text-color, #212121);
          font-size: 0.75rem;
          font-weight: 600;
          padding: 5px 12px;
          border-radius: 12px;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 5px;
          transition: all 0.2s ease;
        }
        .view-toggle-btn:hover {
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
          border-color: var(--primary-color, #03a9f4);
        }
        .color-mode-btn {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.15)));
          color: var(--primary-text-color, #212121);
          border-radius: 50%;
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 0.9rem;
          box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
          transition: all 0.2s ease;
        }
        .color-mode-btn:hover {
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #ffffff);
          border-color: var(--primary-color, #03a9f4);
          transform: scale(1.05);
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
        .action-dialog-new-cat-row {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 4px;
        }
        .action-dialog-input {
          flex: 1;
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
          background: var(--card-background-color, var(--ha-card-background, #ffffff));
          color: var(--primary-text-color, #212121);
          padding: 8px 12px;
          border-radius: 12px;
          font-size: 0.85rem;
          outline: none;
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
        /* Input & Category Toolbar */
        .input-section {
          margin-bottom: 16px;
        }
        .cat-toolbar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
          margin-bottom: 8px;
        }
        .cat-toolbar-left {
          display: flex;
          align-items: center;
          gap: 8px;
          flex: 1 1 auto;
          min-width: 0;
        }
        .cat-toolbar-label {
          font-size: 0.85rem;
          font-weight: 500;
          color: var(--secondary-text-color, #757575);
          white-space: nowrap;
          flex-shrink: 0;
        }
        select.cat-select {
          flex: 1 1 auto;
          min-width: 140px;
          max-width: 280px;
          border: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
          background: var(--card-background-color, #ffffff);
          font-size: 0.85rem;
          font-weight: 500;
          color: var(--primary-text-color, #212121);
          border-radius: 8px;
          padding: 6px 10px;
          outline: none;
          cursor: pointer;
          box-sizing: border-box;
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        select.cat-select:focus {
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 0 0 2px var(--primary-color-alpha, rgba(3, 169, 244, 0.2));
        }
        .cat-add-btn {
          flex: 0 0 auto;
          display: inline-flex;
          align-items: center;
          gap: 5px;
          background: var(--secondary-background-color, rgba(0, 0, 0, 0.04));
          border: 1px dashed var(--divider-color, rgba(0, 0, 0, 0.2));
          color: var(--primary-color, #03a9f4);
          border-radius: 8px;
          padding: 6px 10px;
          font-size: 0.82rem;
          font-weight: 600;
          cursor: pointer;
          box-sizing: border-box;
          transition: all 0.15s ease;
          white-space: nowrap;
        }
        .cat-add-btn:hover {
          background: var(--primary-color-alpha, rgba(3, 169, 244, 0.1));
          border-color: var(--primary-color, #03a9f4);
        }
        .cat-add-btn:active {
          transform: scale(0.96);
        }
        .plus-icon {
          font-size: 0.85rem;
          line-height: 1;
        }
        .input-container {
          display: flex;
          align-items: center;
          gap: 8px;
          background: var(--secondary-background-color, rgba(0, 0, 0, 0.04));
          border: 1px solid var(--divider-color, rgba(0, 0, 0, 0.1));
          border-radius: 12px;
          padding: 6px 8px;
          width: 100%;
          box-sizing: border-box;
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        .input-container:focus-within {
          border-color: var(--primary-color, #03a9f4);
          box-shadow: 0 0 0 2px var(--primary-color-alpha, rgba(3, 169, 244, 0.2));
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
          padding: 8px 6px;
          box-sizing: border-box;
        }
        input[type="text"]::placeholder {
          color: var(--secondary-text-color, #757575);
        }
        button.send-btn {
          flex: 0 0 auto;
          background: var(--primary-color, #03a9f4);
          color: white;
          border: none;
          border-radius: 8px;
          padding: 0 16px;
          height: 38px;
          cursor: pointer;
          font-weight: 600;
          display: flex;
          align-items: center;
          justify-content: center;
          white-space: nowrap;
          box-sizing: border-box;
          transition: opacity 0.2s, transform 0.1s;
        }
        button.send-btn:hover {
          opacity: 0.9;
        }
        button.send-btn:active {
          transform: scale(0.96);
        }
        @media (max-width: 440px) {
          .cat-toolbar {
            gap: 6px;
          }
          select.cat-select {
            min-width: 110px;
          }
          button.send-btn {
            padding: 0 10px;
            font-size: 0.85rem;
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
        .item-actions {
          display: flex;
          align-items: center;
          gap: 2px;
          margin-left: 4px;
        }
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
        }
        .idea-item:hover .edit-btn,
        .idea-item:hover .delete-btn {
          opacity: 0.85;
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
          <div class="title">
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
            <span id="cardTitle">${this._config.title}</span>
          </div>
          <div class="header-right">
            <div class="badge" id="badgeCount">0 Ideen</div>
            <button class="color-mode-btn" id="cardColorModeBtn" title="${this._colorMode === 'theme' ? 'Farbmodus: Theme-Farben aktiv (Klicken für Bunt)' : 'Farbmodus: Bunt aktiv (Klicken für Theme-Farben)'}">${this._colorMode === 'theme' ? '🎨' : '🌈'}</button>
            <button class="view-toggle-btn" id="viewToggleBtn" title="Mindmap als Layer öffnen">🧠 Mindmap</button>
          </div>
        </div>

        <div id="listViewWrap">
          <div class="input-section">
            <div class="cat-toolbar">
              <div class="cat-toolbar-left">
                <span class="cat-toolbar-label">Kategorie:</span>
                <select class="cat-select" id="catSelect">
                  <option value="auto">Auto (Erkennen)</option>
                </select>
              </div>
              <button class="cat-add-btn" id="quickAddCatBtn" title="Neue Kategorie anlegen">
                <span class="plus-icon">➕</span>
                <span class="btn-text">Kategorie</span>
              </button>
            </div>

            <div class="input-container">
              <input 
                type="text" 
                id="ideaInput" 
                placeholder="Blitz-Idee tippen... (z.B. 'Garten: Baum schneiden')" 
              />
              <button class="send-btn" id="sendBtn">
                <span>Hinzufügen</span>
              </button>
            </div>
          </div>

          <div class="pills" id="pillsContainer"></div>

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

    if (cardDialogCloseBtn) {
      cardDialogCloseBtn.addEventListener("click", () => this._closeDialog());
    }
    if (cardDialog) {
      cardDialog.addEventListener("click", (e) => {
        if (e.target === cardDialog) this._closeDialog();
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

      const sensorName = (this._config && this._config.sensor) || "sensor.brainstorm_ideen_ubersicht";
      const sensorEntity = this._hass && this._hass.states ? this._hass.states[sensorName] : null;
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

    // 1. Update Title and Badge
    const titleEl = this.shadowRoot.getElementById("cardTitle");
    if (titleEl && this._config.title) titleEl.textContent = this._config.title;

    const badgeEl = this.shadowRoot.getElementById("badgeCount");
    if (badgeEl) {
      if (completedCount > 0) {
        badgeEl.textContent = `${activeIdeas.length} aktiv • ${completedCount} erledigt`;
      } else {
        badgeEl.textContent = `${activeIdeas.length} Ideen`;
      }
    }

    // 2. Update Select Dropdown without resetting user selection or closing
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
    }

    // 3. Update Category Pills
    const pillsContainer = this.shadowRoot.getElementById("pillsContainer");
    if (pillsContainer) {
      pillsContainer.innerHTML = `
        <div class="pill ${this._selectedCategory === "all" ? "active" : ""}" data-cat="all">
          <span>Alle</span>
          <span class="pill-count">${activeIdeas.length}</span>
        </div>
        ${categories
          .map((cat) => {
            const count = counts[cat] || 0;
            const isActive = this._selectedCategory === cat;
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
          this._selectedCategory = pill.getAttribute("data-cat");
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

    // 4. Update Filtered Ideas List
    const filteredIdeas = isCompletedView
      ? completedIdeas
      : this._selectedCategory === "all"
      ? activeIdeas
      : activeIdeas.filter((i) => i.category === this._selectedCategory);

    const ideasList = this.shadowRoot.getElementById("ideasList");
    if (ideasList) {
      if (filteredIdeas.length === 0) {
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
        ideasList.innerHTML = filteredIdeas
          .map(
            (item) => `
            <div class="idea-item ${isCompletedView ? "completed" : ""}" data-id="${item.id}">
              <button 
                class="check-btn ${isCompletedView ? "checked" : ""}" 
                title="${isCompletedView ? "Wieder als aktiv markieren" : "Als erledigt markieren"}" 
                data-id="${item.id}"
                data-completed="${isCompletedView ? "true" : "false"}"
              >${isCompletedView ? "✓" : ""}</button>
              <div class="idea-content">
                <div class="idea-text" title="${isCompletedView ? "" : "Klicken zum Bearbeiten"}" data-id="${item.id}">${item.text}</div>
                <div class="idea-meta">
                  <span class="category-tag ${isCompletedView ? "" : "clickable"}" title="${isCompletedView ? "Kategorie" : "Kategorie ändern"}" data-id="${item.id}" data-cat="${item.category}" style="color: ${this._getCategoryColor(item.category)}; background: color-mix(in srgb, ${this._getCategoryColor(item.category)} 12%, var(--secondary-background-color, rgba(0,0,0,0.06))); border: 1px solid color-mix(in srgb, ${this._getCategoryColor(item.category)} 25%, transparent);">${item.category}</span>
                  <span>${this._getSourceIcon(item.source)}</span>
                  <span>•</span>
                  <span>${this._formatTime(item.created_at)}</span>
                </div>
              </div>
              <div class="item-actions">
                ${isCompletedView ? "" : `<button class="edit-btn" title="Bearbeiten" data-id="${item.id}">✎</button>`}
                <button class="delete-btn" title="Löschen" data-id="${item.id}">✕</button>
              </div>
            </div>
          `
          )
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

        ideasList.querySelectorAll(".edit-btn").forEach((btn) => {
          btn.addEventListener("click", () => {
            const id = btn.getAttribute("data-id");
            const item = activeIdeas.find((i) => i.id === id);
            if (item) this._editIdea(id, item.text, item.category);
          });
        });

        ideasList.querySelectorAll(".idea-text").forEach((el) => {
          el.addEventListener("click", () => {
            const id = el.getAttribute("data-id");
            if (isCompletedView) return;
            const item = activeIdeas.find((i) => i.id === id);
            if (item) this._editIdea(id, item.text, item.category);
          });
        });

        ideasList.querySelectorAll(".category-tag.clickable").forEach((el) => {
          el.addEventListener("click", () => {
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
  });
}
