<div align="center">

# 🧠 Brainstorm Hub für Home Assistant

**[🇩🇪 Deutsch](README_de.md)** &nbsp;|&nbsp; **[🇬🇧 English](README.md)**

[![German Docs](https://img.shields.io/badge/Sprache-Deutsch%20%F0%9F%87%A9%F0%9F%87%AA-green.svg)](README_de.md)
[![English Docs](https://img.shields.io/badge/Language-English%20%F0%9F%87%AC%F0%9F%87%A7-blue.svg)](README.md)
[![Open in HACS](https://img.shields.io/badge/HACS-Open%20Repository-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)
[![HACS Default](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/default)
[![Start Config Flow](https://img.shields.io/badge/Home%20Assistant-Integration%20hinzuf%C3%BCgen-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)
[![Version](https://img.shields.io/badge/version-1.9.3-blue.svg)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![Vibe Coding](https://img.shields.io/badge/Vibe%20Coding-100%25%20mit%20Hingabe-ff69b4?logo=sparkles&logoColor=white)](https://github.com/nukleuz80/ha_brainstorm)
[![Quality Scale](https://img.shields.io/badge/Quality%20Scale-Gold%20Selbsteinsch%C3%A4tzung-FFD700.svg)](https://contributors.home-assistant.io/core/quality-scale/)
[![GitHub Release](https://img.shields.io/github/v/release/nukleuz80/ha_brainstorm)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/nukleuz80/ha_brainstorm)

</div>

**Brainstorm Hub** ist die smarte Ideen-, Gedanken- und Notizen-Sammelzentrale für dein Home Assistant Smarthome.  
Egal ob beim Kochen, im Garten, unter der Dusche oder unterwegs: Erfasse Geistesblitze sekundenschnell per Sprache (**Amazon Alexa** oder **Home Assistant Assist**), über das Lovelace-Dashboard oder Automationen. Brainstorm ordnet deine Ideen durch intelligente Heuristiken automatisch der passenden Kategorie zu und synchronisiert sie auf Wunsch als Markdown-Dateien für Obsidian, Logseq oder Nextcloud.

> [!NOTE]
> **🎉 Jetzt in HACS:** Am 9. November 2026 wurde Brainstorm Hub [in die Standardliste von HACS aufgenommen](https://github.com/hacs/default/pull/13619). Such in HACS einfach nach **Brainstorm Hub**, ein benutzerdefiniertes Repository brauchst du nicht.

> [!TIP]
> **📘 [Anleitung mit Beispielen](docs/anleitung.md):** Was du sagen, schreiben und einstellen kannst, mit Beispielen für Alexa, Assist, Siri, Karten, Tastatur und Automationen.
>
> **🎬 [Videos](docs/videos.md):** Die wichtigsten Funktionen in 3 Minuten, die Installation, die Einrichtung des eigenen Alexa-Skills, Erinnerungen, der iPhone-Kurzbefehl sowie Privatsphäre und KI-Backlog.

Feedback, Ideen und Verbesserungen sind sehr willkommen, siehe [💬 Feedback & Mitmachen](#-feedback--mitmachen).

---

## 🌍 Sprachunterstützung

Brainstorm Hub funktioniert auf Deutsch und Englisch. Vorhandene Kategorien und Einträge werden dabei nie übersetzt oder umbenannt. Die Tabelle zeigt den aktuellen Stand. Wie eine weitere Sprache dazukommt, steht in [`CONTRIBUTING.md`](CONTRIBUTING.md).

| Bereich | Deutsch | Englisch |
| :--- | :--- | :--- |
| Einstellungen der Integration | ✅ | ✅ |
| Dokumentation | ✅ | ✅ |
| Antworten des Alexa-Skills | ✅ | ✅ |
| Sprachbefehle des Alexa-Skills | ✅ | ✅ |
| Assist-Sätze | ✅ | ✅ (`examples/`) |
| Satzkürzung, Termin und Priorität aus der Sprache | ✅ | ✅ |
| Dashboard-Karten | ✅ | ✅ |
| Erinnerungstexte, Logbuch und Fehlermeldungen | ✅ | ✅ |

---

## 🌟 🗣️ Key Feature: Nahtlose Amazon Alexa Hands-Free Spracherfassung

> 🗣️ *„Alexa, Brainstorm“* ➔ 🤖 *„Brainstorm bereit. Sprich deine Notiz oder sage Ansage.“*  
> 🗣️ *„Dringend Garten: Rasenmäher reparieren“* ➔ 🤖 *„Gespeichert unter Haus & Garten [🔥 Dringend].“*

Brainstorm Hub verwandelt alle deine **Amazon Echo**-Geräte im Haus in sekundenschnelle, reibungslose Ideensammler – perfekt beim Kochen, in der Werkstatt oder im Garten, wenn du keine Hand frei hast!

### ⚡ Warum die Alexa-Spracherfassung das absolute Herzstück ist:
- 🚫 **Keine Musik- & Einkaufslisten-Kollisionen mehr:** Standardmäßig leitet Alexa freie Notizen oft in unübersichtliche Amazon-Einkaufslisten um oder versucht die Rockband *„Brainstorm“* auf Spotify abzuspielen. Brainstorm Hub fängt dies durch vorkonfigurierte Routine-Empfehlungen und automatische Hintergrund-Stopp-Befehle vollständig ab – für ein 100 % lautloses, sauberes Dialogerlebnis!
- 🗣️ **Zwei-Wege-Dialog-Modus:** Sag einfach *„Alexa, Brainstorm“* oder *„Alexa, Neue Idee“*. Alexa hört aktiv zu, quittiert deine Notiz und bestätigt dir direkt per Sprache die zugeordnete Kategorie und Priorität.
- ⚡ **Schnelle Direktbefehle in einem Satz:** Wenn es schnell gehen muss: *„Alexa, notiere in Smarthome Kellerlicht dimmen“* oder *„Alexa, Idee dringend Garten: Terrasse reinigen“*.
- 🧠 **Automatische NLP-Textbereinigung & Grammatik-Transformation:** Filtert lästige Gesprächsfloskeln (*„schreib bitte auf dass wir...“* ➔ *„Terrasse reinigen“*), korrigiert Tipp-/Sprachfehler und wandelt passive Hilfsverb-Endungen in präzise Handlungsaufforderungen um.
- 🏷️ **Intelligente Prioritäts- & Kategorie-Extraktion:** Erkennt Signalwörter (*„dringend“*, *„wichtig“*, *„sofort“*, *„prio 1“*, *„wenn zeit ist“*) und Kontextbegriffe (*„für den Garten“*, *„im Smarthome“*) unabhängig von der Satzreihenfolge.
- 📍 **Geräte-Herkunftserfassung:** Erkennt genau, welches Echo-Gerät die Notiz aufgenommen hat (z. B. `🗣️ Alexa (Echo Show Küche)` vs. `🗣️ Alexa (Garten Echo Dot)`).

---

## 🌟 Highlights & Features

- 🎯 **NEU (v1.4.22): Intelligentes Prioritäten-Management & Visuelle Dringlichkeitsstufen:**
  - **4 Prioritätsstufen:** `low` (🟢 Niedrig), `medium` (🟡 Mittel / Standard), `high` (🔴 Hoch) und `urgent` (🔥 Dringend).
  - **Automatische Spracherkennung (NLP & Heuristik):** Natürliche Erkennung von Dringlichkeits-Signalwörtern und Tags per Sprache oder Texteingabe (z. B. *„Dringend Garten: Rasenmäher reparieren“*, *„Garten: Wichtig Rasenmäher reparieren“*, *„Sofort Notiz…“*, *„Prio 1…“*, *„Wenn Zeit ist…“*, *„!urgent“*, *„!high“*, *„!low“*). Das System erkennt Prioritäten unabhängig von der Reihenfolge vor oder nach dem Kategoriepräfix, filtert die Signalwörter sauber aus dem Notiztext und setzt die Priorität automatisch.
  - **1-Klick Prioritätswechsel im Dashboard:** Direktes Weiterschalten der Priorität (`Mittel` ➔ `Hoch` ➔ `Dringend` ➔ `Niedrig`) per Klick auf das Prioritäts-Badge in der Notizenliste (`brainstorm-card`) oder der Mindmap (`brainstorm-mindmap-card`).
  - **Prioritätsauswahl in Toolbar & Dialogen:** Schnellauswahl in der Erfassungszeile sowie farbige Chip-Auswahl in Neu- und Bearbeiten-Dialogen.
  - **Visuelle Effekte in der Mindmap:** Dringende Gedankenwolken (`urgent`) pulsieren mit einem sanften Feuereffekt (`cloud-urgent`), während hohe Prioritäten (`high`) durch einen dezenten Warm-Glow hervorgehoben werden.
  - **Vollständige Plattform-Integration:** Prioritäten werden im Sensor (`priority_counts`), in To-do-Listen (`todo.brainstorm_hub_*`), im Logbook, in den LLM-Tools und beim Markdown-Export (`[🔥 Dringend]`, `[🔴 Hoch]`) lückenlos gepflegt.
- 🤖 **Assist LLM Tools & Function-Calling API (v1.4.20):**
  - **Freie natürliche Sprache statt starren Befehlen:** Vollständige Integration in das native Home Assistant LLM API (`homeassistant.helpers.llm`). Sprachmodelle (wie OpenAI, Google Gemini, Ollama oder lokale LLMs) erhalten direkten Zugriff auf Brainstorm als Werkzeugsatz.
  - **5 mächtige KI-Werkzeuge:**
    - `brainstorm_add_idea`: Erfasst Gedanken und ordnet sie kontextbezogen der passenden Kategorie zu.
    - `brainstorm_get_ideas`: Beantwortet Fragen zu bestehenden Notizen mit flexiblen Filtern nach Kategorie, Status und Freitext-Suche.
    - `brainstorm_complete_idea`: Hakt Aufgaben per natürlicher Sprache ab (per ID oder Volltextsuche, z. B. *„Die Hecke ist geschnitten“*).
    - `brainstorm_delete_idea`: Löscht Notizen unwiderruflich per Sprachbefehl.
    - `brainstorm_list_categories`: Gibt der KI Überblick über alle Kategorien und Aufgabenstatistiken.
  - **Universell einsetzbar:** Direkt in den Einstellungen jedes Sprachassistenten unter *LLM API: „Brainstorm Hub“* aktivierbar ([Sprachassistenten öffnen](https://my.home-assistant.io/redirect/voice_assistants/)).
- 🧠 **Intelligente Text-Optimierung & NLP-Bereinigung (v1.4.0):**
  - **Ganze Sätze statt Satzreste (v1.5.8):** *„der Rasen muss gemäht werden“* ➔ *„Rasen mähen“*. Verneinungen, Fragen und nicht vollständig umbaubare Sätze behalten ihren Wortlaut. Getippter Text bekommt nur eine Rechtschreibkorrektur.
  - **Termin und Priorität aus dem Satz (v1.5.10):** *„ich muss morgen unbedingt den Arzt anrufen“* ➔ *„Arzt anrufen“*, Termin morgen um 9 Uhr, hohe Priorität. Der Termin löst eine Erinnerung aus und lässt sich abschalten. Der gesprochene Satz bleibt gespeichert und kann in der Karte übernommen werden.
  - **Eigene Begriffe (v1.5.10):** Namen von Personen und Kategorien werden automatisch richtig geschrieben, eigene Begriffe und Korrekturen stehen unter *Allgemeine Einstellungen*.
  - **Optionale KI-Stufe (v1.5.10):** Eine KI-Aufgaben-Entität verbessert den Eintrag im Hintergrund. Fügt sie Wörter oder Zahlen hinzu oder ändert eine Verneinung, bleibt die Fassung der Regeln stehen.
  - **Prägnante Notizen statt Gesprächsfloskeln:** Verwandelt gesprochene Sätze wie *„im brainstorm dass heute die kinder vom flughafen abgeholt werden müssen“* vollautomatisch in *„Heute Kinder vom Flughafen abholen“*.
  - **Filterung von Füllwörtern:** Entfernt Einleitungen (*„notiere bitte dass…“*, *„merke dir…“*, *„kannst du aufschreiben…“*, *„ich muss…“*, *„dass wir…“*).
  - **Grammatik-Transformation (Infinitiv):** Wandelt passive Hilfsverb-Endungen (*„…geschnitten werden müssen“* ➔ *„…schneiden“*, *„…repariert werden soll“* ➔ *„…reparieren“*, *„…bezahlt werden muss“* ➔ *„…bezahlen“*) in präzise Handlungsaufforderungen um.
  - **Rechtschreibung & Groß-/Kleinschreibung:** Automatische Korrektur von typischen Sprach- und Tippfehlern (`terasse` ➔ `Terrasse`, `packet` ➔ `Paket`) und lückenlose Großschreibung deutscher Substantive.
  - **Schalter im Options-Flow:** Kann unter *Konfigurieren ➔ Allgemeine Einstellungen* jederzeit ein- oder ausgeschaltet werden.
- 🗣️ **Zwei-Wege-Spracherfassung:**
  - **Amazon Alexa:** Interaktiver Dialog-Modus (über Alexa Actionable Notifications Skill) und schnelle Direktbefehle ohne Musikunterbrechung oder ungewollte Einkaufslisten-Einträge.
  - **Home Assistant Assist:** Vollständige Unterstützung via lokaler Spracherkennung (Custom Sentences mit Wildcard-Support) und nativer Home Assistant Listen-Befehle.
- 🏷️ **Intelligente, automatische Kategorisierung:**
  - Mehrstufige semantische Heuristik: Erkennung von Präfixen (*„Garten: …“*), Präpositionen (*„im Garten …“*, *„für das Smarthome …“*) und Kontext-Schlagwörtern (Pool, Rasen, Heizung, ESPHome, Lampe etc.).
  - Standard-Kategorien: *Haus & Garten*, *Smarthome*, *Projekte*, *Alltag*, *Inbox*.
- 🎴 **Moderne Custom Lovelace Cards (v1.4.0):**
  - **Brainstorm Card (`custom:brainstorm-card`):**
    - Zweistöckiges Design mit Schnellerfassungs-Toolbar, Auto-Kategorisierung und Pill-Filtern.
    - Integrierter Ansichts-Umschalter (`🧠 Mindmap` ⇄ `📋 Liste`) direkt in der Kopfzeile.
    - Erledigt-Verwaltung mit Durchstreich-Animation, Bearbeitungsfunktion und Quellen-Badges.
    - **Unteraufgaben direkt anlegen (v1.6.29):** 🌿 an einer Hauptaufgabe oder in ihrem Menü bei langem Drücken legt eine Unteraufgabe direkt darunter an, in derselben Kategorie. Mit einer KI-Aufgaben-Entität schlägt ✨ daneben Unteraufgaben vor (v1.6.28).
    - **Anhänge (v1.7.9):** 📎 im Bearbeiten-Dialog beider Karten hängt Screenshots, Fotos, PDFs, Logs und andere Dateien an eine Notiz, bis 10 MB pro Datei und 20 pro Notiz. Am Rechner fügst du einen Screenshot mit Strg+V ein oder ziehst Dateien auf den Dialog, am Handy bietet der Knopf Kamera und Galerie an. Die Liste zeigt 📎 mit der Anzahl, Antippen zeigt die Dateien, Bilder als Vorschau, und öffnet sie. Ist eine Notiz erledigt (oder archiviert), werden ihre Anhänge nach 30 Tagen gelöscht, wird sie wieder geöffnet, bleiben sie. Die Dateien liegen in `/config/brainstorm_attachments/` und gehen nur an Personen, die die Notiz sehen dürfen. Erlaubt: Bilder, PDF, TXT/LOG/MD, CSV, JSON, YAML, ZIP.
    - **Erledigte Einträge löschen (v1.7.13):** Einstellungen › 🧹 Erledigte Einträge löschen löscht erledigte (abgehakte oder archivierte) Einträge nach einer Anzahl Tage von selbst, geprüft alle sechs Stunden, und hat einen Schalter, der alle sofort löscht. Ihre Anhänge gehen mit. Standardmäßig aus (0 Tage). Aktion: `brainstorm.delete_done`.
    - **Titel und Beschreibung (v1.7.8):** ✎ bearbeitet den Titel und darunter eine optionale Beschreibung für Details, Links oder Notizen. Die Liste zeigt bis zu drei Zeilen davon unter dem Titel, Antippen zeigt den Rest. Der Bearbeiten-Dialog der Mindmap hat sie auch, und die To-do-Listen von Home Assistant zeigen und bearbeiten sie als Beschreibung des Eintrags. Aktionen: `description` in `brainstorm.add_idea` und `brainstorm.update_idea` (leer entfernt sie).
    - **Suche in der Liste (v1.8.11):** Das Feld 🔍 über der Liste filtert beim Tippen, in Titel, Beschreibung, Ergebnis und Person, ohne auf Groß-/Kleinschreibung und Akzente zu achten. `#tag` findet Tags. Ein gefundener Unterpunkt zeigt seinen Oberpunkt grau mit, eine gefundene Hauptaufgabe ihre Unterpunkte. ✕ oder Esc leert sie; `show_search: false` blendet das Feld aus.
    - **Unteraufgaben einklappen (v1.7.4):** Eine Hauptaufgabe mit Unteraufgaben zeigt ▾ und deren Anzahl. Antippen klappt sie zu, ▸ klappt sie wieder auf. Praktisch bei langen Bring-Listen. Jeder Browser merkt sich pro Karte, was eingeklappt ist.
  - **Links und etwas Markdown in Notizen (beide Karten, v1.6.21):**
    - Webadressen werden anklickbar, ebenso `[Text](https://…)`. `**fett**`, `*kursiv*`, `~~durchgestrichen~~` und `` `Code` `` erscheinen formatiert, in der Notiz und in ihrer Ergebnisnotiz.
    - Sicher gebaut: Alles andere bleibt reiner Text, HTML in einer Notiz wird nie ausgeführt, und Links führen nur zu `http`-, `https`- und `mailto`-Adressen. Sie öffnen sich in einem neuen Tab, und ein Klick auf einen Link öffnet nicht den Editor.
  - **NEU: Brainstorm Mindmap Card (`custom:brainstorm-mindmap-card`):**
    - Interaktives Radial-Synapsen-Layout für eine visuelle Gedankenlandkarte.
    - Zentraler Knotenpunkt (Inbox / Fokus-Kategorie) mit edlem, transparentem Brainstorm-Logo im Hintergrund.
    - Notizen dargestellt als charmante Gedankenwolken mit gestrichelten Konturen und Kategorie-Farbcodes.
    - Organische Bézier-Verbindungslinien, die beim Überfahren aufleuchten.
    - Frei verschiebbare Notizen per Drag & Drop (auf Desktop und Touchscreens).
    - **Äste:** Unteraufgaben hängen an ihrer Elternidee, ihre Linien gehen von dort statt von der Mitte aus. 🌿 an einer Notiz legt eine Unteridee an.
    - **Unteraufgaben von der KI (v1.6.26):** Ist unter *Konfigurieren ➔ KI* eine KI-Aufgaben-Entität gewählt, fragt ✨ an einer Notiz sie nach bis zu 8 Unteraufgaben. Du nimmst den Haken bei allem weg, was du nicht willst, kannst die Texte ändern, und nur was du übernimmst, landet unter der Notiz. Zur KI geht nur diese Notiz mit ihren Unteraufgaben, und nur wenn du den Knopf drückst. Ein Rückgängig entfernt alle wieder. Auch die Listenkarte hat ✨ (v1.6.28): neben ✎ an jeder Hauptaufgabe und im Menü bei langem Drücken oder Rechtsklick. Lehnt der Anbieter der KI wegen Überlastung ab, fragt Brainstorm nach 2 Sekunden einmal nach und sagt sonst, dass die KI gerade nicht erreichbar ist (v1.6.29).
    - **Gespeicherte Anordnung:** In einer einzelnen Liste behalten verschobene Notizen ihren Platz auf allen Geräten. Eine Elternidee nimmt ihre Unteraufgaben mit. Die Übersicht aller Listen ordnet sich selbst.
    - **Zweige einklappen:** Der runde Knopf an einer Notiz mit Unteraufgaben klappt ihren Zweig zu und zeigt, wie viele Notizen darin stecken. Jedes Gerät merkt sich, was eingeklappt ist.
    - **Anordnung als Baum:** Jeder Zweig bekommt seinen eigenen Ausschnitt des Kreises, Linien kreuzen sich nicht. 🪄 setzt von Hand platzierte Notizen wieder an ihren automatischen Platz.
    - **Tastatur:** Ein Klick wählt eine Notiz aus. **Tab** legt eine Unteraufgabe an, **Enter** eine Notiz daneben, **Entf** löscht nach Rückfrage, **F2** oder Doppelklick bearbeitet den Text. Mit den Pfeiltasten gehst du die Zweige entlang: links zum Oberpunkt, rechts zur ersten Unteraufgabe, hoch und runter zu den Nachbarn.
    - **Direkt bearbeiten:** Ein Klick auf den Text öffnet ihn gleich in der Wolke. **Enter** speichert, **Umschalt+Enter** macht eine neue Zeile, **Esc** bricht ab. Termin, Priorität und Echos stellst du weiter mit ✏️ im Dialog ein.
    - **Mehrere Notizen auswählen:** **Umschalt+Ziehen** auf der leeren Map zieht einen Rahmen, **Umschalt+Klick** oder **Strg+Klick** nimmt eine Notiz dazu oder wieder heraus. Am Handy oder Tablet tippst du unten rechts auf ⬚ und ziehst dann einen Rahmen oder tippst Notizen an. Ziehst du eine ausgewählte Notiz, wandern alle mit, samt Unteraufgaben. Die Leiste über der Map hakt sie ab, verschiebt sie in eine andere Kategorie oder löscht sie nach Rückfrage, ein Rückgängig nimmt den ganzen Schritt zurück. **Esc** oder ✕ hebt die Auswahl auf.
    - **Rückgängig:** **Strg+Z** oder der Knopf ↶ unten rechts nimmt die letzten Schritte dieser Sitzung zurück: neue Notizen, Textänderungen, Erledigt, Priorität, Kategorie, Verschieben, Neu ordnen und auch Löschen. Gelöschte Notizen hält Home Assistant bis zum nächsten Neustart bereit.
    - **Suchen, Filtern und Tags (v1.8.0):** 🔍 oben rechts, oder **/** und **Strg+F** auf der Map, öffnet eine Suchleiste. Treffer bleiben hell, ihre übergeordneten Punkte halb, der Rest der Map tritt zurück. Chips filtern nach Priorität, *Überfällig*, *7 Tage*, *In Arbeit* und den Tags der Liste. **Enter** springt von Treffer zu Treffer und klappt seinen Zweig auf. `#garten` in einer Notiz oder *„Hashtag Garten“* gesagt zeigt das Tag als Chip; ein Tipp darauf filtert die Map. Siehe [Anleitung](docs/anleitung.md#33-mindmap-maus-finger-tastatur).
    - **Marker und Fortschritt (v1.8.1):** ❓ 💡 ⚠️ 💰 ⭐ 🚩 ✅ ⛔ ⏳ ❤️ als kleine Zeichen an einer Notiz, in beiden Karten, wählbar im Bearbeiten-Dialog und filterbar in der Suchleiste. Notizen mit Unteraufgaben zeigen einen Ring mit *3/5*, der sich wie bei MindManager aus den Unteraufgaben füllt; ohne Unteraufgaben schaltet ein Tipp auf den Ring in Viertelschritten weiter.
    - **Fokus und Ebenen (v1.8.2):** 🎯 an einer Notiz mit Unteraufgaben, oder **F4**, zeigt nur diesen Zweig mit der Notiz in der Mitte; eine Brotkrumenleiste über der Map führt zurück, **Umschalt+F4** oder **Esc** gehen eine Stufe hoch. ∞ unten rechts, oder die Tasten **1–9**, klappen die Map bis zu so vielen Ebenen ein, **0** zeigt wieder alle.
    - **Querverbindungen, Rahmen und Callouts (v1.8.2):** 🔗 an einer Notiz, oder **L**, und dann ein Tipp auf eine andere Notiz zieht einen gestrichelten Pfeil zwischen beiden, auch über Zweige hinweg. Ein Tipp auf die Linie gibt ihr eine Beschriftung oder macht sie *blockierend*: Das Ziel wird grau mit ⛔ *Wartet*, bis die erste Notiz erledigt ist. Mehrere Notizen auswählen und ▢ *Rahmen* tippen legt einen benannten Rahmen um sie. Ein *Callout* ist eine kurze Anmerkung in einer Sprechblase über der Notiz. Beides geht auch im Bearbeiten-Dialog, und die Listenkarte zeigt es ebenfalls.
    - **Nummerierung und Sortieren (v1.8.3):** Im ✏️ Bearbeiten-Dialog einer Notiz mit Unteraufgaben setzt *Unterpunkte nummerieren* 1., 1.1 … oder a), b) oder I., II. davor, in beiden Karten. *Unterpunkte sortieren* ordnet sie sofort nach Titel, Priorität, Fälligkeit oder Alter; **S** auf der Map öffnet dieselbe Auswahl, ohne Auswahl für die Hauptnotizen. ↶ macht es rückgängig.
    - **Gliederung exportieren und einfügen (v1.8.4):** 🖼️ speichert die Map auch als Markdown-Gliederung, OPML oder FreeMind-`.mm` (öffnet sich in Freeplane, XMind, MindManager). *Gliederung einfügen* macht aus einer eingefügten Liste oder einer Datei (`.md`, `.txt`, `.opml`, `.mm`) einen Zweig mit Notizen, im Fokus unter der Fokus-Notiz.
    - **Brainstorm-Modus (v1.8.5):** ⚡ oder **B** öffnet eine Schnelleingabe mit Timer von 3 bis 15 Minuten. Jedes Enter ist sofort eine Notiz und erscheint als bunter Zettel; ↶ nimmt die ganze Runde wieder heraus.
    - **Ansichten (v1.8.6–v1.8.8):** Der Ansichts-Knopf unten rechts zeigt die Notizen ◎ rund um die Mitte, als ⇶ Baum, ⊤ Organigramm, ☰ eingerückte Gliederung, ▥ Kanban nach Status (offen, in Arbeit, wartet, erledigt), 📅 Zeitleiste nach Fälligkeit (überfällig, heute, morgen, diese Woche, später, ohne Datum) oder ⊞ Eisenhower-Matrix (sofort erledigen, einplanen, abgeben, später oder gar nicht). Auf den Boards ändert das Ziehen in eine andere Spalte Status, Fälligkeit oder Priorität, ↶ nimmt es zurück. Die Wahl merkt sich der Browser; `layout` legt den Standard fest.
    - **Präsentationsmodus (v1.8.10):** **P** (oder ▶ in der Ansichtswahl) zeigt die Map im Vollbild und geht sie Notiz für Notiz durch, Ast für Ast, mit der Beschreibung darunter. → / Leertaste für die nächste Notiz, ← zurück, Esc beendet.
    - **Wiederkehrende Aufgaben (v1.8.15):** *Wiederholen* im Bearbeiten-Dialog beider Karten: jeden Tag, jeden Werktag, jede Woche, alle 2 Wochen, jeden Monat oder jedes Jahr. Abgehakt kommt die Notiz sofort wieder, fällig zum nächsten Termin, mit ihren Angaben und wieder offenen Unteraufgaben; die erledigte Runde bleibt unter *Erledigt*. Spät abgehakt überspringt sie verpasste Termine. Wird die erledigte Runde wieder aktiviert, verschwindet die neue. Wiederkehrende Notizen zeigen 🔁. Aktion: `repeat` in `brainstorm.update_idea`.
    - **PDF-Export (v1.8.14):** 🖼️ ➔ *PDF* speichert ein PDF mit dem Bild der Map auf der ersten Seite und danach allen Notizen als Gliederung mit Beschreibung, fertig zum Drucken oder Verschicken. *PDF (nur Gliederung)* lässt das Bild weg. Es entsteht im Browser, nichts verlässt Home Assistant.
    - **Bilder in Notizen (v1.8.13):** Das erste angehängte Bild einer Notiz (📎 im Bearbeiten-Dialog, auch per Einfügen oder Ziehen) erscheint direkt in ihr auf der Map, so sind Moodboard oder Skizze auf einen Blick zu sehen. Antippen öffnet es groß. `show_images: false` schaltet es ab.
    - **Regeln (v1.8.12):** 🎨 in der Suchleiste oder **R** macht aus dem aktuellen Filter eine Regel mit Farbe und Zeichen, wie SmartRules in MindManager: *alles 🔥 Dringende rot*, *#garten grün mit ⭐* … Jede passende Notiz wird in der Map und in der Listenkarte eingefärbt, die erste passende Regel gilt. Regeln lassen sich ausschalten, nach oben schieben, bearbeiten und löschen (↶ holt eine zurück). Sie liegen bei deinem Home-Assistant-Benutzer und gelten so auf jedem Gerät.
    - **KI-Hilfe auf der Map (v1.8.9):** Mit einer KI-Aufgaben-Entität kann ✨ an einer Notiz mit Unterpunkten auch **den Ast zusammenfassen**, in ein paar Sätzen, die zur Beschreibung werden können. **Lose Ideen zuordnen** (Taste **Z** oder am Ende einer Brainstorm-Runde) schlägt für jede lose Hauptnotiz der Kategorie einen Oberpunkt vor; du hakst ab, was gelten soll. Vor deiner Bestätigung ändert sich nichts, ↶ nimmt es zurück.
    - **Inhaltsvorlagen (v1.8.8):** 🖼️ ➔ *Gliederung einfügen* hat fertige Zweige wie SWOT-Analyse, Pro und Contra, Projektplan, Wochenplan oder Packliste für die Reise. Text anpassen, dann einfügen.
    - **Vorlagen und Bild-Export:** Vier Vorlagen (Standard, Klar, Skizze, Neon) bestimmen Form, Linien und Farben. Zehn Formen stehen bereit, von Karte, Wolke, Sprech- und Gedankenblase bis Ellipse, Sechseck, Notizzettel und unterstrichenem Text, für die ganze Map oder pro Notiz. 🖼️ oben rechts speichert die Map als SVG oder PNG.
    - Stufenloser Zoom & Pan per Mausrad, Pinch-Geste oder Steuerungsbuttons.
    - **Vollbild-Modus (`⛶`):** Per Knopfdruck oder Dashboard-Einbindung als beeindruckendes Vollbild-Erlebnis (ESC zum Schließen).
    - Direkte Aktionen an jeder Gedankenwolke (Erledigen, Text editieren, Kategorie wechseln, Löschen).
- ⚙️ **Konfigurations- & Options-Flow im HA-Backend:**
  - Unter [*Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren*](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) Kategorien komfortabel pflegen (hinzufügen, löschen, anpassen) und Optionen steuern.
  - Sichere Migration: Beim Löschen einer Kategorie werden verbliebene Ideen automatisch in die `Inbox` verschoben.
- 📝 **Automatischer Markdown-Export:**
  - Exportiert Ideen strukturiert nach Kategorien in Markdown-Dateien (z. B. `/config/brainstorm/`).
  - Ideal für Personal Knowledge Management (Obsidian, Logseq, Foam, SilverBullet).
- 📋 **Native Home Assistant To-do Plattform:**
  - Jede Brainstorm-Kategorie wird als echte Home Assistant To-do-Liste bereitgestellt (`todo.brainstorm_hub_haus_garten`, `todo.brainstorm_hub_inbox`, usw.).
- 🔁 **Gekoppelte To-do-Listen (v1.6.31):**
  - Koppelt eine Kategorie mit einer To-do-Liste einer anderen Integration, etwa **Bring!**, **Google Tasks**, **Todoist** oder einer lokalen To-do-Liste. Neue Einträge, Umbenennen und Abhaken gehen in beide Richtungen, so bleiben *Einkauf* in Brainstorm und deine Einkaufs-App gleich. Siehe *Konfigurieren ➔ To-do-Listen koppeln*.
- 🛒 **Native Bring!-Unterstützung (v1.7.0):**
  - Bring! unter *Konfigurieren ➔ 🛒 Bring!* einschalten, Kategorie wählen oder anlegen, fertig. Jede Bring-Liste wird eine Hauptnotiz, ihre Einträge werden Unteraufgaben. Notizen ohne Liste landen in der Standardliste, das Verschieben einer Unteraufgabe verschiebt den Eintrag, und die Bring-Spezifikation erscheint als Notiz. Umbenennen, Abhaken und neue Einträge gehen in beide Richtungen.
- 💾 **JSON-Export und -Import (v1.6.31):**
  - `brainstorm.export_json` gibt deine Ideen samt Kategorien, Icons und Farben als JSON zurück, auf Wunsch als Datei. `brainstorm.import_json` holt sie zurück, auf demselben oder einem anderen Home Assistant, und überspringt Vorhandenes.
- 🏛️ **100% Home Assistant Standard-konform:**
  - Entwickelt nach den offiziellen Richtlinien von [contributors.home-assistant.io](https://contributors.home-assistant.io/) (strikte Typisierung, non-blocking Event-Loop, `DeviceInfo`, saubere Translation-Keys).

---

## 📦 Installation

### 🔗 Schnelllinks

Diese Buttons öffnen die passende Seite in deinem eigenen Home Assistant:

[![Brainstorm Hub in HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration) [![Brainstorm Hub einrichten](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm) [![Brainstorm Hub öffnen (Konfigurieren, Diagnose, Löschen)](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) [![Brainstorm-Aktionen ausprobieren](https://my.home-assistant.io/badges/tools_actions.svg)](https://my.home-assistant.io/redirect/tools_actions/) [![Sprachassistenten (Assist, LLM API)](https://my.home-assistant.io/badges/voice_assistants.svg)](https://my.home-assistant.io/redirect/voice_assistants/) [![Reparaturen](https://my.home-assistant.io/badges/repairs.svg)](https://my.home-assistant.io/redirect/repairs/) [![Protokolle von Brainstorm Hub](https://my.home-assistant.io/badges/logs.svg)](https://my.home-assistant.io/redirect/logs/?integration=brainstorm)

Die Links laufen über [My Home Assistant](https://my.home-assistant.io/). Beim ersten Klick fragt es nach der Adresse deines Home Assistant und merkt sie sich. Auch die Menüpfade in dieser README und in der [Anleitung](docs/anleitung.md), etwa **Einstellungen ➔ Geräte & Dienste**, sind solche Links, und jede Aktion unter [Dienste](#️-dienste-services) hat einen Link, der sie in den Entwicklerwerkzeugen öffnet.

### Voraussetzungen

1. Home Assistant 2026.10 oder neuer.
2. [HACS](https://hacs.xyz), wenn du darüber installieren möchtest.
3. Optional für die Spracheingabe mit Alexa: die Integration [Alexa Media Player](https://github.com/alandtse/alexa_media_player).
4. Optional für einen eigenen Alexa-Skill: ein Amazon-Entwicklerkonto und eine öffentliche HTTPS-Adresse deines Home Assistant.

Brainstorm Hub verbindet sich von selbst mit keinem externen Dienst. Die Einrichtung braucht also weder Konto noch Passwort.

### Methode 1: Über HACS (Empfohlen – 1 Klick)

Brainstorm Hub steht seit dem 9. November 2026 in der Standardliste von HACS. Der Button öffnet es direkt in deinem HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)

Oder Schritt für Schritt:
1. Öffne **HACS** in deinem Home Assistant.
2. Suche nach **Brainstorm Hub** und klicke auf **Herunterladen**.
3. Starte Home Assistant neu.

Die Karten kommen mit der Integration: Nach dem Neustart lädt Home Assistant sie selbst, ohne Kopieren und ohne Ressourcen-Eintrag.

### Methode 2: Manuelle Installation

1. Lade das neueste Release herunter.
2. Kopiere den Ordner `custom_components/brainstorm` in dein Home Assistant Verzeichnis `/config/custom_components/`.
3. Starte Home Assistant neu. Die Karten liegen im Ordner der Integration (`cards/`) und werden von selbst geladen.

> **Update von einer Version vor 1.7.15:** Entferne die alten Ressourcen `/local/brainstorm-card.js` und `/local/brainstorm-mindmap-card.js` unter [*Einstellungen ➔ Dashboards ➔ Ressourcen*](https://my.home-assistant.io/redirect/lovelace_resources/) (oder aus `resources:` im YAML-Modus) und lösche die Karten-Dateien in `/config/www/`. Sonst kann der Browser noch die alten Karten laden.

### Integration entfernen

1. Öffne [**Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm), klicke auf die drei Punkte und wähle **Löschen**.
2. Über HACS installiert: Öffne Brainstorm Hub in HACS und wähle **Entfernen**. Manuell installiert: Lösche `/config/custom_components/brainstorm`.
3. Entferne alle Brainstorm-Karten aus deinen Dashboards.
4. Starte Home Assistant neu.

Je nachdem, was du genutzt hast, entferne auch:
- **Deinen Alexa-Skill:** Lösche ihn in der Alexa Developer Console und seinen Code in AWS Lambda. Echte Alexa-Erinnerungen bleiben in der Alexa-App, bis du sie dort löschst.
- **Automationen und Sätze:** Eigene Automationen, Skripte und Custom Sentences, die Brainstorm aufrufen, sowie einen iPhone-Kurzbefehl.
- **Deine Daten:** Home Assistant behält deine Ideen in `/config/.storage/brainstorm.storage`, die Skill-Kopplung in `brainstorm.alexa_skill` und den Stand der Erinnerungen in `brainstorm.reminders` im selben Ordner. Lösche diese Dateien und den Markdown-Ordner (Standard `/config/brainstorm`), wenn du nicht zurückkehren möchtest.

---

## ⏰ Erinnerungen & Benachrichtigungen

Brainstorm erinnert dich von selbst an fällige Einträge, und zwar über die Dienste, die du in Home Assistant ohnehin eingerichtet hast. Alles ist optional und läuft lokal.

**Termin festlegen**
- **Per Sprache (Skill):** *„Alexa, sage Brainstorm erinnere mich morgen um 8 an die Mülltonnen“*. Verstanden werden z. B. *heute Abend*, *morgen früh*, *übermorgen*, *am Freitag*, *nächste Woche*, *am 25.11.*, *in zwei Stunden*, *um halb neun*. Auch ausgesprochene Tage klappen: *„am zweiten Dezember um zwölf Uhr“* oder *„am zweiten Zwölften um zwölf“* speichern den 02.12. um 12:00 Uhr. Liegt das Datum dieses Jahr schon hinter dir, nimmt Brainstorm das nächste Jahr.
- **Per Sprache (nativ):** *„Alexa, erinnere mich morgen um 8 an …“*. Amazon legt dabei eventuell zusätzlich eine eigene Erinnerung an.
- **In den Listen:** Fälligkeitsdatum in den To-do-Listen von Home Assistant setzen. Ein reines Datum bedeutet 9:00 Uhr.
- **Auf der Karte:** Eintrag lange drücken ➔ *Erinnern: heute Abend / morgen früh / nächste Woche / Zeitpunkt wählen*.
- **Im Bearbeiten-Dialog:** Beide Karten zeigen ein Datums- und ein Uhrzeitfeld, ohne Uhrzeit erinnert Brainstorm um 9:00 Uhr. Darunter klappt *Erinnern auf* per Tipp auf, dort wählst du die Echos, die diese Erinnerung sprechen. Ohne Auswahl gelten die Erinnerungs-Einstellungen.
- **In Automationen:** `brainstorm.add_idea` und `brainstorm.update_idea` mit dem Feld `due`.

**Einstellen** unter **Brainstorm Hub ➔ Konfigurieren ➔ Erinnerungen & Benachrichtigungen**. Jede Funktion hat ihren eigenen Schalter:

| Bereich | Schalter | Was es tut |
| :--- | :--- | :--- |
| **Ein/Aus & Kanäle** | Erinnerungen nutzen | Hauptschalter für alles in diesem Menü |
| | Alexa-Ansage | Aus, Echo des Eintrags, zuletzt genutzter Echo oder feste Echos (benötigt Alexa Media) |
| | Benachrichtigungen senden | Beliebige `notify`-Dienste; die Companion-App bekommt die Knöpfe **Erledigt**, **1 Stunde später** und **Morgen** |
| | Wichtige offene Einträge erneut senden | Hohe oder dringende Einträge gehen nach einer Wartezeit an weitere Dienste, z. B. Pushover |
| **Ruhezeit, Briefing & Rückblick** | Ruhezeit nutzen | Erinnerungen warten; Dringendes erreicht das Handy, aber kein Echo spricht |
| | Tägliches Briefing | Zu einer Uhrzeit, optional erst wenn ein Sensor oder eine Person jemanden meldet |
| | Wochenrückblick | Nennt lange offene Einträge |
| **Regeln pro Liste** | Regeln pro Liste nutzen | Pro Liste: normale Kanäle, nur Alexa, nur Benachrichtigungen (privat) oder nichts; eigene Dienste; an bestimmten Tagen senden; an einem Ort senden |
| **Orte & Heimkommen** | Beim Heimkommen erinnern | *„erinnere mich wenn ich heimkomme an den Müll“* |
| | An Orten erinnern | *„erinnere mich wenn ich bei Edeka bin an die Milch“* (nutzt deine Zonen) |
| **Personen** | Erinnerungen für andere nutzen | *„erinnere Lenja morgen um 8 an den Termin“* mit eigenen Kanälen pro Person |
| **Kalender & Alexa** | Kalender | Trägt Erinnerungen einmalig in einen Kalender ein; spätere Änderungen werden nicht übertragen |
| | Echte Alexa-Erinnerungen | Legt im Skill zusätzlich eine Amazon-Erinnerung an, dafür muss in der Alexa-Konsole **Build ➔ Permissions ➔ Reminders** eingeschaltet sein und einmal die Zustimmung in der Alexa-App erteilt werden |

Die KI, die Briefing und Rückblick kürzt, stellst du seit v1.6.27 im Hauptmenü unter **Brainstorm Hub ➔ Konfigurieren ➔ KI** ein.

**Listen auf dem Echo Show**

Mit dem Skill zeigt ein Echo mit Bildschirm deine offenen Ideen parallel zur Sprachantwort: eine Seite je Kategorie mit Kacheln, nach links oder rechts wischen wechselt sie, innerhalb einer Seite wird gescrollt. Tippe auf den Kreis vor einer Idee, um sie zu erledigen. Ein Hauptpunkt mit Unterpunkten zeigt *+ 3 Unterpunkte*; Antippen seines Textes klappt sie auf und zu; auf der Karte lässt sie sich wiederherstellen. *„Alexa, sage Brainstorm zeige Alltag“* oder *„… zeige Listen“* zeigt die Listen mit nur einer kurzen Antwort, *„… Ansage“* und *„… alles vorlesen“* zeigen sie beim Vorlesen.

Zur Einrichtung öffnest du in der Alexa-Entwicklerkonsole **Build ➔ Interfaces**, schaltest **Alexa Presentation Language** mit den Echo-Show-Profilen ein und klickst auf **Save**. Kopiere danach die Felder **Sprachmodell** und **Skill-Code** erneut und klicke auf **Build** und **Deploy**. Ohne diese Schritte antwortet der Skill weiter nur per Sprache. Wie lange ein Bildschirm stehen bleibt, entscheidet Amazon; er kann früher als die gewünschten zwei Minuten zum Startbildschirm zurückkehren.

**Weitere Sätze im Skill**
- *„Alexa, sage Brainstorm erledigt Mülltonnen“* oder nur *„… erledigt“* für die letzte Erinnerung
- *„Alexa, sage Brainstorm später“* verschiebt die letzte Erinnerung um eine Stunde
- *„Alexa, sage Brainstorm Ansage Alltag“* liest eine Kategorie vor, *„… Ansage“* nennt nur den Überblick, *„… alles vorlesen“* liest alles vor

**Eigene Automationen:** Jede Erinnerung löst das Ereignis `brainstorm_reminder_due` aus, auch ohne eingerichtete Dienste.

---

## 🛠️ Konfiguration

Klicke auf diesen Button, um die Ersteinrichtung von **Brainstorm Hub** direkt in Home Assistant zu starten:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)

<details>
<summary><b>Alternativ: Manuell über die UI einrichten</b></summary>

1. Gehe in Home Assistant auf [**Einstellungen ➔ Geräte & Dienste ➔ Integration hinzufügen**](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm).
2. Suche nach **Brainstorm Hub** und schließe die Ersteinrichtung ab.
3. Über den Button **Konfigurieren** stehen dir zwei Menübereiche zur Verfügung:
   - **📁 Kategorien verwalten:** Neue Kategorien hinzufügen, ungenutzte löschen oder per Kommaliste anpassen.
   - **⚙️ Allgemeine Einstellungen & Export:** Standard-Kategorie festlegen, automatischen Markdown-Export aktivieren, Zielpfad konfigurieren und die Echos für die Spracheingabe auswählen.
</details>

---

## 🎴 Dashboard Cards einbinden

Alle Kartenoptionen, die Bedienung und die Tastenkürzel der Mindmap stehen in der [Anleitung](docs/anleitung.md#3-schreiben--karten-bedienen).

### 1. Brainstorm Card (Listenansicht mit integriertem Mindmap-Umschalter)
```yaml
type: custom:brainstorm-card
title: Brainstorm Hub
```

### 2. Brainstorm Mindmap Card (Dedizierte interaktive Gedankenlandkarte)
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
| `layout` | `radial`, `tree`, `org`, `outline`, `kanban`, `timeline`, `matrix` | Ansicht der Notizen: rund um die Mitte, Baum, Organigramm, Gliederung, Kanban nach Status, Zeitleiste nach Fälligkeit oder Eisenhower-Matrix. Der Knopf unten rechts schaltet ebenfalls um und merkt sich die Wahl im Browser. Standard `radial`. |
| `map_template` | `standard`, `clean`, `sketch`, `neon` | **Standard:** Karten, Kurven, Kategoriefarben. **Klar:** Rechtecke, eckige Linien. **Skizze:** Kapseln, gestrichelt, Pastell. **Neon:** dunkler Hintergrund mit leuchtenden Rändern. |
| `node_shape` | `template`, `card`, `cloud`, `bubble`, `thought`, `pill`, `rect`, `ellipse`, `hexagon`, `note`, `underline` | Form der Notizen: Karte, Wolke, Sprechblase, Gedankenblase, Kapsel, Rechteck, Ellipse, Sechseck, Notizzettel oder unterstrichener Text. Der Zipfel der Sprechblase und die Bläschen der Gedankenblase zeigen zur übergeordneten Notiz oder zur Mitte; die Linien treffen eine unterstrichene Notiz am Ende ihres Strichs. Eine Notiz kann ihre eigene Form haben (Bearbeiten-Dialog oder `shape` von `brainstorm.update_idea`). |
| `voice_bubbles` | `true`, `false` | Notizen, die Alexa, Siri oder Assist gesagt wurden, erscheinen als Sprechblase, außer sie haben eine eigene Form. Standard `true`. |
| `line_style` | `template`, `curve`, `straight`, `angled`, `dashed` | Linien: Kurve, gerade, eckig oder gestrichelt. |
| `color_scheme` | `template`, `category`, `pastel`, `mono`, `neon` | Farben: Kategoriefarben, Pastell (zart eingefärbt), einfarbig oder Neon. |

### 3. Eigenständiges Seitenleisten-Dashboard (`Brainstorm Hub`)
Für maximale Übersicht lässt sich Brainstorm als vollwertiger Menüpunkt direkt in der linken Home Assistant Seitenleiste einbinden (z. B. unter Pfad `/brainstorm-hub`):
- **Ansicht 1: Übersicht (Kombiniert):** Die interaktive Gedankenlandkarte (`custom:brainstorm-mindmap-card`) thront oben im Großformat (z. B. Höhe 580px), während sich die Schnelleingabe und Notizenliste (`custom:brainstorm-card`) mit Filtern und Badges direkt darunter befindet.
- **Ansicht 2: Mindmap Vollbild:** 100% Panel-Ansicht für ausgedehntes visuelles Brainstorming.
- **Ansicht 3: Listenansicht:** Schnelle, fokussierte Notizenliste für Tastatur- und Touch-Eingaben.

---

## 🗣️ Sprachsteuerung

Alle Sätze und was Brainstorm daraus liest (Kategorie, Priorität, Termin) stehen in der [Anleitung](docs/anleitung.md#1-sagen--sprachbefehle).

### 1. Amazon Alexa

#### Nur ausgewählte Echos nutzen
Standardmäßig kann jeder Echo Ideen erfassen. Zum Einschränken gehst du auf [**Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren ➔ Allgemeine Einstellungen & Export**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) und wählst die Echos unter **Echo-Geräte für die Spracheingabe** aus. Eine leere Liste bedeutet: alle Echos.

Die Alexa-Sprachabläufe laufen als Automationen und Skripte in deiner eigenen Home-Assistant-Konfiguration. Jeder Einstieg braucht deshalb diese Bedingung (`echo_device` enthält den aufrufenden Echo):

```yaml
- condition: template
  value_template: >-
    {% set allowed = state_attr('sensor.brainstorm_ideen_ubersicht', 'allowed_echos') %}
    {{ not allowed or echo_device in allowed }}
```

#### Variante A: Interaktiver Dialog-Modus (Empfohlen)
Triggere den Dialog per Sprachbefehl, Szene oder Alexa-Routine:
> 🗣️ *„Alexa, Neue Idee“* oder *„Alexa, Brainstorm“*  
> 🤖 **Alexa:** *„Brainstorm bereit. Sprich deine Notiz oder sage Ansage.“*  
> 🗣️ **Du:** *„Im Garten müssen die Rosen geschnitten werden.“*  
> 🤖 **Alexa:** *„Gespeichert unter Haus & Garten.“*

##### 📱 Einrichtung der Alexa-Routinen (Wichtig gegen Musik-Konflikte)
Da **„Brainstorm“** auch der Name einer bekannten Rockband und diverser Songs ist, versucht Alexa bei Einzelwörtern ohne Routine standardmäßig, Musik über Amazon Music / Spotify abzuspielen. In Home Assistant fängt zwar ein unbedingter Stopp-Befehl anlaufende Streams ab – für ein absolut sauberes und lautloses Nutzererlebnis empfiehlt sich die Einrichtung von **zwei separaten Alexa-Routinen** in der Smartphone-App (da Amazon pro Routine immer nur genau **einen** Sprachauslöser erlaubt):

1. **Routine 1: Vollständiger Aufruf**
   * **Wenn Folgendes passiert:** Stimme ➔ `Alexa, öffne brainstorm`
   * **Aktion hinzufügen:** Smart Home ➔ Szenen ➔ **`Brainstorm Hauptmenü`** *(in Alexa werden Home Assistant Skripte als Szenen bereitgestellt)*
2. **Routine 2: Kurzer Direktaufruf**
   * **Wenn Folgendes passiert:** Stimme ➔ `Alexa, brainstorm`
   * **Aktion hinzufügen:** Smart Home ➔ Szenen ➔ **`Brainstorm Hauptmenü`**

> [!TIP]
> **Warum zwei getrennte Routinen?**  
> Alexa-Routinen haben bei Amazon immer oberste Priorität vor der allgemeinen Musik- und Websuche. Sobald beide Varianten als separate Routinen angelegt sind, unterdrückt Alexa die Musiksuche vollständig und startet unmittelbar und lautlos die Brainstorm-Sprachabfrage.

#### Variante B: Schnelle Direktbefehle
Direkt in einem Satz sprechen (Automation sendet automatisch einen internen Stopp-Befehl für eventuell gestartete Skills/Musik und bestätigt direkt):
- 🗣️ *„Alexa, **Idee** Rasensprenger reparieren.“* ➔ `Haus & Garten`
- 🗣️ *„Alexa, **Notiere** Kellerlicht dimmen.“* ➔ `Smarthome`
- 🗣️ *„Alexa, **Merke dir für den Garten** Tomaten düngen.“* ➔ `Haus & Garten`
- 🗣️ *„Alexa, **Brainstorm** Balkonkraftwerk Ertrag auswerten.“* ➔ `Smarthome`
- 🗣️ *„Alexa, **Neue Idee für Projekte** Smart Mirror bauen.“* ➔ `Projekte`

#### Variante C: Eigener Alexa-Skill (optional, ein Satz, eine Antwort)
Ohne Skill antwortet Alexa auf *„Alexa, notiere …“* oft zuerst mit einer Fehlermeldung, weil sie den Befehl nicht kennt. Mit deinem eigenen Skill gibt es nur eine einzige Antwort:

> 🗣️ *„Alexa, sage Brainstorm notiere Kellerlicht dimmen.“*  
> 🤖 **Alexa:** *„Gespeichert unter Smarthome.“*

Der Skill gehört dir allein und spricht nur mit deinem eigenen Home Assistant. **Voraussetzungen:** ein kostenloses [Amazon-Entwicklerkonto](https://developer.amazon.com/alexa/console/ask) mit demselben Konto wie deine Echos und ein aus dem Internet per HTTPS erreichbares Home Assistant (z. B. über Home Assistant Cloud). Home Assistant zeigt das Sprachmodell in seiner eigenen Sprache an. Es gibt Deutsch und Englisch, andere Sprachen bekommen das englische. Der Skill antwortet in der Sprache der Anfrage.

> 🎬 **Lieber zuschauen?** Das [Video zur Einrichtung](docs/video-alexa-skill.md) zeigt jede Einstellung in einem eigenen Kapitel (6 Minuten).

1. Gehe in Home Assistant auf **Brainstorm Hub ➔ Konfigurieren ➔ Alexa-Spracheingabe & Skill**, wähle **Skill** oder **Beide** und klicke auf **Weiter**. Lass dieses Fenster offen, es zeigt die beiden Felder zum Kopieren.
2. Klicke in der [Alexa-Entwicklerkonsole](https://developer.amazon.com/alexa/console/ask) auf **Create Skill** und wähle: Name `Brainstorm`, Sprache **German (DE)**, Typ **Custom**, Hosting **Alexa-hosted (Python)**, Vorlage **Start from Scratch**.
3. Öffne **Build ➔ Interaction Model ➔ JSON Editor**, ersetze den Inhalt durch das Feld **Sprachmodell**, klicke auf **Save** und danach auf **Build** und warte auf die Erfolgsmeldung.
4. Ersetze im Tab **Code** den Inhalt von `lambda_function.py` durch das Feld **Skill-Code** und klicke auf **Deploy**.
5. Stelle im Tab **Test** oben **Development** ein.
6. Klicke in Home Assistant auf **Absenden** und sprich am Echo: *„Alexa, sage Brainstorm notiere Testidee.“* Die erste Anfrage koppelt deinen Skill, andere Skills werden danach abgewiesen. Unter **Konfigurieren** siehst du die Kopplung und die letzte Anfrage.

**Hinweise:** Halte den Skill-Code geheim, er enthält deine geheime Adresse. Wurde sie bekannt, erzeugst du dort eine neue und kopierst den Skill-Code erneut. Die Echo-Auswahl und die Geräteanzeige gelten auch im Skill. Dafür lernt Home Assistant jeden Echo beim ersten Satz aus dem Alexa-Verlauf (das braucht die Integration Alexa Media); dieser erste Satz kann bis zu 3,5 Sekunden länger dauern. Kommt der Eintrag im Verlauf später, wird die Idee trotzdem gespeichert und der Echo nachgetragen. Im Menü brauchst du ein Befehlswort wie *„notiere …“* oder einen Satzanfang wie *„wir brauchen …“*, *„wir müssen …“*, *„ich muss …“*. **Freie Sätze ohne Befehlswort** (*„Alexa, sage Brainstorm Duschgel ist alle“*) gibt Alexa dem Skill nicht weiter. Seit v1.6.20 holt Home Assistant solche Sätze aus dem Alexa-Verlauf des Echos (über Alexa Media) und speichert sie trotzdem. Alexa antwortet sofort mit *„Okay, notiert“*. Den Satz schreibt Alexa erst mit dieser Antwort in den Verlauf, deshalb erscheint der Eintrag wenige Sekunden später. Home Assistant erkennt den passenden Verlaufseintrag an genau dieser Antwort. Kommt innerhalb einer Minute keiner, meldet Home Assistant das als Benachrichtigung, statt den Satz still zu verlieren. Für die Alexa-App, die keinen Verlauf meldet, bleibt der Hinweis auf ein Befehlswort. Dafür musst du den Skill-Code einmal neu kopieren. Im Modus **Skill** solltest du die Alexa-Routinen für *„öffne Brainstorm“* aus Variante A löschen, sonst startet statt des Skills der alte Dialog. Der Modus **Skill** schaltet die bisherige Erfassung ab, wenn deine Automation das Attribut `voice_mode` von `sensor.brainstorm_ideen_ubersicht` prüft:

```yaml
- condition: template
  value_template: "{{ state_attr('sensor.brainstorm_ideen_ubersicht', 'voice_mode') != 'skill' }}"
```

**Falls es nicht klappt:** *„Ich weiß nicht, wie ich dabei helfen soll“* bedeutet meist, dass der **Build** fehlt, im Tab **Test** nicht **Development** eingestellt ist oder Konsole und Echo verschiedene Amazon-Konten nutzen. Teste den Satz zuerst im Tab **Test**. Sagt Alexa, die Idee wurde nicht gespeichert, prüfe den Modus und die Erreichbarkeit von Home Assistant.

---

### 2. Home Assistant Assist

Assist versteht deine Notizen sowohl über dedizierte Sprachmuster als auch über Standard-Listenbefehle:

#### Freie Brainstorm-Befehle:
* 🗣️ *„Setze Rasenmähen auf Brainstorm“*
* 🗣️ *„Neue Idee Blumen gießen“*
* 🗣️ *„Notiere Backup der Datenbank erstellen“*
* 🗣️ *„Merke dir Reifen wechseln“*
* 🗣️ *„Brainstorm Zigbee Bewegungsmelder testen“*

Die Vorlagen liegen unter [`examples/custom_sentences/de/brainstorm.yaml`](examples/custom_sentences/de/brainstorm.yaml) und [`examples/intent_script.de.yaml`](examples/intent_script.de.yaml). Kopiere die erste nach `/config/custom_sentences/de/`, ergänze die zweite in deinem `intent_script` und starte Home Assistant neu.

#### Native Listenbefehle:
* 🗣️ *„Setze Rasenmähen auf die Liste Brainstorm Haus und Garten“*
* 🗣️ *„Füge Milch zu Brainstorm Inbox hinzu“*
* 🗣️ *„Hake Rasenmähen auf Brainstorm Haus und Garten ab“*

### 3. iPhone: Kurzbefehl mit Siri, Action-Taste oder Rückseite
Der schnellste Weg vom iPhone: auslösen, sprechen, fertig, ganz ohne eine App zu öffnen. Voraussetzung ist die Home Assistant Companion-App.

1. Lege in der App **Kurzbefehle** einen neuen Kurzbefehl namens **Brainstorm** an. Der Name ist auch dein Siri-Satz.
2. Füge **Text diktieren** hinzu, Sprache **Deutsch**, Hören stoppen **Nach einer Pause**.
3. Füge von **Home Assistant** die Aktion **Aktion ausführen** hinzu und wähle **Idee hinzufügen** (`brainstorm.add_idea`).
4. Füge in das Datenfeld dieses JSON ein und setze zwischen die Anführungszeichen hinter `"text":` die Variable **Diktierter Text**:
   ```json
   {"text": "", "source": "siri", "device": "iPhone"}
   ```
5. Lege den Auslöser fest:
   - **Action-Taste:** **Einstellungen ➔ Action-Taste ➔ Kurzbefehl ➔ Brainstorm**
   - **Rückseite:** **Einstellungen ➔ Bedienungshilfen ➔ Tippen ➔ Auf Rückseite tippen ➔ Doppeltippen ➔ Brainstorm**
   - **Siri:** *„Hey Siri, Brainstorm“*

Die Notiz erscheint als **Siri (iPhone)** mit Apfel-Logo. Den Gerätenamen kannst du im JSON frei wählen.

> [!TIP]
> Meldet der Kurzbefehl *„Die Daten konnten nicht gelesen werden“*, ist das Datenfeld kein gültiges JSON. Oft hat das iPhone beim Tippen typografische Anführungszeichen eingesetzt. Füge den Text deshalb per Kopieren ein oder schalte vorübergehend **Einstellungen ➔ Allgemein ➔ Tastatur ➔ Intelligente Interpunktion** aus.

### 4. Mikrofon in der Schnelleingabe
Neben dem Feld *Blitz-Idee* der Listenkarte gibt es ein **🎙️**. Tippen, sprechen, und der Text steht zum Prüfen im Feld. Die Aufnahme endet bei einer Sprechpause, durch erneutes Tippen oder nach 30 Sekunden. Genutzt wird deine bevorzugte Assist-Pipeline, die dafür eine Spracherkennung braucht. Das Mikrofon erscheint nur über HTTPS, also in der Companion-App oder über eine HTTPS-Adresse wie Home Assistant Cloud. Abschalten kannst du es in den Karteneinstellungen oder mit `show_mic: false`.

---

## 👥 Privatsphäre & Freigaben

Standardmäßig sehen alle Benutzer deines Home Assistant alle Einträge. Unter **Brainstorm Hub ➔ Konfigurieren ➔ Privatsphäre & Benutzer** kannst du das ändern. Wähle dabei einen **Hauptbenutzer**, dem alle vorhandenen Einträge gehören.

- **Eingeschaltet:** Jeder Eintrag gehört der Person, die ihn angelegt hat, und nur sie sowie Personen mit Freigabe sehen ihn.
- **Einzelne Einträge:** Eintrag lange drücken ➔ **👥 Freigeben**, pro Person *Ansehen* oder *Bearbeiten*, oder für *Alle Benutzer*.
- **Kategorien:** Kategorie auswählen ➔ **👥 … freigeben**. Das gilt für deine eigenen Einträge darin, auch für spätere.
- **Mehrere Einträge:** **☑️ Auswählen**, dann auf einmal erledigen, verschieben, freigeben oder löschen. Das geht auch ohne Privatsphäre.
- **Rechte:** *Bearbeiten* erlaubt Ändern und Abhaken. Löschen und Weitergeben bleiben beim Besitzer.
- **In fremde Listen schreiben:** Gibt dir jemand eine Kategorie persönlich mit *Bearbeiten* frei, landen deine neuen Einträge darin in seiner Liste und gehören ihm. Das gilt auch für Unteraufgaben zu seinen Einträgen. Eine Freigabe für *Alle Benutzer* zählt dafür nicht, und haben dir mehrere Personen dieselbe Kategorie freigegeben, bleibt der Eintrag deiner.
- **Wer hat es eingetragen:** Stammt ein Eintrag in deiner Liste von jemand anderem, zeigen beide Karten ein Abzeichen mit seinem Namen, etwa *✍️ Claude*. Hat seine Person in Home Assistant ein Bild, erscheint in der Listenkarte das Bild statt ✍️. So erkennst du auf einen Blick, was eine KI über ihren eigenen Benutzer angelegt hat.
- **Echos und Alexa-Apps:** Unter **Echos & Apps Personen zuordnen** gehört jedes Gerät einer Person. Was dort gesagt wird, gehört ihr, und nur ihre Einträge werden vorgelesen. Home Assistant erkennt keine Stimmen, und im Raum hören alle mit.

> [!IMPORTANT]
> Administratoren und alle mit Zugriff auf die Dateien können weiterhin alles lesen. Die To-do-Listen von Home Assistant zeigen nur, was für alle freigegeben ist, weil sie alle Benutzer lesen können. Bestehende Markdown-Exporte bleiben beim Einschalten liegen; neue entstehen nur, wenn du das erlaubst.

## 🤖 Brainstorm als Aufgabenliste für Coding-KIs

Eine Kategorie kann das Backlog eines Programmierprojekts sein: Du sammelst Aufgaben per Alexa, Karte oder Assist, und eine Coding-KI wie Claude Code liest sie über einen MCP-Server für Home Assistant, setzt sie um und hakt sie mit einer **Ergebnis-Notiz** ab. Beide Karten zeigen diese Notiz unter dem Eintrag, so siehst du ohne Nachfragen, was daraus geworden ist.

**Einrichtung**

1. **Eigener Benutzer für die KI:** Unter [**Einstellungen ➔ Personen**](https://my.home-assistant.io/redirect/people/) einen Benutzer anlegen, etwa *Claude*. Bekommt seine Person ein Bild, zeigen die Karten es an den Einträgen, die die KI anlegt.
2. **Token:** Als dieser Benutzer anmelden, unter [**Profil ➔ Sicherheit**](https://my.home-assistant.io/redirect/profile_security/) ein langlebiges Zugriffstoken erstellen und damit den MCP-Server verbinden, zum Beispiel [ha-mcp](https://github.com/homeassistant-ai/ha-mcp). Ob der Benutzer Adminrechte braucht, hängt davon ab, wie ha-mcp läuft, siehe Hinweis unten.
3. **Privatsphäre einschalten** (siehe oben) und die Backlog-Kategorie für den KI-Benutzer freigeben: *Ansehen* zum Lesen, *Bearbeiten*, wenn er abhaken darf. Alles andere bleibt für ihn unsichtbar.
4. **Skill installieren:** Den Ordner [`examples/claude-code/skills/brainstorm-backlog`](examples/claude-code/skills/brainstorm-backlog/SKILL.md) nach `~/.claude/skills/` kopieren (für alle Projekte) oder nach `.claude/skills/` im Projekt.
5. **Kategorie nennen:** In `CLAUDE.md` oder `AGENTS.md` des Projekts eintragen, etwa: *„Das Backlog ist die Brainstorm-Kategorie ‚Brainstorm‘.“*

**Arbeitsregeln des Skills**

- Gelesen wird nur über `brainstorm.get_ideas`, nie über die Datei in `.storage`. So sieht die KI nur, was freigegeben ist.
- Unteraufgaben werden in ihrer Reihenfolge erledigt, Bedingungen im Text („erst prüfen, ob …“) zuerst.
- Beginnt sie mit einem Eintrag, markiert sie ihn mit `in_progress: true`. Beide Karten zeigen dann **🔧 In Arbeit** mit dem Namen des KI-Benutzers, mit der Maus über dem Abzeichen steht, seit wann. Abhaken entfernt die Markierung, hört die KI vorher auf, entfernt sie sie mit `in_progress: false`. Du kannst die Markierung auch selbst im Menü bei langem Drücken setzen und entfernen (v1.7.10).
- Abgehakt wird nur, was umgesetzt, getestet und eingecheckt ist, mit `status: completed` und einem kurzen `result` (Version, Änderung, Test, offene Punkte). Die Antwort nennt jeden abgehakten Eintrag.
- Löschen, Freigaben und Einstellungen bleiben bei dir. Lehnt eine Aktion ab, sagt die KI dir, welche Freigabe fehlt, statt es anders zu versuchen.

> [!NOTE]
> **Admin oder nicht?** Brainstorm selbst braucht für Lesen, Anlegen, Bearbeiten und Abhaken keine Adminrechte; nur das Entfernen von Kategorien und der Markdown-Export verlangen sie, solange die Privatsphäre an ist. Ein Benutzer ohne Adminrechte ist die sicherere Wahl, weil ein Administrator über andere Wege, etwa Dateizugriff, auch private Einträge lesen kann. Ob das geht, hängt davon ab, wie ha-mcp läuft (geprüft im Code von ha-mcp 9.1.0, noch nicht live ausprobiert):
>
> - **ha-mcp als eigener Server oder als App (Add-on)**, verbunden mit `HOMEASSISTANT_TOKEN`: Ein Token eines Benutzers ohne Adminrechte funktioniert. ha-mcp unterstützt das nicht offiziell und warnt davor; seine Admin-Werkzeuge (Automationen, Konfiguration, Logs und Ähnliches) schlagen fehl. Aktionen laufen über den WebSocket, `brainstorm.get_ideas` und `brainstorm.update_idea` gehen also. ha-mcp meidet die REST-Pfade, die nur Admins dürfen, damit abgelehnte Anfragen nicht als Fehlanmeldung zählen und seine Adresse nicht gesperrt wird.
> - **HA-MCP-Integration (Server in Home Assistant, über HACS):** Sie spricht immer mit dem Token eines Administrators mit Home Assistant und prüft das bei jedem Start. Der KI-Benutzer muss hier also Administrator sein. Erstelle das Token trotzdem als dieser Benutzer: Brainstorm zeigt der KI dann nur die freigegebenen Kategorien, und die Karten zeigen ihre Einträge unter ihrem Namen. Dateizugriff bleibt ihr aber möglich.

---

## 🎛️ Alle Einstellungen

Eine Übersicht mit typischen Beispielen pro Menü steht in der [Anleitung](docs/anleitung.md#41-integration).

### Bei der Einrichtung

Du kannst sie später unter **Neu konfigurieren** ändern. Keine davon ist Pflicht, die Vorgaben funktionieren für alle.

| Feld | Was es bewirkt |
| :--- | :--- |
| Kategorien ohne Notizen (0) ausblenden | Blendet Kategorien ohne Notizen auf den Karten aus. |
| Ideen automatisch als Markdown-Dateien exportieren | Schreibt bei jeder Änderung pro Kategorie eine Markdown-Datei in den unten genannten Ordner. |
| Dateipfad für Markdown-Dateien | Ordner für die Markdown-Dateien, zum Beispiel /config/brainstorm. |

Neu konfigurieren bietet zusätzlich:

| Feld | Was es bewirkt |
| :--- | :--- |
| Intelligente Text-Optimierung | Korrigiert Groß-/Kleinschreibung und Grammatik neuer Ideen und entfernt Füllwörter. |

### Nach der Einrichtung

Du findest sie unter [**Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm).

#### Brainstorm › Kategorien

| Feld | Was es bewirkt |
| :--- | :--- |
| ➕ Neue Kategorie anlegen (optional) | Name einer neuen Kategorie. Leer lassen, um keine anzulegen. |
| 🗑️ Kategorie löschen (optional) | Die Ideen einer gelöschten Kategorie wandern in die Inbox. |
| ✏️ Komplette Liste anpassen (durch Komma getrennt) | Alle Kategorien, durch Komma getrennt. Ändere die Liste, um mehrere auf einmal umzubenennen, umzusortieren oder zu entfernen. |
| Kategorien ohne Notizen (0) ausblenden | Blendet Kategorien ohne Notizen auf den Karten aus. |

#### Brainstorm › Kategorie-Design

| Feld | Was es bewirkt |
| :--- | :--- |
| Kategorie auswählen | Die Kategorie, deren Icon und Farbe du ändern möchtest. |

#### Brainstorm › Kategorie-Design

| Feld | Was es bewirkt |
| :--- | :--- |
| Kategorie-Icon (Home Assistant / MDI) | Wird für diese Kategorie auf den Karten angezeigt. |
| Kategorie-Farbe | Farbe dieser Kategorie auf den Karten. |
| Auf Standard-Icon und -Farbe zurücksetzen | Entfernt Icon und Farbe dieser Kategorie und ignoriert die beiden Felder darüber. |

#### Brainstorm › Allgemein

| Feld | Was es bewirkt |
| :--- | :--- |
| Standard-Kategorie für neue Ideen | Wird genutzt, wenn eine Idee keiner Kategorie zugeordnet werden kann. |
| Intelligente Text-Optimierung (Grammatik, Groß-/Kleinschreibung, Infinitiv) | Korrigiert Groß-/Kleinschreibung und Grammatik neuer Ideen und entfernt Füllwörter. |
| Datum aus gesprochenem Text als Termin übernehmen | Ein gesprochenes „morgen“ oder „am 25.11.“ wandert aus dem Text in den Termin. Ein Termin löst zu dieser Zeit eine Erinnerung aus, ohne Uhrzeit um 9 Uhr. |
| Eigene Begriffe für gesprochenen Text | Ein Begriff pro Zeile, zum Beispiel Lenia, oder eine Korrektur, zum Beispiel fehler = Richtig. Namen von Personen und Kategorien sind automatisch bekannt. |
| Ideen automatisch als Markdown exportieren | Schreibt bei jeder Änderung pro Kategorie eine Markdown-Datei in den unten genannten Ordner. |
| Dateipfad für Markdown-Dateien | Ordner für die Markdown-Dateien, zum Beispiel /config/brainstorm. |
| Echo-Geräte für die Spracheingabe | Nur diese Echos können Ideen per Sprache erfassen und Brainstorm öffnen. Leer lassen, um alle Echos zu nutzen. |

#### Brainstorm › Alexa

| Feld | Was es bewirkt |
| :--- | :--- |
| Spracheingabe | Nativ nutzt den Satz über Alexa Media ohne Skill. Skill und Beide nutzen deinen eigenen Alexa-Skill. |

#### Brainstorm › Alexa › Skill

| Feld | Was es bewirkt |
| :--- | :--- |
| Skill-Code (lambda_function.py) | Kopiere das in die lambda_function.py deines Skills. Halte es geheim, es enthält deine geheime Adresse. |
| Sprachmodell (JSON-Editor) | Füge das im JSON-Editor der Alexa Developer Console ein. |
| Neue geheime Adresse erzeugen und Skill-Kopplung entfernen | Nutze das, wenn die Adresse bekannt wurde oder du einen neuen Skill gebaut hast. Kopiere danach den neuen Skill-Code. |
| Name für dieses unbekannte Gerät | Zum Beispiel Alexa App iPhone. Home Assistant kann die Alexa-App nicht selbst erkennen. Der Name gilt für den letzten Eintrag und alle späteren von diesem Gerät. |

#### Brainstorm › Erinnerungen › Ein/Aus & Kanäle

| Feld | Was es bewirkt |
| :--- | :--- |
| Erinnerungen nutzen | Aus stoppt alle Erinnerungen, das Briefing, den Rückblick und alles andere in diesem Menü. |
| Alexa-Ansage | Welcher Echo eine Erinnerung ansagt. Aus bedeutet keine Ansage. |
| Echos für Ansagen | Für feste Echos, als Ersatz sowie für Briefing und Rückblick. |
| Benachrichtigungen senden | Aus stoppt die Benachrichtigungen, die gewählten Dienste bleiben erhalten. |
| Benachrichtigungsdienste | Diese Dienste erhalten Erinnerungen, zum Beispiel dein Handy. |
| Wartezeit vor Benachrichtigungen (Minuten) | Nur mit Alexa: Du hast Zeit zu reagieren, bevor das Handy benachrichtigt wird. Bei 0 kommt beides sofort. |
| Wichtige offene Einträge erneut senden | Sendet Einträge mit hoher oder dringender Priorität erneut, solange sie offen sind. |
| Dienste für wichtige Einträge | Diese Dienste erhalten die wiederholte Nachricht. |
| Erneut senden nach (Minuten) | Gilt für noch offene Einträge mit hoher oder dringender Priorität. |

#### Brainstorm › Erinnerungen › Ruhezeit, Briefing & Rückblick

| Feld | Was es bewirkt |
| :--- | :--- |
| Ruhezeit nutzen | Aus ignoriert die Zeiten darunter, sie bleiben aber erhalten. |
| Ruhezeit von | Erinnerungen warten bis zum Ende der Ruhezeit. Dringende Einträge erreichen die Benachrichtigungsdienste trotzdem, aber kein Echo spricht. |
| Ruhezeit bis | Zu dieser Zeit werden wartende Erinnerungen gesendet. |
| Tägliches Briefing | Sendet einmal täglich eine Übersicht des Tages. |
| Uhrzeit des Briefings | Wann das Briefing gesendet wird. |
| Nur wenn hier jemand erkannt wird | Optional: Das Briefing wartet nach seiner Uhrzeit bis zu 6 Stunden, bis ein Sensor oder eine Person hier jemanden meldet. |
| Wochenrückblick | Sendet einmal pro Woche eine Übersicht älterer offener Einträge. |
| Tag des Rückblicks | Der Wochentag des Rückblicks. |
| Uhrzeit des Rückblicks | Wann der Rückblick gesendet wird. |
| Einträge nennen, die länger offen sind als (Tage) | Einträge, die länger offen sind, erscheinen im Rückblick. |

#### Brainstorm › Erinnerungen › Regeln pro Liste

| Feld | Was es bewirkt |
| :--- | :--- |
| Regeln pro Liste nutzen | Aus lässt alle Listen die normalen Einstellungen nutzen, die Regeln bleiben erhalten. |
| Liste bearbeiten | Wähle eine Liste, um ihre Regel auf der nächsten Seite zu bearbeiten. |

#### Brainstorm › Erinnerungen › Regeln › …

| Feld | Was es bewirkt |
| :--- | :--- |
| Erinnerungen dieser Liste gehen an | Normale Kanäle folgen den allgemeinen Einstellungen der Erinnerungen. |
| Eigene Benachrichtigungsdienste für diese Liste | Ersetzen die normalen Dienste für diese Liste. Leer nutzt die normalen. |
| Offene Einträge an bestimmten Tagen senden | Sendet die offenen Einträge dieser Liste an den Tagen und zur Uhrzeit darunter. |
| Tage | Die Tage, an denen die Liste gesendet wird. |
| Uhrzeit | Wann die Liste an diesen Tagen gesendet wird. |
| Offene Einträge an einem Ort senden | Wird einmal am Tag gesendet, wenn jemand dort ankommt. Braucht den Schalter für Orte. |
| Ort | Die Zone, in der die offenen Einträge dieser Liste gesendet werden. |

#### Brainstorm › Erinnerungen › Orte & Heimkommen

| Feld | Was es bewirkt |
| :--- | :--- |
| Beim Heimkommen erinnern | Damit kannst du sagen, dass eine Erinnerung beim Heimkommen kommen soll. |
| An Orten (Zonen) erinnern | Damit kannst du für eine Erinnerung eine Zone nennen, zum Beispiel einen Supermarkt. |
| Wer mit "ich" gemeint ist | Ohne Person löst jeder aus, der dort ankommt. |

#### Brainstorm › Erinnerungen › Personen

| Feld | Was es bewirkt |
| :--- | :--- |
| Erinnerungen für andere Personen nutzen | Damit kann eine Erinnerung für jemand anderen sein, zum Beispiel: erinnere Alex. |
| Person bearbeiten | Wähle eine Person, um ihre Kanäle auf der nächsten Seite einzustellen. |

#### Brainstorm › Erinnerungen › Personen › …

| Feld | Was es bewirkt |
| :--- | :--- |
| Benachrichtigungsdienste | Die Benachrichtigungsdienste dieser Person. |
| Echos | Die Echos, die die Erinnerungen dieser Person ansagen. |

#### Brainstorm › Erinnerungen › Kalender & Alexa

| Feld | Was es bewirkt |
| :--- | :--- |
| Erinnerungen in einen Kalender eintragen | Nur in eine Richtung und einmal pro Erinnerung. Spätere Änderungen werden nicht übertragen. |
| Kalender | Der Kalender, der die Erinnerungen erhält. |
| Zusätzlich echte Alexa-Erinnerungen anlegen | Schalte in der Alexa-Konsole zusätzlich Reminders unter Build ➔ Permissions ein. Alexa klingelt dann selbst, und Home Assistant spricht nicht zusätzlich. |

#### Brainstorm › KI

Brainstorm nutzt eine KI-Aufgaben-Entität von Home Assistant, etwa Google Gemini, OpenAI oder Ollama. Ohne Entität bleibt alles aus.

| Feld | Was es bewirkt |
| :--- | :--- |
| KI-Aufgaben-Entität | Ist sie gewählt, schlägt ✨ an einer Notiz der Mindmap Unteraufgaben vor. Gesendet werden nur diese Notiz, ihre Kategorie und ihre Unteraufgaben, und nur, wenn du den Knopf drückst. |
| Gesprochene Einträge per KI verbessern | Jeder gesprochene Eintrag wird zuerst gespeichert und wenige Sekunden später verbessert. Das Ergebnis wird verworfen, wenn es Wörter hinzufügt oder eine Verneinung ändert. Der Text geht an den Anbieter der gewählten KI. |
| Briefing und Rückblick per KI kürzen | Morgen-Briefing und Wochenrückblick der Erinnerungen werden gekürzt. Deine Einträge gehen dafür an den Anbieter der gewählten KI. |

#### Brainstorm › Erledigte Einträge löschen

Die Seite zeigt, wie viele erledigte (abgehakte oder archivierte) Einträge es gibt. Gelöschte Einträge lassen sich nicht zurückholen, exportiere sie vorher, wenn du sie behalten willst.

| Feld | Was es bewirkt |
| :--- | :--- |
| Erledigte Einträge löschen nach (Tagen) | Einträge, die so viele Tage erledigt sind, werden von selbst gelöscht, geprüft alle sechs Stunden und einmal direkt beim Speichern. 0 (Standard) behält sie. Offene Unteraufgaben bleiben als Hauptaufgaben, Anhänge gehen mit. |
| Alle erledigten Einträge jetzt löschen | Löscht beim Speichern jeden erledigten Eintrag, egal wie lange er schon erledigt ist. Das Menü zeigt danach, wie viele es waren. |

#### Brainstorm › To-do-Listen koppeln

Ein Feld pro Kategorie. Wähle eine To-do-Liste einer anderen Integration, etwa Bring!, Google Tasks, Todoist oder eine lokale To-do-Liste, und beide bleiben gleich:

| Was passiert | Auf der Liste | In Brainstorm |
| :--- | :--- | :--- |
| Etwas kommt dazu | wird zur Notiz in der Kategorie | eine aktive Notiz landet auf der Liste |
| Etwas wird umbenannt oder abgehakt | die Notiz zieht mit | der Eintrag zieht mit |
| Etwas wird gelöscht | ein entfernter Eintrag hakt seine Notiz ab | eine gelöschte Notiz entfernt ihren Eintrag |

- **Wann:** sofort nach einer Änderung in Brainstorm oder einem neuen Eintrag auf der Liste, und alle 5 Minuten für Umbenennungen, die Listen nicht melden.
- **Beide geändert:** Wurde derselbe Eintrag zwischen zwei Abgleichen auf beiden Seiten umbenannt, gewinnt der Name auf der Liste.
- **Erstes Koppeln:** Offene Einträge mit gleichem Text werden verbunden statt verdoppelt, und die Schreibweise der Liste gewinnt. Erledigte Notizen kommen nicht auf die Liste.
- **Fälligkeiten** gehen auf die Liste, wenn sie welche kennt, als Datum mit Uhrzeit oder als Datum. Geänderte Fälligkeiten auf der Liste werden nicht übernommen.
- **Privatsphäre:** Ist sie an, werden nur Notizen abgeglichen, die mit allen geteilt sind, denn jeder mit Zugriff auf die andere Liste sieht sie. Einträge von der Liste sind mit allen geteilt.
- **Entkoppeln:** Ein geleertes Feld entkoppelt die Liste. Ihre Einträge bleiben, wo sie sind.
- Jede Liste lässt sich nur mit einer Kategorie koppeln, und die eigenen Listen von Brainstorm stehen nicht zur Wahl.

#### Brainstorm › 🛒 Bring!

Erscheint nur, wenn die Integration [Bring!](https://www.home-assistant.io/integrations/bring/) eingerichtet ist. Alle Bring-Listen landen in einer Kategorie: Jede Liste wird eine Hauptnotiz, ihre Artikel werden zu Unteraufgaben.

```
🛒 Einkauf
├─ 🏠 Zu Hause
│   ├─ Milch
│   └─ Brot
└─ 🚐 Camper
    └─ Gas
```

| Feld | Was es bewirkt |
| :--- | :--- |
| Bring! synchronisieren | Schaltet den Abgleich ein oder aus. Ausgeschaltet bleiben Notizen und Artikel, wo sie sind. |
| Kategorie | Wähle eine Kategorie oder tippe einen neuen Namen, sie wird beim Speichern angelegt. |
| Listen | Leer lassen, um alle Listen abzugleichen, auch später hinzugefügte. |
| Standardliste | Notizen, die ohne Liste in die Kategorie kommen, etwa *„wir brauchen Milch“* per Sprache, landen auf dieser Liste und hängen unter ihrer Notiz. |
| Gekauftes ausblenden nach (Tagen) | Abgehakte Einträge verschwinden nach so vielen Tagen (Standard 3) aus der Erledigt-Ansicht und werden archiviert. In Bring bleiben sie in den zuletzt gekauften Einträgen zum erneuten Kaufen. 0 behält sie. |
| Kategorie mit allen teilen | Nur mit Privatsphäre sichtbar. Abgeglichen werden nur Notizen, die mit allen geteilt sind, denn jeder mit Zugriff auf Bring sieht sie. |

- **Beide Richtungen:** Neue Artikel, Abhaken und Löschen gehen zwischen Brainstorm und Bring hin und her. Abhaken schiebt den Artikel in Bring unter *Zuletzt verwendet*.
- **Verschieben:** Hängst du eine Unteraufgabe unter eine andere Listen-Notiz, wandert der Artikel auf diese Liste.
- **Schon mal gekauft:** Eine Notiz mit dem Namen eines Artikels aus *Zuletzt verwendet* holt diesen zurück, statt ihn doppelt anzulegen, denn Bring erlaubt jeden Namen nur einmal pro Liste.
- **Mengen:** Die Spezifikation eines Bring-Artikels, etwa *1,5 l*, wird an der Notiz gespeichert (Feld `spec`).
- **Listen-Notizen** übernehmen ihren Namen von Bring. Eine gelöschte Listen-Notiz kommt mit ihren Artikeln zurück, die Notiz einer nicht mehr abgeglichenen Liste wird archiviert.
- **Schnell:** Änderungen anderer werden über die Aktivitäts-Ereignisse von Bring erkannt, zusätzlich wird alle 5 Minuten verglichen.

#### Brainstorm › Erinnerungen › Sperrzeiten pro Echo

Hält einzelne Echos zu festen Zeiten für Brainstorm still, etwa nachts im Kinderzimmer (v1.7.7). Bis zu drei Sperrzeiten, jede für ein oder mehrere Echos, auch über Mitternacht.

| Feld | Was es bewirkt |
| :--- | :--- |
| Echos 1 | Die Echos von Sperrzeit 1. Leer entfernt sie. |
| Von 1 | Beginn von Sperrzeit 1. |
| Bis 1 | Ende von Sperrzeit 1. Früher als der Beginn heißt am nächsten Morgen. |
| Auch „Nicht stören“ 1 | Schaltet „Nicht stören“ dieser Echos zu Beginn ein und am Ende aus, dann ist auch Alexa selbst still. Braucht Alexa Media Player. |
| Echos 2 | Die Echos von Sperrzeit 2. Leer entfernt sie. |
| Von 2 | Beginn von Sperrzeit 2. |
| Bis 2 | Ende von Sperrzeit 2. Früher als der Beginn heißt am nächsten Morgen. |
| Auch „Nicht stören“ 2 | Schaltet „Nicht stören“ dieser Echos zu Beginn ein und am Ende aus, dann ist auch Alexa selbst still. Braucht Alexa Media Player. |
| Echos 3 | Die Echos von Sperrzeit 3. Leer entfernt sie. |
| Von 3 | Beginn von Sperrzeit 3. |
| Bis 3 | Ende von Sperrzeit 3. Früher als der Beginn heißt am nächsten Morgen. |
| Auch „Nicht stören“ 3 | Schaltet „Nicht stören“ dieser Echos zu Beginn ein und am Ende aus, dann ist auch Alexa selbst still. Braucht Alexa Media Player. |

- **Andere Echos sprechen weiter:** Eine Erinnerung geht weiter an die Echos der Erinnerung, die nicht gesperrt sind.
- **Handy als Ersatz:** Ist kein Echo mehr übrig, geht die Erinnerung sofort aufs Handy statt erst nach der Wartezeit.
- **Test:** *🧪 Kanäle jetzt testen* spricht auch in einer Sperrzeit, weil du ihn selbst startest.

#### Brainstorm › 🔋 Batterien

Macht aus schwachen Batterien Aufgaben (v1.7.5). Jeder Batterie-Sensor zählt: ein Stand in Prozent oder ein Sensor, der nur „Batterie schwach“ meldet.

| Feld | Was es bewirkt |
| :--- | :--- |
| Batterie-Aufgaben anlegen | Schaltet die Batterie-Aufgaben ein oder aus. Ausgeschaltet entstehen keine neuen, vorhandene bleiben. |
| Schwelle | Bei diesem Stand oder darunter entsteht eine Aufgabe (Standard 20 %). |
| Kategorie | Wähle eine Kategorie oder tippe einen neuen Namen, sie wird beim Speichern angelegt. Vorgeschlagen wird *Smarthome*. |
| Auslassen | Batterien, die nie eine Aufgabe anlegen sollen, etwa ein Hausakku. Ein ausgelassener Sensor lässt sein ganzes Gerät aus. |
| Handys und Tablets einbeziehen | Geräte der Companion-App werden täglich geladen und bleiben deshalb außen vor, außer du schaltest es ein. |

- **Eine Aufgabe pro Gerät**, auch wenn Integrationen wie Battery Notes weitere Sensoren für dieselbe Batterie anlegen. Sie ist nach dem Gerät benannt, z. B. *Batterie wechseln: Bewegungsmelder Flur (18 %)*.
- **Hakt sich selbst ab:** Meldet kein Sensor des Geräts mehr eine schwache Batterie und liegt der Stand 10 Punkte über der Schwelle, wird die Aufgabe abgehakt. Der Abstand verhindert, dass eine Batterie an der Schwelle ständig Aufgaben anlegt und schließt.
- **Von Hand abgehakt**, bevor die Batterie gewechselt ist, kommt die Aufgabe nicht wieder. Erst die nächste schwache Batterie legt eine neue an.
- **Nach einem Neustart** werden alle Batterien einmal geprüft.

#### Brainstorm › Privatsphäre & Benutzer

| Feld | Was es bewirkt |
| :--- | :--- |
| Einträge privat halten | Dann sieht jede Person nur ihre eigenen Einträge und was mit ihr geteilt wurde. |
| Hauptbenutzer | Besitzt alle vorhandenen Einträge und alles, was an einem Echo gesagt wird. Sprache, Briefing und Rückblick nennen nur die Einträge dieser Person. |
| Weiter in Markdown-Dateien exportieren | Diese Dateien enthalten alle Einträge und sind für alle mit Zugriff auf den Config-Ordner lesbar. |
| Diese Benutzer für Freigaben anbieten | Leer bedeutet alle. Damit blendest du technische Konten wie MQTT aus. |

#### Brainstorm › Echos & Apps zuordnen

| Feld | Was es bewirkt |
| :--- | :--- |
| Echo oder Alexa-App | Der Echo oder die Alexa-App, die du zuordnen möchtest. Du kannst auch einen Namen eintippen. |
| Person | Leer lassen, um die Zuordnung zu entfernen. |

---

## 🧩 Entitäten

| Entität | Was sie zeigt |
|---|---|
| `sensor.brainstorm_ideen_ubersicht` | Anzahl offener Ideen. Attribute: `active_count`, `completed_count`, `category_counts`, `priority_counts`, `categories`, `active_categories`, `latest_idea`, `recent_ideas`, `ideas`, `speech_overview`, `voice_mode`, `allowed_echos`. Mit eingeschalteter Privatsphäre sind nur Zahlen zu sehen. |
| `todo.<kategorie>` | Eine To-do-Liste pro Kategorie. Einträge lassen sich in der To-do-Ansicht anlegen, umbenennen, erledigen, mit Termin versehen und löschen; die Karten zeigen das sofort. Neue Kategorien bekommen gleich eine Liste, gelöschte verlieren ihre. |

Alle Entitäten gehören zum Gerät **Brainstorm Hub**. Unter [**Einstellungen > Geräte & Dienste > Brainstorm Hub > ⋮ > Diagnose herunterladen**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) gibt es eine Datei für Fehlerberichte. Sie enthält Zahlen und Einstellungen, aber keine Ideen-Texte, Personen oder Echos.

## 🛠️ Dienste (Services)

Jede Aktion bleibt verfügbar, solange die Integration nicht geladen ist, und erklärt dann, warum sie nicht ausgeführt werden kann.

### `brainstorm.add_idea`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.add_idea)

Fügt blitzschnell eine neue Brainstorm-Idee hinzu. Erkennt automatisch Kategorien im Text (z.B. 'Garten: Blumen pflanzen' oder '#smarthome').

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `text` | Ja | Der Inhalt des Gedankens oder der Idee. |
| `category` | Nein | Thema/Kategorie. Bleibt dies leer, wird sie aus dem Text ermittelt oder 'Inbox' zugewiesen. |
| `priority` | Nein | Dringlichkeit der Idee (low, medium, high, urgent). Wird andernfalls automatisch erkannt. |
| `source` | Nein | Woher die Idee stammt (z.B. alexa, assist, dashboard). Ohne Quelle gilt der Text als getippt und behält seinen Wortlaut. Nur mit einer Sprachquelle werden gesprochene Sätze gekürzt. |
| `device` | Nein | Das auslösende Gerät (z.B. "Echo Show Küche", "Wohnzimmer Echo Dot", "Jan (Handy)"). |
| `tags` | Nein | Zusätzliche Schlagworte. |
| `parent_id` | Nein | ID der übergeordneten Idee für Unteraufgaben/Einrückung (optional). |
| `due` | Nein | Wann Brainstorm an diese Idee erinnern soll. |
| `parse_due` | Nein | Erkennt Angaben wie "morgen um 8" im Text und nimmt sie als Termin. |
| `assignee` | Nein | Wer erinnert werden soll. |
| `zone` | Nein | Erinnert beim Betreten dieser Zone. |
| `language` | Nein | Sprache des Textes (z.B. "de" oder "en"). Ohne Angabe gilt die Sprache von Home Assistant. |

### `brainstorm.update_idea`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.update_idea)

Aktualisiert Text, Kategorie oder Status einer bestehenden Idee.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | Eindeutige ID der Idee. |
| `text` | Nein | Geänderter Text. |
| `category` | Nein | Neue Kategorie. |
| `priority` | Nein | Neue Priorität (low, medium, high, urgent). |
| `status` | Nein | Neuer Status (active, completed, archived). |
| `device` | Nein | Gerät aktualisieren. |
| `parent_id` | Nein | ID der übergeordneten Idee für Unteraufgaben/Einrückung (leer = Hauptaufgabe). |
| `order` | Nein | Benutzerdefinierter Sortierindex. |
| `due` | Nein | Wann Brainstorm an diese Idee erinnern soll. |
| `assignee` | Nein | Wer erinnert werden soll. |
| `zone` | Nein | Erinnert beim Betreten dieser Zone. |
| `echos` | Nein | Die Echos, die die Erinnerung an diesen Eintrag sprechen, als Liste. `null` gilt wieder die Erinnerungs-Einstellungen. |
| `result` | Nein | Was aus dem Eintrag geworden ist, meist beim Abhaken notiert (höchstens 1000 Zeichen). Beide Karten zeigen es unter dem Text. Bleibt beim Wiederöffnen erhalten, leer oder `null` entfernt es. |
| `shape` | Nein | Form der Notiz auf der Mindmap: `card`, `cloud`, `bubble`, `thought`, `pill`, `rect`, `ellipse`, `hexagon`, `note` oder `underline`. Leer oder `null` nimmt wieder das Aussehen der Map. |
| `markers` | Nein | Marker als Liste: `question`, `idea`, `warning`, `money`, `star`, `flag`, `check`, `blocked`, `waiting`, `heart`. Ersetzt die bisherigen, eine leere Liste oder `null` entfernt sie. |
| `progress` | Nein | Fortschritt einer Notiz ohne Unteraufgaben: `0`, `25`, `50`, `75` oder `100`. `0` oder `null` entfernt ihn. Notizen mit Unteraufgaben berechnen ihn selbst. |
| `links` | Nein | Querverbindungen zu anderen Notizen als Liste von `{to: <id>, label: <Text, bis 40>, blocks: true/false}`, höchstens 20. `blocks: true` lässt das Ziel warten, bis diese Notiz erledigt ist. Ersetzt die bisherigen, eine leere Liste oder `null` entfernt sie. |
| `frame` | Nein | Name eines Rahmens in der Mindmap, bis 40 Zeichen. Notizen mit demselben Namen teilen sich einen Rahmen. Leer oder `null` entfernt ihn. |
| `callout` | Nein | Kurze Anmerkung in einer Sprechblase über der Notiz, bis 200 Zeichen. Leer oder `null` entfernt sie. |
| `repeat` | Nein | Lässt die Idee nach dem Abhaken wiederkommen: `daily`, `weekdays`, `weekly`, `biweekly`, `monthly` oder `yearly`. Die neue Idee ist zum nächsten Termin nach jetzt fällig, mit gleichen Angaben und wieder offenen Unteraufgaben. Leer oder `null` beendet es. |
| `numbering` | Nein | Nummeriert die Unteraufgaben der Notiz und deren Unteraufgaben: `decimal` (1., 1.1), `alpha` (a), b)) oder `roman` (I., II.). Leer oder `null` entfernt sie. |

### `brainstorm.delete_idea`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.delete_idea)

Entfernt eine Idee. Bis zum nächsten Start von Home Assistant holt `brainstorm.restore_idea` sie zurück.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | ID der zu löschenden Idee. |

### `brainstorm.delete_done`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.delete_done)

Löscht erledigte (abgehakte oder archivierte) Einträge auf einmal. Mit eingeschalteter Privatsphäre nur die eigenen. Gelöschte Einträge lassen sich nicht zurückholen. Die Antwort nennt die Anzahl (`deleted`).

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `older_than_days` | Nein | Nur Einträge, die mindestens so viele Tage erledigt sind. `0` (Standard) löscht alle erledigten. |

### `brainstorm.restore_idea`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.restore_idea)

Holt eine Idee zurück, die seit dem letzten Start von Home Assistant gelöscht wurde, samt der Verbindung zu ihren Unteraufgaben. Das kann nur, wer sie gelöscht hat. Die Mindmap-Karte nutzt das für „Rückgängig“.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | ID der gelöschten Idee. |

### `brainstorm.get_ideas`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.get_ideas)

Gibt eine Liste gespeicherter Ideen zurück (für Templates oder Automationen).

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Nein | Optional nach Kategorie filtern. |
| `priority` | Nein | Optional nach Priorität filtern (low, medium, high, urgent). |
| `status` | Nein | Status-Filter (active, completed oder all). |

### `brainstorm.get_announcement`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.get_announcement)

Erzeugt einen flüssigen, gesprochenen Ansagetext für Alexa oder Assist über alle oder eine bestimmte Kategorie.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Nein | Optional nach einer bestimmten Kategorie filtern (z.B. Smarthome). Ohne Angabe werden alle aktiven Kategorien vorgelesen. |
| `device` | Nein | Das Gerät, das gefragt hat. Bei eingeschalteter Privatsphäre bestimmt es, wessen Einträge genannt werden. |

### `brainstorm.add_category`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.add_category)

Erstellt eine neue Brainstorm-Kategorie und die dazugehörige To-do-Liste.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `name` | Ja | Name der neuen Kategorie. |
| `icon` | Nein | Optionales Home Assistant / MDI Icon. |
| `color` | Nein | Optionale Akzentfarbe (Hexadezimal wie #ff7800). |

### `brainstorm.set_category_style`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.set_category_style)

Legt ein benutzerdefiniertes Icon und/oder eine Akzentfarbe für eine Kategorie fest.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Ja | Name der zu formatierenden Kategorie. |
| `icon` | Nein | Home Assistant / MDI Icon. |
| `color` | Nein | Akzentfarbe für Notizen und Filter (Hexadezimal wie #06b6d4). |
| `reset` | Nein | Falls aktiviert, werden benutzerdefiniertes Icon und Farbe entfernt und auf Standard zurückgesetzt. |

### `brainstorm.remove_category`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.remove_category)

Entfernt eine Kategorie (verbleibende Ideen werden nach 'Inbox' verschoben).

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `name` | Ja | Name der Kategorie. |

### `brainstorm.export_markdown`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.export_markdown)

Schreibt alle Kategorien und Ideen als Markdown-Dateien ins Dateisystem.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `path` | Nein | Zielordner (Standard: der Markdown-Ordner aus den Optionen, `/config/brainstorm`). Nur Admins dürfen einen Ordner wählen; er muss in `/config/brainstorm`, im Markdown-Ordner aus den Optionen oder in `allowlist_external_dirs` liegen. |

### `brainstorm.export_json`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.export_json)

Gibt die Ideen, die du sehen darfst, samt Kategorien, Icons und Farben als JSON zurück. Zum Sichern, für den Umzug auf ein anderes Home Assistant oder zum Teilen einer Kategorie.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Nein | Nur diese Kategorie exportieren. Standard: alle Kategorien. |
| `path` | Nein | Den Export zusätzlich in diese Datei schreiben, etwa `brainstorm/sicherung.json` (relativ zu `/config`). Der Name muss auf `.json` enden. Erlaubt sind nur `/config/brainstorm`, der Markdown-Ordner aus den Optionen und `allowlist_external_dirs`. Nur Admins dürfen Dateien schreiben. |

```yaml
action: brainstorm.export_json
data:
  path: brainstorm/sicherung.json
response_variable: sicherung
```

### `brainstorm.import_json`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.import_json)

Fügt die Ideen eines JSON-Exports hinzu, die es hier noch nicht gibt. Ideen mit vorhandener ID werden übersprungen, zweimal dieselbe Datei zu importieren ändert also nichts. Fehlende Kategorien werden angelegt, Icons und Farben übernommen, wo eine Kategorie noch keine hat.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `data` | Eins von beiden | Die Antwort von `brainstorm.export_json`. |
| `path` | Eins von beiden | Eine von `brainstorm.export_json` geschriebene Datei, relativ zu `/config`, aus denselben Ordnern wie beim Export. Nur Admins dürfen Dateien lesen. |

Besitzer und Freigaben bleiben nur für Benutzer dieses Home Assistant erhalten, Besitzer nur, wenn ein Admin importiert. Sonst gehören die Ideen dem, der importiert. Die Antwort nennt, wie viele Ideen hinzugefügt (`added`) und übersprungen (`skipped`) wurden und welche Kategorien neu sind.

### `brainstorm.bring_message`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.bring_message)

Sagt allen auf einer Bring-Liste etwas, über die Benachrichtigungen von Bring selbst. In der Karte bietet der 🛒-Knopf einer Listen-Notiz *Ich gehe einkaufen*, *Einkauf erledigt* und *Liste geändert*; das Menü eines Eintrags auf einer Liste bietet *Dringend in Bring melden*.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | ID einer Bring-Listen-Notiz oder eines Eintrags auf so einer Liste. |
| `message` | Ja | `going_shopping`, `changed_list`, `shopping_done` oder `urgent_message`. Eine dringende Nachricht braucht einen Eintrag, dessen Text Bring mitschickt. |

### `brainstorm.reorder_ideas`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.reorder_ideas)

Aktualisiert die benutzerdefinierte Sortierreihenfolge der Notizen anhand einer Liste von IDs.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `idea_ids` | Ja | Geordnete Liste der Notiz-IDs. |

### `brainstorm.import_outline`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.import_outline)

Legt einen Baum von Notizen aus einer Markdown-Gliederung, eingerücktem Text, OPML oder einer FreeMind-/Freeplane-Map (`.mm`) an, höchstens 300 Notizen. Gibt `added` und die neuen `ids` zurück.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `text` | Ja | Die Gliederung: Überschriften, Listen mit `-`/`*`/`1.` oder eingerückte Zeilen; `- [x]` legt einen Punkt als erledigt an, eine `>`-Zeile unter einem Punkt ist seine Beschreibung. Oder der Inhalt einer OPML- oder `.mm`-Datei. |
| `format` | Nein | `auto` (Standard), `markdown`, `opml` oder `freemind`. |
| `category` | Nein | Wohin die Notizen kommen; ohne Angabe die Standardkategorie. |
| `parent_id` | Nein | Hängt die Gliederung unter diese Notiz, in deren Kategorie. |

### `brainstorm.sort_children`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.sort_children)

Sortiert die Unteraufgaben einer Notiz oder die Hauptnotizen einer Kategorie innerhalb der Plätze, die sie schon haben. Andere Notizen bleiben, wo sie sind.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `parent_id` | Nein | Die Notiz, deren Unteraufgaben sortiert werden. |
| `category` | Nein | Ohne `parent_id`: die Kategorie, deren Hauptnotizen sortiert werden. |
| `by` | Nein | `text` (A–Z), `priority` (dringend zuerst), `due` (früheste zuerst, Notizen ohne Datum am Ende) oder `created` (älteste zuerst). |
| `ids` | Nein | Statt `by`: die Unteraufgaben in fester Reihenfolge, etwa um ein Sortieren rückgängig zu machen. |
| `reverse` | Nein | Sortiert andersherum. |

### `brainstorm.share`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.share)

Gibt mehrere Einträge oder eine ganze Kategorie für Personen frei. Braucht eingeschaltete Privatsphäre.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `ids` | Nein | IDs der freizugebenden Einträge. |
| `category` | Nein | Alle eigenen Einträge dieser Kategorie freigeben, auch spätere. |
| `shares` | Ja | Benutzer-ID (oder "all") und Stufe, z. B. {"all": "view"}. Stufen sind view und edit; null entfernt die Freigabe. |

---

## 🔄 Wie die Daten aktualisiert werden

Brainstorm Hub speichert alle Ideen lokal in `.storage/brainstorm.storage` und fragt nichts in Abständen ab. Jede Änderung, ob von einer Karte, Alexa, Assist, einer Aktion oder einer To-do-Liste, aktualisiert Sensor und To-do-Listen im selben Moment und geht über die WebSocket-API an alle offenen Karten.

## 💡 Beispiele

Mehr Beispiele, auch für Ereignisse und Sensor-Attribute, stehen in der [Anleitung](docs/anleitung.md#5-automatisieren).

**Jeden Morgen die offenen Ideen vorlesen:**
```yaml
triggers:
  - trigger: time
    at: "07:30:00"
actions:
  - action: brainstorm.get_announcement
    response_variable: ueberblick
  - action: notify.alexa_media
    data:
      target: media_player.echo_kuche
      data:
        type: announce
      message: "{{ ueberblick.speech }}"
```

**Notieren, wenn die Waschmaschine fertig ist:**
```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.waschmaschine_lauft
    to: "off"
actions:
  - action: brainstorm.add_idea
    data:
      text: Wäsche aufhängen
      category: Alltag
      priority: high
```

Weitere Beispiele für Assist und Alexa liegen im Ordner [`examples/`](examples/).

## ⚠️ Bekannte Einschränkungen

- **Freie Sätze im Skill:** Alexa gibt einem Skill nur Text weiter, wenn der Satz mit einem bekannten Wort beginnt, z. B. *notiere*, *wir brauchen* oder *ich muss*. Andere Sätze enden in einem kurzen Hinweis, mit *notiere* anzufangen.
- **Echo-Erkennung** braucht die Integration Alexa Media. Ohne sie werden Ideen aus dem Skill trotzdem gespeichert, nur ohne den Echo, von dem sie kamen.
- **Der Name „Brainstorm“** ist auch eine Band. Ohne eigenen Skill oder Routinen startet Alexa womöglich Musik.
- **Erinnerungen auf Echos** werden über Alexa Media gesprochen. Echte Alexa-Erinnerungen brauchen zusätzlich die Erinnerungs-Berechtigung deines Skills.
- **Eine Installation:** Pro Home Assistant lässt sich nur ein Brainstorm Hub einrichten.

## 🩺 Fehlerbehebung

| Problem | Lösung |
|---|---|
| Der Skill sagt, er erreicht Home Assistant nicht | Sieh unter [**Einstellungen > Reparaturen**](https://my.home-assistant.io/redirect/repairs/) nach. Home Assistant braucht eine öffentliche HTTPS-Adresse, z. B. über Home Assistant Cloud. Danach den Skill-Code neu kopieren. |
| Alexa sagt immer wieder, ich soll mit *notiere* anfangen | Das aktuelle Sprachmodell in die Alexa-Entwicklerkonsole kopieren, dann **Save** und **Build**. |
| *„Alexa, öffne Brainstorm“* startet den alten Dialog | Die Alexa-Routinen für *öffne Brainstorm* in der Alexa-App löschen. |
| Eine Idee landet in der falschen Kategorie | Die Kategorie vorne nennen: *„notiere für den Einkauf Milch“*. Eine eigene Kategorie hat Vorrang vor Standard-Begriffen mit ihrem Namen. |
| Eine Karte zeigt noch eine alte Version | Die Ressource auf die aktuelle `?v=`-Nummer setzen und die Seite ohne Cache neu laden. |
| Ein Echo wird nicht erkannt oder ignoriert | Die Echo-Auswahl unter [**Konfigurieren**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) prüfen. [**Einstellungen > Reparaturen**](https://my.home-assistant.io/redirect/repairs/) nennt gewählte Echos, die es nicht mehr gibt. |
| Etwas anderes klappt nicht | Die Diagnose herunterladen (siehe *Entitäten*) und ein [Issue](https://github.com/nukleuz80/ha_brainstorm/issues) eröffnen. |

## 📜 Versionshistorie & Changelog

| Version | Datum | Status & Highlights |
| :--- | :--- | :--- |
| **`v1.9.3`** | 09.11.2026 | **Sichtbar in HACS.** Brainstorm Hub erscheint jetzt in der normalen HACS-Suche, der Ausweichweg über ein benutzerdefiniertes Repository ist aus der Installation entfernt. Ein Hinweis ganz oben und ein *HACS Default*-Badge halten die Aufnahme in die Standardliste am 9. November 2026 fest. Wer das Repository früher selbst eingetragen hat, kann es in HACS wieder entfernen; die Installation bleibt erhalten. |
| **`v1.9.2`** | 09.11.2026 | **Jetzt in der HACS-Standardliste.** Installation über die normale Suche in HACS; der Weg über ein benutzerdefiniertes Repository bleibt als Ausweichweg, bis der Eintrag überall sichtbar ist. |
| **`v1.9.1`** | 09.11.2026 | **Sicherheit (HACS-Review).** Die Aktionen `export_json`, `export_markdown` und `import_json` nehmen eine Datei bzw. einen Ordner (`path`) nur noch von Admins an, auch ohne Privatsphäre. Geschrieben und gelesen wird nur noch im Ordner `/config/brainstorm`, im Markdown-Ordner aus den Optionen oder in `allowlist_external_dirs`, damit keine Dateien anderer Integrationen überschrieben werden können. Importierte IDs müssen `[A-Za-z0-9_-]{1,64}` entsprechen, sonst gibt es eine neue ID; Position, Auslöser und Textfelder werden beim Import auf ihren Typ geprüft. Beide Karten escapen IDs, den Kategorienamen im Leer-Hinweis, den Kartentitel und Icons. |
| **`v1.9.0`** | 09.11.2026 | **Release aller Neuerungen seit 1.8.0** (Suche in der Listenkarte, Regeln, Bilder in Notizen, PDF-Export, wiederkehrende Aufgaben, Präsentationsmodus, Gliederungsansicht, Inhaltsvorlagen, KI-Zusammenfassungen, gleicher Bearbeiten-Dialog in Liste und Mindmap, Doku-Links). **Fehlerbehebung auf dem Echo Show:** Ein Hauptpunkt zeigt jetzt *+ 3 Unterpunkte*; Antippen seines Textes klappt sie direkt auf dem Echo auf und zu, in jeder Tiefe und eingerückt. Vorher erschien nur die erste Ebene, immer offen, tiefere Unterpunkte fehlten. Funktioniert mit dem bisherigen Skill-Code, nichts neu zu kopieren. Auf breiten Bildschirmen ist die Liste jetzt einspaltig, damit offene Unterpunkte unter ihrem Hauptpunkt bleiben. |
| **`v1.8.19`** | 09.11.2026 | **Doku: Links in dein Home Assistant.** Neue Zeile *Schnelllinks* unter *Installation* mit My-Home-Assistant-Buttons für HACS, Einrichtung, die Seite der Integration (Konfigurieren, Diagnose, Löschen), die Aktionen, Sprachassistenten, Reparaturen und die Protokolle. Menüpfade in README und Anleitung wie *Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren*, *Dashboards ➔ Ressourcen*, *Personen*, *Profil ➔ Sicherheit* und *Reparaturen* sind jetzt Links, die die Seite direkt öffnen. Jede Aktion unter *Dienste* hat einen Link *In Home Assistant ausprobieren*, der sie in den Entwicklerwerkzeugen öffnet. |
| **`v1.8.18`** | 09.11.2026 | **Fehlerbehebung: Kopfzeile der Mindmap.** Bei vielen Kategorien liefen die Kategorie-Knöpfe unter die Symbole rechts, kürzten den Titel und versteckten die letzten Kategorien, selbst auf großen Bildschirmen. Die Kategorien haben jetzt eine eigene Zeile, die umbricht, sodass alle, der Titel und die Symbole sichtbar bleiben. Auf schmalen Karten bleibt es eine Zeile zum Wischen. |
| **`v1.8.17`** | 09.11.2026 | **Fehlerbehebung:** Ein *bitte* am Satzanfang fällt bei gesprochenen Notizen weg. *„Alexa, notiere bitte, dass der Rasen gemäht werden muss“* ergab „Bitte dass der Rasen mähen“, weil der Sprachbefehl *notiere* schon abgeschnitten hatte; jetzt steht wieder „Rasen mähen“ da. |
| **`v1.8.16`** | 09.11.2026 | **Gleicher Bearbeiten-Dialog in Liste und Mindmap:** Beide Karten zeigen jetzt dieselben Felder in derselben Reihenfolge: Titel, Beschreibung, Anhänge, Original gesprochen, Priorität, Marker, Fortschritt, Kategorie, Termin, Wiederholen, Erinnern auf, übergeordnete Aufgabe, Unterpunkte nummerieren und sortieren, Callout, Rahmen und Form. Die Liste kann jetzt nummerieren, sortieren (mit Rückgängig im Dialog), Callout, Rahmen und Form; die Mindmap zeigt das gesprochene Original und die übergeordnete Aufgabe. **Fehlerbehebungen:** Die Auswahl der übergeordneten Aufgabe in der Liste bietet auch Unterpunkte an und löst eine Notiz unter einem Unterpunkt beim Speichern nicht mehr. Der Mindmap-Dialog hängt jetzt am Fenster statt an der Karte, bleibt dadurch ganz sichtbar und scrollt sauber, auch wenn die Map höher als der Bildschirm ist. |
| **`v1.8.15`** | 09.11.2026 | **Wiederkehrende Aufgaben:** Neues Feld *Wiederholen* im Bearbeiten-Dialog von Liste und Mindmap (jeden Tag, Werktag, jede Woche, alle 2 Wochen, jeden Monat, jedes Jahr) und `repeat` in `brainstorm.update_idea`. Abhaken legt sofort die nächste Runde an: gleicher Text, Kategorie, Priorität, Beschreibung, Marker, Person und Freigaben, fällig zum nächsten Termin nach jetzt (der 31. fällt in kürzeren Monaten auf den letzten Tag), Unteraufgaben aller Ebenen wieder offen und um dieselbe Zeit verschoben. Offene Unteraufgaben der alten Runde werden mit abgehakt. Wird die alte Runde wieder aktiviert, verschwindet die neue, solange sie noch offen ist. Wiederkehrende Notizen zeigen 🔁. |
| **`v1.8.14`** | 09.11.2026 | **PDF-Export:** 🖼️ in der Mindmap hat *PDF (Map und Gliederung)* und *PDF (nur Gliederung)*. Die erste Seite zeigt die Map, wie sie gerade aussieht, quer oder hoch; die folgenden Seiten listen alle Notizen der Map oder des Fokus-Zweigs als Gliederung, Hauptnotizen fett, mit Beschreibung, über so viele A4-Seiten wie nötig. Markdown-Zeichen werden entfernt, Emojis fallen weg, weil die Standardschriften im PDF sie nicht zeigen können. Die Datei entsteht im Browser ohne zusätzliche Bibliotheken. |
| **`v1.8.13`** | 09.11.2026 | **Bilder in Notizen:** Der erste Bildanhang einer Notiz erscheint als Bild in der Notiz auf der Mindmap; Antippen öffnet es groß, Ziehen verschiebt die Notiz wie gewohnt. Kartenoption `show_images` (Standard an). |
| **`v1.8.12`** | 09.11.2026 | **Regeln:** 🎨 in der Suchleiste der Mindmap (oder **R**) speichert den aktuellen Filter als Regel mit einer von neun Farben und einem Zeichen. Passende Notizen bekommen Farbe und Zeichen, in der Mindmap und in der Listenkarte; die erste passende Regel gilt. Die Regelliste schaltet Regeln an und aus, verschiebt, bearbeitet und löscht sie, ↶ macht ein Löschen rückgängig. Regeln liegen in den Benutzerdaten von Home Assistant und gelten so auf jedem Gerät des Benutzers. |
| **`v1.8.11`** | 09.11.2026 | **Suche in der Listenkarte:** Ein Feld 🔍 über der Liste filtert die Notizen beim Tippen, in Titel, Beschreibung, Ergebnis und Person, ohne auf Groß-/Kleinschreibung oder Akzente zu achten; `#tag` findet Tags. Gefundene Unterpunkte zeigen ihren Oberpunkt grau mit, gefundene Hauptaufgaben behalten ihre Unterpunkte, eingeklappte Äste öffnen sich beim Suchen. ✕ oder Esc leert sie. Kartenoption `show_search` (Standard an). |
| **`v1.8.10`** | 08.11.2026 | **Präsentationsmodus:** **P** oder ▶ *Präsentieren* in der Ansichtswahl öffnet die Map im Vollbild ohne Knöpfe. Der erste Schritt zeigt die ganze Map, danach jede Notiz in der Reihenfolge der Äste: Die Ansicht zoomt hin, Oberpunkt und Unterpunkte bleiben halb sichtbar, der Rest tritt zurück. Eine Leiste unten zeigt den Weg, den Titel und die Beschreibung. →, Leertaste oder Enter gehen weiter, ← zurück, Pos1 zum Überblick, Esc beendet; eingeklappte Äste öffnen sich unterwegs und klappen danach wieder zu. |
| **`v1.8.9`** | 08.11.2026 | **KI: Ast zusammenfassen und lose Ideen zuordnen.** ✨ an einer Notiz mit Unterpunkten bietet jetzt *Unteraufgaben vorschlagen* oder *Ast zusammenfassen*: Die KI liest den ganzen Ast (Erledigtes markiert) und schreibt zwei bis vier Sätze, die du ändern, kopieren oder vor die Beschreibung setzen kannst. *Lose Ideen zuordnen* (Taste **Z** oder ✨ im Brainstorm-Dialog) fragt die KI, wohin die Hauptnotizen ohne Unterpunkte der Kategorie gehören, und zeigt die Vorschläge als Liste zum Abhaken. Neue WebSocket-Befehle `brainstorm/summarize_branch` und `brainstorm/suggest_parents`; gespeichert wird erst nach deiner Bestätigung. |
| **`v1.8.8`** | 08.11.2026 | **Gliederungsansicht:** ☰ in der Ansichtswahl zeigt die Notizen untereinander, Unterpunkte eingerückt unter ihrer Notiz wie in einem Outliner, mit Linien am linken Rand. Die Breite passt sich der Karte an, längere Listen verschiebt man durch Ziehen. **Inhaltsvorlagen:** 🖼️ ➔ *Gliederung einfügen* bietet acht fertige Zweige (SWOT-Analyse, Pro und Contra, Projektplan, Wochenplan, Feier, Reise, Rückblick, Raum renovieren). Ein Tipp schreibt die Gliederung ins Textfeld, dort lässt sie sich vor dem Einfügen ändern. |
| **`v1.8.7`** | 08.11.2026 | **Kanban, Zeitleiste und Eisenhower-Matrix:** Der Ansichts-Knopf der Mindmap öffnet jetzt eine Auswahl aus sechs Ansichten. Kanban sortiert die Notizen nach Status; Ziehen nach *In Arbeit* markiert sie, nach *Erledigt* hakt sie ab. Die Zeitleiste sortiert nach Fälligkeit; Ziehen verschiebt das Datum und behält die Uhrzeit. Die Eisenhower-Matrix sortiert nach Wichtigkeit (Priorität) und Dringlichkeit (🔥 oder fällig in drei Tagen); Ziehen setzt die Priorität oder eine Fälligkeit für morgen. Jeder Zug lässt sich mit ↶ zurücknehmen. |
| **`v1.8.6`** | 08.11.2026 | **Layouts Baum und Organigramm:** Ein neuer Knopf in den Bedienknöpfen der Mindmap schaltet zwischen runder Map, Baum nach rechts und Organigramm nach unten um. Eltern stehen mittig über ihren Unterpunkten, die Linien verlaufen rechtwinklig, und die Ansicht passt sich der Karte an. Die Wahl merkt sich jeder Browser; die Kartenoption `layout` (`radial`, `tree`, `org`) legt den Standard fest. |
| **`v1.8.5`** | 08.11.2026 | **Brainstorm-Modus:** ⚡ in den Bedienknöpfen der Mindmap, oder **B**, öffnet eine Schnelleingabe mit Timer (3, 5, 10, 15 Minuten oder offen). Die Uhr startet mit der ersten Idee und wird in den letzten 30 Sekunden orange. Jedes Enter speichert sofort eine Notiz und zeigt sie als bunten Zettel, ✕ löscht sie wieder. Die Ideen landen in der gezeigten Kategorie oder unter der Fokus-Notiz; nach *Fertig* nimmt ein ↶ die ganze Runde heraus. |
| **`v1.8.4`** | 08.11.2026 | **Gliederung exportieren und einfügen:** Der 🖼️-Dialog der Mindmap speichert alle Notizen der Map (oder des Fokus-Zweigs) als Markdown, OPML oder FreeMind-`.mm` und fügt eine getippte, kopierte oder aus einer Datei gelesene Gliederung ein. Neuer Dienst `brainstorm.import_outline` liest Markdown-Überschriften, Listen und eingerückten Text (`- [x]` als erledigt, `>`-Zeilen als Beschreibung), OPML (`_note`, `_complete`) und FreeMind-/Freeplane-Maps mit Notizen; bis zu 300 Notizen in einem Speichervorgang, in ihrer Reihenfolge, oben in der Liste. XML mit DOCTYPE oder Entitäten wird abgelehnt. ↶ nimmt ein Einfügen wieder heraus. |
| **`v1.8.3`** | 08.11.2026 | **Nummerierung und Sortieren:** Eine Notiz kann ihre Unteraufgaben und alle darunter nummerieren (`numbering`: decimal 1., 1.1, alpha a), roman I.), sichtbar in beiden Karten. Neuer Dienst `brainstorm.sort_children` sortiert die Unteraufgaben einer Notiz oder die Hauptnotizen einer Kategorie nach Titel, Priorität, Fälligkeit oder Erstellzeit, nur innerhalb ihrer eigenen Plätze; `ids` gibt eine feste Reihenfolge vor, die die Karten fürs Rückgängigmachen nutzen. In der Mindmap: Bearbeiten-Dialog und Taste **S**. |
| **`v1.8.2`** | 08.11.2026 | **Fokus und Ebenen:** 🎯 oder **F4** zeigt einen Zweig allein mit Brotkrumen zurück, **Umschalt+F4**/**Esc** gehen hoch; ∞ oder die Tasten **1–9** klappen die Map bis zu so vielen Ebenen ein, **0** zeigt alle. **Querverbindungen:** 🔗 oder **L** zieht einen gebogenen, gestrichelten Pfeil zu einer beliebigen anderen Notiz, auf Wunsch beschriftet; eine *blockierende* Verbindung graut ihr Ziel mit ⛔ *Wartet* aus, bis die erste Notiz erledigt ist (`blocked_by` in der Übersicht). **Rahmen:** Notizen auswählen und ▢ tippen legt einen benannten Rahmen um sie. **Callouts:** eine kurze Anmerkung in einer Sprechblase über der Notiz. Neue Felder `links`, `frame` und `callout` bei `brainstorm.update_idea`, JSON-Import und -Export behalten sie; Rahmen und Verbindungen stehen auch im Bild-Export. |
| **`v1.8.1`** | 08.11.2026 | **Marker und Fortschritt:** Zehn Marker (❓ Frage, 💡 Idee, ⚠️ Achtung, 💰 Geld, ⭐ Stern, 🚩 Flagge, ✅ Haken, ⛔ Blockiert, ⏳ Wartet, ❤️ Herz) erscheinen in beiden Karten an der Notiz. Gesetzt werden sie im Bearbeiten-Dialog oder mit `markers` bei `brainstorm.update_idea`; die Suchleiste der Mindmap filtert nach ihnen, ein Tipp auf einen Marker auch. **Fortschritt:** Notizen mit Unteraufgaben zeigen einen Ring mit *erledigt/gesamt*, der sich wie bei MindManager füllt (erledigt = 100 %, eine Unteraufgabe mit Unteraufgaben zählt deren Durchschnitt). Ohne Unteraufgaben gibt es den Fortschritt in Viertelschritten, per Tipp auf den Ring, im Dialog oder mit `progress`. Marker und Fortschritt stehen auch im Bild-Export und im JSON-Export. |
| **`v1.8.0`** | 08.11.2026 | **Suchen, Filtern und Tags in der Mindmap:** 🔍 (oder **/**, **Strg+F**) öffnet eine Leiste über der Map. Wörter, Prioritäten, *Überfällig*, *7 Tage*, *In Arbeit* und Tags grenzen sie ein; Treffer bleiben hell, ihre übergeordneten Punkte halb, der Rest tritt zurück, und **Enter** geht von Treffer zu Treffer und klappt den Zweig auf. **Tags:** `#wort` in Titel oder Beschreibung erscheint in beiden Karten als Chip, ein Tipp filtert die Map. Gesprochen wird *„Hashtag Garten“* zu `#garten` am Ende der Notiz, ohne den Satz zu zerreißen. Tags brauchen einen Buchstaben, `#1` und Farben wie `#ff7800` sind also keine, und Tags werden klein gespeichert. Tags aus `tags:` erreichen jetzt auch die Karten. Neue Kartenoption `show_filter`. |
| **`v1.7.22`** | 08.11.2026 | **Alle Videos mit richtiger Aussprache:** Auch die Videos [*Die wichtigsten Funktionen*](docs/videos.md#die-wichtigsten-funktionen-3-minuten), [*Installation*](docs/videos.md#installation-3-minuten) und [*Eigener Alexa-Skill*](docs/video-alexa-skill.md) sprechen englische Begriffe wie *Create Skill*, *JSON Editor*, *Deploy*, *Dashboard* oder *Markdown* jetzt richtig aus. Alle sechs Videos hängen am Release v1.7.22. Keine Änderung am Code der Integration. |
| **`v1.7.21`** | 08.11.2026 | **Drei neue Videos:** [*Erinnerungen & Benachrichtigungen*](docs/videos.md#erinnerungen--benachrichtigungen), [*iPhone-Kurzbefehl*](docs/videos.md#iphone-kurzbefehl) und [*Privatsphäre, Freigaben & KI-Backlog*](docs/videos.md#privatsphäre-freigaben--ki-backlog), mit Intro und Kapitelmarken. **Englische Begriffe richtig ausgesprochen:** Die deutsche Stimme bekommt für Wörter wie *iPhone*, *JSON*, *Home Assistant* oder *Claude Code* eine Lautschrift (`tools/video/pron.py`), geprüft per Spracherkennung. Keine Änderung am Code der Integration. |
| **`v1.7.20`** | 08.11.2026 | **Zwei neue Videos:** [*Die wichtigsten Funktionen*](docs/videos.md#die-wichtigsten-funktionen-3-minuten) (3 Minuten, mit echten Screenshots der Karten) und [*Installation*](docs/videos.md#installation-3-minuten) (3 Minuten, von HACS bis zur ersten Idee), beide mit Intro und Kapitelmarken. Neue Übersicht [`docs/videos.md`](docs/videos.md), verlinkt oben in der README. Videos hängen ab jetzt nur noch an den Releases und liegen nicht mehr im Repository. Die Werkzeuge unter `tools/video` rendern die echten Karten mit Beispieldaten und sprechen nur geänderte Szenen neu. |
| **`v1.7.19`** | 08.11.2026 | **Video zur Skill-Einrichtung:** Neues Erklärvideo [`docs/video-alexa-skill.md`](docs/video-alexa-skill.md) (6 Minuten, deutsch) mit einem Kapitel pro Einstellung in der Alexa-Entwicklerkonsole: Name, Sprache, Modell, Hosting, Vorlage, Interfaces, Permissions, JSON Editor, Aufrufname, Skill-Code, Test, Kopplung, Alexa-App und Fehlerbehebung, mit Kapitelmarken im MP4. Dazu ein wiederverwendbares animiertes Intro mit dem Brainstorm-Logo und die Werkzeuge zum Erzeugen unter `tools/video`. |
| **`v1.7.18`** | 07.11.2026 | **Kategorie in eckigen Klammern:** `[Alltag] Oma anrufen` speichert jetzt *Oma anrufen* in *Alltag*. Bisher blieb `[Alltag]` im Text stehen, wenn kein Doppelpunkt folgte, und die Kategorie wurde nur über Stichwörter erraten. |
| **`v1.7.17`** | 07.11.2026 | **Anleitung mit Beispielen:** Neuer Bereich [`docs/anleitung.md`](docs/anleitung.md) (englisch [`docs/guide.md`](docs/guide.md)) mit Beispielen zu allem, was man sagen, schreiben, einstellen und automatisieren kann: Alexa, Assist, Siri, KI-Assistent, Kategorie-, Prioritäts- und Terminerkennung, Markdown, Bedienung und Tastenkürzel der Karten, alle Kartenoptionen, Menüs, Dienste, Ereignisse. Aufgeräumt: alte Logo- und Icon-Dateien entfernt, die seit dem Brand-Ordner nicht mehr gebraucht werden. |
| **`v1.7.16`** | 07.11.2026 | **MIT-Lizenzdatei:** Das Repository hat jetzt seine `LICENSE`-Datei (MIT, wie im README schon immer angegeben), die HACS zum Erkennen der Lizenz braucht. HACS Action und hassfest laufen beide durch. |
| **`v1.7.15`** | 07.11.2026 | **Karten kommen mit der Integration:** Die Karten liegen jetzt im Ordner der Integration und Home Assistant lädt sie beim Start selbst, auch im YAML-Modus. Eine Installation über HACS bringt damit alles mit; Kopieren nach `/config/www/` und Ressourcen-Einträge entfallen. Nach dem Update die alten `/local/brainstorm-…`-Ressourcen entfernen. Dazu prüfen GitHub Actions jetzt jede Änderung mit der HACS Action und hassfest, als Vorbereitung für die Aufnahme in die HACS-Standardliste. |
| **`v1.7.14`** | 07.11.2026 | **Mindmap: fünf weitere Formen:** Gedankenblase (eine Wolke mit zwei kleinen Bläschen zur übergeordneten Notiz), Ellipse, Sechseck, Notizzettel (getöntes Papier mit umgeknickter Ecke) und Unterstrichen (nur der Text über einem Strich in der Kategoriefarbe, die Linien der Map treffen ihn an den Enden des Strichs). Wählbar für die ganze Map (`node_shape`), pro Notiz im Bearbeiten-Dialog und mit `shape` von `brainstorm.update_idea`, und mit im Bild-Export. |
| **`v1.7.13`** | 07.11.2026 | **Erledigte Einträge löschen:** Einstellungen › 🧹 Erledigte Einträge löschen löscht erledigte Einträge nach einer Anzahl Tage von selbst (geprüft alle sechs Stunden, 0 = aus) und hat einen Schalter, der alle sofort löscht. Offene Unteraufgaben eines gelöschten Eintrags bleiben als Hauptaufgaben, Einträge verknüpfter To-do-Listen und Anhänge gehen mit. Neue Aktion `brainstorm.delete_done` mit `older_than_days`. |
| **`v1.7.12`** | 07.11.2026 | **Mindmap: Form pro Notiz:** Der Bearbeiten-Dialog der Mindmap wählt für eine einzelne Notiz Karte, Wolke, Sprechblase, Kapsel oder Rechteck; „Automatisch“ folgt der Map. `brainstorm.update_idea` nimmt das neue Feld `shape`, JSON-Export und -Import behalten es. Notizen, die Alexa, Siri oder Assist gesagt wurden, erscheinen von selbst als Sprechblase; die neue Option `voice_bubbles` schaltet das ab. |
| **`v1.7.11`** | 07.11.2026 | **Mindmap: echte Wolken und Sprechblasen:** zwei neue Formen für Notizen, als SVG-Umriss gezeichnet, der seine Bögen bei jeder Größe behält. Der Zipfel der Sprechblase zeigt zur übergeordneten Notiz oder zur Mitte und wandert beim Ziehen mit. Die bisherige „Wolke“ war eine abgerundete Karte und heißt jetzt **Karte** (`card`), die Standard-Vorlage behält sie; `node_shape: cloud` zeichnet jetzt die echte Wolke. Beide Formen folgen den Farbvorlagen, der Priorität und der Auswahl und kommen mit in den Bild-Export. |
| **`v1.7.10`** | 05.11.2026 | **In Arbeit:** `brainstorm.update_idea` nimmt `in_progress`. Beide Karten zeigen 🔧 In Arbeit mit dem Namen dessen, der angefangen hat, das Menü bei langem Drücken setzt und entfernt die Markierung, Abhaken entfernt sie. Der Claude-Code-Skill markiert den Eintrag, an dem er arbeitet. Die Mindmap zeigt auch das 📎-Abzeichen. |
| **`v1.7.9`** | 05.11.2026 | **Anhänge:** Screenshots, Fotos, PDFs und Logs an einer Notiz, angehängt im Bearbeiten-Dialog beider Karten, per Strg+V eingefügt oder hineingezogen. Die Liste zeigt 📎 mit der Anzahl. Dateien von Notizen, die seit 30 Tagen erledigt sind, werden gelöscht. Nur wer eine Notiz sehen darf, bekommt ihre Dateien. |
| **`v1.7.8`** | 05.11.2026 | **Titel und Beschreibung:** Jede Notiz kann unter dem Titel eine Beschreibung haben, bearbeitet mit ✎ in beiden Karten. Die Liste zeigt drei Zeilen, Antippen zeigt alles. Die To-do-Listen von Home Assistant zeigen und bearbeiten sie, die Aktionen nehmen `description`. Markdown- und JSON-Export enthalten sie. |
| **`v1.7.7`** | 05.11.2026 | **Sperrzeiten pro Echo:** Unter *Erinnerungen ➔ Sperrzeiten pro Echo* halten bis zu drei Sperrzeiten gewählte Echos für Brainstorm still, etwa nachts im Kinderzimmer. Andere Echos sprechen weiter, ist keines übrig, geht die Erinnerung sofort aufs Handy. Auf Wunsch wird „Nicht stören“ mit der Sperrzeit ein- und ausgeschaltet. |
| **`v1.7.6`** | 05.11.2026 | **Batterie-Aufgaben pro Gerät:** Weitere Sensoren für dieselbe Batterie (z. B. Battery Notes) legen keine zweite Aufgabe mehr an, und abgehakt wird erst, wenn kein Sensor des Geräts mehr „schwach“ meldet. Handys und Tablets der Companion-App bleiben außen vor, außer du schaltest sie ein, und ein ausgelassener Sensor lässt sein Gerät aus. |
| **`v1.7.5`** | 05.11.2026 | **Batterie-Aufgaben:** Eine Batterie unter der Schwelle (Standard 20 %) oder mit „schwach“ legt eine Aufgabe wie *Batterie wechseln: Bewegungsmelder Flur (18 %)* an, die sich nach dem Wechsel selbst abhakt. Einrichten unter *Konfigurieren ➔ 🔋 Batterien*, mit Batterien zum Auslassen. |
| **`v1.7.4`** | 05.11.2026 | **Unteraufgaben in der Liste einklappen:** ▾ mit der Zahl der Unteraufgaben an jeder Hauptaufgabe klappt sie zu, ▸ wieder auf. Jeder Browser merkt es sich pro Karte. |
| **`v1.7.3`** | 05.11.2026 | **Bring!-Einstellungen speichern wieder:** Gehört die Standardliste nicht zu den gewählten Listen, gilt die erste gewählte, statt das Formular zu blockieren. |
| **`v1.7.2`** | 04.11.2026 | **Bring!-Nachrichten:**<br>• **🛒-Knopf an jeder Bring-Listen-Notiz:** *Ich gehe einkaufen*, *Einkauf erledigt* oder *Liste geändert* benachrichtigt alle auf der Liste über Bring.<br>• **Dringend in Bring melden** im Menü eines Eintrags schickt den Eintrag mit.<br>• Neue Aktion `brainstorm.bring_message` für Automationen, etwa wenn jemand zum Supermarkt aufbricht. |
| **`v1.7.1`** | 04.11.2026 | **Gekauftes ausblenden:**<br>• Neue Einstellung *Gekauftes ausblenden nach (Tagen)* auf der Seite 🛒 Bring!, Standard 3 Tage, 0 behält alles.<br>• Abgehakte Einträge der Bring-Kategorie werden danach archiviert und verschwinden aus der Erledigt-Ansicht; in Bring bleiben sie in den zuletzt gekauften Einträgen.<br>• Erneut notiert, kommt der früher gekaufte Eintrag zurück statt eines Duplikats. |
| **`v1.7.0`** | 04.11.2026 | **Native Bring!-Unterstützung:**<br>• **Alle Bring-Listen in einer Kategorie** unter *Konfigurieren ➔ 🛒 Bring!*: einschalten, Kategorie wählen oder anlegen, Standardliste festlegen.<br>• **Eine Hauptnotiz pro Liste**, ihre Einträge als Unteraufgaben; eine gelöschte Listen-Notiz kommt zurück, eine abgewählte Liste wird archiviert und behält ihre Einträge in Bring.<br>• **Unteraufgabe verschieben** unter eine andere Listen-Notiz verschiebt den Eintrag zwischen den Bring-Listen.<br>• **Bring-Eigenheiten berücksichtigt:** Umbenennen behält den Eintrag, obwohl Bring eine neue ID vergibt, erneut Gekauftes holt den alten Eintrag zurück statt eines Duplikats, und die Bring-Spezifikation erscheint als Notiz.<br>• Bring-Listen verlassen die allgemeine To-do-Kopplung, damit nichts doppelt synchronisiert wird. |
| **`v1.6.31`** | 04.11.2026 | **To-do-Listen koppeln, JSON-Export und -Import:**<br>• **Eine Kategorie mit einer To-do-Liste koppeln**, etwa Bring!, Google Tasks oder Todoist, unter *Konfigurieren ➔ To-do-Listen koppeln*. Neue Einträge, Umbenennen und Abhaken gehen in beide Richtungen. Eine gelöschte Notiz entfernt ihren Eintrag, ein von der Liste entfernter Eintrag hakt seine Notiz ab. Fälligkeiten gehen auf die Liste, wenn sie welche kennt.<br>• **Sicher mit Privatsphäre:** Nur mit allen geteilte Notizen kommen auf die andere Liste. Entkoppeln lässt ihre Einträge stehen.<br>• **Neue Aktionen `brainstorm.export_json` und `brainstorm.import_json`:** Deine Ideen samt Kategorien, Icons und Farben als JSON, auf Wunsch als Datei. Der Import überspringt Vorhandenes, hält Unteraufgaben zusammen und behält Besitzer nur für Benutzer dieses Home Assistant.<br>• Tests für beides, gegen die eigene Einkaufsliste von Home Assistant. |
| **`v1.6.30`** | 04.11.2026 | **Ausgesprochene Tage als Datum:**<br>• *„am zweiten Dezember um zwölf Uhr“*, *„den dritten November“* und *„am zweiten Zwölften“* werden jetzt als Termin verstanden (1. bis 31., Monat als Name oder als Ordnungszahl).<br>• Wendungen wie *„zum zweiten Mal“* bleiben Text, ein *„dreißigster Februar“* wird kein Termin. |
| **`v1.6.29`** | 04.11.2026 | **🌿 in der Listenkarte, klarere KI-Fehler:**<br>• **🌿 neben ✨** an jeder Hauptaufgabe und im Menü bei langem Drücken: Die Unteraufgabe landet direkt darunter, in ihrer Kategorie. Enter speichert.<br>• **Überlastete KI:** Lehnt der Anbieter ab (etwa Googles *503 high demand*), fragt Brainstorm nach 2 Sekunden einmal nach. Ein Timeout wird nicht wiederholt, damit du nicht doppelt wartest.<br>• **Klare Meldung:** Ist die KI nicht erreichbar, sagen beide Karten das, statt zu behaupten, sie habe keine Unteraufgaben geliefert. Neuer WebSocket-Fehlercode `ai_unavailable`. |
| **`v1.6.28`** | 04.11.2026 | **KI-Unteraufgaben auch in der Listenkarte:**<br>• **✨ neben ✎** an jeder Hauptaufgabe, die du ändern darfst, und **im Menü** bei langem Drücken oder Rechtsklick. Derselbe Dialog wie in der Mindmap: Haken weg, Texte ändern, übernehmen.<br>• Die neuen Unteraufgaben bekommen die Kategorie ihrer Hauptaufgabe. Unteraufgaben selbst haben kein ✨, weil die Liste eine Ebene Unteraufgaben zeigt.<br>• Nur sichtbar, wenn unter *Konfigurieren ➔ KI* eine KI-Aufgaben-Entität gewählt ist. |
| **`v1.6.27`** | 04.11.2026 | **Eigener Menüpunkt für die KI:**<br>• Die KI-Einstellungen sind von *Erinnerungen ➔ Kalender, KI & Alexa-Erinnerungen* in einen eigenen Punkt **KI** im Hauptmenü gezogen: KI-Aufgaben-Entität, gesprochene Einträge verbessern, Briefing und Rückblick kürzen. Gespeicherte Einstellungen bleiben, wie sie sind.<br>• Der Erinnerungs-Bereich heißt jetzt *Kalender & Alexa-Erinnerungen*.<br>• Der ✨-Dialog der Mindmap nennt den neuen Ort, wenn noch keine KI gewählt ist.<br>• **Neuer Abschnitt *Feedback & Mitmachen*:** Rückmeldungen, Ideen und Pull Requests sind sehr willkommen. |
| **`v1.6.26`** | 04.11.2026 | **Mindmap: Unteraufgaben von der KI vorschlagen lassen:**<br>• **✨ an einer Notiz** fragt die KI-Aufgaben-Entität aus den Einstellungen nach bis zu 8 Unteraufgaben. Gespeichert wird erst, wenn du auswählst: Haken weg, Texte ändern, übernehmen. Die neuen Unteraufgaben bekommen die Kategorie der Notiz, der Ast klappt auf, und ein Rückgängig entfernt alle.<br>• **Wenig Daten:** Zur KI gehen nur die Notiz, ihre Kategorie und ihre vorhandenen Unteraufgaben, und nur auf Knopfdruck. Fragen kannst du nur für Notizen, die du ändern darfst.<br>• **Neuer WebSocket-Befehl** `brainstorm/suggest_subtasks`; das Sensor-Attribut `ai_subtasks` sagt den Karten, ob eine KI-Aufgaben-Entität gewählt ist. Tests für den Parser, die Rechte und den Dialog. |
| **`v1.6.25`** | 04.11.2026 | **Mindmap: mehrere Notizen per Lasso auswählen:**<br>• **Umschalt+Ziehen** auf der leeren Map zieht einen Rahmen um mehrere Notizen, **Umschalt+Klick** oder **Strg+Klick** nimmt einzelne dazu oder heraus. Auf Touch-Geräten schaltet der neue Knopf ⬚ unten rechts aufs Auswählen um: Rahmen ziehen oder Notizen antippen.<br>• **Gemeinsam:** Ziehst du eine ausgewählte Notiz, wandern alle ausgewählten samt Unteraufgaben mit. Eine Leiste über der Map hakt sie ab, verschiebt sie in eine andere Kategorie oder löscht sie nach einer Rückfrage; **Entf** geht auch.<br>• **Ein Rückgängig für alle:** Strg+Z nimmt den ganzen Schritt zurück. Gelöschte Unteraufgaben hängen danach wieder an ihrem Oberpunkt.<br>• **Esc** oder ✕ hebt die Auswahl auf und beendet das Auswählen. |
| **`v1.6.24`** | 04.11.2026 | **Coding-KIs: Adminrechte für ha-mcp geklärt:**<br>• Das Kapitel *Brainstorm als Aufgabenliste für Coding-KIs* sagt jetzt, wann der KI-Benutzer Adminrechte braucht: ha-mcp als eigener Server geht auch ohne (seine Admin-Werkzeuge schlagen fehl, Brainstorms Aktionen gehen), die HA-MCP-Integration läuft immer mit dem Token eines Administrators. Geprüft im Code von ha-mcp 9.1.0.<br>• Der Claude-Code-Skill nennt dieselbe Regel in seiner Einrichtung. |
| **`v1.6.23`** | 04.11.2026 | **Mindmap: Zeitangabe bleibt in der Wolke:**<br>• Bei langen Gerätenamen (*„Jans Echo Dot - Garten“*) ragte die Zeit (*„vor 14m“*) auf schmalen Bildschirmen über den Rand der Wolke. Jetzt wird der Gerätename mit „…“ gekürzt, die Zeit bleibt immer sichtbar. |
| **`v1.6.22`** | 04.11.2026 | **Skill antwortet bei freien Sätzen sofort:**<br>• Alexa schreibt einen Satz erst zusammen mit der Antwort des Skills in den Verlauf. Das Warten darauf war deshalb vergeblich und kostete gut 4 Sekunden Stille. Jetzt antwortet der Skill sofort mit *„Okay, notiert“*, der Eintrag erscheint wenige Sekunden später.<br>• Home Assistant erkennt den passenden Verlaufseintrag an genau dieser Antwort (Feld `response` von Alexa Media). Andere Fragen am selben Echo werden nicht mehr versehentlich gespeichert. Ältere Alexa-Media-Versionen ohne dieses Feld nutzen weiter die Zuordnung über das Echo.<br>• Kommt innerhalb einer Minute kein Verlaufseintrag, erscheint eine Benachrichtigung in Home Assistant, statt den Satz still zu verlieren. |
| **`v1.6.21`** | 04.11.2026 | **Links und Markdown in Notizen:**<br>• Beide Karten zeigen Webadressen und `[Text](https://…)` als anklickbare Links, dazu `**fett**`, `*kursiv*`, `~~durchgestrichen~~` und `` `Code` ``, auch in der Ergebnisnotiz.<br>• Sichere Maskierung: Der Text wird vollständig maskiert, nur die selbst erzeugten Tags sind HTML. Links nur zu `http`, `https` und `mailto`, mit `rel="noopener noreferrer"`. Gegen eingeschleustes HTML und `javascript:`-Links getestet.<br>• Ein Klick auf einen Link öffnet weder den Editor noch startet er das Verschieben einer Wolke. |
| **`v1.6.20`** | 04.11.2026 | **Skill speichert freie Sätze ohne Befehlswort:**<br>• Versteht der Skill einen Satz nicht (*„sage Brainstorm Duschgel ist alle“*), fragt er Home Assistant. Das nimmt den Satz aus dem Alexa-Verlauf des Echos, entfernt *„sage Brainstorm“* und speichert ihn wie eine Notiz.<br>• Im offenen Skill (*„öffne Brainstorm“*) zählt nur ein Satz vom selben Echo, Sätze anderer Echos im Haus werden nicht verwechselt.<br>• Kommt der Verlauf zu spät, antwortet Alexa *„Okay, ich speichere das gleich“* und der Eintrag wird bis zu 60 Sekunden lang nachgetragen.<br>• **Skill-Code neu kopieren** (Brainstorm Hub ➔ Konfigurieren ➔ Alexa-Spracheingabe & Skill), sonst bleibt der alte Hinweis. |
| **`v1.6.19`** | 03.11.2026 | **Brainstorm als Aufgabenliste für Coding-KIs:**<br>• Neues Kapitel „🤖 Brainstorm als Aufgabenliste für Coding-KIs“: eigener KI-Benutzer, Token, Freigabe der Backlog-Kategorie, Arbeitsregeln.<br>• Neuer Claude-Code-Skill unter `examples/claude-code/skills/brainstorm-backlog`: liest das Backlog über `brainstorm.get_ideas`, hält Reihenfolge und Bedingungen ein und hakt nur Fertiges mit Ergebnis-Notiz ab.<br>• Hinweis, welche Aktionen Adminrechte brauchen und warum ein Benutzer ohne Adminrechte sicherer ist. |
| **`v1.6.18`** | 03.11.2026 | **Ergebnis-Notiz beim Abhaken:**<br>• `brainstorm.update_idea` hat das neue Feld `result`. Damit lässt sich beim Abhaken festhalten, was aus einem Eintrag geworden ist, etwa „Erledigt in v1.6.18, getestet“.<br>• Beide Karten zeigen die Notiz mit grünem Rand unter dem Text, die Liste auch in der Ansicht „Erledigt“.<br>• Beim Wiederöffnen bleibt die Notiz stehen, ein leeres `result` entfernt sie. |
| **`v1.6.17`** | 03.11.2026 | **Mindmap: Export als Bild:**<br>• Der neue Knopf 🖼️ oben rechts speichert die Map als **SVG** (Vektor, scharf in jeder Größe) oder **PNG** (in doppelter Auflösung).<br>• Das Bild zeigt Linien, Notizen und die Mitte in den Farben der gewählten Vorlage, ohne Knöpfe und Abzeichen. Eingeklappte Zweige bleiben weg.<br>• Der Dateiname enthält Liste und Datum, etwa `brainstorm-haus-garten-2026-11-03.png`. Mit `show_export_btn: false` lässt sich der Knopf ausblenden. |
| **`v1.6.16`** | 03.11.2026 | **Mindmap: Vorlagen für das Aussehen:**<br>• Vier Vorlagen im Karten-Editor: **Standard** (Wolken, Kurven, Kategoriefarben), **Klar** (Rechtecke, eckige Linien), **Skizze** (Kapseln, gestrichelt, Pastell) und **Neon** (dunkel und leuchtend).<br>• Form (`node_shape`), Linien (`line_style`) und Farben (`color_scheme`) lassen sich einzeln anders wählen, etwa Neon mit Rechtecken oder Standard einfarbig.<br>• Alle Vorlagen nutzen die Farben des Home-Assistant-Themes, nur Neon bringt seinen eigenen dunklen Hintergrund mit. |
| **`v1.6.15`** | 03.11.2026 | **Mindmap: Rückgängig:**<br>• **Strg+Z** oder der neue Knopf ↶ unten rechts nimmt die letzten 30 Schritte dieser Sitzung zurück: neue Notizen, Text, Dialog-Änderungen, Erledigt, Priorität, Kategorie, Verschieben, Neu ordnen und Löschen. Eine kurze Meldung zeigt, was zurückgenommen wurde.<br>• **Löschen rückgängig:** Neue Aktion `brainstorm.restore_idea`. Home Assistant hält gelöschte Ideen bis zum nächsten Start bereit (höchstens 50), samt Verbindung zu ihren Unteraufgaben. Zurückholen darf nur, wer gelöscht hat. |
| **`v1.6.14`** | 03.11.2026 | **Mindmap: Tastatur und Bearbeiten direkt in der Wolke:**<br>• **Auswahl:** Ein Klick wählt eine Notiz aus, sie bekommt einen farbigen Rahmen.<br>• **Tastatur:** Tab legt eine Unteraufgabe an, Enter eine Notiz daneben. Dafür erscheint gleich ein leeres Feld auf der Map, nach dem Speichern geht es von der neuen Notiz aus weiter. Entf löscht nach Rückfrage, F2 bearbeitet, die Pfeiltasten gehen die Zweige entlang, Esc hebt die Auswahl auf.<br>• **Direkt bearbeiten:** Ein Klick auf den Text oder ein Doppelklick öffnet ihn in der Wolke. Enter speichert, Esc bricht ab. Was in der Zeit von Home Assistant kommt, zeigt die Map erst danach an, damit nichts verloren geht. Für Termin, Priorität und Echos bleibt der Dialog hinter ✏️.<br>• Ein Klick, der ein Ziehen beendet, öffnet nichts mehr. |
| **`v1.6.13`** | 03.11.2026 | **Mindmap: Zweige einklappen und als Baum ordnen:**<br>• **Einklappen:** Notizen mit Unteraufgaben haben einen runden Knopf. Er klappt den Zweig zu und zeigt dann, wie viele Notizen darin stecken, etwa „+5“. Jedes Gerät merkt sich das für sich. Ziehst du eine eingeklappte Notiz, wandern die gespeicherten Plätze ihrer Unteraufgaben mit.<br>• **Baum-Anordnung:** Gibt es Zweige, bekommt jeder einen Ausschnitt des Kreises passend zu seiner Größe. Unteraufgaben liegen weiter außen, Linien kreuzen sich nicht. Von Hand verschobene Notizen bleiben, wo sie sind. Listen ohne Zweige sehen aus wie bisher.<br>• **Neu ordnen (🪄):** Der neue Knopf unten rechts setzt nach einer Rückfrage alle von Hand platzierten Notizen der Liste wieder an ihren automatischen Platz, auf allen Geräten. |
| **`v1.6.12`** | 03.11.2026 | **Mindmap mit Ästen und gespeicherter Anordnung:**<br>• **Äste:** Unteraufgaben hängen in der Map an ihrer Elternidee, die Linie geht von ihr aus. Ein neuer Knopf 🌿 an jeder Notiz legt eine Unteridee an.<br>• **Positionen bleiben:** Ziehst du in einer einzelnen Liste eine Notiz, merkt sich Brainstorm ihren Platz im neuen Feld `map_pos`, relativ zur Mitte und damit passend für jede Bildschirmgröße. Sie steht danach auf allen Geräten dort. Eine Elternidee nimmt beim Ziehen ihre Unteraufgaben mit.<br>• **Neuer WebSocket-Befehl** `brainstorm/map_positions` speichert oder löscht mehrere Positionen auf einmal, nur für Ideen, die du bearbeiten darfst. Wechselt eine Idee die Kategorie, vergisst sie ihre Position. |
| **`v1.6.11`** | 03.11.2026 | **Getippter Text bleibt, wie er ist:** Ruft man die Aktion `brainstorm.add_idea` ohne `source` auf (Entwicklerwerkzeuge, Skripte, KI-Agenten), gilt der Text als getippt. Er behält seinen Wortlaut statt wie ein gesprochener Satz gekürzt zu werden, der Großbuchstaben mitten im Satz bekam und Wörter verlor. Sprachwege mit eigener Quelle wie `alexa` oder `assist` kürzen weiter wie bisher. |
| **`v1.6.10`** | 03.11.2026 | **Verfasser anzeigen:** Legt jemand einen Eintrag in einer fremden Liste an, merkt sich Brainstorm ihn im neuen Feld `created_by`. Beide Karten zeigen dann ein Abzeichen mit seinem Namen, die Listenkarte mit dem Bild seiner Person, falls vorhanden. |
| **`v1.6.9`** | 03.11.2026 | **In freigegebene Listen schreiben:** Wer eine Kategorie persönlich mit *Bearbeiten* freigegeben bekommt, legt dort neue Einträge für den Besitzer an, statt sie für sich zu behalten. Unteraufgaben gehören dem Besitzer der übergeordneten Aufgabe. Damit kann zum Beispiel eine KI über ihren eigenen Benutzer Aufgaben in deine Liste schreiben. Löschen bleibt beim Besitzer. |
| **`v1.6.8`** | 03.11.2026 | **Home Assistant Quality Scale: Gold (Selbsteinschätzung):**<br>• **Diagnose:** *Diagnose herunterladen* liefert Zahlen und Einstellungen für Fehlerberichte, ohne Ideen-Texte, Personen oder Echos.<br>• **Reparaturen:** Home Assistant meldet, wenn der Skill-Modus an ist, aber keine öffentliche HTTPS-Adresse existiert, und wenn gewählte Echos nicht mehr da sind.<br>• **Icons:** Icons für Sensor, Listen und alle Aktionen kommen aus `icons.json`.<br>• **Übersetzte Fehler:** Auch der Fehler beim Lesen der gespeicherten Daten ist übersetzt.<br>• **Doku:** Neue Abschnitte zu Entitäten, Aktualisierung, Beispielen, bekannten Einschränkungen und Fehlerbehebung. |
| **`v1.6.7`** | 03.11.2026 | **Skill versteht natürlichere Sätze:**<br>• **Ohne Befehlswort:** *„sage Brainstorm wir brauchen Duschgel“*, *„… wir müssen …“*, *„… ich muss …“*, *„… dass …“* werden als Notiz gespeichert. Auch *„Nokia …“*, wie Alexa *„notiere“* oft versteht, und *„notiere mir …“* klappen.<br>• **Listen und Erinnerungen:** *„zeige mir die Liste Brainstorm“*, *„erinnere mich um/am …“*.<br>• **Klare Rückfrage:** Versteht Alexa einen Satz nicht, sagt der Skill *„Fang mit notiere an“*, statt nur Beispiele aufzuzählen.<br>• **Eigene Kategorie zuerst:** *„notiere für den Einkauf Duschgel“* landet in deiner Kategorie *Einkauf* (statt *Alltag*) und heißt nur *Duschgel*.<br>• **Termin mit Uhrzeit:** *„notiere Termin Zahnarzt um neun“* bekommt die Uhrzeit, auch ohne Tag.<br>• **Neues Sprachmodell und neuer Skill-Code:** Beides einmal neu in die Alexa-Entwicklerkonsole kopieren. |
| **`v1.6.6`** | 03.11.2026 | **Echo-Auswahl eingeklappt:** Im Bearbeiten-Dialog ist *Erinnern auf* zunächst eingeklappt und zeigt die gewählten Echos oder *Wie in den Einstellungen*. Ein Tipp klappt die Liste auf. |
| **`v1.6.5`** | 03.11.2026 | **Termin im Bearbeiten-Dialog:**<br>• **Datum und Uhrzeit:** Beide Karten setzen, ändern und entfernen den Termin eines Eintrags direkt im Dialog. Ohne Uhrzeit erinnert Brainstorm um 9:00 Uhr.<br>• **Echos wählen:** Pro Eintrag wählst du, welche Echos die Erinnerung sprechen. Ohne Auswahl gelten wie bisher die Erinnerungs-Einstellungen.<br>• **Neues Feld:** `brainstorm.update_idea` nimmt `echos` an. |
| **`v1.6.4`** | 02.11.2026 | Die Dialoge drücken ihre Felder nicht mehr zusammen: Auf dem iPhone ist die Auswahl **Übergeordnete Aufgabe** wieder lesbar und der Notiztext hat seine volle Höhe. |
| **`v1.6.3`** | 02.11.2026 | **Mindmap-Karte auf dem Handy:**<br>• **Kopfzeile:** Logo, Titel und Buttons stehen in einer Zeile, die Kategorien in einer zweiten; nichts wird mehr gequetscht oder überdeckt.<br>• **Vollbild:** Die Kopfzeile verschwindet nicht mehr hinter Notch oder Dynamic Island, die Buttons unten halten Abstand zum Home-Balken.<br>• **iPhone:** Die Handy-Ansicht greift jetzt auch in Safari und der Companion-App.<br>• **Notizen:** Sie überlappen sich nicht mehr und stehen in zwei Spalten um die Mitte. |
| **`v1.6.2`** | 02.11.2026 | Der Hinzufügen-Button der Karte zeigt auf dem Handy und am Desktop nur noch das Plus. |
| **`v1.6.1`** | 02.11.2026 | Die Erinnerungs-Einstellungen zeigen keine scheinbar anklickbare Liste mehr: Der aktuelle Stand steht jetzt direkt unter jedem klickbaren Bereich. |
| **`v1.6.0`** | 02.11.2026 | **Englisch offiziell unterstützt:**<br>• **Vollständig:** Einstellungen, Karten, gesprochene Notizen, Termine, Prioritäten, Erinnerungen, der Alexa-Skill und die Assist-Sätze funktionieren auf Englisch.<br>• **Deine Daten bleiben:** Gespeicherte Kategorien und Einträge werden in keiner Sprache übersetzt, umbenannt oder migriert. Ein Test prüft das für Deutsch, Englisch und eine unbekannte Sprache.<br>• **Weitere Sprachen:** `CONTRIBUTING.md` erklärt in drei Schritten, wie eine dazukommt. Bis dahin behalten andere Sprachen deinen Text wie er ist und antworten auf Englisch. |
| **`v1.5.16`** | 02.11.2026 | **Englisch sprechen mit dem eigenen Skill:**<br>• **Sprachmodell:** Home Assistant zeigt ein englisches Sprachmodell an, wenn es auf Englisch läuft: *„Alexa, ask Brainstorm to note dim the basement light“*, *„remind me tomorrow at 8 to …“*, *„done“*, *„later“*, *„read“*, *„show my lists“*.<br>• **Sprache der Anfrage:** Mit dem neuen Skill-Code folgt der Skill der Sprache des Echos. Vorhandene Skills laufen ohne Änderung weiter und nutzen die Sprache von Home Assistant.<br>• **Ohne Home Assistant:** Der Skill-Code enthält seine Meldungen in allen Sprachen für den Fall, dass Home Assistant nicht erreichbar ist.<br>• **Vorlagen:** `examples/` enthält Assist-Sätze und Intent-Skripte in beiden Sprachen sowie eine englische Alexa-Dialog- und Direktbefehl-Automation. |
| **`v1.5.15`** | 02.11.2026 | **Die Karten auf Englisch:**<br>• **Alle Texte:** Beide Karten und ihre Editoren zeigen ihre Texte in der Sprache deines Home-Assistant-Profils, die Daten passend dazu. Sprachen ohne eigene Texte zeigen Englisch.<br>• **Neue Datei zum Kopieren:** `www/brainstorm-i18n.js` enthält die Texte. Kopiere sie bei einem Update von Hand neben die beiden Karten-Dateien. Sie braucht keinen Ressourcen-Eintrag.<br>• **Karteneditor:** Die Kategorieauswahl bietet nur noch vorhandene Kategorien an. |
| **`v1.5.14`** | 02.11.2026 | **Englische Texte im Backend:**<br>• **Erinnerungen:** Gesprochene Erinnerungen, Benachrichtigungen mit ihren Knöpfen, das Briefing, der Wochenrückblick und die KI-Zusammenfassung folgen der Sprache von Home Assistant.<br>• **Auch auf Englisch:** Logbuch, To-do-Beschreibungen, Markdown-Export, Ansagen, Antworten der KI-Werkzeuge und die Listen auf dem Echo Show.<br>• **Erinnerungssätze:** *„when I get home“*, *„when I get to the market“* und *„remind Alex tomorrow at 8“* gehen auf Englisch.<br>• **Fehlermeldungen und Aktionen:** Sie nutzen jetzt die Übersetzungen von Home Assistant und erscheinen damit in der Sprache des jeweiligen Benutzers.<br>• **Deutsch bleibt:** Alle deutschen Texte behalten ihren Wortlaut. |
| **`v1.5.13`** | 02.11.2026 | **Englische Notizen:**<br>• **Kurze Aufgaben:** *„the lawn has to be mowed“* ➔ *„Mow lawn“*, *„I need to call the doctor“* ➔ *„Call doctor“*. Verneinungen, Fragen und nicht vollständig umbaubare Sätze behalten ihren Wortlaut.<br>• **Termin und Priorität aus dem Satz:** *tomorrow at 8*, *next Monday at 5 pm*, *in two hours*, *March 15th*, *asap*, *important*, *someday*.<br>• **Englische Kategorien:** Eine neue englische Installation beginnt mit englischen Kategorien. Vorhandene Kategorien behalten ihre Namen und verstehen zusätzlich englische Wörter.<br>• **Neues Feld:** `brainstorm.add_idea` nimmt `language` an, zum Beispiel für einen Kurzbefehl in einer anderen Sprache. |
| **`v1.5.12`** | 02.11.2026 | **Vorbereitet auf weitere Sprachen, keine Änderung im Deutschen:**<br>• **Sprachpakete:** Alle deutschen Regeln liegen jetzt in einem eigenen Paket, bereit für weitere Sprachen.<br>• **Gleiche Ergebnisse:** Ein Referenztest mit über 1.100 Sätzen stellt sicher, dass deutsche Einträge genau wie bisher entstehen.<br>• **Andere Sprachen:** Home Assistant in einer anderen Sprache wendet keine deutsche Grammatik mehr auf deinen Text an. Er bleibt wie gesprochen, mit großem Anfangsbuchstaben. |
| **`v1.5.11`** | 02.11.2026 | **Ehrliche englische Dokumentation:**<br>• **Tabelle zur Sprachunterstützung:** Beide READMEs zeigen, was heute in welcher Sprache geht. Spracheingabe und Karten sind vorerst deutsch.<br>• **Richtige Beispiele:** Englische Beispiele für Befehle, die es nicht gibt, sind durch die echten deutschen mit Übersetzung ersetzt.<br>• **Fehlende Kapitel:** Das englische README beschreibt jetzt Sprachbefehle, manuelle Installation, das Einbinden der Karten und das Seitenleisten-Dashboard, sein Changelog ist vollständig.<br>• **HACS-Hinweis:** Beide READMEs sagen, dass HACS die Karten nicht mit installiert. |
| **`v1.5.10`** | 01.11.2026 | **Wörterbuch und optionale KI für gesprochene Einträge:**<br>• **Richtige Schreibweisen:** Namen von Personen und Kategorien sowie feste Begriffe wie *PDF* oder *Home Assistant* werden automatisch richtig geschrieben. Eigene Begriffe und Korrekturen stehen unter *Allgemeine Einstellungen*.<br>• **Mehr Hauptwörter:** Eine Wortliste und zusammengesetzte Wörter wie *Sportverein* verbessern die Großschreibung.<br>• **Optionale KI-Stufe:** Unter *Kalender, KI & Alexa* verbessert eine KI-Aufgaben-Entität den Eintrag im Hintergrund. Fügt sie Wörter oder Zahlen hinzu oder ändert eine Verneinung, bleibt die Fassung der Regeln stehen. Der Text geht an den Anbieter der gewählten KI, die Stufe ist standardmäßig aus. |
| **`v1.5.9`** | 01.11.2026 | **Datum, Priorität und Originaltext:**<br>• **Datum aus dem Satz:** *„morgen Arzt anrufen“* wird zu *„Arzt anrufen“* mit Termin und damit einer Erinnerung, ohne Uhrzeit um 9 Uhr. Der Skill sagt den Termin an. Der neue Schalter unter *Allgemeine Einstellungen* schaltet das ab, und ohne Erinnerungen bleibt das Datum im Text.<br>• **Priorität aus dem Satz:** „ganz wichtig“, „unbedingt“, „dringend“ und „irgendwann“ werden überall im Satz erkannt.<br>• **Originaltext:** Der gesprochene Satz bleibt gespeichert und lässt sich im Bearbeiten-Dialog der Karte übernehmen.<br>• **Kategorie als Subjekt:** *„Garten muss gegossen werden“* wird zu *„Garten gießen“* statt *„Muss gegossen werden“*. |
| **`v1.5.8`** | 01.11.2026 | **Bessere Kürzung gesprochener Einträge:**<br>• **Ganze Sätze werden umgebaut:** *„der Rasen muss gemäht werden“* wird zu *„Rasen mähen“* statt *„Rasen muss mähen“*. Das erkennt jetzt auch „sollte“, „will“, „möchte“ und trennbare Verben wie *„rausgestellt“*.<br>• **Neue Einstiege und Füllwörter:** „äh“, „ich glaube“, „mir ist eingefallen“, „vergiss nicht“, „mal“, „halt“ und ähnliche fallen weg.<br>• **Ganz oder gar nicht:** Verneinungen, Fragen und nicht vollständig umbaubare Sätze behalten ihren Wortlaut.<br>• **Getippter Text bleibt:** Eingaben im Dashboard und in To-do-Listen bekommen nur noch eine Rechtschreibkorrektur. |
| **`v1.5.7`** | 01.11.2026 | **Logo auf dem Echo Show:** Die Kopfzeile jeder Seite zeigt das Brainstorm-Logo. Der Echo lädt es aus diesem GitHub-Repository. Es ist kein neuer Skill-Code nötig. |
| **`v1.5.6`** | 01.11.2026 | **Neues Aussehen auf dem Echo Show:** Kacheln in zwei Spalten statt einer einfachen Liste, eine farbige Kopfzeile je Kategorie mit offenen und dringenden Einträgen, Seitenpunkte und Hinweise zu Priorität, Termin und übergeordneter Aufgabe. Überfällige Termine sind rot. Es ist kein neuer Skill-Code nötig. |
| **`v1.5.5`** | 01.11.2026 | **Listen erscheinen auf dem Echo Show:** Auf einem echten Echo Show blieb der Bildschirm leer, weil das Dokument seine Daten nicht bekam, und die Seitenzahl stimmte nicht. Es ist kein neuer Skill-Code nötig. |
| **`v1.5.4`** | 01.11.2026 | **Listen auf dem Echo Show:**<br>• **Bildschirm parallel zur Sprachantwort:** Eine Seite je Kategorie zum Wischen, mit Unteraufgaben und Prioritätsfarben.<br>• **Erledigen per Touch:** Antippen des Kreises erledigt eine Idee und beachtet private Ideen.<br>• **Neuer Satz:** *„zeige Alltag“* zeigt die Listen mit kurzer Antwort.<br>• **Einrichtung:** Braucht die Alexa Presentation Language in der Entwicklerkonsole sowie das neue Sprachmodell und den neuen Skill-Code. Älterer Skill-Code funktioniert weiter per Sprache. |
| **`v1.5.3`** | 01.11.2026 | **Karten bleiben bei privaten Ideen aktuell:**<br>• **Einrücken funktioniert wieder:** Mit aktiver Privatsphäre änderte sich der Sensor nicht, wenn eine Idee eingerückt, bearbeitet oder verschoben wurde, und die Karten zeigten weiter die alte Liste. Das konnte beim Einrücken auch zu einer falschen Zyklus-Meldung führen. Der Sensor hat jetzt ein Attribut `revision` ohne Ideeninhalte, das die Karten neu laden lässt. |
| **`v1.5.2`** | 01.11.2026 | **Home Assistant Quality Scale: Silber:**<br>• **Silber Regel für Regel geprüft:** Weiterhin eine Selbsteinschätzung.<br>• **Aktionen melden Fehler:** Eine nicht vorhandene Kategorie, unbekannte Einträge beim Sortieren oder Freigeben, eine unbekannte übergeordnete Idee und ein fehlgeschlagener Markdown-Export lösen jetzt einen klaren Fehler aus, statt `success: false` zu liefern oder ignoriert zu werden. To-do-Listen verhalten sich bei verschwundenen Einträgen genauso.<br>• **Tests:** Jedes Modul ist zu über 95 % abgedeckt, auch das Aufräumen beim Entladen.<br>• **Doku:** Alle Einrichtungsfelder und Einstellungen sind beschrieben. |
| **`v1.5.1`** | 01.11.2026 | **Home Assistant Quality Scale: Bronze:**<br>• **Bronze Regel für Regel geprüft:** README und Manifest nannten Silber, das stimmte nicht. Der Stand ist jetzt Bronze als Selbsteinschätzung, denn Home Assistant hat diese Custom-Integration nicht geprüft.<br>• **Kürzere Namen:** Listen heißen jetzt *Alltag* statt *Brainstorm: Alltag*, der Sensor *Ideen Übersicht*. Vorhandene Entitäts-IDs bleiben gleich, neue Listen erhalten `todo.brainstorm_hub_*`.<br>• **Kein Polling mehr:** Entitäten aktualisieren sich nur noch, wenn sich etwas ändert.<br>• **Klare Fehler:** Lassen sich gespeicherte Daten nicht lesen, versucht Home Assistant die Einrichtung erneut. Aktionen erklären, wenn die Integration nicht geladen ist.<br>• **Einstellungen:** Neue Einrichtungen speichern ihre Einstellungen in den Optionen, und jedes Feld hat jetzt eine Erklärung.<br>• **Tests und Doku:** Der Einrichtungsablauf ist vollständig getestet. Alle Aktionen und Felder, die Voraussetzungen und das Entfernen sind dokumentiert.<br>• **Markenbilder:** Jetzt echte PNG-Dateien in den richtigen Größen. |
| **`v1.5.0`** | 01.11.2026 | **Großes Update: Skill, Erinnerungen, Privatsphäre & Freigaben** (Zusammenfassung von v1.4.46 bis v1.4.64):<br>• **Sprache in einem Satz:** Optionaler eigener Alexa-Skill mit einer einzigen sauberen Antwort, Echo-Herkunft, Echo-Auswahl, iPhone-Kurzbefehl und Mikrofon in der Schnelleingabe.<br>• **Proaktive Erinnerungen:** Termine per Sprache, Liste, Karte oder Dienst, über Alexa und beliebige `notify`-Dienste, mit Handy-Knöpfen, Ruhezeiten, Briefing, Wochenrückblick, Regeln pro Liste, Orten, Personen, Kalender und KI.<br>• **Privatsphäre & Freigaben:** Private Einträge pro Benutzer, Freigabe von Einträgen und Kategorien mit Ansehen- oder Bearbeiten-Recht, Auswahlmodus, Echos und Apps pro Person.<br>• **Einstellungen:** Zurück-Navigation, Live-Status, Kanal-Test und ein Schalter für jede Funktion. |
| **`v1.4.64`** | 01.11.2026 | **Apfel-Logo für Siri:** Einträge aus einem iPhone-Kurzbefehl zeigen ein Apfel-Logo. |
| **`v1.4.63`** | 01.11.2026 | **Dokumentation:** iPhone-Kurzbefehl, Mikrofon, Privatsphäre und Freigaben sowie die neuen Dienste ergänzt. |
| **`v1.4.62`** | 01.11.2026 | **Siri als Quelle:** Einträge aus einem iPhone-Kurzbefehl mit der Quelle `siri` zeigen auf beiden Karten jetzt Siri und ihr Gerät. |
| **`v1.4.61`** | 01.11.2026 | **Assist-Mikrofon in der Schnelleingabe:** Ein Mikrofon neben dem Eingabefeld wandelt Sprache mit deiner bevorzugten Assist-Pipeline in Text um. Du kannst den Text vor dem Hinzufügen prüfen. Es lässt sich in den Karteneinstellungen abschalten und braucht HTTPS. |
| **`v1.4.60`** | 01.11.2026 | **Mehrere Einträge auswählen, Echos pro Person:**<br>• **Auswahlmodus:** Mehrere Einträge auf der Listenkarte auswählen und auf einmal erledigen, verschieben, freigeben oder löschen.<br>• **Echos und Apps pro Person:** Was an einem zugeordneten Gerät gesagt wird, gehört dieser Person, und nur ihre Einträge werden vorgelesen. Assist auf einem Satelliten ohne Benutzer bleibt beim Hauptbenutzer.<br>• **Native Ansagen:** Sie nutzen den Dienst `brainstorm.get_announcement` und funktionieren dadurch auch mit Privatsphäre. |
| **`v1.4.59`** | 01.11.2026 | **Einträge und Kategorien freigeben:** Mit eingeschalteter Privatsphäre lassen sich Einträge und ganze Kategorien für ausgewählte Personen oder alle freigeben, zum Ansehen oder Bearbeiten. Die Listenkarte bekommt einen Freigabe-Dialog, die Filter *Alle*, *Meine* und *Mit mir geteilt* sowie Kennzeichnungen. Die To-do-Listen zeigen, was für alle freigegeben ist, und wer eine Erinnerung bekommt, erhält auch Zugriff. Neuer Dienst `brainstorm.share`. |
| **`v1.4.58`** | 31.10.2026 | **Private Einträge pro Benutzer (Grundlage):** Neuer Schalter *Privatsphäre & Benutzer*, standardmäßig aus. Eingeschaltet gehören Einträge der Person, die sie angelegt hat: Der Sensor enthält keine Texte mehr, die Karten laden nur die eigenen Einträge, und Dienste, Assist, Logbuch, Sprache, Briefing und Erinnerungen halten sich daran. Vorhandene Einträge gehören dem gewählten Hauptbenutzer. Die To-do-Listen bleiben dabei leer. Freigaben folgen in der nächsten Etappe. |
| **`v1.4.57`** | 31.10.2026 | **Ausgewählte Kategorie bleibt:** Beide Karten merken sich die gewählte Kategorie nach dem Neuladen der Seite, pro Browser. Bei einer gelöschten Kategorie erscheinen wieder alle. |
| **`v1.4.56`** | 31.10.2026 | **Einstellungen mit Zurück-Navigation, Live-Status und Kanal-Test:**<br>• **In den Einstellungen bleiben:** Speichern wirkt sofort und führt zurück ins Menü. Jedes Formular kann ohne Speichern zurück, und die Titel zeigen, wo du bist.<br>• **Live-Status:** Das Erinnerungsmenü zeigt, was eingeschaltet ist und welche Erinnerung als Nächstes kommt.<br>• **Kanal-Test:** *Kanäle jetzt testen* sendet eine echte Nachricht und meldet das Ergebnis pro Kanal. |
| **`v1.4.55`** | 31.10.2026 | **Eigener Name für die Alexa-App:** Home Assistant kann die Alexa-App nicht selbst erkennen. In den Skill-Einstellungen lässt sich das zuletzt unbekannte Gerät deshalb benennen, zum Beispiel *Alexa App iPhone*. Der Name steht danach ohne Wartezeit an seinen Einträgen. |
| **`v1.4.54`** | 31.10.2026 | **Verlässliche Erinnerungsziele:** Bei unbekannter Herkunft, etwa einem Satz aus der Alexa-App, sprechen nur feste Echos und nie der zuletzt genutzte. Ein über seine Notify-Entität gewähltes Handy findet seinen eigenen Dienst jetzt auch nach dem Umbenennen, sodass die Knöpfe erscheinen. |
| **`v1.4.53`** | 31.10.2026 | **Löschen:** Ein Doppeltipp auf Löschen in der Listenkarte zeigt keine falsche Fehlermeldung mehr. |
| **`v1.4.52`** | 31.10.2026 | **Erinnerungen erreichen den richtigen Echo:** Gleichnamige Echos aus anderen Integrationen wie Music Assistant bekommen die Ansage nicht mehr. Auch beim Auswählen der Notify-Entität eines Handys erscheinen jetzt die Knöpfe. |
| **`v1.4.51`** | 31.10.2026 | **Erinnerungsregeln, Orte, Personen, Kalender und KI:**<br>• **Jede Funktion hat einen eigenen Schalter** in einem neuen Einstellungsmenü, dazu ein Hauptschalter.<br>• **Regeln pro Liste:** private Listen nur aufs Handy, Listen an bestimmten Tagen oder an einem Ort.<br>• **Orte und Personen:** Erinnerungen beim Heimkommen oder an Zonen und für andere Personen mit eigenen Kanälen.<br>• **Nachfassen und Extras:** wichtige offene Einträge an weitere Dienste, ein Briefing, das auf jemanden wartet, Kalendereinträge, KI-Zusammenfassungen und optional echte Alexa-Erinnerungen. |
| **`v1.4.50`** | 31.10.2026 | **Proaktive Erinnerungen, Briefing und Wochenrückblick:**<br>• **Termine** per Sprache, in den To-do-Listen, auf der Karte und über Dienste.<br>• **Deine Kanäle:** Alexa-Ansage und beliebige `notify`-Dienste, Handy-Knöpfe, Wartezeit und das Ereignis `brainstorm_reminder_due`.<br>• **Ruhezeiten, tägliches Briefing und Wochenrückblick.**<br>• **Skill:** neue Sätze *erinnere mich*, *erledigt* und *später*; *Ansage* gibt jetzt einen kurzen Überblick. Der Skill braucht einen neuen Build und neuen Code. |
| **`v1.4.49`** | 31.10.2026 | **Alexa-Skill mit den nativen Funktionen:**<br>• **Echo-Herkunft:** Ideen aus dem Skill zeigen den Echo, von dem sie stammen. Home Assistant lernt jeden Echo einmal aus dem Alexa-Verlauf und kennt ihn danach sofort.<br>• **Echo-Auswahl:** Echos außerhalb der Auswahl werden auch im Skill still ignoriert.<br>• **Gleiche Sprache:** Der Skill versteht die nativen Befehlswörter und bereinigt den Text genauso.<br>• **Ansage und Menü:** *„Alexa, sage Brainstorm Ansage“* liest deine Ideen vor, auch pro Kategorie, und *„Alexa, starte Brainstorm“* öffnet das Menü. |
| **`v1.4.48`** | 31.10.2026 | **Alexa-Skill mit Home Assistant Cloud:** Die Skill-Einrichtung meldet keine fehlende öffentliche HTTPS-Adresse mehr, wenn Home Assistant über Home Assistant Cloud (Nabu Casa) erreichbar ist. Unverschlüsselte Adressen werden nie angeboten. |
| **`v1.4.47`** | 31.10.2026 | **Optionaler Alexa-Skill für die Spracheingabe in einem Satz:**<br>• **Sprachmodi:** Neue Optionen unter *Alexa-Spracheingabe & Skill* mit **Nativ** (Standard, unverändert), **Skill** und **Beide**.<br>• **Eigener Skill:** *„Alexa, sage Brainstorm notiere …“* gibt jetzt eine einzige saubere Antwort. Home Assistant erzeugt Skill-Code und Sprachmodell zum Kopieren, koppelt den ersten Skill automatisch und weist andere ab.<br>• **Verlässliche Antworten:** Alexa bestätigt nur, was wirklich gespeichert wurde. |
| **`v1.4.46`** | 31.10.2026 | **Ausgewählte Echos für die Spracheingabe:**<br>• **Neue Option:** Unter *Allgemeine Einstellungen & Export* gibt es jetzt eine Mehrfachauswahl für Alexa-Media-Echos. Nur die ausgewählten Echos können Ideen per Sprache erfassen und Brainstorm öffnen; bei leerer Liste funktionieren weiterhin alle Echos.<br>• **Für Automationen:** Die Auswahl steht als Attribut `allowed_echos` von `sensor.brainstorm_ideen_ubersicht` bereit. |
| **`v1.4.45`** | 31.10.2026 | **Zuverlässige Kategorien, Auto-Export, LLM-Tools, Text-Optimierung & Sicherheit:**<br>• **Options-Flow:** Hinzufügen und Löschen von Kategorien wird nicht mehr durch das vorausgefüllte Listenfeld rückgängig gemacht; die Liste wird nur noch übernommen, wenn sie tatsächlich bearbeitet wurde.<br>• **Dauerhafte Kategorien:** Gelöschte Standardkategorien bleiben nach Reload oder Neustart gelöscht, die eigene Reihenfolge bleibt erhalten.<br>• **Auto-Export:** Ein fehlgeschlagener Markdown-Export wird protokolliert und bricht die Aktion nicht mehr ab, Events und Entity-Updates laufen weiter. Die Exportdaten werden im Event-Loop statt im Executor zusammengestellt.<br>• **LLM-Tools:** `brainstorm_list_categories` stürzt nicht mehr ab, die Kategorie `all` und Namen in beliebiger Schreibweise funktionieren, und mehrdeutige Lösch- oder Erledigt-Anfragen liefern jetzt die Kandidaten, statt den ersten Treffer zu ändern.<br>• **Text-Optimierung:** Bleibt nur ein Wort übrig, bleibt das Kategoriewort erhalten (*Haus streichen*), Schreibweisen wie *WLAN* oder *iPhone* bleiben bestehen, und Großschreibung, Infinitive und Genitiv-Artikel werden korrekt behandelt.<br>• **Sicherheit:** Markdown-Exporte sind auf Unterordner des Config-Verzeichnisses und `allowlist_external_dirs` beschränkt, Kategorienamen werden in beiden Karten maskiert, Icons und Farben werden geprüft (Farben müssen Hex-Werte sein).<br>• **Recorder:** Große Sensor-Attribute werden nicht mehr aufgezeichnet, das vermeidet das 16-KB-Limit.<br>• **Reconfigure:** Änderungen greifen jetzt auch bei vorhandenen Optionen, ohne den veralteten Reload-Helper.<br>• **Lifecycle:** Modul-Reload zur Laufzeit und Eingriffe in den Übersetzungs-Cache entfernt, Services werden jetzt in `async_setup` registriert, der nicht funktionsfähige YAML-Import ist entfernt. Python-Änderungen brauchen jetzt einen Neustart.<br>• **To-do-Listen:** Entitäten gelöschter Kategorien werden entfernt, archivierte Ideen erscheinen nicht mehr als offen, und das Bearbeiten erledigter Ideen löst `idea_completed` nicht erneut aus.<br>• **Datenintegrität:** Eltern-Zyklen werden abgelehnt, unbekannte IDs lösen einen Fehler aus, und die Option `default_category` funktioniert jetzt.<br>• **Kompatibilität:** LLM-Tools nutzen `ToolResult` und Annotations, Mindestversion ist Home Assistant 2026.10.<br>• **Tests:** Testsuite ergänzt, die gegen echtes Home Assistant läuft. |
| **`v1.4.44`** | 30.10.2026 | **Anzeige der zuletzt aktiven Alexa (Last Alexa) mit Entitätsauswahl & Robuster visueller Karteneditor:**<br>• **Last-Alexa-Badge in Karten-Kopfzeilen:** Anzeige eines dezenten, interaktiven Badges (`.last-alexa-badge`) mit Mikrofon-Icon und Klarnamen des aktiven Echo-Geräts im Header der `brainstorm-card` und der Toolbar der `brainstorm-mindmap-card`. Ein Klick auf das Badge öffnet direkt den nativen Home Assistant *More-Info*-Dialog des aktiven Geräts.<br>• **Visuelle Entitätsauswahl in den Karteneinstellungen:** Schalter *„Zuletzt aktive Alexa (Last Alexa) anzeigen“* (`show_last_alexa`) sowie Entitäts-Picker für *„Last Alexa Entität“* (`last_alexa_entity`, z. B. `sensor.last_alexa` oder beliebiges `media_player`-Gerät) in beiden visuellen Lovelace-Karteneditoren.<br>• **Robuster visueller Karteneditor:** Grundlegende Absicherung der Editor-Komponenten (`BrainstormCardEditor` & `BrainstormMindmapCardEditor`) mit Vorab-Initialisierung der Lovelace-Form-Helper (`static async getConfigElement()`), `connectedCallback()`-Lifecycle und bereinigtem Event-Merging, wodurch versehentliches Zurücksetzen von Boolean-Einstellungen ausgeschlossen ist. |
| **`v1.4.43`** | 30.10.2026 | **Optimierte Benutzerführung im Kategorie-Design (Klare Schritt-Abfolge & Aktionen):**<br>• **Eindeutiger „Weiter“-Button statt verwirrendem „OK“:** In Schritt 1 der Kategorie-Auswahl wurde `last_step=False` hinterlegt. Der Home-Assistant-Aktionsbutton heißt nun eindeutig *„Weiter“* anstelle des missverständlichen *„OK“*, wodurch sofort ersichtlich ist, dass es sich um einen 2-Schritt-Assistenten handelt.<br>• **Aussagekräftige Schritt-Titel & Beschreibungen:** Schritt 1 ist jetzt klar als *„Kategorie-Design (Schritt 1 von 2)“* ausgewiesen mit dem Hinweis, dass Icon und Farbe im nächsten Schritt folgen. Schritt 2 leitet mit *„Design für ‚{category}‘ (Schritt 2 von 2)“* direkt in die MDI-Icon-Suche und Farbwahl.<br>• **Zustands-Vorschau in der Auswahlliste:** Das Kategorie-Dropdown zeigt nun für jede Kategorie die aktuell vergebenen Icons und Farben in Klammern an (z. B. `Smarthome (Icon: mdi:home, Farbe: #03a9f4)` oder `Inbox (Standard)`).<br>• **Aktion „Fertig & Schließen“:** Nach dem Speichern des Stylings steht nun neben *„Weitere Kategorie anpassen“* und *„Zurück zum Hauptmenü“* die direkte Option *„Fertig & Schließen“* zur Verfügung. |
| **`v1.4.42`** | 30.10.2026 | **Direkte Menü-Label-Übergabe in den Hub-Optionen (Dauerhafte Behebung der leeren Menüzeile):**<br>• **Garantierte Menübeschriftung:** Übergabe expliziter lokalisierter Wörterbücher (`dict[str, str]`) in `async_show_menu` für die Schritte `init` und `category_style_done`. Dadurch wird die fehleranfällige Frontend-Übersetzungs-Cache-Auflösung vollständig umgangen. Der Menüpunkt *„Kategorie-Design (Farbe & Icon)“* wird unabhängig vom Zustand des lokalen Browser-Caches oder Home-Assistant-Neustarts immer zuverlässig und sauber dargestellt.<br>• **Zweisprachige Unterstützung:** Automatische Erkennung der Spracheinstellung (`de` vs. `en`) mit sicherem Fallback. |
| **`v1.4.41`** | 30.10.2026 | **Maximale Raumnutzung der Glühbirne & Prägnantes Logodesign:**<br>• **Flächendeckende Birnen-Geometrie:** Das Vektordesign der Brainstorm-Glühbirne wurde mit einer breiteren, runderen Kuppel (Seitenverhältnis ~0.92:1) und einem kompakten Metallsockel grundlegend optimiert. Leere Seitenränder im quadratischen Logo-Container gehören der Vergangenheit an – die sichtbare Fläche der leuchtenden Birne hat sich mehr als verdoppelt (+132 %).<br>• **Präzise ViewBox & Minimiertes Padding:** Durch die maßgeschneiderte `viewBox="136 58 240 261"` und 1px Innenabstand im 36px-Container nutzt die Glühbirne den verfügbaren Platz in der Kopfzeile beider Karten nun vollständig von Rand zu Rand aus.<br>• **Universelle Asset-Aktualisierung:** Synchroner Einsatz des optimierten Vektors in `brainstorm-card`, `brainstorm-mindmap-card`, `brainstorm-logo.svg` und `brainstorm-bulb.svg` (inkl. zentralem Mindmap-Wasserzeichen und Konfigurations-Editoren). |
| **`v1.4.40`** | 29.10.2026 | **Adaptives Logo-Design (Hell & Dunkel), Vektor-Optimierung & Ein-/Ausblenden:**<br>• **Design-Adaptiver Logo-Hintergrund:** Der Logo-Container in `brainstorm-card` und `brainstorm-mindmap-card` passt sich über dynamisches CSS-Color-Mixing (`color-mix(in srgb, var(--primary-color) 12%, var(--card-background-color))`) nun nahtlos dem aktiven Home Assistant Theme an. Kein unschöner schwarzer Kasten mehr bei hellen Themes!<br>• **Gestochen scharfe Vektorgrafik:** Überarbeitete Vektor-Glühbirne mit transparentem Hintergrund, leuchtenden Synapsen, goldenem Ideen-Blitz und metallischem Sockel ohne unleserlichen Mikro-Text oder Artefakte bei kompakten Icon-Größen.<br>• **Logo ein- und ausblenden (`show_logo`):** Neuer Schalter `show_logo: true/false` sowohl per YAML als auch in den visuellen UI-Karteneditoren (`BrainstormCardEditor` & `BrainstormMindmapCardEditor`), um das Logo in der Kopfzeile nach Wunsch ein- oder auszublenden.<br>• **Synchronisation des Optionsmenüs:** Bereinigung der Menü-Labels in den Hub-Optionen (`async_step_init`), sodass stets alle Menüpunkte vollständig beschriftet sind. |
| **`v1.4.39`** | 29.10.2026 | **100 % Responsive Kartendesigns & Umfassende Mobile-Optimierung:**<br>• **Container Queries & Dynamische Spaltenanpassung:** Einführung moderner CSS Container Queries (`@container (max-width: ...)`) parallel zu Viewport-`@media`-Queries in `brainstorm-card` und `brainstorm-mindmap-card`. Die Karten passen ihre Dichte, Typografie, Header und Schnellerfassungsleisten nun dynamisch an die exakte Breite ihres Einbettungscontainers an – egal ob auf Smartphones, Tablets oder in schmalen Mehrspalten-Sektionen auf Desktop-Dashboards.<br>• **Adaptive Mindmap-Geometrie & Mobiles Auto-Fit:** Das radiale Mindmap-Layout passt seine elliptischen Radien (`rx0`, `ry0`) und Kollisionsabstände bei geringer Kartenbreite (< 550px) dynamisch an. Die automatische Skalierungsuntergrenze wurde auf 0.35 abgesenkt, sodass selbst umfangreiche Mindmaps auf Handydisplays immer vollständig zentriert sichtbar bleiben ohne abzuschneiden.<br>• **Mobiles Vollbild-Mindmap-Modal:** Das Öffnen des Mindmap-Popup-Layers auf Mobilgeräten (< 768px) füllt nun nahtlos 100 % des Bildschirms im App-Stil aus (ohne störende Ränder oder Randverschnitt).<br>• **Touch-Bedienbarkeit & Schutz vor iOS-Auto-Zoom:** Text- und Eingabefelder erzwingen eine Mindestschriftgröße von 16px (`max(0.92rem, 16px)`), wodurch das lästige automatische Hineinzoomen von iOS Safari beim Fokussieren von Eingabefeldern wirksam unterbunden wird. Aufgaben-Aktionen (`✎`, `✕`, `↳`) bleiben auf Touchscreens (`@media (hover: none)`) dauerhaft sichtbar und bequem bedienbar.<br>• **Responsive Modaldialoge:** Prioritäts- und Kategorie-Raster in Bearbeitungsdialogen wechseln auf kleinen Displays automatisch in ein sauberes 2-Spalten-Layout ohne Textüberlauf. |
| **`v1.4.38`** | 29.10.2026 | **Bugfix Menü-Labels in den Optionen & Dynamische Cache-Invalidierung:**<br>• **Direkte Label-Übergabe im Optionsmenü:** Behebung der leeren Menüzeile in den Hub-Einstellungen (*„Brainstorm Hub Optionen“*), bei der der zweite Menüpunkt (*„Kategorie-Design (Farbe & Icon)“*) aufgrund eines verzögerten Frontend-Übersetzungscaches ohne Text dargestellt wurde. `async_show_menu` übergibt die Menüeinträge nun direkt als lokalisiertes Wörterbuch.<br>• **Automatische Übersetzungscache-Bereinigung:** `async_setup_entry` invalidiert nun zur Laufzeit den internen Home Assistant `_TranslationCache` (`async_invalidate`), sodass neue Schritte und Optionsmenüs sofort nach dem Neuladen der Integration aktiv sind, ohne dass ein kompletter Home-Assistant-Neustart erforderlich ist. |
| **`v1.4.37`** | 29.10.2026 | **Logbuch- & Aktivitäts-Zuordnung (Home Assistant „Was ist passiert?“ Ursachen-Kette):**<br>• **Aufgabe als Grund im Aktivitäts-Dialog:** Beim Öffnen des Reiters *„Aktivität“* (Logbuch) auf `sensor.brainstorm_ideen_ubersicht` und Klick auf einen Eintrag wird unter *„Was ist passiert?“* nun die konkrete Aufgabe mit Kategorie und Aktion (`Idee erfasst`, `Idee erledigt`, `Idee geändert`, `Idee gelöscht`) direkt als Grund ausgewiesen, anstelle von leeren Zustandswechseln oder *„Für diese Aktivität wurde kein Grund erfasst“*.<br>• **Native Kontext- & Entitäts-Verknüpfung:** Eintreffende Ereignisse (`EVENT_IDEA_ADDED`, `EVENT_IDEA_COMPLETED`, `EVENT_IDEA_UPDATED`, `EVENT_IDEA_DELETED`) übergeben nun die `entity_id` (`sensor.brainstorm_ideen_ubersicht`) und bewahren den ursprünglichen Aktionskontext (`call.context`). Über `async_set_context(context)` verknüpft der native Chain-Resolver von Home Assistant den auslösenden Benutzer, den Dienstaufruf und das Brainstorm-Ereignis nahtlos miteinander.<br>• **Sensor-Attribut `last_action`:** `sensor.brainstorm_ideen_ubersicht` stellt die letzte Aktion mit Notiztext, Kategorie, Priorität, Zeitstempel und Zusammenfassung als Attribut für Templates, Scripts und Automationen bereit. |
| **`v1.4.36`** | 29.10.2026 | **Schlankes, kompaktes Zeilendesign & Smartphone-Optimierung:**<br>• **Reduzierte Aufgaben-Zeilenhöhe:** Grundlegende Straffung der Aufgabenhöhe in `brainstorm-card` (Padding von 12px auf 8px/6px reduziert, vertikaler Listenabstand von 8px auf 5px/4px, optimierte Zeilenhöhe). Deutlich mehr Notizen auf einen Blick ohne langes Scrollen.<br>• **Smartphone- & iPhone-Feinschliff:** Spezifische Mobile-Breakpoints (`@media (max-width: 600px)` und `380px`) mit schlankeren Checkboxen (18px), kompakten Badges und optimierter Unteraufgaben-Einrückung (10px statt 24px/16px). Verhindert horizontales Zusammendrücken und vorzeitiges Umbrechen auf schmalen iPhone-Displays.<br>• **Neue Option „Kompakte Zeilenhöhe“ (`compact_mode`):** Im visuellen UI-Karteneditor zuschaltbar für maximale Informationsdichte auf Tablets und Dashboards.<br>• **Kompakte Mindmap-Wolken:** Proportionierte Notizwolken in `brainstorm-mindmap-card` auf mobilen Bildschirmen. |
| **`v1.4.35`** | 29.10.2026 | **Frei wählbare Farben & Home Assistant MDI-Icons für Kategorien:**<br>• **Kategorie-Design in den Einstellungen:** Neuer Menüpunkt *„Kategorie-Design (Farbe & Icon)“* im Hub-Optionsmenü (`OptionsFlow`). Kategorien können nun direkt mit dem nativen Home Assistant Icon-Picker (`selector.IconSelector` mit MDI-Volltextsuche) und visuellem Farb-Picker (`selector.ColorRGBSelector`) gestaltet werden.<br>• **1-Klick Farb- & Icon-Editor auf der Karte:** Über das neue 🎨-Icon auf dem aktiven Kategorie-Tab in `brainstorm-card` lässt sich das Design direkt aus dem Dashboard im Dialog mit Live-Vorschau anpassen oder auf Standard zurücksetzen.<br>• **Nahtlose Visualisierung:** Sämtliche Kategorie-Pills, Notiz-Tags und der zentrale Mindmap-Hub (`brainstorm-mindmap-card`) rendern die Icons und Akzentfarben harmonisch im gesamten Dashboard.<br>• **Neuer Service:** `brainstorm.set_category_style` zur Steuerung über Scripts und Automationen; `brainstorm.add_category` um optionale Attribute `icon` und `color` erweitert. |
| **`v1.4.34`** | 29.10.2026 | **Bereinigung der Kategorie-Optionen (Deduplizierung `hide_empty_categories`):**<br>• Die redundante Konfigurationsoption *„Kategorien ohne Notizen (0) ausblenden“* wurde aus den *„Allgemeinen Einstellungen“* des Hubs entfernt.<br>• Die globale Standardeinstellung für Dashboards verbleibt nun logisch und fokussiert direkt unter *„Kategorien verwalten“* sowie individuell konfigurierbar je Lovelace-Karte. |
| **`v1.4.33`** | 29.10.2026 | **Vibe Coding Manifest & Badges:** Offizieller Hinweis und Badges zur leidenschaftlichen KI-gestützten Entwicklung (*„Vibe Coding mit voller Hingabe“*) in Dokumentation und Repositories aufgenommen. |
| **`v1.4.32`** | 29.10.2026 | **Zweisprachige Dokumentation (EN/DE), Alexa Key-Feature Spotlight & 1-Klick Installation:**<br>• **Vollständige englische Dokumentation:** Umfassendes englisches Handbuch (`README.md`) parallel zur deutschen Version (`README_de.md`) mit intuitivem Länderflaggen-Umschalter (`🇩🇪 Deutsch` ⇄ `🇬🇧 English`).<br>• **Key-Feature Spotlight Amazon Alexa:** Ausführliche Dokumentation der nahtlosen Alexa-Spracherfassung als zentrales Highlight (Hands-Free Notizenerfassung, Zwei-Wege-Dialog, Schutz vor Musik- und Einkaufslisten-Kollisionen, automatische NLP-Grammatikbereinigung und Echo-Geräteherkunft).<br>• **1-Klick My Home Assistant Badges:** Schnelle Installation via HACS-Redirect und nativer Config-Flow-Start mit einem Klick.<br>• **Versions- & Komponenten-Synchronisation:** Einheitlicher Release-Stand für Karten, Sensoren und Plattform. |
| **`v1.4.31`** | 29.10.2026 | **Hintergrund-Rendering Fix & Synchrones Punktraster:**<br>• **Beseitigung von Farb- und Blockartefakten im Hintergrund:** Behebung eines Darstellungsfehlers in `brainstorm-mindmap-card`, bei dem harte Gradientenstopps (`radial-gradient`) und GPU-Layer-Promotion (`will-change: transform`) auf dem Canvas zu Moiré-Interferenzen, Kachelsäumen und sichtbaren Farbblöcken führten, die sich beim Zoomen oder Scrollen störend verschoben haben.<br>• **Subpixel-Anti-Aliasing & Canvas-Transparenz:** Weiche Anti-Aliasing-Übergänge für das Punktraster sowie vollständige Bereinigung überlagernder Hintergrundfarben (`canvas-area` transparent über `ha-card`).<br>• **Synchrones Pan & Zoom:** Das Hintergrundraster bewegt und skaliert sich nun natürlich mit dem Mindmap-Viewport (`background-position` & `background-size`).<br>• **Konfigurierbares Raster:** Neue Option `show_grid` (im UI-Editor als *„Punktraster im Hintergrund anzeigen“* schaltbar). |
| **`v1.4.30`** | 29.10.2026 | **Bugfix Mindmap-Synapsen beim Umschalten von Kategorien:**<br>• **Keine Geisterlinien / leere Verbindungslinien mehr:** Behebung eines Fehlers in `brainstorm-mindmap-card`, bei dem beim Wechsel der Kategorie (z. B. von *„Alle“* auf *„Smarthome“*) die synaptischen Bézier-Linien zuvor angezeigter Notizen ohne Ideenkärtchen im Raum stehenblieben. Die Rendering-Logik (`_drawConnections`) validiert nun strikt, dass Verbindungslinien ausschließlich für Notizen der aktuell aktiven Kategorie gezeichnet werden, die auch tatsächlich als DOM-Element existieren.<br>• **Zuverlässige Layout- & Positions-Bereinigung:** Beim Umschalten auf eine andere Kategorie (via Toolbar-Pill oder Klick auf den Zentrums-Node) werden vorherige Knotenpositionen (`_nodePositions`) und Drag-Zustände sofort zurückgesetzt, sodass die verbleibenden Notizen harmonisch und frei von Artefakten neu arrangiert werden. |
| **`v1.4.29`** | 29.10.2026 | **Drag & Drop Sortierung, Unteraufgaben-Zuweisung & Apple Reminders Kontextmenü:**<br>• **Drag & Drop Sortierung in der Liste:** Notizen lassen sich nun per Drag & Drop über den Anfasser (`⠿`) intuitiv und flüssig in der Notizenliste nach oben oder unten verschieben. Die Reihenfolge wird über den Service `brainstorm.reorder_ideas` persistent im Store gespeichert (`order`-Attribut).<br>• **Drag & Drop Unteraufgaben-Zuweisung:** Ziehen einer Notiz nach rechts auf eine bestehende Hauptaufgabe blendet ein visuelles Feedback (`↳ Als Unteraufgabe`) ein und weist die Notiz beim Loslassen direkt als Unteraufgabe zu.<br>• **Apple Reminders Touch-Interaktion (Smartphone):** Langes Drücken (~420ms) auf eine Notiz am Smartphone (bzw. Rechtsklick am Desktop) öffnet ein elegantes Apple Reminders Style Kontextmenü mit dezentem Haptik-Feedback (`vibrate`). Ermöglicht 1-Tap Einrücken unter die vorherige Hauptaufgabe (*„Unteraufgabe einrücken (unter: ‚...‘)“*), Ausrücken (*„Wieder zur Hauptaufgabe machen“*), Verschieben nach oben/unten sowie direktes Bearbeiten und Löschen. |
| **`v1.4.28`** | 29.10.2026 | **Ausblenden leerer Kategorien (0) als Standard aktiviert (`hide_empty_categories: true`):**<br>• **Standardmäßig saubere Filterleisten:** Kategorien ohne aktive Notizen (z. B. *„Inbox 0“*, *„Projekte 0“*, *„Familie 0“*, *„Einkauf 0“*) werden nun in `brainstorm-card` und `brainstorm-mindmap-card` standardmäßig ausgeblendet, ohne dass eine manuelle Konfiguration in jedem Dashboard nötig ist.<br>• **Konfigurationsauflösung korrigiert:** Behebung eines Problems in beiden Karten, bei dem ungesetzte Card-Properties fälschlicherweise das globale Ausblenden überschrieben haben. Die Priorität greift nun zuverlässig: Individuelle Karteneinstellung ➔ Globale Integrationsoption ➔ Standard aktiv (`true`).<br>• **Fokus-Sichtbarkeit:** Neu erstellte oder aktiv angeklickte leere Kategorien bleiben zur Orientierung und schnellen Befüllung sichtbar, solange sie im Fokus stehen. |
| **`v1.4.27`** | 28.10.2026 | **Hierarchische Unteraufgaben, Aktives Kategorie-Routing & Mobile Mindmap-Pills:**<br>• **Unteraufgaben in der Liste einrücken:** Notizen lassen sich nun mit 1 Tap (`↳` unter vorherige Hauptaufgabe einrücken / `↰` zur Hauptaufgabe ausrücken) sowie über ein neues Dropdown im Bearbeiten-Dialog (`✏️`) als Unteraufgabe zuweisen. Mobile-optimierte Touch-Targets (mind. 28×28px, dauerhafte Sichtbarkeit auf Smartphones) für einfache Handhabung unterwegs. Visuelle Darstellung mit Einrückung, farbiger Führungslinie, `↳`-Indikator und Badge.<br>• **Schnellerfassung in aktiver Kategorie:** Wenn ein Kategorie-Tab (z. B. *„Smarthome“*, *„Haus & Garten“*, *„Brainstorm“*) aktiv ist, werden neue Notizen aus dem Schnellerfassungsfeld automatisch exakt dieser Kategorie zugeordnet, ohne bei fehlenden Schlagwörtern in die *„Inbox“* zu rutschen. Kategorie-Dropdown und Platzhaltertext passen sich synchron an den aktiven Tab an.<br>• **Mindmap-Toolbar auf Smartphones:** Die Kategorie *„Alle“* wird auf Mobilgeräten (`≤ 600px`) in der Mindmap-Toolbar automatisch ausgeblendet, um den horizontalen Platz optimal für konkrete Themenkategorien zu nutzen; das Antippen des Zentrum-Nodes überspringt *„Alle“* auf Smartphones automatisch. |
| **`v1.4.26`** | 28.10.2026 | **Konfigurierbares Ausblenden leerer Kategorien (0):** Neue Option *„Kategorien ohne Notizen (0) ausblenden“* (`hide_empty_categories`), um die Filterleisten (Pills) von `brainstorm-card` und `brainstorm-mindmap-card` von ungenutzten Kategorien freizuhalten. Die Funktion ist flexibel an zwei Stellen konfigurierbar: direkt in den Integrations-Optionen (unter *„Kategorien verwalten“* und *„Allgemeine Einstellungen“* als globale Standardeinstellung für alle Dashboards) sowie individuell je Lovelace-Karte im visuellen Karteneditor (`ha-form` & Fallback). Bei aktiver Option werden nur Kategorien mit mindestens einem aktiven Eintrag angezeigt; die gerade ausgewählte Kategorie bleibt zur Orientierung sichtbar und Schnellerfassungs-Dropdowns behalten stets den vollen Zugriff auf alle Kategorien. |
| **`v1.4.25`** | 25.10.2026 | **Dynamisches Kategorie-Dropdown in visuellen Karteneditoren:** Ersatz des statischen Textfelds für *„Standard-Kategorie im Fokus“* (`default_category`) in den Lovelace-UI-Editoren (`ha-form`) beider Karten (`brainstorm-card` und `brainstorm-mindmap-card`) durch ein dynamisches Dropdown-Menü. Das Dropdown listet automatisch alle verfügbaren Standard- und benutzerdefinierten Kategorien mit passenden Icons (z. B. `🌟 Alle Kategorien`, `📥 Inbox`, `🔷 Smarthome`, `🟢 Haus & Garten`, `🟣 Projekte`, `🟡 Alltag`, `🔮 Brainstorm`) auf und erlaubt dank `custom_value: true` bei Bedarf weiterhin die freie Eingabe. |
| **`v1.4.24`** | 25.10.2026 | **Bugfix JavaScript-Syntaxfehler in Brainstorm Mindmap Card:** Behebung eines Syntaxfehlers (`orphaned code block / unexpected token`) in `brainstorm-mindmap-card.js` innerhalb des `_showAddDialog`-Event-Listeners, durch den das Skript im Browser nicht evaluiert werden konnte und Home Assistant den Fehler *„Konfigurationsfehler: Custom element doesn't exist: brainstorm-mindmap-card“* anzeigte. Vollständige Bereinigung des Codes und Aktualisierung der Cache-Buster. |
| **`v1.4.23`** | 25.10.2026 | **Responsiver Header & Farbmodus-Fix:** Vollständige Neustrukturierung und Entrümpelung des Card-Headers und der Schnellerfassung in `brainstorm-card`. Integration von Titel und Status-Badge (`header-titles`), kompakte Anordnung der Aktionen (`header-actions`) und Ablösung der überladenen, doppelten Toolbar durch eine ultra-schlanke, einteilige **Quick Capture Card** (`.quick-capture-card`). Wegfall redundanter Buttons und statischer Textlabels; elegante Chip-Dropdowns für Kategorie (`🏷️`) und Priorität nebeneinander. Optimierte Mobile-Breakpoints (`@media (max-width: 520px)` und `380px`) für perfekte Touch-Bedienung und zentriertes Layout auf Smartphones. **Bugfix Farbmodus-Umschalter:** Korrektur von `_getCategoryColor` in beiden Karten (`brainstorm-card` und `brainstorm-mindmap-card`), sodass der runde Farbmodus-Button (`🎨` / `🌈`) nun sofort und reaktiv zwischen dem aktiven Home Assistant Theme-Farbton (`var(--primary-color)`) und lebendigen Multicolor-Kategoriefarben umschaltet und die Auswahl browserweit synchronisiert. |
| **`v1.4.22`** | 25.10.2026 | **Prioritäten-Management & Visuelle Dringlichkeit:** Einführung von vier Prioritätsstufen (`low` 🟢, `medium` 🟡, `high` 🔴, `urgent` 🔥) mit automatischer Signalwort- und Tag-Erkennung (`dringend`, `wichtig`, `sofort`, `eilig`, `prio 1`, `wenn zeit`, `!urgent`, `!high` etc.) bei Spracheingaben via Alexa und Assist. 2-Pass-Parsing filtert Signalwörter unabhängig von der Reihenfolge der Kategoriepräfixe sauber heraus. 1-Klick-Prioritätswechsel direkt auf den Badges beider Lovelace-Cards (`brainstorm-card` und `brainstorm-mindmap-card`). Feuer- und Puls-Effekte für dringende Gedankenwolken in der Mindmap. Vollständige Integration in Sensoren (`priority_counts`), To-do-Listen, Logbook, Markdown-Export und Assist LLM Function-Calling API. |
| **`v1.4.21`** | 25.10.2026 | **Dynamische Kategorie-Erkennung & Semantisches Routing:** Vollständige dynamische Synthese von Aliassen und Schlagwörtern für alle aktiven Kategorien (inkl. *„Brainstorm“* und frei erstellten Kategorien) zur Laufzeit. Direkte Erkennung zusammengesetzter Projekt- und Themenpräfixe (*„Projekt Brainstorm erweitern“* ➔ ordnet *„Brainstorm erweitern“* zielsicher der Kategorie *„Projekte“* bzw. *„Brainstorm“* zu, statt in der Inbox zu landen). Behebung einer Fehlleitung im Alexa-Hauptmenü-Workflow (`brainstorm_alexa_main_menu_response`), bei der gesprochene Notizen mit Projektbezug versehentlich als Abfragebefehl abgefangen wurden. |
| **`v1.4.20`** | 24.10.2026 | **Assist LLM Tools & Function-Calling Integration:** Vollständige Bereitstellung des offiziellen Home Assistant LLM API (`homeassistant.helpers.llm`) für Sprachmodelle (OpenAI, Google Gemini, Ollama, Groq, lokale LLMs). Implementierung von 5 nativen Werkzeugen (`brainstorm_add_idea`, `brainstorm_get_ideas`, `brainstorm_complete_idea`, `brainstorm_delete_idea`, `brainstorm_list_categories`). Ermöglicht völlig freie, kontextsensitive Konversationen (z. B. *„Was steht im Smarthome noch an?“*, *„Markiere Hecke schneiden als erledigt“* oder *„Wir brauchen neue Blumentöpfe, merk dir das mal“* mit automatischer Kategorisierung). Sauberes Unload-Lifecycle-Management via `async_on_unload`. |
| **`v1.4.19`** | 24.10.2026 | **Silver Quality Scale als Selbsteinschätzung (in v1.5.1 auf Bronze korrigiert, erreicht mit v1.5.2) & Home Assistant Logbook / Aktivität Integration:** Umsetzung von Kriterien der Home Assistant Integration Quality Scale für den **Silber-Status** (u. a. native `logbook.py`-Plattform mit `async_describe_events` zur lückenlosen Formatierung aller Brainstorm-Ereignisse – Idee erfasst, aktualisiert, erledigt, gelöscht – inklusive Icon und direkter Verknüpfung mit dem Geräte-Logbuch/Aktivitäts-Panel von Home Assistant; nativer Reconfigure-Flow (`async_step_reconfigure`) zur Live-Anpassung der Konfiguration direkt aus der HA-Oberfläche ohne Neuinstallation; standardkonforme Dienst-Fehlerbehandlung mittels `ServiceValidationError` und `HomeAssistantError` (`action-exceptions`); saubere Deregistrierung aller Dienste und Entitäten beim Entladen (`config-entry-unregistered`); offizielle Silver-Klassifizierung in `quality_scale.yaml` und `manifest.json`). |
| **`v1.4.18`** | 24.10.2026 | **Bronze Quality Scale als Selbsteinschätzung (in v1.5.1 nachgeprüft) & Alexa-Speedup:** Umsetzung von Kriterien der Home Assistant Integration Quality Scale für den **Bronze-Status** (u. a. `runtime-data` nach modernstem HA 2024.4+ Standard mit `entry.runtime_data = store`, Parallelitäts-Steuerung `PARALLEL_UPDATES = 0` auf den Plattformen `sensor` und `todo`, Ergänzung von `"quality_scale": "bronze"` in `manifest.json` sowie Bereitstellung der offiziellen `quality_scale.yaml`). Zudem umfassende Performance-Optimierung der Alexa-Sprachsteuerung: Wegfall von künstlichen Delays und redundanten Cloud-Stopps sowie Einführung der direkten Ein-Schritt-Spracherfassung (*„Brainstorm bereit. Sprich deine Notiz oder sage Ansage.“*) für 4x schnellere Dialoge. |
| **`v1.4.17`** | 23.10.2026 | **Individuelle Kategoriefarben & Pill-Dots:** Vollständige Neuausrichtung des Farbsystems. Jede Kategorie erhält nun eine unverwechselbare, harmonische und kontraststarke Einzelfarbe (z. B. Inbox = Royal Blue `#2563eb`, Smarthome = Aqua/Cyan `#06b6d4`, Haus & Garten = Emerald Green `#10b981`, Projekte = Indigo `#6366f1`, Alltag = Warm Amber `#f59e0b`, Brainstorm = Electric Purple `#a855f7`, Ideen = Pink `#ec4899`, Einkauf = Orange `#ea580c`, Finanzen = Teal `#14b8a6`, Familie = Rose `#f43f5e`, Gesundheit = Lime `#84cc16`). Automatische, deterministische Zuweisung einzigartiger Farbtöne für alle benutzerdefinierten Kategorien via Hash-Algorithmus. Kartenkanten, synaptische Verbindungslinien und Kategorie-Tags in Mindmap und Notizenliste spiegeln die Kategoriefarbe unmittelbar wider. Ergänzung von farbigen Indikatorpunkten (`pill-dot`) in der oberen Kategorie-Leiste zur sofortigen optischen Orientierung. |
| **`v1.4.16`** | 23.10.2026 | **Organische Multi-Ring Mindmap & Antikollisions-Layout:** Vollständige Neukonzeption der visuellen Mindmap-Knotenanordnung. Statt aller Notizen auf einem engen Kreisradius nutzt Brainstorm Mindmap nun ein intelligentes, mehrstufiges konzentrisches Ellipsen-Layout (1 Ring bei bis zu 6 Notizen, 2 Ringe bei 7–12 Notizen, 3 gestaffelte Ringe bei 13–20+ Notizen) unter optimaler Ausnutzung der Bildschirmbreite. Ein nativer Physik-Entspannungsdurchlauf (25 Iterationen) verhindert jegliche Überlappungen zwischen Ideenkarten und stellt sicher, dass das zentrale Glühbirnen-Symbol stets vollständig frei und sichtbar bleibt. Farbkodierte synaptische Bézier-Verbindungslinien passend zur jeweiligen Notizkategorie mit interaktivem Hover-Leuchten. Automatisches Zoom-to-Fit bei vielen Notizen und Beibehaltung manuell verschobener Karten. |
| **`v1.4.15`** | 23.10.2026 | **Bugfix Visueller Karteneditor & Seitenleisten-Dashboard:** Behebung eines Problems, bei dem Schalter im visuellen Lovelace-Karteneditor (`ha-form`) beim Ein- oder Ausschalten keine Wirkung zeigten und stets alle Elemente angezeigt blieben. Implementierung robuster Standardwerte (`default: true` in Schema & Initialisierung), vollständige Synchronisation deaktivierter Schalter (`show_quick_input`, `show_categories`, `show_badge`, `show_mindmap_button`, `show_color_toggle`, `show_source_icons`, `show_timestamps`, `allow_edit`, `allow_delete` bzw. `show_bulb_watermark`, `show_toolbar`, `show_fullscreen_btn`, `show_controls`, `show_add_btn`) und Beseitigung von Event-Bubbling-Kollisionen. Sofortige Live-Reaktivität in der Kartenvorschau und auf Dashboards. Optimierung der Dashboard-Einbindung für die Seitenleiste (Mindmap oben im Großformat, Notizenliste darunter). |
| **`v1.4.14`** | 23.10.2026 | **Geräte-Herkunftserfassung für Alexa & Assist:** Erfassung und optische Anzeige des konkreten Auslösegeräts bei Spracheingaben sowohl in `brainstorm-card` als auch in `brainstorm-mindmap-card` (z. B. `🗣️ Alexa (Echo Show Küche)`, `🗣️ Alexa (Wohnzimmer Echo Dot)`, `✨ Assist (Jan)` oder `✨ Assist (Küche Satellit)`). Vollständige Unterstützung in Sensor-Attributen (`device`), To-Do-Listen-Beschreibungen, Markdown-Export und `add_idea`/`update_idea`-Services. |
| **`v1.4.13`** | 22.10.2026 | **Sprachausgabe & Abfrage via Alexa & Assist:** Neuer Service `brainstorm.get_announcement` und Attribut `speech_overview` zur schnellen, flüssigen und gut verständlichen Sprachausgabe aktiver Notizen aller oder einzelner Kategorien (z. B. *„Smarthome hat drei Einträge: a, b und c“*). Interaktiver Alexa-Sprachdialog (*„Alexa, öffne Brainstorm“* ➔ *„Eintrag oder Ansage?“*) und native Assist-Intents (*„Was steht in Brainstorm?“*, *„Was habe ich in Smarthome notiert?“*). |
| **`v1.4.12`** | 22.10.2026 | **Resilienter Sensor-Fallback & Integration-Scoped Picker:** Automatischer Fallback auf `sensor.brainstorm_ideen_ubersicht`, falls in der Kartenkonfiguration eine fremde Entität (z. B. Feuchte-/Temperatursensor) ohne `ideas`-Attribut hinterlegt ist. Schutz im visuellen Editor durch Einschränkung des Entitäten-Selectors auf `integration: brainstorm`. |
| **`v1.4.11`** | 22.10.2026 | **Whitespace-Trimming & Robuster Kategorie-Filter:** Automatisches `.trim()` auf Kategorienamen bei Initialisierung (`default_category`), Pill-Klicks und Filterlogik in `brainstorm-card` und `brainstorm-mindmap-card`. Verhindert das versehentliche Nicht-Anzeigen von Ideen bei versehentlich eingegebenen Leerzeichen am Ende von Kategorienamen (z. B. `"Brainstorm "`). |
| **`v1.4.10`** | 21.10.2026 | **Kategorie- & Notiz-Validierung:** Robuste Validierung beim Erstellen und Ändern von Kategorien sowie beim Bearbeiten von Notizen in beiden Lovelace-Karten. Verhindert das Absenden leerer Eingaben oder von Duplikaten (Groß-/Kleinschreibung-unabhängig) mit klarer Fehlermeldung (`⚠️ Bitte gib einen Kategorienamen ein.`), roter Umrandung und sanfter Schüttel-Animation (`dialog-shake`). Automatisches Zurücksetzen der Fehleranzeige beim Weitertippen. Ergänzung von `ServiceValidationError` im Backend (`__init__.py` und `store.py`) für saubere Fehlermeldungen bei Service-Aufrufen. |
| **`v1.4.9`** | 21.10.2026 | **Notizen-Rendering Fix:** Behebung eines Laufzeitfehlers (`TypeError: this._escapeHtml is not a function`), durch den aktive Ideen in der Hauptkarten-Listenansicht nicht gerendert wurden. Implementierung von `_escapeHtml()` und `_getSensorEntity()` in `BrainstormCard`. |
| **`v1.4.8`** | 21.10.2026 | **Kategorie-Eingabefeld Layout-Fix:** Behebung des CSS-Kollabierens des Eingabefelds im Modal-Dialog *„Neue Kategorie“* (`width: 100%`, `box-sizing: border-box`, `min-height: 42px` und flexibler Wrapper), sodass das Feld über die volle Dialogbreite dargestellt wird und nicht mehr horizontal zusammengestaucht ist. |
| **`v1.4.7`** | 21.10.2026 | **Bugfix SyntaxError & Stabilität der Lovelace-Cards:** Behebung eines doppelten Deklarationsfehlers (`Identifier 'pillsContainer' has already been declared`), der das Laden der Karte im Browser verhinderte. `customElements.define`-Guards für beide Karten und Editoren ergänzt. Behebung des YAML-Parsingfehlers für unquoted Doppelpunkte in `services.yaml`. |
| **`v1.4.6`** | 20.10.2026 | **Visuelle Kartenkonfiguratoren (Lovelace Visual Editor):** Vollständige Unterstützung des nativen Home Assistant UI-Karteneditors (`getConfigElement()` & `getStubConfig()`) für beide Karten (`brainstorm-card` und `brainstorm-mindmap-card`). Alle Einstellungen lassen sich nun komfortabel per Klick, Dropdown und Schalter ohne YAML-Code anpassen: Kartentitel, Sensor-Auswahl mit Entitätenfilter, Farbmodus (`theme` vs. `multicolor`), Standard-Kategorie, Maximalanzahl an Notizen (`max_items`), Ein-/Ausblenden der Schnelleingabezeile, Kategorie-Filterleiste, Zähler-Badge, Mindmap-Button, Theme-Farbumschalter, Quellen-Icons, Zeitstempel sowie Bearbeitungs- und Löschrechte. In der Mindmap zusätzlich Steuerung von Höhe (`height`), Glühbirnen-Wasserzeichen, Toolbar, Vollbild-Button und Zoom-/Zentrier-Controls. |
| **`v1.4.5`** | 20.10.2026 | **Dynamische Home Assistant Theme-Farben & Farbmodus-Umschalter:** Neuer Farbmodus-Umschalter (`🎨` Theme-Modus ⇄ `🌈` Bunt-Modus) sowohl in der Lovelace-Hauptkarte als auch in der Mindmap. Im Theme-Modus passen sich alle Knoten, Kategorie-Pills, Verbindungslinien und Tags dynamisch an das aktive Home Assistant Theme an (`var(--primary-color)` und semantische Farbvariablen via `color-mix`), sodass sich das Design nahtlos in Dark/Light-Themes sowie Mushroom/Minimalist-Themes einfügt. Präferenz wird browserweit in `localStorage` (`brainstorm_color_mode`) und via Card-Option (`color_mode`) synchronisiert. |
| **`v1.4.4`** | 20.10.2026 | **Transparente Glühbirne & Vollständige Raumnutzung:** Ersatz des überlagerten Wasserzeichens durch ein transparentes SVG der leuchtenden Brainstorm-Birne (`brainstorm-bulb.svg` ohne störenden grauen Kasten, 100% freigestellt). Vollständige Ausnutzung der gesamten Bildschirm-/Popup-Höhe im 3/4-Modal (`height: 100%`, dynamische Radius-Skalierung und `ResizeObserver` zur Beseitigung ungenutzter Freiflächen). |
| **`v1.4.3`** | 20.10.2026 | **Zitterfreie Interaktion & Native Mushroom-Dialoge:** Beseitigung jeglichen Ruckelns/Zitterns beim Anklicken und Bearbeiten von Notizen (Hysterese-Drag-Schwelle von 5px, Entfernung sprung-auslösender Hover-Translationen und Drosselung unnötiger State-Re-Renders). Vollständiger Ersatz aller nativen Browser-Prompts (`prompt()` / `confirm()`) durch hochwertige, animierte In-Card Mushroom-Dialoge für Notiz-Bearbeitung, Kategorie-Auswahl-Chips und Neuanlage. |
| **`v1.4.2`** | 20.10.2026 | **Mushroom & Minimalist Design & 3/4-Modal-Layer:** Vollständige Designanpassung der Mindmap an Mushroom / UI Minimalist Design (helle/neutrale runde Buttons, dezente Pastell-/Kategoriefarben, feine Rahmen statt harter Kontraste). Die Mini-Vorschau in der Karte wurde durch ein zentriertes 3/4-Bildschirm-Modal-Popup (`75vw` × `75vh`) mit Blur-Backdrop und Schließen-Button ersetzt. |
| **`v1.4.1`** | 20.10.2026 | **Mindmap-Darstellung:** Theme-konforme Farben für Kategorien und Vollbild-Schaltfläche sowie nahezu bildschirmhohe Standarddarstellung. |
| **`v1.4.0`** | 20.10.2026 | **Intelligente Text-Optimierung & NLP:** Automatische Bereinigung gesprochener Notizen (Filterung von Gesprächsfloskeln, Partizip-zu-Infinitiv-Transformation, Rechtschreibprüfung und automatische Substantiv-Großschreibung). Schalter im Options-Flow hinzugefügt. |
| **`v1.3.0`** | 20.10.2026 | **Brainstorm Mindmap Card:** Neue interaktive Lovelace-Karte (`custom:brainstorm-mindmap-card`) mit Radial-Synapsen-Layout, transparentem Logo-Wasserzeichen im Zentrum, Gedankenwolken und Vollbild-Modus (`⛶`). Integrierter Umschalter (`🧠 Mindmap` ⇄ `📋 Liste`) in der Hauptkarte. |
| **`v1.2.1`** | 20.10.2026 | **Fehlerbehebungen & Stabilität:** Beseitigung von `ResponseNone`-Einträgen, Vermeidung von Musik-Kollisionen bei Alexa-Befehlen, Korrektur des Assist-Wildcard-Parsing-Fehlers, Behebung des Dashboard-Kartenfehlers (`counts is not defined`). |
| **`v1.1.0`** | 20.10.2026 | **Frontend Redesign & Standards:** 2-stufiges Layout für die Lovelace Card, HACS-Kompatibilität, vollständige `DeviceInfo`-Anbindung und Assist-Sprachunterstützung. |
| **`v1.0.0`** | 19.10.2026 | **Initiales Release:** Kern-Integration Brainstorm Hub, To-do-Plattform, Markdown-Export und Alexa-Sprachdialog. |

---

## 💬 Feedback & Mitmachen

Ich freue mich wirklich über jede Rückmeldung und bin sehr dankbar dafür. Brainstorm Hub ist aus meinem eigenen Alltag entstanden, und erst durch eure Erfahrungen wird es für alle besser.

- **Etwas klappt nicht?** Öffne ein [Issue](https://github.com/nukleuz80/ha_brainstorm/issues). Die Diagnose hilft dabei sehr (siehe *Fehlerbehebung*).
- **Eine Idee oder ein Wunsch?** Auch dafür gern ein [Issue](https://github.com/nukleuz80/ha_brainstorm/issues). Kleine Ideen sind genauso willkommen wie große.
- **Selbst etwas verbessern?** Pull Requests sind herzlich willkommen, ob Code, Übersetzung, Doku oder Tippfehler. Für größere Änderungen lass uns vorher kurz in einem Issue sprechen, damit nichts doppelt entsteht.
- **Einfach erzählen,** wie du Brainstorm nutzt. Auch das hilft mir bei der Weiterentwicklung.

Ich bin offen für Verbesserungen und freue mich über alle, die Brainstorm mit weiterentwickeln.

---

## ✨ 🚀 Vibe Coding mit voller Hingabe

> *„Vibe Coding ist die Kunst, reine Ideen durch fließenden Dialog, menschliche Kreativität und KI-Superkräfte in funktionierende Realität zu verwandeln.“*

Dieses Projekt wurde und wird mit voller Hingabe durch **Vibe Coding** erschaffen. Wir verstecken uns nicht hinter KI, sondern stehen mit Stolz und voller Transparenz dazu:
- **Menschliche Produkt- & UX-Vision:** Jedes Feature, jede Smartphone-Geste, jedes Detail der interaktiven Mindmap und jede Alexa-Routine entstammt echter Alltagserfahrung und der Leidenschaft für ein smarteres Zuhause.
- **High-Velocity AI Pair-Programming:** Durch den Einsatz moderner agentischer KI-Entwicklung (Google Antigravity & Claude/Gemini) entstehen anspruchsvolle Architekturen, Bugfixes und Feinschliff in Höchstgeschwindigkeit.
- **100 % Open Source & Community First:** Transparent, erweiterbar und für jeden in der Home Assistant Community frei nutzbar.

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert – siehe [LICENSE](LICENSE) für Details.

Copyright © 2026 [nukleuz80](https://github.com/nukleuz80)
