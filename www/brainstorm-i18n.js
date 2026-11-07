/**
 * Brainstorm Hub - texts of the cards.
 *
 * The German text is the key, so the cards read naturally and German needs no
 * dictionary. To add a language, add a dictionary below; a missing text shows the
 * English one.
 */
const DICTIONARIES = {
  en: {
    "+ Kategorie": "+ Category",
    "0 Ideen": "0 ideas",
    "0 Notizen": "0 notes",
    "Abbrechen": "Cancel",
    "Aktionen für Notiz": "Actions for note",
    "Akzentfarbe:": "Accent color:",
    "Alle": "All",
    "Alle Benutzer": "All users",
    "Als erledigt markieren": "Mark as done",
    "Ansehen": "View",
    "Aufnahme beenden": "Stop recording",
    "Ausrücken": "Outdent",
    "Ausrücken (zu Hauptaufgabe)": "Outdent (to main task)",
    "Auto (Erkennen)": "Auto (detect)",
    "Bearbeiten": "Edit",
    "Bearbeiten von Notizen erlauben (Klick & Stift-Icon)": "Allow editing notes (click and pencil icon)",
    "Bitte im Format {format} eingeben.": "Please use the format {format}.",
    "Blitz-Idee tippen... (z.B. 'Garten: Baum schneiden')": "Type a quick idea... (for example 'Garden: cut the tree')",
    "Brainstorm Hub – Visuelle Kartenkonfiguration": "Brainstorm Hub – visual card configuration",
    "Brainstorm Logo in Toolbar anzeigen": "Show the Brainstorm logo in the toolbar",
    "Brainstorm Mindmap – Visuelle Kartenkonfiguration": "Brainstorm Mindmap – visual card configuration",
    "Das Mikrofon ist nicht erlaubt. Bitte im Browser freigeben.": "The microphone is not allowed. Please allow it in your browser.",
    "Design für '{name}' anpassen": "Change the design of '{name}'",
    "Die Spracherkennung konnte nicht starten.": "Speech recognition could not start.",
    "Enthaltene Notizen werden automatisch in die Kategorie <em>Inbox</em> verschoben.": "Notes in it are moved to the category <em>Inbox</em> automatically.",
    "Ergebnis": "Result",
    "Erinnern: Zeitpunkt wählen": "Remind: choose a time",
    "Erinnern: heute Abend": "Remind: this evening",
    "Erinnern: morgen früh": "Remind: tomorrow morning",
    "Erinnern: nächste Woche": "Remind: next week",
    "Erinnert an diesem Ort": "Reminds at this place",
    "Erinnerung": "Reminder",
    "Erinnerung entfernen": "Remove reminder",
    "Erledigt": "Completed",
    "Erledigte Ideen anzeigen": "Show completed ideas",
    "Farbmodus": "Color mode",
    "Farbmodus-Umschalter (🎨/🌈) im Header anzeigen": "Show the color mode switch (🎨/🌈) in the header",
    "Farbmodus-Umschalter (🎨/🌈) in Toolbar anzeigen": "Show the color mode switch (🎨/🌈) in the toolbar",
    "Farbmodus: Bunt aktiv (Klicken für Theme-Farben)": "Color mode: multicolor on (click for theme colors)",
    "Farbmodus: Theme-Farben aktiv (Klicken für Bunt)": "Color mode: theme colors on (click for multicolor)",
    "Freigeben": "Share",
    "Für andere freigegeben": "Shared with others",
    "Für diese Person": "For this person",
    "Gerät": "Device",
    "Gerät: {device}": "Device: {device}",
    "Geteilt": "Shared",
    "Geteilt von {name}, du darfst ansehen": "Shared by {name}, you may view it",
    "Geteilt von {name}, du darfst bearbeiten": "Shared by {name}, you may edit it",
    "Eingetragen von {name}": "Added by {name}",
    "Unteridee anlegen": "Add a subidea",
    "Bring-Nachricht senden": "Send Bring! message",
    "Anhänge:": "Attachments:",
    "Anhänge anzeigen": "Show attachments",
    "Anhang löschen": "Delete attachment",
    "Keine Anhänge.": "No attachments.",
    "Wird hochgeladen …": "Uploading …",
    "📎 Datei anhängen": "📎 Attach file",
    "Bilder auch per Einfügen oder Ziehen. Nach dem Erledigen bleiben Anhänge 30 Tage.": "Images can also be pasted or dropped. Attachments stay for 30 days after an idea is done.",
    "„{name}“ löschen?": "Delete “{name}”?",
    "Der Anhang konnte nicht gespeichert werden ({status}).": "The attachment could not be saved ({status}).",
    "📎 Anhänge: {title}": "📎 Attachments: {title}",
    "Schließen": "Close",
    "In Arbeit": "In progress",
    "In Arbeit seit {time}": "In progress since {time}",
    "{name} arbeitet daran seit {time}": "{name} has been working on it since {time}",
    "Als „In Arbeit“ markieren": "Mark as “in progress”",
    "Markierung „In Arbeit“ entfernen": "Remove the “in progress” mark",
    "Unteraufgaben einklappen": "Collapse subtasks",
    "Batterie": "Battery",
    "Titel:": "Title:",
    "Beschreibung:": "Description:",
    "Optional: Details, Links, Notizen …": "Optional: details, links, notes …",
    "Antippen zum Auf- und Zuklappen": "Tap to expand or collapse",
    "Unteraufgaben ausklappen": "Expand subtasks",
    "Dringend in Bring melden": "Report as urgent in Bring!",
    "Alle auf der Liste bekommen eine Nachricht": "Everyone on the list gets a message",
    "Ich gehe einkaufen": "I'm going shopping",
    "Einkauf erledigt": "Shopping done",
    "Liste geändert": "List changed",
    "Bring-Nachricht gesendet": "Bring! message sent",
    "Bring-Nachricht fehlgeschlagen: {error}": "Bring! message failed: {error}",
    "🌿 Neue Unteridee": "🌿 New subidea",
    "Unter: {text}": "Below: {text}",
    "Neue Unteridee …": "New subtask …",
    "Neue Idee …": "New note …",
    "↶ Rückgängig: {text}": "↶ Undone: {text}",
    "↶ Rückgängig": "↶ Undone",
    "Rückgängig ging nicht": "Could not undo",
    "Rückgängig (Strg+Z)": "Undo (Ctrl+Z)",
    "Map als Bild speichern": "Save the map as a picture",
    "🖼️ Map als Bild speichern": "🖼️ Save the map as a picture",
    "Gespeichert wird, was gerade auf der Map steht, ohne eingeklappte Zweige.": "The picture shows what is on the map right now, without folded branches.",
    "SVG (Vektor)": "SVG (vector)",
    "PNG (Bild)": "PNG (image)",
    "Auf der Map ist nichts zum Speichern": "There is nothing on the map to save",
    "Speichern als Bild ging nicht": "Could not save the picture",
    "Schaltfläche zum Speichern als Bild (🖼️) anzeigen": "Show the button to save as a picture (🖼️)",
    "Vorlage für das Aussehen": "Template for the look",
    "Standard: Karten, Kurven, Kategoriefarben": "Standard: cards, curves, category colors",
    "Klar: Rechtecke, eckige Linien": "Clean: rectangles, angled lines",
    "Skizze: Kapseln, gestrichelt, Pastell": "Sketch: pills, dashed, pastel",
    "Neon: dunkel und leuchtend": "Neon: dark and glowing",
    "Form der Notizen": "Shape of the notes",
    "Wie die Vorlage": "As in the template",
    "Karte": "Card",
    "Wolke": "Cloud",
    "Sprechblase": "Speech bubble",
    "Sprachnotizen als Sprechblase zeigen": "Show voice notes as speech bubbles",
    "Automatisch": "Automatic",
    "Form auf der Mindmap:": "Shape on the mind map:",
    "Automatisch: Sprachnotizen als Sprechblase, sonst die Form der Map.": "Automatic: voice notes as speech bubbles, otherwise the shape of the map.",
    "Kapsel": "Pill",
    "Rechteck": "Rectangle",
    "Linien": "Lines",
    "Kurve": "Curve",
    "Gerade": "Straight",
    "Eckig": "Angled",
    "Gestrichelt": "Dashed",
    "Farbschema": "Color scheme",
    "Kategoriefarben": "Category colors",
    "Pastell": "Pastel",
    "Einfarbig": "Single color",
    "Neon": "Neon",
    "Zweig aufklappen": "Unfold branch",
    "Zweig einklappen": "Fold branch",
    "Ordnen": "Arrange",
    "🪄 Map neu ordnen?": "🪄 Arrange the map again?",
    "{count} von Hand verschobene Notizen kommen wieder an ihren automatischen Platz, auf allen Geräten.": "{count} notes you placed by hand go back to their automatic place, on every device.",
    "Neu ordnen: von Hand verschobene Notizen wieder automatisch platzieren": "Arrange again: place notes you moved by hand automatically",
    "Halten & Ziehen zum Sortieren oder Unteraufgabe zuordnen": "Hold and drag to sort or to make a subtask",
    "Handy": "Phone",
    "Heute {clock}": "Today {clock}",
    "Hinzufügen": "Add",
    "Höhe der Mindmap (z.B. 600px, 75vh, calc(100vh - 32px))": "Height of the mindmap (for example 600px, 75vh, calc(100vh - 32px))",
    "Ich höre zu … Zum Beenden nochmal tippen.": "Listening … Tap again to stop.",
    "Icon (Home Assistant / MDI):": "Icon (Home Assistant / MDI):",
    "Idee": "idea",
    "Idee / Gedanke:": "Idea / thought:",
    "Idee erfassen": "Capture idea",
    "Idee sprechen": "Speak an idea",
    "Ideen": "ideas",
    "Interaktive Mindmap-Darstellung für deine Brainstorm Hub Notizen und Ideen.": "Interactive mindmap of your Brainstorm Hub notes and ideas.",
    "Kartentitel": "Card title",
    "Kategorie": "Category",
    "Kategorie '{name}' löschen": "Delete category '{name}'",
    "Kategorie erstellen": "Create category",
    "Kategorie wählen:": "Choose a category:",
    "Kategorie ändern": "Change category",
    "Kategorie-Leiste (Filter-Pills) anzeigen": "Show the category bar (filter pills)",
    "Kategorie:": "Category:",
    "Kategorien ohne Notizen (0) ausblenden": "Hide categories without notes (0)",
    "Kategoriename...": "Category name...",
    "Keine Freigabe": "Not shared",
    "Keine Ideen in der Kategorie \"{category}\".": "No ideas in the category \"{category}\".",
    "Keine aktiven Notizen in dieser Kategorie.<br>Klicke unten links auf \"+ Idee\", um eine hinzuzufügen.": "No active notes in this category.<br>Click \"+ Idea\" at the bottom left to add one.",
    "Keine erledigten Ideen vorhanden.": "No completed ideas yet.",
    "Klicken zum Bearbeiten": "Click to edit",
    "Klicken zum Bearbeiten (Lange drücken für Kontextmenü)": "Click to edit (long press for the menu)",
    "Kompakte Zeilenhöhe (mehr Aufgaben auf einen Blick)": "Compact rows (more tasks at a glance)",
    "Last Alexa Entität": "Last Alexa entity",
    "Last Alexa Entität (Echo / Sensor)": "Last Alexa entity (Echo / sensor)",
    "Leuchtende Glühbirne im Zentrum als Wasserzeichen anzeigen": "Show the glowing bulb in the center as a watermark",
    "Logo im Header anzeigen": "Show the logo in the header",
    "Löschen": "Delete",
    "Löschen von Notizen erlauben (✕-Schaltfläche)": "Allow deleting notes (✕ button)",
    "Maximale Notizenanzahl (0 = Unbegrenzt)": "Maximum number of notes (0 = unlimited)",
    "Meine": "Mine",
    "Mikrofon im Schnelleingabe-Feld anzeigen (nur über HTTPS)": "Show the microphone in the quick input (HTTPS only)",
    "Mindmap als Layer öffnen": "Open mindmap as a layer",
    "Mindmap schließen (ESC)": "Close mindmap (ESC)",
    "Mindmap-Schaltfläche (🧠) im Header anzeigen": "Show the mindmap button (🧠) in the header",
    "Mindmap-Titel": "Mindmap title",
    "Mit mir geteilt": "Shared with me",
    "Moderne Schnellerfassung und Themen-Filter für Brainstorm Hub": "Modern quick capture and topic filters for Brainstorm Hub",
    "Morgen {clock}": "Tomorrow {clock}",
    "Möchtest du die Kategorie <strong>\"{name}\"</strong> wirklich löschen?": "Do you really want to delete the category <strong>\"{name}\"</strong>?",
    "Möchtest du diese Notiz wirklich unwiderruflich aus Brainstorm entfernen?": "Do you really want to remove this note from Brainstorm for good?",
    "Nach oben verschieben": "Move up",
    "Nach unten verschieben": "Move down",
    "Name der neuen Kategorie:": "Name of the new category:",
    "Neue Idee": "New idea",
    "Neue Kategorie erstellen": "Create a new category",
    "Neue Notiz-Schaltfläche (+ Idee) anzeigen": "Show the new note button (+ Idea)",
    "Nicht geändert: {items}": "Not changed: {items}",
    "Nicht ändern": "Do not change",
    "Notiz": "Note",
    "Notiz bearbeiten": "Edit note",
    "Notiz in \"{category}\" verfassen...": "Write a note in \"{category}\"...",
    "Notiz löschen": "Delete note",
    "Obere Werkzeugleiste (Titel & Filter-Pills) anzeigen": "Show the top toolbar (title and filter pills)",
    "Oder neue Kategorie anlegen:": "Or create a new category:",
    "Original gesprochen:": "Originally spoken:",
    "Priorität festlegen": "Set priority",
    "Priorität:": "Priority:",
    "Priorität: 🔥 Dringend (Klicken zum Umschalten)": "Priority: 🔥 Urgent (click to change)",
    "Priorität: 🔴 Hoch (Klicken zum Umschalten)": "Priority: 🔴 High (click to change)",
    "Priorität: 🟡 Mittel (Klicken zum Umschalten)": "Priority: 🟡 Medium (click to change)",
    "Priorität: 🟢 Niedrig (Klicken zum Umschalten)": "Priority: 🟢 Low (click to change)",
    "Punktraster im Hintergrund anzeigen": "Show the dot grid in the background",
    "Quelle": "Source",
    "Quelle: {name}": "Source: {name}",
    "Quelle: {name} • Gerät: {device}": "Source: {name} • Device: {device}",
    "Quellen-Icons anzeigen (Alexa, Assist, Handy, Dashboard)": "Show source icons (Alexa, Assist, phone, dashboard)",
    "Relative Zeitangaben anzeigen (z.B. 'vor 5 Min.')": "Show relative times (for example '5 min ago')",
    "Schließen (ESC)": "Close (ESC)",
    "Schnelleingabe-Feld für neue Notizen anzeigen": "Show the quick input for new notes",
    "Sensor-Entität": "Sensor entity",
    "Speichern": "Save",
    "Sprache": "Voice",
    "Standard-Farbmodus": "Default color mode",
    "Standard-Filterkategorie beim Öffnen": "Category selected when opening",
    "Standard-Kategorie im Fokus": "Category in focus by default",
    "Titel": "Title",
    "Unter vorherige Aufgabe einrücken": "Indent under the previous task",
    "Unteraufgabe": "Subtask",
    "Unteraufgabe einrücken": "Indent as a subtask",
    "Vergrößern": "Zoom in",
    "Verkleinern": "Zoom out",
    "Verschieben": "Move",
    "Vollbild beenden": "Leave full screen",
    "Vollbild umschalten (ESC zum Beenden)": "Toggle full screen (ESC to leave)",
    "Vollbild-Schaltfläche (⛶) anzeigen": "Show the full screen button (⛶)",
    "Wann soll Brainstorm erinnern? ({format})": "When should Brainstorm remind you? ({format})",
    "Was möchtest du festhalten?...": "What do you want to keep?...",
    "Wieder als aktiv markieren": "Mark as active again",
    "Wieder zur Hauptaufgabe machen": "Make it a main task again",
    "Zentrieren / Anordnen": "Center / arrange",
    "Ziel-Kategorie auswählen": "Choose a target category",
    "Zoom- & Zentrieren-Schaltflächen anzeigen": "Show the zoom and center buttons",
    "Zuhause": "Home",
    "Zuletzt aktive Alexa (Last Alexa) anzeigen": "Show last active Alexa",
    "Zuletzt aktive Alexa: {name} (Klicken für Details)": "Last active Alexa: {name} (click for details)",
    "Zurücksetzen": "Reset",
    "Zähler-Badge im Header anzeigen": "Show the counter badge in the header",
    "gerade eben": "just now",
    "vor {count} Min.": "{count} min ago",
    "vor {count} Std.": "{count} h ago",
    "vor {count}h": "{count}h ago",
    "vor {count}m": "{count}m ago",
    "z. B. Smart Home, Finanzen, Einkaufen...": "For example Smart Home, Finances, Shopping...",
    "z. B. mdi:home-automation": "For example mdi:home-automation",
    "{count} Ideen": "Ideas: {count}",
    "{active} aktiv • {done} erledigt": "{active} active • {done} completed",
    "{count} ausgewählt": "{count} selected",
    "{count} fremde Einträge bleiben erhalten.": "Entries of other people that stay: {count}",
    "{count} fremde Einträge werden ausgelassen.": "Entries of other people that are skipped: {count}",
    "Überfällig": "Overdue",
    "Übergeordnete Aufgabe:": "Parent task:",
    "Erinnern auf:": "Remind on:",
    "Ohne Auswahl gelten die Einstellungen der Erinnerungen.": "Without a choice, the reminder settings apply.",
    "Ohne Uhrzeit erinnert Brainstorm um 9:00.": "Without a time, Brainstorm reminds you at 9:00.",
    "Termin:": "Due:",
    "Wie in den Einstellungen": "As in the settings",
    "Termin entfernen": "Remove due date",
    "Übernehmen": "Use it",
    "— Keine (Hauptaufgabe) —": "— None (main task) —",
    "☑️ Auswählen": "☑️ Select",
    "⚠️ Bitte gib einen Kategorienamen ein.": "⚠️ Please enter a category name.",
    "⚠️ Der Text darf nicht leer sein.": "⚠️ The text must not be empty.",
    "⚠️ Die Kategorie \"{name}\" existiert bereits.": "⚠️ The category \"{name}\" already exists.",
    "✏️ Notiz bearbeiten": "✏️ Edit note",
    "✓ Erledigen": "✓ Complete",
    "✨ Noch keine aktiven Ideen. Tippe oben eine Idee ein oder sprich mit Alexa!": "✨ No active ideas yet. Type one above or talk to Alexa!",
    "➕ Erstellen": "➕ Create",
    "➕ Neue Kategorie": "➕ New category",
    "🌈 Bunt (Multicolor)": "🌈 Multicolor",
    "🌈 Bunt (Multicolor-Kategoriefarben)": "🌈 Multicolor (category colors)",
    "🌟 Alle Kategorien (Gesamtübersicht)": "🌟 All categories (overview)",
    "🌟 Alle Kategorien (Standard)": "🌟 All categories (default)",
    "🎨 Design für „{name}“": "🎨 Design of “{name}”",
    "🎨 Theme-Farben": "🎨 Theme colors",
    "🎨 Theme-Farben (Dynamisch nach Home Assistant Theme)": "🎨 Theme colors (follow the Home Assistant theme)",
    "🏷️ Kategorie auswählen": "🏷️ Choose a category",
    "🏷️ Verschieben": "🏷️ Move",
    "🏷️ {count} Einträge verschieben": "🏷️ Move entries: {count}",
    "👥 Freigeben": "👥 Share",
    "👥 {category} freigeben": "👥 Share {category}",
    "👥 {count} Einträge freigeben": "👥 Share entries: {count}",
    "💡 Neue Idee erfassen": "💡 Capture a new idea",
    "🔥 Dringend": "🔥 Urgent",
    "🔴 Hoch": "🔴 High",
    "🗑️ Kategorie löschen?": "🗑️ Delete category?",
    "🗑️ Löschen": "🗑️ Delete",
    "🗑️ Notiz löschen?": "🗑️ Delete note?",
    "🗑️ {count} Einträge löschen?": "🗑️ Delete entries: {count}?",
    "🟡 Mittel": "🟡 Medium",
    "🟢 Niedrig": "🟢 Low",
    "Abhaken": "Done",
    "Alle abhaken": "Mark all as done",
    "Auswahl": "Selection",
    "Auswahl aufheben (ESC)": "Clear selection (ESC)",
    "Auswählen: Rahmen um mehrere Notizen ziehen (oder Umschalt+Ziehen)": "Select: drag a frame around several notes (or Shift+drag)",
    "Möchtest du diese Notizen wirklich aus Brainstorm entfernen?": "Do you really want to remove these notes from Brainstorm?",
    "Rahmen ziehen oder Notizen antippen": "Drag a frame or tap notes",
    "{count} Notizen": "{count} notes",
    "{count} Notizen erledigt": "{count} notes done",
    "{count} Notizen gelöscht": "{count} notes deleted",
    "🗑️ {count} Notizen löschen?": "🗑️ Delete {count} notes?",
    "… und {count} weitere": "… and {count} more",
    "Unteraufgaben von der KI vorschlagen lassen": "Let the AI suggest subtasks",
    "✨ Unteraufgaben vorschlagen": "✨ Suggest subtasks",
    "Die KI denkt nach …": "The AI is thinking …",
    "Nochmal versuchen": "Try again",
    "Haken weg bei allem, was du nicht willst. Du kannst die Texte noch ändern.": "Untick what you do not want. You can still change the texts.",
    "Neue Vorschläge": "New suggestions",
    "{count} übernehmen": "Add {count}",
    "{count} Unteraufgaben angelegt": "{count} subtasks added",
    "{count} Unteraufgaben": "{count} subtasks",
    "Die KI hat keine Unteraufgaben geliefert.": "The AI gave no subtasks.",
    "Die KI ist gerade nicht erreichbar. Versuch es gleich nochmal.": "The AI cannot be reached right now. Try again in a moment.",
    "Wähle zuerst eine KI-Aufgaben-Entität unter Brainstorm Hub ➔ Konfigurieren ➔ KI.": "First choose an AI task entity under Brainstorm Hub ➔ Configure ➔ AI.",
    "Du darfst diese Notiz nicht ändern.": "You may not change this note.",
  },
};

