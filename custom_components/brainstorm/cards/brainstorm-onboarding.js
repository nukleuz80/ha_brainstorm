/**
 * Brainstorm Hub - guided first start of the list card.
 *
 * Loaded only when the list is empty or still holds the examples, so the card
 * itself stays small. The card passes its own t() so the texts follow the
 * language of the card.
 */

// Notes made by "Add examples" carry this tag, "Remove examples" deletes them
export const SAMPLE_TAGS = ["beispiel", "example"];

// [text, priority, due in days or null, subtasks]
const SAMPLES = (t) => [
  [t("Willkommen! Tippe auf eine Notiz, um sie zu bearbeiten"), "medium", null, []],
  [t("Geburtstagsgeschenk für Oma besorgen"), "high", 3, [t("Ideen sammeln"), t("Bestellen")]],
  [t("Urlaub planen"), "medium", 14, [t("Ziel aussuchen"), t("Unterkunft buchen"), t("Packliste schreiben")]],
  [t("Fahrradreifen aufpumpen"), "low", null, []],
  [t("Milch und Brot kaufen"), "urgent", 1, []],
];

export const TOUR_STEPS = (t) => [
  [".quick-capture-card", t("Hier tippst du eine Idee ein. Mit „Garten: Baum schneiden“ landet sie gleich in der Kategorie Garten.")],
  ["#pillsContainer", t("Die Kategorien filtern die Liste. Eine neue legst du mit ➕ an.")],
  [".idea-item", t("Tippe auf eine Notiz, um sie zu bearbeiten. Im ⋯-Menü rechts findest du Unteraufgaben, Termin und Erinnerung.")],
  ["#viewToggleBtn", t("Die Mindmap zeigt alles als Karte, mit Baum, Kanban, Zeitleiste und Pinnwand.")],
  [null, t("Per Sprache geht es auch: mit Alexa, Assist oder Siri. Die Anleitungen stehen im Wiki unter Sprachsteuerung.")],
];

export function isSample(idea) {
  return Array.isArray(idea && idea.tags) && idea.tags.some((tag) => SAMPLE_TAGS.includes(String(tag).toLowerCase()));
}

export function welcomeHtml(t) {
  return `
    <div class="bs-welcome">
      <div class="bs-welcome-title">👋 ${t("Willkommen bei Brainstorm")}</div>
      <div class="bs-welcome-text">${t("Noch ist die Liste leer. Tippe oben eine Idee ein, sprich mit Alexa oder schau dir zuerst an, wie es geht.")}</div>
      <div class="bs-welcome-actions">
        <button class="bs-welcome-btn primary" data-onboarding="samples">${t("Beispiele anlegen")}</button>
        <button class="bs-welcome-btn" data-onboarding="tour">${t("Kurze Tour")}</button>
      </div>
    </div>`;
}

export function sampleBarHtml(t, count) {
  return `
    <div class="bs-sample-bar">
      <span>${t("{count} Beispiele in der Liste.", { count })}</span>
      <button class="bs-welcome-btn" data-onboarding="tour">${t("Kurze Tour")}</button>
      <button class="bs-welcome-btn" data-onboarding="remove">${t("Beispiele entfernen")}</button>
    </div>`;
}

export const ONBOARDING_CSS = `
  .bs-welcome {
    text-align: center;
    padding: 22px 14px;
    border: 1px dashed var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 12px;
  }
  .bs-welcome-title { font-size: 1.05rem; font-weight: 600; color: var(--primary-text-color); }
  .bs-welcome-text { margin: 8px auto 14px; max-width: 420px; font-size: 0.86rem; color: var(--secondary-text-color); }
  .bs-welcome-actions { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
  .bs-welcome-btn {
    min-height: 36px;
    padding: 6px 14px;
    border-radius: 18px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    background: var(--secondary-background-color, transparent);
    color: var(--primary-text-color);
    font: inherit;
    font-size: 0.84rem;
    cursor: pointer;
  }
  .bs-welcome-btn.primary { background: var(--primary-color, #03a9f4); border-color: transparent; color: var(--text-primary-color, #fff); }
  .bs-welcome-btn:disabled { opacity: 0.6; cursor: default; }
  .bs-sample-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    padding: 6px 10px;
    border-radius: 8px;
    background: color-mix(in srgb, var(--primary-color, #03a9f4) 10%, transparent);
    font-size: 0.82rem;
    color: var(--primary-text-color);
  }
  .bs-sample-bar span { flex: 1 1 auto; }
  .bs-tour-target {
    position: relative;
    z-index: 61;
    outline: 3px solid var(--primary-color, #03a9f4);
    outline-offset: 3px;
    border-radius: 10px;
  }
  .bs-tour-shade { position: absolute; inset: 0; z-index: 60; background: rgba(0, 0, 0, 0.35); border-radius: inherit; }
  .bs-tour-tip {
    position: absolute;
    z-index: 62;
    left: 16px;
    right: 16px;
    max-width: 420px;
    margin: 0 auto;
    padding: 12px 14px;
    border-radius: 12px;
    background: var(--card-background-color, #fff);
    color: var(--primary-text-color);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
    font-size: 0.86rem;
  }
  .bs-tour-foot { display: flex; align-items: center; gap: 8px; margin-top: 10px; }
  .bs-tour-step { flex: 1; color: var(--secondary-text-color); font-size: 0.78rem; }
`;

