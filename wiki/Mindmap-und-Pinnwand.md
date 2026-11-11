🏠 [Start](Home) · 🇬🇧 [English version](Mind-Map-and-Pinboard)

## Brainstorm Mindmap Card (Dedizierte interaktive Gedankenlandkarte)
Ideal für reguläre Dashboard-Karten oder als **Panel-Ansicht (Vollbild)** auf Tablets und Monitoren:
```yaml
type: custom:brainstorm-mindmap-card
title: Brainstorm Mindmap
height: 600px               # Optionale Höhe (z.B. 550px, 600px, 100%)
default_category: Inbox     # Standard-Kategorie beim Laden (oder 'all')
map_template: standard      # Aussehen: standard, clean, sketch oder neon
show_export_btn: true       # 🖼️ Map als SVG oder PNG speichern
```
*Tipp:* Klicke oben rechts auf das Vollbild-Symbol `⛶`, um die Mindmap jederzeit auf den gesamten Bildschirm zu vergrößern!

**Aussehen mit Vorlagen:** Im Karten-Editor wählst du eine Vorlage und kannst Form, Linien und Farben einzeln anders einstellen. `template` heißt: wie die Vorlage.

| Option | Werte | Bedeutung |
| :--- | :--- | :--- |
| `layout` | `radial`, `tree`, `org`, `outline`, `pin`, `kanban`, `timeline`, `matrix` | Ansicht der Notizen: rund um die Mitte, Baum, Organigramm, Gliederung, Pinnwand, Kanban nach Status, Zeitleiste nach Fälligkeit oder Eisenhower-Matrix. Der Knopf unten rechts schaltet ebenfalls um und merkt sich die Wahl im Browser. Standard `radial`. |
| `map_template` | `standard`, `clean`, `sketch`, `neon` | **Standard:** Karten, Kurven, Kategoriefarben. **Klar:** Rechtecke, eckige Linien. **Skizze:** Kapseln, gestrichelt, Pastell. **Neon:** dunkler Hintergrund mit leuchtenden Rändern. |
| `node_shape` | `template`, `card`, `cloud`, `bubble`, `thought`, `pill`, `rect`, `ellipse`, `hexagon`, `note`, `underline` | Form der Notizen: Karte, Wolke, Sprechblase, Gedankenblase, Kapsel, Rechteck, Ellipse, Sechseck, Notizzettel oder unterstrichener Text. Der Zipfel der Sprechblase und die Bläschen der Gedankenblase zeigen zur übergeordneten Notiz oder zur Mitte; die Linien treffen eine unterstrichene Notiz am Ende ihres Strichs. Eine Notiz kann ihre eigene Form haben (Bearbeiten-Dialog oder `shape` von `brainstorm.update_idea`). |
| `voice_bubbles` | `true`, `false` | Notizen, die Alexa, Siri oder Assist gesagt wurden, erscheinen als Sprechblase, außer sie haben eine eigene Form. Standard `true`. |
| `line_style` | `template`, `curve`, `straight`, `angled`, `dashed` | Linien: Kurve, gerade, eckig oder gestrichelt. |
| `color_scheme` | `template`, `category`, `pastel`, `mono`, `neon` | Farben: Kategoriefarben, Pastell (zart eingefärbt), einfarbig oder Neon. |

## ✨ Funktionen im Überblick

