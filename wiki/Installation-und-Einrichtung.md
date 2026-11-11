🏠 [Start](Home) · 🇬🇧 [English version](Installation-and-Setup)

## 🔗 Schnelllinks

Diese Buttons öffnen die passende Seite in deinem eigenen Home Assistant:

[![Brainstorm Hub in HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration) [![Brainstorm Hub einrichten](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm) [![Brainstorm Hub öffnen (Konfigurieren, Diagnose, Löschen)](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) [![Brainstorm-Aktionen ausprobieren](https://my.home-assistant.io/badges/tools_actions.svg)](https://my.home-assistant.io/redirect/tools_actions/) [![Sprachassistenten (Assist, LLM API)](https://my.home-assistant.io/badges/voice_assistants.svg)](https://my.home-assistant.io/redirect/voice_assistants/) [![Reparaturen](https://my.home-assistant.io/badges/repairs.svg)](https://my.home-assistant.io/redirect/repairs/) [![Protokolle von Brainstorm Hub](https://my.home-assistant.io/badges/logs.svg)](https://my.home-assistant.io/redirect/logs/?integration=brainstorm)

Die Links laufen über [My Home Assistant](https://my.home-assistant.io/). Beim ersten Klick fragt es nach der Adresse deines Home Assistant und merkt sie sich. Auch die Menüpfade in diesem Wiki, etwa **Einstellungen ➔ Geräte & Dienste**, sind solche Links, und jede Aktion unter [Dienste](Dienste-und-Ereignisse) hat einen Link, der sie in den Entwicklerwerkzeugen öffnet.

## Voraussetzungen

1. Home Assistant 2026.10 oder neuer.
2. [HACS](https://hacs.xyz), wenn du darüber installieren möchtest.
3. Optional für die Spracheingabe mit Alexa: die Integration [Alexa Media Player](https://github.com/alandtse/alexa_media_player).
4. Optional für einen eigenen Alexa-Skill: ein Amazon-Entwicklerkonto und eine öffentliche HTTPS-Adresse deines Home Assistant.

Brainstorm Hub verbindet sich von selbst mit keinem externen Dienst. Die Einrichtung braucht also weder Konto noch Passwort.

## Methode 1: Über HACS (Empfohlen – 1 Klick)

Brainstorm Hub steht seit dem 9. November 2026 in der Standardliste von HACS. Der Button öffnet es direkt in deinem HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)

Oder Schritt für Schritt:
1. Öffne **HACS** in deinem Home Assistant.
2. Suche nach **Brainstorm Hub** und klicke auf **Herunterladen**.
3. Starte Home Assistant neu.

Die Karten kommen mit der Integration: Nach dem Neustart lädt Home Assistant sie selbst, ohne Kopieren und ohne Ressourcen-Eintrag.

## Methode 2: Manuelle Installation

1. Lade das neueste Release herunter.
2. Kopiere den Ordner `custom_components/brainstorm` in dein Home Assistant Verzeichnis `/config/custom_components/`.
3. Starte Home Assistant neu. Die Karten liegen im Ordner der Integration (`cards/`) und werden von selbst geladen.

> **Update von einer Version vor 1.7.15:** Entferne die alten Ressourcen `/local/brainstorm-card.js` und `/local/brainstorm-mindmap-card.js` unter [*Einstellungen ➔ Dashboards ➔ Ressourcen*](https://my.home-assistant.io/redirect/lovelace_resources/) (oder aus `resources:` im YAML-Modus) und lösche die Karten-Dateien in `/config/www/`. Sonst kann der Browser noch die alten Karten laden.

## Integration entfernen

1. Öffne [**Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm), klicke auf die drei Punkte und wähle **Löschen**.
2. Über HACS installiert: Öffne Brainstorm Hub in HACS und wähle **Entfernen**. Manuell installiert: Lösche `/config/custom_components/brainstorm`.
3. Entferne alle Brainstorm-Karten aus deinen Dashboards.
4. Starte Home Assistant neu.

Je nachdem, was du genutzt hast, entferne auch:
- **Deinen Alexa-Skill:** Lösche ihn in der Alexa Developer Console und seinen Code in AWS Lambda. Echte Alexa-Erinnerungen bleiben in der Alexa-App, bis du sie dort löschst.
- **Automationen und Sätze:** Eigene Automationen, Skripte und Custom Sentences, die Brainstorm aufrufen, sowie einen iPhone-Kurzbefehl.
- **Deine Daten:** Home Assistant behält deine Ideen in `/config/.storage/brainstorm.storage`, die Skill-Kopplung in `brainstorm.alexa_skill` und den Stand der Erinnerungen in `brainstorm.reminders` im selben Ordner. Lösche diese Dateien und den Markdown-Ordner (Standard `/config/brainstorm`), wenn du nicht zurückkehren möchtest.

## 🛠️ Einrichten

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
