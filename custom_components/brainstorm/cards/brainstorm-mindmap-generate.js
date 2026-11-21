/**
 * Brainstorm Hub - mind map card, part "generate".
 *
 * The AI dialog that turns a topic, text, web page or PDF into notes.
 * Loaded the first time it is used, so the card itself loads faster. The
 * methods are copied onto the card, so `this` is the card.
 */

import { t } from "./brainstorm-i18n.js?v=1.23.0";

export default class MindmapPart {
  // Let the AI turn a topic, a pasted text, a web page or a PDF into notes, picked in a preview
  _showGenerateMapDialog(prefill = "") {
    if (!this._hass) return;
    const focus = this._focusIdea();
    const target = focus
      ? t("Landet unter „{text}“.", { text: this._escapeHtml(focus.text) })
      : this._selectedCategory === "all"
        ? t("Landet in der Standardkategorie.")
        : t("Landet als Hauptnotizen in „{category}“.", { category: this._escapeHtml(this._selectedCategory) });
    let input = String(prefill || "");
    // The source of the last request, so "new suggestions" asks for the same
    let source = null;
    const pdfs = ((focus && focus.attachments) || []).filter(
      (a) => a.type === "application/pdf" || /\.pdf$/i.test(String(a.name || ""))
    );
    const isUrl = (text) => /^https?:\/\/\S+$/i.test(text.trim());
    this._openDialog(t("✨ Map aus Thema erzeugen"), (body) => {
      const showInput = (error = "") => {
        if (!this._isModalOpen) return;
        body.innerHTML = `
          <div class="dialog-hint">${t("Ein Thema wie „Sommerfest planen“, einen längeren Text, eine Webadresse oder ein PDF. Die KI macht daraus eine Map mit bis zu drei Ebenen, du wählst vor dem Übernehmen aus.")}</div>
          <textarea class="dialog-input dialog-textarea" id="mapTopic" rows="5" maxlength="6000" placeholder="${t("Thema, Text oder Webadresse")}"></textarea>
          <div class="dialog-hint" id="mapUrlHint" style="display: none;">🌐 ${t("Home Assistant lädt die Seite und gibt ihren Text an die KI.")}</div>
          <div class="export-row map-sources">
            <button class="dialog-btn dialog-btn-cancel" id="mapPdf">📄 ${t("PDF wählen")}</button>
            ${pdfs.map((a) => `<button class="dialog-btn dialog-btn-cancel" data-attachment="${this._escapeHtml(a.id)}">📎 ${this._escapeHtml(a.name || "PDF")}</button>`).join("")}
            <input type="file" id="mapPdfFile" accept="application/pdf,.pdf" hidden />
          </div>
          <div class="dialog-hint outline-target">${target}</div>
          <div class="dialog-error" id="mapError" style="display: ${error ? "flex" : "none"};">${error}</div>
          <div class="dialog-footer">
            <button class="dialog-btn dialog-btn-cancel" id="mapCancel">${t("Abbrechen")}</button>
            <button class="dialog-btn dialog-btn-primary" id="mapGenerate">✨ ${t("Erzeugen")}</button>
          </div>
        `;
        const area = body.querySelector("#mapTopic");
        const go = body.querySelector("#mapGenerate");
        const urlHint = body.querySelector("#mapUrlHint");
        const typed = () => {
          go.disabled = !input.trim();
          urlHint.style.display = isUrl(input) ? "flex" : "none";
        };
        area.value = input;
        typed();
        area.addEventListener("input", () => {
          input = area.value;
          typed();
        });
        const fromText = () => {
          source = { text: input.trim() };
          load();
        };
        area.addEventListener("keydown", (e) => {
          if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && input.trim()) {
            e.preventDefault();
            fromText();
          }
        });
        body.querySelector("#mapCancel").addEventListener("click", () => this._closeDialog());
        go.addEventListener("click", fromText);
        const file = body.querySelector("#mapPdfFile");
        body.querySelector("#mapPdf").addEventListener("click", () => file.click());
        file.addEventListener("change", () => {
          const chosen = file.files && file.files[0];
          if (!chosen) return;
          source = { file: chosen };
          load();
        });
        body.querySelectorAll("[data-attachment]").forEach((btn) =>
          btn.addEventListener("click", () => {
            source = { attachment: btn.dataset.attachment };
            load();
          })
        );
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
      const errorText = (code) =>
        ({
          ai_not_configured: t("Wähle zuerst eine KI-Aufgaben-Entität unter Brainstorm Hub ➔ Konfigurieren ➔ KI."),
          ai_unavailable: t("Die KI ist gerade nicht erreichbar. Versuch es gleich nochmal."),
          source_blocked: t("Adressen im eigenen Netz liest Brainstorm nicht."),
          source_unreachable: t("Die Seite oder Datei ließ sich nicht laden."),
          source_unsupported: t("Das kann Brainstorm nicht lesen. Es gehen Webseiten, Text und PDF."),
          source_too_large: t("Die Datei ist zu groß, höchstens 8 MB."),
          source_empty: t("Darin steht kein lesbarer Text, etwa bei einem eingescannten PDF."),
        })[code] || t("Die KI hat keine Map geliefert.");
      const request = async () => {
        const language = this._hass.language ? { language: this._hass.language } : {};
        if (source.file) {
          const form = new FormData();
          form.append("file", source.file, source.file.name);
          if (language.language) form.append("language", language.language);
          const response = await this._hass.fetchWithAuth("/api/brainstorm/map_source", { method: "POST", body: form });
          let result = {};
          try {
            result = await response.json();
          } catch (_err) {
            result = {};
          }
          if (!response.ok) throw { code: result.code || "ai_failed" };
          return result;
        }
        if (source.attachment) {
          return this._hass.callWS({ type: "brainstorm/generate_map", idea_id: focus.id, attachment_id: source.attachment, ...language });
        }
        return this._hass.callWS({ type: "brainstorm/generate_map", text: source.text, ...language });
      };
      const load = async () => {
        if (!source || (source.text !== undefined && !source.text)) return;
        const reading = source.file || source.attachment || isUrl(source.text || "");
        body.innerHTML = `<div class="dialog-label suggest-status">${reading ? t("Lese die Quelle, dann denkt die KI nach …") : t("Die KI denkt nach …")}</div>`;
        try {
          const result = await request();
          const nodes = (result && result.nodes) || [];
          if (!nodes.length) showInput(t("Die KI hat keine Map geliefert."));
          else showPreview(nodes);
        } catch (err) {
          showInput(errorText(err && err.code));
        }
      };
      showInput();
    });
  }

}
