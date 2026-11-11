// Extra demo states for single video shots: index.html?scene=social|comments|aimap
const PEOPLE = { u1: "Olaf", u2: "Frida", u3: "Ben" };
const ago = (min) => new Date(Date.now() - min * 60000).toISOString();

const COMMENTS = [
  { id: "c1", by: "u2", name: "Frida", at: ago(95), text: "Die Kinder wollen unbedingt zu den **Pinguinen** 🐧", mine: false, can_delete: true },
  { id: "c2", by: "u3", name: "Ben", at: ago(70), text: "Sonntag soll es regnen, Samstag wäre besser.", mine: false, can_delete: true },
  { id: "c3", by: "u1", name: "Olaf", at: ago(12), text: "Dann Samstag! @Frida kaufst du die Tickets online?", mine: true, can_delete: true },
];

const MAP = [
  { text: "Sommerfest im Garten", depth: 0 },
  { text: "Essen & Trinken", depth: 1 },
  { text: "Grillgut und Salate", depth: 2 },
  { text: "Getränke kühlen", depth: 2 },
  { text: "Musik", depth: 1 },
  { text: "Playlist erstellen", depth: 2 },
  { text: "Lautsprecher testen", depth: 2 },
  { text: "Gäste", depth: 1 },
  { text: "Einladungen verschicken", depth: 2 },
  { text: "Deko", depth: 1 },
  { text: "Lichterketten aufhängen", depth: 2 },
];

let n = 900;
const note = (text, extra = {}) => ({
  id: `scene${++n}`, text, category: "Ausflug", priority: "medium", status: "active",
  created_at: ago(n - 880), source: "dashboard", device: null, parent_id: null, order: n,
  due: null, assignee: null, trigger: null, echos: null, raw_text: null, people: PEOPLE, ...extra,
});

/** Change the demo data before the card gets it. */
export function setup(scene, hass) {
  const sensor = hass.states["sensor.brainstorm_ideen_ubersicht"];
  const attrs = sensor.attributes;
  if (scene === "social" || scene === "comments") {
    const zoo = note("Zoo Hannover", {
      priority: "high", votes: { u1: 2, u2: 1, u3: 1 }, reactions: { heart: ["u2", "u3"], like: ["u1"] }, comment_count: 3,
    });
    const ideas = [
      zoo,
      note("Tickets online kaufen", { parent_id: zoo.id }),
      note("Picknick packen", { parent_id: zoo.id }),
      note("Badesee", { votes: { u2: 2, u3: 1 }, reactions: { like: ["u1", "u3"] } }),
      note("Kletterpark", { votes: { u1: 1 }, reactions: { laugh: ["u3"] }, comment_count: 1 }),
      note("Museum", { reactions: { important: ["u2"] } }),
    ];
    attrs.ideas = [...attrs.ideas, ...ideas];
    attrs.categories = [...attrs.categories, "Ausflug"];
    attrs.category_icons = { ...attrs.category_icons, Ausflug: "mdi:map-marker-radius" };
    attrs.category_colors = { ...attrs.category_colors, Ausflug: "#00bfa5" };
    attrs.category_counts = { ...(attrs.category_counts || {}), Ausflug: ideas.length };
    attrs.voting = { Ausflug: { votes: 5, used: 3, hidden: false, by: "u1" } };
    attrs.current_user = "u1";
    hass._sceneIdea = zoo;
  }
  if (scene === "aimap") {
    attrs.ai_subtasks = true;
    attrs.categories = [...attrs.categories, "Sommerfest"];
    attrs.category_icons = { ...attrs.category_icons, Sommerfest: "mdi:party-popper" };
    attrs.category_colors = { ...attrs.category_colors, Sommerfest: "#ffb300" };
  }
  hass.callWS = async (msg) => {
    if (msg.type === "brainstorm/comments") return { comments: COMMENTS, can_edit: true };
    if (msg.type === "brainstorm/generate_map") return { nodes: MAP };
    if (msg.type === "brainstorm/ideas") return { current_user: "u1" };
    return {};
  };
}

/** Act on the rendered card, for example open a dialog. */
export async function after(scene, el, hass) {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  if (scene === "social" && el._drawMinimap) el._drawMinimap();
  if (scene === "comments") el._showComments(hass._sceneIdea);
  if (scene === "aimap") {
    el._showGenerateMapDialog("Sommerfest im Garten planen");
    await wait(100);
    el.shadowRoot.getElementById("mapGenerate").click();
  }
}
