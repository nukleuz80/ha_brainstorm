// Demo data and a minimal hass object for rendering the cards outside Home Assistant.
// index.html?lang=en switches the cards and the data to English.
const EN = new URLSearchParams(location.search).get("lang") === "en";
const L = (de, en) => (EN ? en : de);
window.demoL = L;
const now = Date.now();
const ago = (min) => new Date(now - min * 60000).toISOString();
const inDays = (d, h = 9) => { const x = new Date(now + d * 86400000); x.setHours(h, 0, 0, 0); return x.toISOString(); };
const C = {
  garden: L("Haus & Garten", "House & Garden"), smart: L("Smarthome", "Smart Home"),
  shop: L("Einkauf", "Shopping"), proj: L("Projekte", "Projects"), daily: L("Alltag", "Daily Life"),
};
let n = 0;
const idea = (text, category, extra = {}) => ({
  id: `demo${++n}`, text, category, priority: "medium", status: "active",
  created_at: ago(n * 37), source: "dashboard", device: null, parent_id: null, order: n,
  due: null, assignee: null, trigger: null, echos: null, raw_text: null, ...extra,
});
const ideas = [
  idea(L("Rasensprenger reparieren", "Fix the lawn sprinkler"), C.garden, { priority: "high", source: "alexa", device: L("Echo Küche", "Kitchen Echo"), due: inDays(1), markers: ["warning"], tags: [L("garten", "garden")] }),
  idea(L("Tomaten düngen", "Fertilize the tomatoes"), C.garden, { source: "alexa", device: L("Echo Wohnzimmer", "Living Room Echo"), repeat: "weekly", due: inDays(3, 18), tags: [L("garten", "garden")] }),
  idea(L("Kellerlicht per Bewegungsmelder dimmen", "Dim the basement light by motion"), C.smart, { priority: "urgent", source: "assist", in_progress: { user: "Claude", since: ago(12) } }),
  idea(L("Zigbee-Sensor im Bad tauschen", "Replace the Zigbee sensor in the bathroom"), C.smart, { source: "siri", device: "iPhone" }),
  idea(L("Balkonkraftwerk auswerten", "Analyze the balcony solar panels"), C.smart, { priority: "low", source: "dashboard", markers: ["money"], progress: 50 }),
  idea(L("Milch", "Milk"), C.shop, { source: "alexa", device: L("Echo Küche", "Kitchen Echo") }),
  idea(L("Duschgel", "Shower gel"), C.shop, { source: "alexa", device: L("Echo Bad", "Bathroom Echo") }),
  idea(L("Smart Mirror bauen", "Build a smart mirror"), C.proj, { priority: "high", description: L("**Raspberry Pi** mit Spiegelfolie, Kalender und Wetter", "**Raspberry Pi** with mirror film, calendar and weather"), markers: ["star"], numbering: "decimal", callout: L("Bis Weihnachten fertig", "Done by Christmas") }),
  idea(L("Oma anrufen", "Call Grandma"), C.daily, { due: inDays(0, 18), source: "companion", device: "Pixel" }),
  idea(L("Reifen wechseln", "Change the tires"), C.daily, { due: inDays(5), priority: "high" }),
];
const parent = ideas[7];
const steps = [];
for (const [t, extra] of [
  [L("Spiegelfolie bestellen", "Order mirror film"), { markers: ["check"], in_progress: { user: "Olaf", since: ago(30) } }],
  [L("MagicMirror installieren", "Install MagicMirror"), { markers: ["question"] }],
  [L("Rahmen bauen", "Build the frame"), { due: inDays(4) }],
]) {
  const s = idea(t, C.proj, { parent_id: parent.id, ...extra });
  steps.push(s);
  ideas.push(s);
}
for (const t of [L("Kalender-Modul", "Calendar module"), L("Wetter-Modul", "Weather module")]) {
  ideas.push(idea(t, C.proj, { parent_id: steps[1].id }));
}
for (const t of [L("Holz zuschneiden", "Cut the wood"), L("Lackieren", "Paint it")]) {
  ideas.push(idea(t, C.proj, { parent_id: steps[2].id }));
}
steps[2].links = [{ to: steps[0].id, label: L("braucht Maße", "needs measurements"), blocks: false }];
ideas.push(idea(L("Gartenhaus streichen", "Paint the garden shed"), C.proj, { priority: "low", markers: ["idea"] }));
const completed = [
  idea(L("Backup der Datenbank erstellen", "Create a database backup"), C.smart, { status: "completed", result: L("v1.7.19: Backup läuft täglich um 3 Uhr", "v1.7.19: backup runs daily at 3 am") }),
  idea(L("Brot", "Bread"), C.shop, { status: "completed" }),
];
const categories = ["Inbox", C.garden, C.smart, C.shop, C.proj, C.daily];
const counts = Object.fromEntries(categories.map((c) => [c, ideas.filter((i) => i.category === c).length]));
const sensor = {
  entity_id: "sensor.brainstorm_ideen_ubersicht", state: String(ideas.length), last_updated: ago(1),
  attributes: {
    friendly_name: L("Brainstorm Ideen Übersicht", "Brainstorm Ideas Overview"), speech_overview: "", last_action: null,
    active_count: ideas.length, completed_count: completed.length, categories,
    category_icons: { [C.garden]: "mdi:flower", [C.smart]: "mdi:home-automation", [C.shop]: "mdi:cart", [C.proj]: "mdi:rocket-launch", [C.daily]: "mdi:calendar-heart", Inbox: "mdi:inbox" },
    category_colors: { [C.garden]: "#4caf50", [C.smart]: "#03a9f4", [C.shop]: "#ff9800", [C.proj]: "#9c27b0", [C.daily]: "#e91e63", Inbox: "#607d8b" },
    active_categories: categories.filter((c) => counts[c] > 0), hide_empty_categories: true,
    allowed_echos: [], voice_mode: "skill", ai_subtasks: true, category_counts: counts,
    priority_counts: { urgent: 1, high: 4, medium: 9, low: 1 },
    latest_idea: ideas[0], recent_ideas: ideas.slice(0, 5), ideas, completed_ideas: completed, category_shares: {},
  },
};
const lang = EN ? "en" : "de";
document.documentElement.lang = lang;
window.demoHass = {
  language: lang, locale: { language: lang }, themes: { darkMode: true },
  user: { id: "u1", name: "Olaf", is_admin: true },
  states: { [sensor.entity_id]: sensor },
  callService: async () => {}, callWS: async () => ({}),
  connection: { subscribeMessage: async () => () => {}, subscribeEvents: async () => () => {} },
};