- Interaktives Radial-Synapsen-Layout für eine visuelle Gedankenlandkarte.
- Zentraler Knotenpunkt (Inbox / Fokus-Kategorie) mit edlem, transparentem Brainstorm-Logo im Hintergrund.
- Notizen dargestellt als charmante Gedankenwolken mit gestrichelten Konturen und Kategorie-Farbcodes.
- Organische Bézier-Verbindungslinien, die beim Überfahren aufleuchten.
- Frei verschiebbare Notizen per Drag & Drop (auf Desktop und Touchscreens).
- **Äste:** Unteraufgaben hängen an ihrer Elternidee, ihre Linien gehen von dort statt von der Mitte aus. 🌿 an einer Notiz legt eine Unteridee an.
- **Gespeicherte Anordnung:** In einer einzelnen Liste behalten verschobene Notizen ihren Platz auf allen Geräten. Eine Elternidee nimmt ihre Unteraufgaben mit. Die Übersicht aller Listen ordnet sich selbst.
- **Zweige einklappen:** Der runde Knopf an einer Notiz mit Unteraufgaben klappt ihren Zweig zu und zeigt, wie viele Notizen darin stecken. Jedes Gerät merkt sich, was eingeklappt ist.
- **Anordnung als Baum:** Jeder Zweig bekommt seinen eigenen Ausschnitt des Kreises, Linien kreuzen sich nicht. 🪄 setzt von Hand platzierte Notizen wieder an ihren automatischen Platz.
- **Tastatur:** Ein Klick wählt eine Notiz aus. **Tab** legt eine Unteraufgabe an, **Enter** eine Notiz daneben, **Entf** löscht nach Rückfrage, **F2** oder Doppelklick bearbeitet den Text. Mit den Pfeiltasten gehst du die Zweige entlang: links zum Oberpunkt, rechts zur ersten Unteraufgabe, hoch und runter zu den Nachbarn.
- **Direkt bearbeiten:** Ein Klick auf den Text öffnet ihn gleich in der Wolke. **Enter** speichert, **Umschalt+Enter** macht eine neue Zeile, **Esc** bricht ab. Termin, Priorität und Echos stellst du weiter mit ✏️ im Dialog ein.
- **Mehrere Notizen auswählen:** **Umschalt+Ziehen** auf der leeren Map zieht einen Rahmen, **Umschalt+Klick** oder **Strg+Klick** nimmt eine Notiz dazu oder wieder heraus. Am Handy oder Tablet tippst du unten rechts auf ⬚ und ziehst dann einen Rahmen oder tippst Notizen an. Ziehst du eine ausgewählte Notiz, wandern alle mit, samt Unteraufgaben. Die Leiste über der Map hakt sie ab, verschiebt sie in eine andere Kategorie oder löscht sie nach Rückfrage, ein Rückgängig nimmt den ganzen Schritt zurück. **Esc** oder ✕ hebt die Auswahl auf.
- **Rückgängig:** **Strg+Z** oder der Knopf ↶ unten rechts nimmt die letzten Schritte dieser Sitzung zurück: neue Notizen, Textänderungen, Erledigt, Priorität, Kategorie, Verschieben, Neu ordnen und auch Löschen. Gelöschte Notizen hält Home Assistant bis zum nächsten Neustart bereit.
- **Suchen, Filtern und Tags (v1.8.0):** 🔍 oben rechts, oder **/** und **Strg+F** auf der Map, öffnet eine Suchleiste. Treffer bleiben hell, ihre übergeordneten Punkte halb, der Rest der Map tritt zurück. Chips filtern nach Priorität, *Überfällig*, *7 Tage*, *In Arbeit* und den Tags der Liste. **Enter** springt von Treffer zu Treffer und klappt seinen Zweig auf. `#garten` in einer Notiz oder *„Hashtag Garten“* gesagt zeigt das Tag als Chip; ein Tipp darauf filtert die Map. Siehe [Maus, Finger, Tastatur](#mindmap-maus-finger-tastatur).
- **Marker und Fortschritt (v1.8.1):** ❓ 💡 ⚠️ 💰 ⭐ 🚩 ✅ ⛔ ⏳ ❤️ als kleine Zeichen an einer Notiz, in beiden Karten, wählbar im Bearbeiten-Dialog und filterbar in der Suchleiste. Notizen mit Unteraufgaben zeigen einen Ring mit *3/5*, der sich wie bei MindManager aus den Unteraufgaben füllt; ohne Unteraufgaben schaltet ein Tipp auf den Ring in Viertelschritten weiter.
- **Fokus und Ebenen (v1.8.2):** 🎯 an einer Notiz mit Unteraufgaben, oder **F4**, zeigt nur diesen Zweig mit der Notiz in der Mitte; eine Brotkrumenleiste über der Map führt zurück, **Umschalt+F4** oder **Esc** gehen eine Stufe hoch. ∞ unten rechts, oder die Tasten **1–9**, klappen die Map bis zu so vielen Ebenen ein, **0** zeigt wieder alle.
- **Querverbindungen, Rahmen und Callouts (v1.8.2):** 🔗 an einer Notiz, oder **L**, und dann ein Tipp auf eine andere Notiz zieht einen gestrichelten Pfeil zwischen beiden, auch über Zweige hinweg. Ein Tipp auf die Linie gibt ihr eine Beschriftung oder macht sie *blockierend*: Das Ziel wird grau mit ⛔ *Wartet*, bis die erste Notiz erledigt ist. Mehrere Notizen auswählen und ▢ *Rahmen* tippen legt einen benannten Rahmen um sie. Ein *Callout* ist eine kurze Anmerkung in einer Sprechblase über der Notiz. Beides geht auch im Bearbeiten-Dialog, und die Listenkarte zeigt es ebenfalls.
- **Nummerierung und Sortieren (v1.8.3):** Im ✏️ Bearbeiten-Dialog einer Notiz mit Unteraufgaben setzt *Unterpunkte nummerieren* 1., 1.1 … oder a), b) oder I., II. davor, in beiden Karten. *Unterpunkte sortieren* ordnet sie sofort nach Titel, Priorität, Fälligkeit oder Alter; **S** auf der Map öffnet dieselbe Auswahl, ohne Auswahl für die Hauptnotizen. ↶ macht es rückgängig.
- **Gliederung exportieren und einfügen (v1.8.4):** 🖼️ speichert die Map auch als Markdown-Gliederung, OPML oder FreeMind-`.mm` (öffnet sich in Freeplane, XMind, MindManager). *Gliederung einfügen* macht aus einer eingefügten Liste oder einer Datei (`.md`, `.txt`, `.opml`, `.mm`) einen Zweig mit Notizen, im Fokus unter der Fokus-Notiz.
- **Brainstorm-Modus (v1.8.5):** ⚡ oder **B** öffnet eine Schnelleingabe mit Timer von 3 bis 15 Minuten. Jedes Enter ist sofort eine Notiz und erscheint als bunter Zettel; ↶ nimmt die ganze Runde wieder heraus.
- **Ansichten (v1.8.6–v1.8.8):** Der Ansichts-Knopf unten rechts zeigt die Notizen ◎ rund um die Mitte, als ⇶ Baum, ⊤ Organigramm, ☰ eingerückte Gliederung, ▥ Kanban nach Status (offen, in Arbeit, wartet, erledigt), 📅 Zeitleiste nach Fälligkeit (überfällig, heute, morgen, diese Woche, später, ohne Datum) oder ⊞ Eisenhower-Matrix (sofort erledigen, einplanen, abgeben, später oder gar nicht). Auf den Boards ändert das Ziehen in eine andere Spalte Status, Fälligkeit oder Priorität, ↶ nimmt es zurück. Die Wahl merkt sich der Browser; `layout` legt den Standard fest.
- **Übersicht / Minimap (v1.10.6):** 🗺️ unten rechts oder **M** zeigt unten links die ganze Map im Kleinen, in den Kategoriefarben, mit dem sichtbaren Ausschnitt als Rahmen. Tippen oder Ziehen darin springt dorthin. Auf breiten Karten ist sie anfangs offen, am Handy zu; jeder Browser merkt sich die Wahl. Funktioniert in allen Ansichten, auch auf den Boards. `show_minimap: false` blendet sie samt Knopf aus.
- **Präsentationsmodus (v1.8.10):** **P** (oder ▶ in der Ansichtswahl) zeigt die Map im Vollbild und geht sie Notiz für Notiz durch, Ast für Ast, mit der Beschreibung darunter. → / Leertaste für die nächste Notiz, ← zurück, Esc beendet.
- **Wiederkehrende Aufgaben (v1.8.15):** *Wiederholen* im Bearbeiten-Dialog beider Karten: jeden Tag, jeden Werktag, jede Woche, alle 2 Wochen, jeden Monat oder jedes Jahr. Abgehakt kommt die Notiz sofort wieder, fällig zum nächsten Termin, mit ihren Angaben und wieder offenen Unteraufgaben; die erledigte Runde bleibt unter *Erledigt*. Spät abgehakt überspringt sie verpasste Termine. Wird die erledigte Runde wieder aktiviert, verschwindet die neue. Wiederkehrende Notizen zeigen 🔁. Aktion: `repeat` in `brainstorm.update_idea`.
- **PDF-Export (v1.8.14):** 🖼️ ➔ *PDF* speichert ein PDF mit dem Bild der Map auf der ersten Seite und danach allen Notizen als Gliederung mit Beschreibung, fertig zum Drucken oder Verschicken. *PDF (nur Gliederung)* lässt das Bild weg. Es entsteht im Browser, nichts verlässt Home Assistant.
- **Bilder in Notizen (v1.8.13):** Das erste angehängte Bild einer Notiz (📎 im Bearbeiten-Dialog, auch per Einfügen oder Ziehen) erscheint direkt in ihr auf der Map, so sind Moodboard oder Skizze auf einen Blick zu sehen. Antippen öffnet es groß. `show_images: false` schaltet es ab.
- **Regeln (v1.8.12):** 🎨 in der Suchleiste oder **R** macht aus dem aktuellen Filter eine Regel mit Farbe und Zeichen, wie SmartRules in MindManager: *alles 🔥 Dringende rot*, *#garten grün mit ⭐* … Jede passende Notiz wird in der Map und in der Listenkarte eingefärbt, die erste passende Regel gilt. Regeln lassen sich ausschalten, nach oben schieben, bearbeiten und löschen (↶ holt eine zurück). Sie liegen bei deinem Home-Assistant-Benutzer und gelten so auf jedem Gerät.
- **Freihand zeichnen (v1.11.7):** 🖍️ in den Bedienknöpfen oder **D** legt einen Stift über die runde Map einer Kategorie: freie Striche, ➚ Pfeile und ◯ Kreise in sechs Farben und drei Stärken, 🧽 radiert angetippte Striche weg, 🗑️ löscht alles, ↶ nimmt jeden Schritt zurück. Die Zeichnung bleibt pro Kategorie gespeichert, ist auf jedem Gerät zu sehen und kommt mit ins Bild, ins PDF und in den JSON-Export. Esc oder ✓ beendet das Zeichnen.
- **Pinnwand (v1.11.6):** 📌 in der Ansichtswahl zeigt die Notizen einer Kategorie als farbige Haftzettel ohne Baum und Linien, auch die Unterpunkte. Zieh einen Zettel irgendwohin, dort bleibt er, auf jedem Gerät; noch nicht platzierte Zettel stehen in Reihen darunter. Die Farbe (gelb, rosa, grün, blau, orange, lila) wählst du unter ⋯, Gruppen bekommen wie auf der Map einen Rahmen (▢ in der Auswahlleiste). ↶ nimmt Verschieben und Farbe zurück.
- **Inhaltsvorlagen (v1.8.8):** 🖼️ ➔ *Gliederung einfügen* hat fertige Zweige wie SWOT-Analyse, Pro und Contra, Projektplan, Wochenplan oder Packliste für die Reise. Text anpassen, dann einfügen.
- **Vorlagen und Bild-Export:** Vier Vorlagen (Standard, Klar, Skizze, Neon) bestimmen Form, Linien und Farben. Zehn Formen stehen bereit, von Karte, Wolke, Sprech- und Gedankenblase bis Ellipse, Sechseck, Notizzettel und unterstrichenem Text, für die ganze Map oder pro Notiz. 🖼️ oben rechts speichert die Map als SVG oder PNG.
- Stufenloser Zoom & Pan per Mausrad, Pinch-Geste oder Steuerungsbuttons.
- **Vollbild-Modus (`⛶`):** Per Knopfdruck oder Dashboard-Einbindung als beeindruckendes Vollbild-Erlebnis (ESC zum Schließen).
- Direkte Aktionen an jeder Gedankenwolke (Erledigen, Text editieren, Kategorie wechseln, Löschen).

## Mindmap: Maus, Finger, Tastatur

**Maus und Finger**

| Aktion | So geht es |
|---|---|
| Verschieben | Notiz ziehen |
| Unterpunkt anlegen | Notiz auswählen und **Tab** |
| Text ändern | Doppelklick auf die Notiz |
| Mehrere auswählen | **Umschalt** oder **Strg** + Klick, mit gedrückter **Umschalt**-Taste einen Rahmen ziehen, oder ⬚ und dann Rahmen ziehen (am Handy) |
| Zoomen | Mausrad oder zwei Finger |
| Fläche bewegen | leere Fläche ziehen |
| Zweig ein-/ausklappen | Knopf am Ast, oder **→** auf einem eingeklappten Punkt |
| Als Bild oder Gliederung speichern, Gliederung einfügen | 🖼️ |
| Vollbild | ⛶ |
| Suchen und filtern | 🔍, oder **/** bzw. **Strg+F** auf der Map |
| Nach einem Tag filtern | auf ein #Tag in einer Notiz tippen |
| Marker setzen | ✏️ Bearbeiten ➔ *Marker*, ein Tipp auf einen Marker an der Notiz filtert danach |
| Fortschritt weiterschalten | auf den Ring an einer Notiz ohne Unteraufgaben tippen: 0 ➔ 25 ➔ 50 ➔ 75 ➔ 100 % |
| Nur einen Zweig zeigen | 🎯 an der Notiz oder **F4**, zurück über die Brotkrumen, **Umschalt+F4** oder **Esc** |
| Ebenen ein- und ausklappen | ∞ unten rechts: 1 ➔ 2 ➔ 3 ➔ alle, oder die Tasten **1–9**, **0** = alle |
| Abstimmen | 🗳️ unten rechts oder **V**: Kategorie, Stimmen pro Person und *verdeckt* wählen, dann − / + an den Notizen; *Beenden* in der Leiste oben zeigt die Rangliste |
| Reagieren | ⋯ an der Notiz ➔ 👍 ❤️ 😂 ❗; ein Tipp auf eine Reaktion schaltet die eigene um |
| Kommentieren | ⋯ an der Notiz ➔ 💬 *Kommentare*, oder auf 💬 an der Notiz tippen; `@Name` benachrichtigt die Person |
| Übersicht (Minimap) | 🗺️ unten rechts oder **M**; in der Übersicht unten links tippen oder ziehen springt dorthin |
| Zwei Notizen verbinden | 🔗 an der Notiz oder **L**, dann die Ziel-Notiz antippen; zwei ausgewählte Notizen ➔ 🔗 *Verbinden* |
| Verbindung beschriften oder löschen | auf die gestrichelte Linie tippen |
| Rahmen um Notizen | Notizen auswählen ➔ ▢ *Rahmen*, oder ✏️ Bearbeiten ➔ *Rahmen*; ein Tipp auf den Rahmennamen benennt um |
| Callout | ✏️ Bearbeiten ➔ *Callout* |
| Brainstorm: schnell viele Ideen sammeln | ⚡ unten rechts oder **B** |
| Baum, Organigramm, Gliederung, Pinnwand, Kanban, Zeitleiste oder Eisenhower-Matrix | Ansichts-Knopf über ⚡ |
| Unterpunkte nummerieren | ✏️ Bearbeiten ➔ *Unterpunkte nummerieren*: 1., 1.1 · a) · I. |
| Unterpunkte sortieren | ✏️ Bearbeiten ➔ *Unterpunkte sortieren*, oder **S** (ohne Auswahl: die Hauptnotizen) |

