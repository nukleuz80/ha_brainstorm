// Demo data and a minimal hass object for rendering the cards outside Home Assistant
const now = Date.now();
const ago = (min) => new Date(now - min * 60000).toISOString();
const inDays = (d, h = 9) => { const x = new Date(now + d * 86400000); x.setHours(h, 0, 0, 0); return x.toISOString(); };
let n = 0;
const idea = (text, category, extra = {}) => ({
  id: `demo${++n}`, text, category, priority: "medium", status: "active",
  created_at: ago(n * 37), source: "dashboard", device: null, parent_id: null, order: n,
  due: null, assignee: null, trigger: null, echos: null, raw_text: null, ...extra,
});
const ideas = [
  idea("Rasensprenger reparieren", "Haus & Garten", { priority: "high", source: "alexa", device: "Echo Küche", due: inDays(1), markers: ["warning"], tags: ["garten"] }),
  idea("Tomaten düngen", "Haus & Garten", { source: "alexa", device: "Echo Wohnzimmer", repeat: "weekly", due: inDays(3, 18), tags: ["garten"] }),
  idea("Kellerlicht per Bewegungsmelder dimmen", "Smarthome", { priority: "urgent", source: "assist", in_progress: { user: "Claude", since: ago(12) } }),
  idea("Zigbee-Sensor im Bad tauschen", "Smarthome", { source: "siri", device: "iPhone" }),
  idea("Balkonkraftwerk auswerten", "Smarthome", { priority: "low", source: "dashboard", markers: ["money"], progress: 50 }),
  idea("Milch", "Einkauf", { source: "alexa", device: "Echo Küche" }),
  idea("Duschgel", "Einkauf", { source: "alexa", device: "Echo Bad" }),
  idea("Smart Mirror bauen", "Projekte", { priority: "high", description: "**Raspberry Pi** mit Spiegelfolie, Kalender und Wetter", markers: ["star"], numbering: "decimal", callout: "Bis Weihnachten fertig" }),
  idea("Oma anrufen", "Alltag", { due: inDays(0, 18), source: "companion", device: "Pixel" }),
  idea("Reifen wechseln", "Alltag", { due: inDays(5), priority: "high" }),
];
const parent = ideas.find((i) => i.text === "Smart Mirror bauen");
const steps = {};
for (const [t, extra] of [
  ["Spiegelfolie bestellen", { markers: ["check"], in_progress: { user: "Jan", since: ago(30) } }],
  ["MagicMirror installieren", { markers: ["question"] }],
  ["Rahmen bauen", { due: inDays(4) }],
]) {
  steps[t] = idea(t, "Projekte", { parent_id: parent.id, ...extra });
  ideas.push(steps[t]);
}
for (const t of ["Kalender-Modul", "Wetter-Modul"]) {
  ideas.push(idea(t, "Projekte", { parent_id: steps["MagicMirror installieren"].id }));
}
for (const t of ["Holz zuschneiden", "Lackieren"]) {
  ideas.push(idea(t, "Projekte", { parent_id: steps["Rahmen bauen"].id }));
}
steps["Rahmen bauen"].links = [{ to: steps["Spiegelfolie bestellen"].id, label: "braucht Maße", blocks: false }];
ideas.push(idea("Gartenhaus streichen", "Projekte", { priority: "low", markers: ["idea"] }));
const completed = [
  idea("Backup der Datenbank erstellen", "Smarthome", { status: "completed", result: "v1.7.19: Backup läuft täglich um 3 Uhr" }),
  idea("Brot", "Einkauf", { status: "completed" }),
];
const categories = ["Inbox", "Haus & Garten", "Smarthome", "Einkauf", "Projekte", "Alltag"];
const counts = Object.fromEntries(categories.map((c) => [c, ideas.filter((i) => i.category === c).length]));
const sensor = {
  entity_id: "sensor.brainstorm_ideen_ubersicht", state: String(ideas.length), last_updated: ago(1),
  attributes: {
    friendly_name: "Brainstorm Ideen Übersicht", speech_overview: "", last_action: null,
    active_count: ideas.length, completed_count: completed.length, categories,
    category_icons: { "Haus & Garten": "mdi:flower", Smarthome: "mdi:home-automation", Einkauf: "mdi:cart", Projekte: "mdi:rocket-launch", Alltag: "mdi:calendar-heart", Inbox: "mdi:inbox" },
    category_colors: { "Haus & Garten": "#4caf50", Smarthome: "#03a9f4", Einkauf: "#ff9800", Projekte: "#9c27b0", Alltag: "#e91e63", Inbox: "#607d8b" },
    active_categories: categories.filter((c) => counts[c] > 0), hide_empty_categories: true,
    allowed_echos: [], voice_mode: "skill", ai_subtasks: true, category_counts: counts,
    priority_counts: { urgent: 1, high: 4, medium: 9, low: 1 },
    latest_idea: ideas[0], recent_ideas: ideas.slice(0, 5), ideas, completed_ideas: completed, category_shares: {},
  },
};
window.demoHass = {
  language: "de", locale: { language: "de" }, themes: { darkMode: true },
  user: { id: "u1", name: "Jan", is_admin: true },
  states: { [sensor.entity_id]: sensor },
  callService: async () => {}, callWS: async () => ({}),
  connection: { subscribeMessage: async () => () => {}, subscribeEvents: async () => () => {} },
};
