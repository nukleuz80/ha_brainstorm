/**
 * Brainstorm Hub - mind map card, part "export".
 *
 * Export and import: outline files, SVG, PNG and PDF of the map.
 * Loaded the first time it is used, so the card itself loads faster. The
 * methods are copied onto the card, so `this` is the card.
 */

import { contentTemplates, importFileText, outlineFreemind, outlineMarkdown, outlineOpml, outlinePdf, t } from "./brainstorm-i18n.js?v=1.29.1";

// Helpers of the card itself, handed over by the card when it loads this part
let shapeParts;
export function bind(helpers) {
  ({ shapeParts } = helpers);
}

export default class MindmapPart {
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
          <label class="dialog-btn dialog-btn-cancel outline-file">📂 ${t("Datei wählen")}<input type="file" id="outlineFile" accept=".md,.markdown,.txt,.opml,.mm,.xml,.json,.csv,.tsv,text/plain,text/markdown,text/xml,text/csv,application/json"></label>
          <span class="dialog-hint outline-target">${target}</span>
        </div>
        <div class="dialog-hint">${t("Auch Trello (JSON) sowie CSV aus Todoist, Miro oder Excel.")}</div>
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
      // The format of a chosen Trello or CSV file, null lets Home Assistant tell
      let format = null;
      const error = body.querySelector("#outlineError");
      text.addEventListener("input", () => {
        importBtn.disabled = !text.value.trim();
      });
      body.querySelectorAll("[data-template]").forEach((chip) => {
        chip.addEventListener("click", () => {
          const tpl = contentTemplates().find((item) => item.key === chip.dataset.template);
          if (!tpl) return;
          text.value = tpl.outline;
          format = null;
          importBtn.disabled = false;
          error.textContent = "";
          text.focus();
        });
      });
      body.querySelector("#outlineFile").addEventListener("change", (e) => {
        const file = e.target.files && e.target.files[0];
        if (!file) return;
        const isJson = /\.json$/i.test(file.name);
        if (file.size > (isJson ? 20000000 : 200000)) {
          error.textContent = t("Die Datei ist zu groß (höchstens 200 KB).");
          return;
        }
        const reader = new FileReader();
        reader.onload = () => {
          const prepared = importFileText(file.name, reader.result);
          if (prepared.error) {
            error.textContent = prepared.error;
            return;
          }
          text.value = prepared.text;
          format = prepared.format;
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
        }, format);
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

  async _importOutline(text, onError, format = null) {
    const data = { text };
    if (format) data.format = format;
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

}