**Bilder:** Das erste Bild unter den Anhängen einer Notiz erscheint in der Notiz. Antippen öffnet es groß. Ein Bild kommt per 📎 im Bearbeiten-Dialog dazu, oder per Einfügen oder Ziehen dorthin.

**Regeln:** In der Suchleiste einen Filter einstellen, dann 🎨 (oder **R**) ➔ *Aktuellen Filter als Regel*. Name, eine von neun Farben und ein Zeichen wählen. Jede passende Notiz bekommt Farbe und Zeichen, in der Map und in der Listenkarte; passen mehrere Regeln, gilt die obere. In der Regelliste schaltet das Kästchen eine Regel an oder aus, ↑ schiebt sie nach oben, ✎ bearbeitet sie und 🗑️ löscht sie (↶ holt sie zurück). Regeln gehören zu deinem Home-Assistant-Benutzer und gelten auf jedem Gerät.

**Suchen und filtern:** 🔍 öffnet eine Leiste über der Map. Alle getippten Wörter müssen im Titel, in der Beschreibung, im Ergebnis oder bei der Person vorkommen; `#gar` findet Notizen mit einem Tag, das mit *gar* beginnt. Die Chips filtern nach Priorität (🔥 🔴 🟡 🟢), nach *Überfällig* oder *7 Tage*, nach *In Arbeit* und nach den Tags der Liste, mit ihrer Anzahl. Passende Notizen bleiben hell, ihre übergeordneten Punkte halb, der Rest tritt zurück. Ein eingeklappter Zweig mit Treffern zeigt seinen Knopf farbig. **Enter** springt zum nächsten Treffer und klappt seinen Zweig auf, **Umschalt+Enter** zum vorigen, **Esc** leert die Suche und schließt danach die Leiste, das hebt auch den Filter auf.