let language = (document.documentElement.lang || navigator.language || "en").toLowerCase();

const code = () => language.split(/[-_]/)[0];

/** Follow the language of the person's Home Assistant profile. */
export function setLanguage(hass) {
  const next = hass && (hass.locale?.language || hass.language);
  if (next) language = next.toLowerCase();
}

/** Return a text in the current language with its values filled in. */
export function t(text, values) {
  let result = text;
  if (code() !== "de") {
    result = DICTIONARIES[code()]?.[text] ?? DICTIONARIES.en[text] ?? text;
  }
  if (values) {
    for (const [name, value] of Object.entries(values)) {
      result = result.split(`{${name}}`).join(String(value));
    }
  }
  return result;
}

/** Return the locale for dates. */
export function dateLocale() {
  return code() === "de" ? "de-DE" : language;
}

const pad = (value) => String(value).padStart(2, "0");

/** Return a day and month, without the year. */
export function shortDate(date) {
  if (code() === "de") return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.`;
  return date.toLocaleDateString(language, { month: "short", day: "numeric" });
}

/** Return the format a person types a date and time in. */
export function dueInputFormat() {
  return code() === "de" ? "TT.MM.JJJJ HH:MM" : "YYYY-MM-DD HH:MM";
}

/** Return a date and time in the format a person types. */
export function formatDueInput(date) {
  const clock = `${pad(date.getHours())}:${pad(date.getMinutes())}`;
  if (code() === "de") {
    return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()} ${clock}`;
  }
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${clock}`;
}

/** Return the date a person typed, null if it does not fit the format. */
export function parseDueInput(input) {
  const text = input.trim();
  const german = text.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})$/);
  if (german) return new Date(+german[3], +german[2] - 1, +german[1], +german[4], +german[5]);
  const iso = text.match(/^(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2})$/);
  if (iso) return new Date(+iso[1], +iso[2] - 1, +iso[3], +iso[4], +iso[5]);
  return null;
}

/** Return the values of a date and a time input for a due date. */
export function dueInputValues(due) {
  const date = due ? new Date(due) : null;
  if (!date || Number.isNaN(date.getTime())) return { date: "", time: "" };
  return {
    date: `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`,
    time: `${pad(date.getHours())}:${pad(date.getMinutes())}`,
  };
}

/** Return the due date of a date and a time input, a missing time meaning 09:00. */
export function dueFromInputValues(date, time) {
  if (!date) return null;
  const due = new Date(`${date}T${time || "09:00"}`);
  return Number.isNaN(due.getTime()) ? null : due.toISOString();
}

/** Return the Echos of the Alexa Media Player integration, sorted by name. */
export function alexaEchos(hass) {
  return Object.keys((hass && hass.entities) || {})
    .filter((id) => id.startsWith("media_player.") && hass.entities[id].platform === "alexa_media")
    .map((id) => {
      const state = hass.states[id];
      return { id, name: (state && state.attributes.friendly_name) || id };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}

const ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (char) => ESCAPES[char]);
}

/** Return the link target if it is a web or mail address, otherwise null. */
function safeHref(url) {
  try {
    const parsed = new URL(url);
    return ["http:", "https:", "mailto:"].includes(parsed.protocol) ? parsed.href : null;
  } catch (err) {
    return null;
  }
}

function link(url, label) {
  const href = safeHref(url);
  if (!href) return escapeHtml(label);
  return `<a class="bs-link" href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`;
}

// `code`, [label](url), bare http(s) addresses, **bold**, ~~strike~~, *italic*
const MARKDOWN =
  /`([^`\n]+)`|\[([^\]\n]+)\]\(((?:https?:\/\/|mailto:)[^\s()]+)\)|(https?:\/\/[^\s<>"']+)|\*\*(?=\S)([^*\n]*?\S)\*\*|~~(?=\S)([^~\n]*?\S)~~|\*(?=[^\s*])([^*\n]*?[^\s*])\*/g;

/**
 * Turn the text of an idea into safe HTML with links and a little Markdown.
 *
 * Everything is escaped; only the tags made here are HTML, and links only go
 * to web or mail addresses.
 */
export function formatText(text) {
  if (text === null || text === undefined) return "";
  const raw = String(text);
  let html = "";
  let last = 0;
  for (const match of raw.matchAll(MARKDOWN)) {
    const [whole, code, label, target, bare, bold, strike, italic] = match;
    html += escapeHtml(raw.slice(last, match.index));
    last = match.index + whole.length;
    if (code !== undefined) {
      html += `<code>${escapeHtml(code)}</code>`;
    } else if (label !== undefined) {
      html += link(target, label);
    } else if (bare !== undefined) {
      // Punctuation after an address belongs to the sentence, and so does a
      // closing bracket without an opening one in the address.
      let url = bare.replace(/[.,;:!?]+$/, "");
      while (url.endsWith(")") && (url.match(/\(/g) || []).length < (url.match(/\)/g) || []).length) {
        url = url.slice(0, -1).replace(/[.,;:!?]+$/, "");
      }
      html += link(url, url);
      last = match.index + url.length;
    } else if (bold !== undefined) {
      html += `<strong>${formatText(bold)}</strong>`;
    } else if (strike !== undefined) {
      html += `<s>${formatText(strike)}</s>`;
    } else {
      html += `<em>${formatText(italic)}</em>`;
    }
  }
  return html + escapeHtml(raw.slice(last));
}

const ATTACHMENT_URL = "/api/brainstorm/attachments";
const ATTACHMENT_ACCEPT = "image/*,.pdf,.txt,.log,.md,.csv,.json,.yaml,.yml,.zip";
const signedUrls = new Map();

/** Return a signed address, so an image tag can load a file without a token. */
async function signedAttachmentUrl(hass, ideaId, attachmentId) {
  const path = `${ATTACHMENT_URL}/${encodeURIComponent(ideaId)}/${encodeURIComponent(attachmentId)}`;
  const cached = signedUrls.get(path);
  if (cached && cached.until > Date.now()) return cached.url;
  const result = await hass.callWS({ type: "auth/sign_path", path, expires: 3600 });
  signedUrls.set(path, { url: result.path, until: Date.now() + 50 * 60 * 1000 });
  return result.path;
}

async function attachmentRequest(hass, path, init) {
  const response = await hass.fetchWithAuth(path, init);
  let body = {};
  try {
    body = await response.json();
  } catch (_err) {
    body = {};
  }
  if (!response.ok) {
    throw new Error(body.message || t("Der Anhang konnte nicht gespeichert werden ({status}).", { status: response.status }));
  }
  return body;
}

function formatSize(bytes) {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1).replace(".", code() === "de" ? "," : ".")} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

/** Return the 🔧 badge of an idea someone is working on, or nothing. */
export function inProgressBadge(idea) {
  const mark = idea && idea.in_progress;
  if (!mark) return "";
  const since = mark.since ? new Date(mark.since) : null;
  const when = since && !Number.isNaN(since.getTime())
    ? since.toLocaleString(dateLocale(), { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })
    : "";
  const name = mark.name ? escapeHtml(mark.name) : "";
  const title = name ? t("{name} arbeitet daran seit {time}", { name, time: when }) : t("In Arbeit seit {time}", { time: when });
  return `<span class="in-progress-badge" title="${title}">🔧 ${t("In Arbeit")}${name ? ` · ${name}` : ""}</span>`;
}

/** Return the 📎 badge of an idea with files, or nothing. */
export function attachmentBadge(idea) {
  const count = (idea && idea.attachments && idea.attachments.length) || 0;
  if (!count) return "";
  return `<span class="attachment-badge" data-id="${escapeHtml(idea.id)}" title="${t("Anhänge anzeigen")}">📎 ${count}</span>`;
}

/**
 * Show the files of an idea in a container, with adding and removing for people
 * who may edit it. Images can also be pasted or dropped onto `dropTarget`.
 */
export function renderAttachments(container, { hass, idea, canEdit, dropTarget, onChange }) {
  let attachments = [...((idea && idea.attachments) || [])];
  let busy = false;

  const draw = () => {
    container.innerHTML = `
      <style>
        .bs-att { display: flex; flex-direction: column; gap: 8px; }
        .bs-att-grid { display: flex; flex-wrap: wrap; gap: 8px; }
        .bs-att-item { position: relative; width: 84px; height: 84px; border-radius: 10px; overflow: hidden;
          border: 1px solid var(--divider-color, rgba(127,127,127,0.3)); background: var(--secondary-background-color, rgba(127,127,127,0.1));
          display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .bs-att-item img { width: 100%; height: 100%; object-fit: cover; }
        .bs-att-file { display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 4px; text-align: center;
          font-size: 0.68rem; line-height: 1.2; color: var(--primary-text-color); word-break: break-all; }
        .bs-att-file span:first-child { font-size: 1.5rem; }
        .bs-att-del { position: absolute; top: 2px; right: 2px; width: 26px; height: 26px; border-radius: 50%; border: none;
          background: rgba(0,0,0,0.6); color: #fff; font-size: 0.8rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .bs-att-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
        .bs-att-add { min-height: 40px; padding: 0 14px; border-radius: 10px; cursor: pointer; font: inherit;
          border: 1px dashed var(--primary-color, #03a9f4); background: transparent; color: var(--primary-color, #03a9f4); }
        .bs-att-add:disabled { opacity: 0.5; cursor: progress; }
        .bs-att-hint { font-size: 0.75rem; color: var(--secondary-text-color); }
        .bs-att-error { font-size: 0.8rem; color: var(--error-color, #db4437); }
        .bs-att-empty { font-size: 0.8rem; color: var(--secondary-text-color); }
      </style>
      <div class="bs-att">
        ${attachments.length ? `<div class="bs-att-grid">${attachments.map((a) => `
          <div class="bs-att-item" data-att="${escapeHtml(a.id)}" title="${escapeHtml(a.name)} · ${formatSize(a.size || 0)}">
            ${String(a.type || "").startsWith("image/") && a.type !== "image/heic"
              ? `<img alt="${escapeHtml(a.name)}" data-img="${escapeHtml(a.id)}">`
              : `<div class="bs-att-file"><span>${a.type === "application/pdf" ? "📕" : a.type === "application/zip" ? "🗜️" : "📄"}</span><span>${escapeHtml(a.name.length > 24 ? `${a.name.slice(0, 21)}…` : a.name)}</span></div>`}
            ${canEdit ? `<button class="bs-att-del" data-del="${escapeHtml(a.id)}" title="${t("Anhang löschen")}" aria-label="${t("Anhang löschen")}">✕</button>` : ""}
          </div>`).join("")}</div>` : canEdit ? "" : `<div class="bs-att-empty">${t("Keine Anhänge.")}</div>`}
        ${canEdit ? `
          <div class="bs-att-actions">
            <button type="button" class="bs-att-add" ${busy ? "disabled" : ""}>${busy ? t("Wird hochgeladen …") : t("📎 Datei anhängen")}</button>
            <span class="bs-att-hint">${t("Bilder auch per Einfügen oder Ziehen. Nach dem Erledigen bleiben Anhänge 30 Tage.")}</span>
            <input type="file" multiple accept="${ATTACHMENT_ACCEPT}" style="display: none;">
          </div>` : ""}
        <div class="bs-att-error" style="display: none;"></div>
      </div>`;

    container.querySelectorAll("img[data-img]").forEach(async (img) => {
      try {
        img.src = await signedAttachmentUrl(hass, idea.id, img.dataset.img);
      } catch (err) {
        console.error("[Brainstorm] Could not load attachment", err);
      }
    });
    container.querySelectorAll(".bs-att-item").forEach((el) => {
      el.addEventListener("click", async (e) => {
        if (e.target.closest(".bs-att-del")) return;
        // Open the window first, so pop-up blockers see the tap
        const win = window.open("", "_blank");
        try {
          const url = await signedAttachmentUrl(hass, idea.id, el.dataset.att);
          if (win) win.location.href = url;
          else window.location.href = url;
        } catch (err) {
          if (win) win.close();
          showError(err.message);
        }
      });
    });
    container.querySelectorAll(".bs-att-del").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const att = attachments.find((a) => a.id === btn.dataset.del);
        if (!att || !window.confirm(t("„{name}“ löschen?", { name: att.name }))) return;
        try {
          const body = await attachmentRequest(hass, `${ATTACHMENT_URL}/${encodeURIComponent(idea.id)}/${encodeURIComponent(att.id)}`, { method: "DELETE" });
          attachments = body.attachments || [];
          draw();
          if (onChange) onChange(attachments);
        } catch (err) {
          showError(err.message);
        }
      });
    });
    const input = container.querySelector('input[type="file"]');
    const addBtn = container.querySelector(".bs-att-add");
    if (input && addBtn) {
      addBtn.addEventListener("click", () => input.click());
      input.addEventListener("change", () => upload([...input.files]));
    }
  };

  const showError = (message) => {
    const el = container.querySelector(".bs-att-error");
    if (!el) return;
    el.textContent = `⚠️ ${message}`;
    el.style.display = "block";
  };

  const upload = async (files) => {
    if (!canEdit || busy || !files.length) return;
    const form = new FormData();
    files.forEach((file, idx) => {
      // Pasted screenshots are all called image.png
      const name = file.name && file.name !== "image.png"
        ? file.name
        : `Screenshot ${new Date().toISOString().slice(0, 19).replace("T", " ").replace(/:/g, "-")}${idx ? `-${idx + 1}` : ""}.png`;
      form.append("file", file, name);
    });
    busy = true;
    draw();
    try {
      const body = await attachmentRequest(hass, `${ATTACHMENT_URL}/${encodeURIComponent(idea.id)}`, { method: "POST", body: form });
      attachments = body.attachments || attachments;
      busy = false;
      draw();
      if (onChange) onChange(attachments);
    } catch (err) {
      busy = false;
      draw();
      showError(err.message);
    }
  };

  if (dropTarget) {
    // The dialog body is reused, so the listeners of the last idea must go
    if (dropTarget._bsAttachments) dropTarget._bsAttachments.abort();
    dropTarget._bsAttachments = null;
  }
  if (canEdit && dropTarget) {
    const controller = new AbortController();
    dropTarget._bsAttachments = controller;
    const { signal } = controller;
    dropTarget.addEventListener("paste", (e) => {
      const files = [...((e.clipboardData && e.clipboardData.files) || [])];
      if (!files.length) return;
      e.preventDefault();
      upload(files);
    }, { signal });
    dropTarget.addEventListener("dragover", (e) => {
      if (e.dataTransfer && [...e.dataTransfer.types].includes("Files")) e.preventDefault();
    }, { signal });
    dropTarget.addEventListener("drop", (e) => {
      const files = [...((e.dataTransfer && e.dataTransfer.files) || [])];
      if (!files.length) return;
      e.preventDefault();
      upload(files);
    }, { signal });
  }

  draw();
}
