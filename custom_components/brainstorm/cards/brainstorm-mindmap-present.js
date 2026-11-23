/**
 * Brainstorm Hub - mind map card, part "present".
 *
 * Presentation mode: the map walks through its notes one by one.
 * Loaded the first time it is used, so the card itself loads faster. The
 * methods are copied onto the card, so `this` is the card.
 */

import { formatText, t } from "./brainstorm-i18n.js?v=1.28.2";

export default class MindmapPart {
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

}