**Tags:** `#garten` oder `#3d-druck` irgendwo in Titel oder Beschreibung schreiben, oder Alexa bzw. Assist *„Hashtag Garten“* sagen. Ein Tag braucht einen Buchstaben, `#1` bleibt also eine Zahl und eine Farbe wie `#ff7800` eine Farbe. Tags aus `tags:` bei `brainstorm.add_idea` zählen auch.

**Marker:** Kleine Zeichen an einer Notiz, wie bei MindManager: ❓ Frage, 💡 Idee, ⚠️ Achtung, 💰 Geld, ⭐ Stern, 🚩 Flagge, ✅ Haken, ⛔ Blockiert, ⏳ Wartet, ❤️ Herz. Du setzt sie im Bearbeiten-Dialog beider Karten oder mit `markers` bei `brainstorm.update_idea`. Die Suchleiste bekommt für jeden Marker der Liste einen Chip.

**Fortschritt:** Eine Notiz mit Unteraufgaben zeigt einen Ring mit *erledigt/gesamt*, z. B. `3/5`. Der Ring füllt sich wie bei MindManager: Erledigte Unteraufgaben zählen 100 %, eine Unteraufgabe mit eigenen Unteraufgaben den Durchschnitt davon, jede andere ihren eigenen Fortschritt. Bei einer Notiz ohne Unteraufgaben stellst du den Fortschritt selbst ein, in Viertelschritten im Bearbeiten-Dialog, per Tipp auf den Ring oder mit `progress` bei `brainstorm.update_idea`. Bei 100 % wird der Ring grün.

