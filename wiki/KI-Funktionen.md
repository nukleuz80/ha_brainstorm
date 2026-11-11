🏠 [Start](Home) · 🇬🇧 [English version](AI-Features)

## ✨ Was die KI kann

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
- **Unteraufgaben von der KI (v1.6.26):** Ist unter *Konfigurieren ➔ KI* eine KI-Aufgaben-Entität gewählt, fragt ✨ an einer Notiz sie nach bis zu 8 Unteraufgaben. Du nimmst den Haken bei allem weg, was du nicht willst, kannst die Texte ändern, und nur was du übernimmst, landet unter der Notiz. Zur KI geht nur diese Notiz mit ihren Unteraufgaben, und nur wenn du den Knopf drückst. Ein Rückgängig entfernt alle wieder. Auch die Listenkarte hat ✨ (v1.6.28): neben ✎ an jeder Hauptaufgabe und im Menü bei langem Drücken oder Rechtsklick. Lehnt der Anbieter der KI wegen Überlastung ab, fragt Brainstorm nach 2 Sekunden einmal nach und sagt sonst, dass die KI gerade nicht erreichbar ist (v1.6.29).
- **KI: Map aus Thema oder Text (v1.11.1):** ✨ *Map aus Thema erzeugen* auf einer leeren Map, Taste **G** oder ✨ *Mit KI erzeugen* unter 🖼️ ➔ *Gliederung einfügen*. Ein Thema wie „Sommerfest planen“ oder ein eingefügter Text wird zu einer Vorschau mit bis zu drei Ebenen unter einem Titel. Haken weg bei allem, was du nicht willst (Unterpunkte rücken nach oben), Texte ändern, übernehmen; ↶ nimmt alles zurück. Landet im Fokus-Zweig oder in der gewählten Kategorie.
- **KI: Nach Themen gruppieren (v1.11.4):** Viele lose Notizen in einer Kategorie? Taste **K**, ✨ *Nach Themen gruppieren* am Ende einer Brainstorm-Runde oder im Dialog *Lose Ideen zuordnen*, wenn dort nichts passt: Die KI fasst die Hauptnotizen ohne Unterpunkte zu drei bis sieben Themen zusammen. In der Vorschau hakst du Themen und Notizen ab und änderst die Titel; jedes Thema wird ein neuer Oberpunkt an der Stelle der ersten Notiz, die Notizen kommen darunter. ↶ nimmt es zurück. Braucht mindestens vier lose Notizen.
- **KI-Hilfe auf der Map (v1.8.9):** Mit einer KI-Aufgaben-Entität kann ✨ an einer Notiz mit Unterpunkten auch **den Ast zusammenfassen**, in ein paar Sätzen, die zur Beschreibung werden können. **Lose Ideen zuordnen** (Taste **Z** oder am Ende einer Brainstorm-Runde) schlägt für jede lose Hauptnotiz der Kategorie einen Oberpunkt vor; du hakst ab, was gelten soll. Vor deiner Bestätigung ändert sich nichts, ↶ nimmt es zurück.

## KI-Assistent (LLM)

Ein Gesprächsagent wie OpenAI, Google Gemini oder Ollama kann Brainstorm bedienen, wenn du in seinen Optionen unter **Home Assistant steuern** zusätzlich **Brainstorm Hub** auswählst. Er bekommt diese Werkzeuge:

| Werkzeug | Beispiel |
|---|---|
| `brainstorm_add_idea` | „Schreib auf, dass wir Grillkohle brauchen, für Samstag.“ |
| `brainstorm_get_ideas` | „Was steht noch auf meiner Gartenliste?“ |
| `brainstorm_complete_idea` | „Die Grillkohle habe ich gekauft.“ |
| `brainstorm_delete_idea` | „Lösch die Notiz mit dem Fahrradschloss.“ |
| `brainstorm_list_categories` | „Welche Listen gibt es?“ |

Unter **Konfigurieren ➔ KI** kannst du außerdem einen KI-Dienst wählen, der gesprochene Texte aufräumt (Füllwörter, Satzzeichen).

## 🤖 Brainstorm als Aufgabenliste für Coding-KIs

Eine Kategorie kann das Backlog eines Programmierprojekts sein: Du sammelst Aufgaben per Alexa, Karte oder Assist, und eine Coding-KI wie Claude Code liest sie über einen MCP-Server für Home Assistant, setzt sie um und hakt sie mit einer **Ergebnis-Notiz** ab. Beide Karten zeigen diese Notiz unter dem Eintrag, so siehst du ohne Nachfragen, was daraus geworden ist.

**Einrichtung**

1. **Eigener Benutzer für die KI:** Unter [**Einstellungen ➔ Personen**](https://my.home-assistant.io/redirect/people/) einen Benutzer anlegen, etwa *Claude*. Bekommt seine Person ein Bild, zeigen die Karten es an den Einträgen, die die KI anlegt.
2. **Token:** Als dieser Benutzer anmelden, unter [**Profil ➔ Sicherheit**](https://my.home-assistant.io/redirect/profile_security/) ein langlebiges Zugriffstoken erstellen und damit den MCP-Server verbinden, zum Beispiel [ha-mcp](https://github.com/homeassistant-ai/ha-mcp). Ob der Benutzer Adminrechte braucht, hängt davon ab, wie ha-mcp läuft, siehe Hinweis unten.
3. **Privatsphäre einschalten** (siehe oben) und die Backlog-Kategorie für den KI-Benutzer freigeben: *Ansehen* zum Lesen, *Bearbeiten*, wenn er abhaken darf. Alles andere bleibt für ihn unsichtbar.
4. **Skill installieren:** Den Ordner [`examples/claude-code/skills/brainstorm-backlog`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/claude-code/skills/brainstorm-backlog/SKILL.md) nach `~/.claude/skills/` kopieren (für alle Projekte) oder nach `.claude/skills/` im Projekt.
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