async function addIdea(hass, data) {
  const result = await hass.callWS({
    type: "call_service",
    domain: "brainstorm",
    service: "add_idea",
    service_data: data,
    return_response: true,
  });
  const idea = result && result.response && result.response.idea;
  return idea && idea.id;
}

function dueIn(days) {
  const due = new Date();
  due.setDate(due.getDate() + days);
  due.setHours(18, 0, 0, 0);
  const pad = (n) => String(n).padStart(2, "0");
  return `${due.getFullYear()}-${pad(due.getMonth() + 1)}-${pad(due.getDate())}T18:00:00`;
}

// Spread the examples over the categories the user already has
export async function addSamples(hass, t, categories) {
  const cats = (categories || []).filter(Boolean);
  const tags = [t("beispiel")];
  let index = 0;
  for (const [text, priority, days, subtasks] of SAMPLES(t)) {
    const data = { text, priority, source: "dashboard", tags };
    if (cats.length) data.category = cats[index % cats.length];
    if (days !== null) data.due = dueIn(days);
    const parentId = await addIdea(hass, data);
    for (const sub of subtasks) {
      if (!parentId) break;
      await addIdea(hass, { text: sub, source: "dashboard", tags, parent_id: parentId, ...(data.category ? { category: data.category } : {}) });
    }
    index += 1;
  }
}

// Subtasks first, so deleting a parent never trips over its children
export async function removeSamples(hass, ideas) {
  const samples = (ideas || []).filter(isSample);
  samples.sort((a, b) => (b.parent_id ? 1 : 0) - (a.parent_id ? 1 : 0));
  let removed = 0;
  for (const idea of samples) {
    try {
      await hass.callService("brainstorm", "delete_idea", { id: idea.id });
      removed += 1;
    } catch (err) {
      // Already gone with its parent
    }
  }
  return removed;
}

// Steps whose target is hidden by the card settings are left out
export function startTour(root, card, t) {
  const steps = TOUR_STEPS(t).filter(([selector]) => {
    if (!selector) return true;
    const el = root.querySelector(selector);
    return Boolean(el && el.offsetParent !== null);
  });
  if (!steps.length || !card) return;
  root.querySelectorAll(".bs-tour-shade, .bs-tour-tip").forEach((el) => el.remove());
  const shade = document.createElement("div");
  shade.className = "bs-tour-shade";
  const tip = document.createElement("div");
  tip.className = "bs-tour-tip";
  tip.setAttribute("role", "dialog");
  const oldPosition = card.style.position;
  if (getComputedStyle(card).position === "static") card.style.position = "relative";
  card.append(shade, tip);
  let current = -1;
  let target = null;

  const finish = () => {
    if (target) target.classList.remove("bs-tour-target");
    shade.remove();
    tip.remove();
    card.style.position = oldPosition;
  };
  const show = (index) => {
    if (target) target.classList.remove("bs-tour-target");
    if (index >= steps.length) {
      finish();
      return;
    }
    current = index;
    const [selector, text] = steps[index];
    target = selector ? root.querySelector(selector) : null;
    const last = index === steps.length - 1;
    tip.innerHTML = `
      <div>${text}</div>
      <div class="bs-tour-foot">
        <span class="bs-tour-step">${index + 1} / ${steps.length}</span>
        ${last ? "" : `<button class="bs-welcome-btn" data-tour="skip">${t("Überspringen")}</button>`}
        <button class="bs-welcome-btn primary" data-tour="next">${last ? t("Fertig") : t("Weiter")}</button>
      </div>`;
    tip.querySelector('[data-tour="next"]').addEventListener("click", () => show(current + 1));
    const skip = tip.querySelector('[data-tour="skip"]');
    if (skip) skip.addEventListener("click", finish);
    // Below the target, or above it when it sits low in the card
    const box = card.getBoundingClientRect();
    if (target) {
      target.classList.add("bs-tour-target");
      target.scrollIntoView({ block: "nearest", behavior: "smooth" });
      const rect = target.getBoundingClientRect();
      const below = rect.bottom - box.top + 12;
      tip.style.top = `${Math.max(8, below)}px`;
      tip.style.bottom = "";
      if (below + 160 > box.height) {
        tip.style.top = "";
        tip.style.bottom = `${Math.max(8, box.bottom - rect.top + 12)}px`;
      }
    } else {
      tip.style.bottom = "";
      tip.style.top = `${Math.max(8, box.height / 2 - 60)}px`;
    }
    tip.querySelector('[data-tour="next"]').focus();
  };
  shade.addEventListener("click", finish);
  show(0);
}