**Fokus und Ebenen:** Bei großen Maps zeigt 🎯 (oder **F4**) nur den Zweig einer Notiz, die Notiz rückt in die Mitte. Über der Map steht der Weg dorthin, ein Tipp auf einen Eintrag springt zurück, ✕ zeigt wieder die ganze Map. Neue Notizen landen im Fokus unter der Fokus-Notiz. ∞ unten rechts klappt alle Zweige ab der gewählten Ebene ein, die Tasten **1** bis **9** tun das direkt, **0** klappt alles wieder auf.

**Querverbindungen:** Die Linien der Map zeigen, was wozu gehört. Eine Querverbindung verbindet zwei beliebige Notizen, auch aus verschiedenen Zweigen, mit einem gebogenen, gestrichelten Pfeil. 🔗 an der Notiz (oder **L**) startet, ein Tipp auf das Ziel beendet, **Esc** bricht ab. Ein Tipp auf die Linie öffnet einen Dialog für eine Beschriftung wie *braucht* oder *siehe auch*. Mit dem Haken *blockiert* wird die Verbindung rot: Die Ziel-Notiz wird grau und zeigt ⛔ *Wartet*, bis die erste Notiz erledigt ist. Das Abzeichen erscheint auch in der Listenkarte.

**Nummerierung und Sortieren:** Im Bearbeiten-Dialog einer Notiz mit Unteraufgaben nummeriert *Unterpunkte nummerieren* alles darunter, wie in MindManager: 1., 1.1, 1.2 … oder a), b) oder I., II. Eine Unteraufgabe kann eine eigene Art wählen, die dann für ihren Zweig gilt. Die Nummern stehen in beiden Karten vor dem Text und passen sich an, wenn Punkte dazukommen oder wandern. *Unterpunkte sortieren* ordnet sofort nach Titel (A → Z oder Z → A), Priorität, Fälligkeit oder Alter. Die übrigen Notizen bleiben an ihrem Platz, ↶ macht es rückgängig. Auf der Map öffnet **S** dieselbe Auswahl, ohne ausgewählte Notiz für die Hauptnotizen der Kategorie. Bei frei verschobenen Notizen ordnet 🪄 die Map danach passend neu.

