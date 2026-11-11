// Extra demo states for single video shots: index.html?scene=social|comments|aimap|cluster|round
// Texts follow ?lang=en through window.demoL from demo.js.
const L = window.demoL || ((de) => de);
const PEOPLE = { u1: "Olaf", u2: "Frida", u3: "Ben" };
const ago = (min) => new Date(Date.now() - min * 60000).toISOString();
export const TRIP = L("Ausflug", "Day trip");
export const PARTY = L("Sommerfest", "Summer party");

const COMMENTS = [
  { id: "c1", by: "u2", name: "Frida", at: ago(95), text: L("Die Kinder wollen unbedingt zu den **Pinguinen** 🐧", "The kids really want to see the **penguins** 🐧"), mine: false, can_delete: true },
  { id: "c2", by: "u3", name: "Ben", at: ago(70), text: L("Sonntag soll es regnen, Samstag wäre besser.", "It's supposed to rain on Sunday, Saturday would be better."), mine: false, can_delete: true },
  { id: "c3", by: "u1", name: "Olaf", at: ago(12), text: L("Dann Samstag! @Frida kaufst du die Tickets online?", "Saturday then! @Frida can you buy the tickets online?"), mine: true, can_delete: true },
];

const MAP = [
  [L("Sommerfest im Garten", "Summer party in the garden"), 0],
  [L("Essen & Trinken", "Food & drinks"), 1],
  [L("Grillgut und Salate", "Barbecue and salads"), 2],
  [L("Getränke kühlen", "Chill the drinks"), 2],
  [L("Musik", "Music"), 1],
  [L("Playlist erstellen", "Create a playlist"), 2],
  [L("Lautsprecher testen", "Test the speakers"), 2],
  [L("Gäste", "Guests"), 1],
  [L("Einladungen verschicken", "Send the invitations"), 2],
  [L("Deko", "Decoration"), 1],
  [L("Lichterketten aufhängen", "Hang up fairy lights"), 2],
].map(([text, depth]) => ({ text, depth }));

const THEMES = [
  { title: L("Garten", "Garden"), ideas: [L("Rasen vertikutieren", "Scarify the lawn"), L("Hecke schneiden", "Trim the hedge"), L("Regentonne aufstellen", "Set up a rain barrel")] },
  { title: L("Haus & Reparaturen", "House & repairs"), ideas: [L("Dachrinne reinigen", "Clean the gutter"), L("Tür quietscht", "Door squeaks"), L("Fenster abdichten", "Seal the windows")] },
  { title: L("Smarthome", "Smart Home"), ideas: [L("Bewegungsmelder im Flur", "Motion sensor in the hallway"), L("Rollläden automatisieren", "Automate the shutters")] },
].map((theme, t) => ({ title: theme.title, ideas: theme.ideas.map((text, i) => ({ idea_id: `c${t}${i}`, text })) }));

let n = 900;
const note = (text, extra = {}) => ({
  id: `scene${++n}`, text, category: TRIP, priority: "medium", status: "active",
  created_at: ago(n - 880), source: "dashboard", device: null, parent_id: null, order: n,
  due: null, assignee: null, trigger: null, echos: null, raw_text: null, people: PEOPLE, ...extra,
});

/** Change the demo data before the card gets it. */
export function setup(scene, hass) {
  const sensor = hass.states["sensor.brainstorm_ideen_ubersicht"];
  const attrs = sensor.attributes;
  if (scene === "social" || scene === "comments") {
    const zoo = note(L("Zoo Hannover", "City zoo"), {
      priority: "high", votes: { u1: 2, u2: 1, u3: 1 }, reactions: { heart: ["u2", "u3"], like: ["u1"] }, comment_count: 3,
    });
    const ideas = [
      zoo,
      note(L("Tickets online kaufen", "Buy tickets online"), { parent_id: zoo.id }),
      note(L("Picknick packen", "Pack a picnic"), { parent_id: zoo.id }),
      note(L("Badesee", "Swimming lake"), { votes: { u2: 2, u3: 1 }, reactions: { like: ["u1", "u3"] } }),
      note(L("Kletterpark", "Climbing park"), { votes: { u1: 1 }, reactions: { laugh: ["u3"] }, comment_count: 1 }),
      note(L("Museum", "Museum"), { reactions: { important: ["u2"] } }),
    ];
    attrs.ideas = [...attrs.ideas, ...ideas];
    attrs.categories = [...attrs.categories, TRIP];
    attrs.category_icons = { ...attrs.category_icons, [TRIP]: "mdi:map-marker-radius" };
    attrs.category_colors = { ...attrs.category_colors, [TRIP]: "#00bfa5" };
    attrs.category_counts = { ...(attrs.category_counts || {}), [TRIP]: ideas.length };
    attrs.voting = { [TRIP]: { votes: 5, used: 3, hidden: false, by: "u1" } };
    attrs.current_user = "u1";
    hass._sceneIdea = zoo;
  }
  if (scene === "cluster") {
    attrs.ai_subtasks = true;
  }
  if (scene === "round") {
    const ends = new Date(Date.now() + 4 * 60000 + 30000).toISOString();
    attrs.rounds = { [hass._sceneCategory || L("Haus & Garten", "House & Garden")]: { since: ago(1), by: "u2", ends_at: ends, hidden_count: 3 } };
  }
  if (scene === "aimap") {
    attrs.ai_subtasks = true;
    attrs.categories = [...attrs.categories, PARTY];
    attrs.category_icons = { ...attrs.category_icons, [PARTY]: "mdi:party-popper" };
    attrs.category_colors = { ...attrs.category_colors, [PARTY]: "#ffb300" };
  }
  hass.callWS = async (msg) => {
    if (msg.type === "brainstorm/comments") return { comments: COMMENTS, can_edit: true };
    if (msg.type === "brainstorm/generate_map") return { nodes: MAP };
    if (msg.type === "brainstorm/cluster_ideas") return { themes: THEMES };
    if (msg.type === "brainstorm/ideas") return { ...attrs, current_user: "u1" };
    return {};
  };
}

/** Act on the rendered card, for example open a dialog. */
export async function after(scene, el, hass) {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  if (scene === "social" && el._drawMinimap) el._drawMinimap();
  if (scene === "comments") el._showComments(hass._sceneIdea);
  if (scene === "cluster") el._showClusterDialog();
  if (scene === "round") el._showBrainstorm();
  if (scene === "aimap") {
    el._showGenerateMapDialog(L("Sommerfest im Garten planen", "Plan a summer party in the garden"));
    await wait(100);
    el.shadowRoot.getElementById("mapGenerate").click();
  }
}