**Brainstorm-Modus:** ⚡ unten rechts (oder **B**) öffnet ein großes Eingabefeld mit Timer: 3, 5, 10 oder 15 Minuten oder ohne Zeit. Die Uhr startet mit der ersten Idee. Jede Idee wird mit **Enter** sofort als Notiz gespeichert, das Feld ist gleich wieder frei, und die Idee erscheint als bunter Zettel darunter. ✕ auf einem Zettel löscht sie wieder. Die Ideen landen in der gewählten Kategorie, im Fokus unter der Fokus-Notiz, unter *Alle* in der passenden Kategorie. Nach *Fertig* nimmt ↶ alle gesammelten Ideen auf einmal heraus, 🪄 ordnet die Map neu. Danach lassen sie sich per Ziehen in Zweige sortieren.

**Layouts:** Der Knopf über ⚡ öffnet die Ansichtswahl: ◎ rund um die Mitte, ⇶ Baum nach rechts (Hauptnotizen in einer Spalte, Unterpunkte rechts daneben), ⊤ Organigramm nach unten und ☰ Gliederung (eine Notiz pro Zeile, Unterpunkte eingerückt darunter). Im Baum und im Organigramm steht eine Notiz mittig zu ihren Unterpunkten, und die Linien verlaufen rechtwinklig. Die Wahl merkt sich dieser Browser; die Kartenoption `layout` legt den Standard fest. Verschobene Notizen bleiben, wo du sie hingelegt hast, bis du das Layout wieder wechselst.

**Wer ist da:** Oben links stehen die Personen, die dieselbe Liste gerade offen haben, als Kreis mit Initialen. Bearbeitet jemand eine Notiz, hat der Kreis einen Ring und an der Notiz hängt ✏️ mit dem Namen. Gespeichert wird davon nichts.

**Zeichnen:** 🖍️ oder **D** öffnet oben eine Leiste mit Stift, Pfeil, Kreis und Radierer, sechs Farben und drei Stärken. Ziehen zeichnet, der Radierer löscht angetippte Striche, ↶ nimmt jeden Schritt zurück, Esc oder ✓ beendet. Das geht auf der runden Map einer einzelnen Kategorie; dort bleibt die Zeichnung gespeichert und kommt mit ins Bild und in den Export.

**Pinnwand:** 📌 zeigt die Notizen als farbige Haftzettel, ohne Baum und Linien. Zieh einen Zettel irgendwohin, dort bleibt er auf jedem Gerät; noch nicht platzierte stehen in Reihen darunter. Die Farbe wählst du unter ⋯, für Gruppen markierst du Zettel und legst mit ▢ einen Rahmen darum.

**Boards:** Drei weitere Ansichten zeigen die Notizen in Spalten statt als Map. **▥ Kanban** sortiert nach Status: *Offen*, *In Arbeit*, *Wartet* (blockierende Verbindung) und *Erledigt*. Zieh eine Notiz nach *In Arbeit*, um sie zu markieren, zurück nach *Offen*, um die Markierung zu entfernen, auf *Erledigt*, um sie abzuhaken. **📅 Zeitleiste** sortiert nach Fälligkeit: *Überfällig*, *Heute*, *Morgen*, *Diese Woche*, *Später*, *Ohne Datum*. Ziehen setzt das Datum und behält die Uhrzeit (09:00 bei einer Notiz ohne); *Ohne Datum* entfernt es. **⊞ Eisenhower-Matrix** sortiert nach Wichtigkeit (Priorität 🔥 oder 🔴) und Dringlichkeit (🔥 oder fällig in drei Tagen): *Sofort erledigen*, *Einplanen*, *Abgeben*, *Später oder gar nicht*. Ziehen setzt die Priorität; *Abgeben* gibt einer Notiz ohne nahes Datum eines für morgen. Spalten, die sich aus etwas anderem ergeben (*Wartet*, *Überfällig*, ein nahes Datum), erreicht man nicht durch Ziehen; ein kurzer Hinweis sagt warum. ↶ nimmt jeden Zug zurück.

**Präsentation:** **P** (oder ▶ *Präsentieren* in der Ansichtswahl) macht die Map zur Diashow. Sie öffnet sich im Vollbild ohne Knöpfe, zuerst mit der ganzen Map, dann Notiz für Notiz in der Reihenfolge der Äste. Die Ansicht zoomt auf die Notiz, Oberpunkt und Unterpunkte bleiben halb sichtbar, und eine Leiste unten zeigt den Weg, den Titel und die Beschreibung. **→**, **Leertaste** oder **Enter** gehen weiter, **←** zurück, **Pos1** zum Überblick, **Esc** beendet. Eingeklappte Äste öffnen sich unterwegs und klappen am Ende wieder zu. Das geht in jeder Ansicht, auch im Fokus.

**KI-Hilfe:** Mit einer KI-Aufgaben-Entität (Brainstorm Hub ➔ Konfigurieren ➔ KI) schlägt ✨ an einer Notiz Unteraufgaben vor. An einer Notiz mit Unterpunkten fragt ✨ zuerst: *Unteraufgaben vorschlagen* oder *Ast zusammenfassen*. Die Zusammenfassung umfasst die Notiz und alles darunter, auch Erledigtes, in zwei bis vier Sätzen; du kannst sie ändern, kopieren oder vor die Beschreibung setzen. **Z** (oder *✨ Lose Ideen zuordnen* am Ende einer Brainstorm-Runde) schaut sich die Hauptnotizen der Kategorie ohne Unterpunkte an und schlägt vor, wohin jede gehört. Nimm den Haken weg bei allem, was bleiben soll; *Übernehmen* hängt den Rest um, ↶ macht es rückgängig. Zur KI gehen nur die Notizen dieser Kategorie. **G** (oder ✨ *Map aus Thema erzeugen* auf einer leeren Map, ✨ *Mit KI erzeugen* unter 🖼️ ➔ *Gliederung einfügen*) macht aus einem Thema oder einem eingefügten Text eine Map mit bis zu drei Ebenen; in der Vorschau abhaken und Texte ändern, dann übernehmen. Ein weggenommener Haken lässt die Unterpunkte nach oben rücken.

**Export und Import:** 🖼️ speichert die Map als Bild (SVG, PNG), als **PDF** (das Bild der Map auf der ersten Seite, danach alle Notizen als Gliederung mit Beschreibung; *PDF (nur Gliederung)* ohne das Bild; Emojis fallen weg) oder als Gliederung: **Markdown** (eine verschachtelte Liste, Beschreibungen als `>`-Zeile), **OPML** (für Gliederungsprogramme wie Workflowy, OmniOutliner oder Logseq) und **FreeMind** (`.mm`, öffnet sich in Freeplane, XMind und MindManager). Die Gliederung enthält alle Notizen der Map, auch eingeklappte; im Fokus nur den Zweig. Unter *Gliederung einfügen* tippst oder kopierst du eine Liste hinein, eine Zeile pro Notiz, Unterpunkte eingerückt oder mit `-`, `*`, `1.` und Überschriften `#`. Oder du wählst eine Datei (`.md`, `.txt`, `.opml`, `.mm`). `- [x]` legt den Punkt gleich als erledigt an. Die Notizen landen als Hauptnotizen der Kategorie, im Fokus unter der Fokus-Notiz. Höchstens 300 Notizen auf einmal, ↶ nimmt alle wieder heraus. **Inhaltsvorlagen:** Über dem Textfeld stehen fertige Zweige: SWOT-Analyse, Pro und Contra, Projektplan, Wochenplan, Feier, Reise (mit Packliste), Rückblick und Raum renovieren. Ein Tipp schreibt die Vorlage ins Feld; Zeilen ändern oder ergänzen, dann *Einfügen*. Für Automationen gibt es den Dienst `brainstorm.import_outline`.

**Rahmen und Callouts:** Ein Rahmen ist ein gestricheltes Rechteck mit Namen um mehrere Notizen, etwa *Phase 1* oder *Erdgeschoss*. Notizen mit demselben Rahmennamen teilen sich einen Rahmen. Ein Callout ist eine kurze Anmerkung in einer Sprechblase über der Notiz, für Dinge wie *Farbe noch offen*. Die Listenkarte zeigt den Rahmen als Chip und den Callout unter dem Text.

**Tastatur** (eine Notiz ist ausgewählt)

| Taste | Wirkung |
|---|---|
| **Tab** | neuer Unterpunkt |
| **Enter** | neuer Punkt daneben (ohne Auswahl: neue Notiz) |
| **F2** | Text bearbeiten |
| **Entf** / **Rücktaste** | löschen (mit Rückfrage, auch für mehrere) |
| **←** | zum übergeordneten Punkt |
| **→** | zum ersten Unterpunkt, eingeklappten Zweig öffnen |
| **↑** / **↓** | zum vorherigen / nächsten Geschwister |
| **F4** / **Umschalt+F4** | nur diesen Zweig zeigen / eine Ebene zurück |
| **1**–**9** / **0** | Ebenen bis 1–9 zeigen / alle Ebenen |
| **L** | Querverbindung zu einer anderen Notiz ziehen |
| **B** | Brainstorm-Modus |
| **S** | Unterpunkte sortieren (ohne Auswahl: Hauptnotizen) |
| **Z** | KI: lose Ideen zuordnen |
| **K** | KI: lose Notizen nach Themen gruppieren |
| **D** | Zeichnen: Stift, Pfeil, Kreis und Radierer über der Map |
| **G** | KI: Map aus Thema oder Text erzeugen |
| **R** | Regeln: Notizen färben, die zu einem gespeicherten Filter passen |
| **M** | Übersicht (Minimap) ein/aus |
| **V** | Abstimmung starten oder beenden |
| **P** | Präsentationsmodus |
| **Esc** | Auswahl aufheben, im Fokus eine Ebene zurück, beim Verbinden abbrechen |
| **Strg+Z** | rückgängig |

Im Textfeld: **Enter** speichert, **Umschalt+Enter** macht eine neue Zeile, **Esc** bricht ab.

## ⚙️ Kartenoptionen der Mindmap (`brainstorm-mindmap-card`)

```yaml
type: custom:brainstorm-mindmap-card
map_template: sketch    # standard, clean, sketch, neon
layout: kanban          # radial, tree, org, outline, kanban, timeline, matrix
node_shape: thought     # überschreibt die Vorlage
line_style: curve
color_scheme: pastel
height: 75vh
default_category: Projekte
```

**Vorlagen** setzen Form, Linien und Farben auf einmal:

| `map_template` | Form | Linien | Farben |
|---|---|---|---|
| `standard` | Karte | geschwungen | Kategorie |
| `clean` | Rechteck | eckig | Kategorie |
| `sketch` | Pille | gestrichelt | Pastell |
| `neon` | Pille | geschwungen | Neon |

Jeder Teil lässt sich einzeln überschreiben, `template` heißt „wie die Vorlage“:

- `node_shape`: `card`, `cloud` (Wolke), `bubble` (Sprechblase), `thought` (Gedankenblase), `pill`, `rect`, `ellipse`, `hexagon` (Sechseck), `note` (Notizzettel), `underline` (unterstrichen)
- `line_style`: `curve`, `straight`, `angled`, `dashed`
- `color_scheme`: `category`, `pastel`, `mono`, `neon`

Pro Notiz kannst du die Form auch im Bearbeiten-Dialog wählen oder per Dienst setzen (`node_shape` bei `brainstorm.update_idea`).

| Option | Standard | Bedeutung |
|---|---|---|
| `title` | Brainstorm Mindmap | Titel |
| `level` | wie in den Einstellungen | Bedienstufe nur dieser Karte, siehe [4.0](Einstellungen#bedienstufe) |
| `height` | `calc(100vh - 32px)` | Höhe, z. B. `600px` oder `75vh` |
| `voice_bubbles` | `true` | Sprachnotizen als Sprechblase |
| `default_category` | `all` | Kategorie im Fokus |
| `show_toolbar` | `true` | Werkzeugleiste mit Filtern |
| `show_logo` | `true` | Logo |
| `show_bulb_watermark` | `true` | leuchtende Glühbirne in der Mitte |
| `show_grid` | `true` | Punktraster |
| `show_controls` | `true` | Zoom und Zentrieren |
| `show_add_btn` | `true` | „+ Idee“ |
| `show_export_btn` | `true` | 🖼️ Als Bild oder Gliederung speichern, Gliederung einfügen |
| `show_filter` | `true` | 🔍 Suchen und filtern |
| `show_images` | `true` | erstes Bild der Anhänge in der Notiz |
| `show_minimap` | `true` | Übersicht (Minimap) und ihr Knopf 🗺️ |
| `show_fullscreen_btn` | `true` | ⛶ Vollbild |
| `show_color_toggle` | `true` | 🎨/🌈 |
| `hide_empty_categories` | `true` | leere Kategorien ausblenden |
| `color_mode`, `sensor`, `show_last_alexa`, `last_alexa_entity` | | wie bei der Listenkarte |
