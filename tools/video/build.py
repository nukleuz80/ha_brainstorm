"""Render the storyboard into an MP4 with German narration and chapters."""
from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import importlib

SCRIPT = next((a for a in sys.argv[1:] if not a.startswith("--")), "script")
_mod = importlib.import_module(SCRIPT)
CHAPTERS, SPOKEN = _mod.CHAPTERS, _mod.SPOKEN
VIDEO_TITLE = getattr(_mod, "TITLE", "Brainstorm: Eigenen Alexa-Skill einrichten")
OUT_NAME = getattr(_mod, "OUT_NAME", "brainstorm-alexa-skill")

ROOT = Path(__file__).parent
OUT = ROOT / ("out" if SCRIPT == "script" else f"out_{SCRIPT}")
FFMPEG = str(next((ROOT / "vv/lib").glob("python*/site-packages/imageio_ffmpeg/binaries/ffmpeg-*")))
PIPER = str(ROOT / "vv/bin/piper")
VOICE = str(ROOT / "de_DE-thorsten-high.onnx")
W, H = 1280, 720
PAD_BEFORE, PAD_AFTER = 0.5, 1.1

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1280px;height:720px;overflow:hidden;font-family:'Noto Sans','DejaVu Sans',sans-serif;
 background:radial-gradient(circle at 15% 0%,#1e3a5f 0%,#0d1b2a 55%,#0a1420 100%);color:#e8eef5}
.top{position:absolute;left:48px;top:30px;right:48px;display:flex;align-items:center;gap:14px}
.badge{background:#ffb703;color:#10202f;font-weight:800;border-radius:999px;padding:6px 16px;font-size:18px}
.ctitle{font-size:30px;font-weight:800;letter-spacing:.2px}
.logo{margin-left:auto;display:flex;align-items:center;gap:10px;font-size:16px;color:#9fb3c8}
.logo img{width:34px;height:34px;border-radius:8px}
.stage{position:absolute;left:48px;right:48px;top:96px;height:470px}
.cap{position:absolute;left:48px;right:48px;bottom:34px;min-height:96px;background:rgba(0,0,0,.55);
 border-radius:14px;padding:12px 20px;font-size:21px;line-height:1.38;color:#fff;display:flex;align-items:center}
.prog{position:absolute;left:48px;right:48px;bottom:14px;display:flex;gap:4px}
.prog div{flex:1;height:6px;border-radius:3px;background:#2b4057}
.prog .done{background:#4f7ca8}.prog .cur{background:#ffb703}
.note{position:absolute;right:0;top:412px;background:#fff4d6;color:#4a3500;border-left:6px solid #ffb703;
 border-radius:10px;padding:10px 16px;font-size:18px;max-width:820px;font-weight:600}
.hl{outline:4px solid #ffb703;outline-offset:3px;box-shadow:0 0 0 10px rgba(255,183,3,.18);border-radius:6px}
.schema{position:absolute;left:0;top:416px;font-size:13px;color:#7f93a8}
/* title */
.tt{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:22px}
.tt img{width:150px;height:150px;border-radius:32px;box-shadow:0 10px 40px rgba(0,0,0,.5)}
.tt h1{font-size:52px;font-weight:800}.tt p{font-size:26px;color:#b9cde0}
/* bullets */
.bl h2{font-size:34px;margin:6px 0 24px}
.bl li{list-style:none;display:flex;gap:18px;align-items:flex-start;font-size:25px;margin:0 0 18px;line-height:1.35}
.bl .ic{min-width:44px;height:44px;border-radius:12px;background:#1f3b57;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;color:#ffb703}
.bl code{background:#1f3b57;padding:1px 6px;border-radius:5px;font-size:21px}
/* console mock */
.win{position:absolute;left:0;top:0;width:1184px;height:400px;background:#f4f6f8;color:#16191f;border-radius:12px;overflow:hidden;box-shadow:0 14px 40px rgba(0,0,0,.45)}
.bar{height:38px;background:#232f3e;color:#fff;display:flex;align-items:center;padding:0 16px;font-size:15px;gap:22px}
.bar b{font-size:16px}.tabs{display:flex;gap:4px;margin-left:30px}
.tabs span{padding:9px 14px;color:#c9d3df}.tabs .on{color:#fff;border-bottom:3px solid #ffb703}
.side{position:absolute;left:0;top:38px;bottom:0;width:250px;background:#fff;border-right:1px solid #dde3ea;padding:10px 12px;font-size:14px}
.side div{padding:4px 10px;border-radius:5px;margin-bottom:2px}.side .sec{font-size:11px;color:#687078;font-weight:700;margin-top:6px}
.side .sub{padding-left:26px}.side .on{background:#e6f0fb;color:#0b62c4;font-weight:700}
.main{position:absolute;left:250px;right:0;top:38px;bottom:0;padding:14px 28px;font-size:17px}
.main h3{font-size:21px;margin-bottom:10px}
.btn{display:inline-block;background:#0b62c4;color:#fff;border-radius:6px;padding:7px 16px;font-weight:700;font-size:15px;margin-right:8px}
.btn.alt{background:#fff;color:#0b62c4;border:1px solid #0b62c4}
.tog{display:inline-block;width:46px;height:24px;border-radius:12px;background:#0b62c4;position:relative;vertical-align:middle;margin-right:12px}
.tog::after{content:'';position:absolute;right:3px;top:3px;width:18px;height:18px;border-radius:50%;background:#fff}
.tog.off{background:#aab4be}.tog.off::after{left:3px;right:auto}
.row{display:flex;align-items:center;padding:8px 12px;margin-bottom:8px;background:#fff;border:1px solid #dde3ea;border-radius:8px}
.cb{display:inline-block;width:18px;height:18px;border-radius:4px;background:#0b62c4;color:#fff;font-size:13px;text-align:center;line-height:18px;margin-right:8px}
.pre{background:#1e1e1e;color:#d4d4d4;font-family:'DejaVu Sans Mono',monospace;font-size:14px;line-height:1.5;padding:14px 18px;border-radius:8px;white-space:pre}
.k{color:#569cd6}.s{color:#ce9178}.c{color:#6a9955}
/* wizard */
.steps{display:flex;gap:10px;margin-bottom:12px}
.steps span{flex:1;padding:8px 10px;border-radius:6px;background:#e3e8ee;font-size:14px;color:#545b64}
.steps .on{background:#0b62c4;color:#fff;font-weight:700}
.field{margin-bottom:10px}.field label{display:block;font-size:14px;color:#545b64;font-weight:700;margin-bottom:6px}
.field .val{background:#fff;border:1px solid #aab7c4;border-radius:6px;padding:7px 14px;font-size:18px;width:520px}
/* ha dialog */
.ha{position:absolute;left:180px;top:0;width:820px;background:#fff;color:#212121;border-radius:16px;overflow:hidden;box-shadow:0 14px 40px rgba(0,0,0,.45)}
.ha .hd{background:#03a9f4;color:#fff;padding:16px 24px;font-size:22px;font-weight:700}
.ha .bd{padding:18px 24px}.ha .lb{font-size:14px;color:#616161;margin-bottom:4px}
.ha .in{border:1px solid #bdbdbd;border-radius:6px;padding:10px 12px;font-size:17px;margin-bottom:6px;font-family:'DejaVu Sans Mono',monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ha .ds{font-size:13px;color:#757575;margin-bottom:14px}
.ha .ft{text-align:right;padding:4px 24px 18px}.ha .ft span{color:#03a9f4;font-weight:800;font-size:17px}
.path{position:absolute;left:180px;top:-2px;transform:translateY(-110%);font-size:15px;color:#9fb3c8}
/* speech */
.sp{display:flex;flex-direction:column;gap:22px;padding:20px 120px}
.bub{max-width:760px;padding:18px 26px;border-radius:22px;font-size:28px;line-height:1.35}
.bub.du{align-self:flex-end;background:#2f80ed;border-bottom-right-radius:6px}
.bub.alexa{align-self:flex-start;background:#00caff;color:#06222e;border-bottom-left-radius:6px;font-weight:700}
.bub.hab{align-self:center;background:#03a9f4;font-size:20px;border-radius:10px}
.who{font-size:15px;opacity:.75;display:block;margin-bottom:4px;font-weight:600}
.sph{font-size:30px;font-weight:800;text-align:center;margin-bottom:6px}
/* phone */
.phone{position:absolute;left:120px;top:0;width:300px;height:450px;border-radius:34px;background:#0f1a24;border:8px solid #2a3a4a;padding:22px 16px;color:#fff}
.phone .t{font-size:17px;color:#9fb3c8;margin-bottom:10px}.phone .it{background:#1c2c3c;border-radius:10px;padding:12px;margin-bottom:10px;font-size:16px}
.side2{position:absolute;left:500px;top:30px;right:0}
.shot{position:absolute;left:0;top:0;height:470px;display:flex;align-items:flex-start}
.shot img{border-radius:14px;box-shadow:0 14px 40px rgba(0,0,0,.55);border:1px solid #2b4057}
.shotside{position:absolute;right:0;top:20px;width:520px}.shotside li{font-size:23px}
.tf{display:flex;flex-direction:column;align-items:center;gap:14px;padding-top:10px}
.tfin{background:#2f80ed;border-radius:22px;padding:18px 28px;font-size:28px;max-width:1000px}
.tfarrow{font-size:34px;color:#ffb703}
.tfout{background:#1c1c1c;border:1px solid #2b4057;border-left:6px solid #03a9f4;border-radius:14px;padding:16px 26px;min-width:560px}
.tftext{font-size:30px;font-weight:700;margin-bottom:12px}
.chip{display:inline-block;border-radius:8px;padding:4px 12px;margin:0 8px 6px 0;font-size:19px;background:#1f3b57;font-weight:600}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.tile{background:#13283d;border:1px solid #2b4057;border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;gap:4px;min-height:118px}
.tile .ti{font-size:28px}.tile b{font-size:21px}.tile span{font-size:17px;color:#b9cde0;line-height:1.35}
/* ha options menu */
.ha .mi{display:flex;align-items:center;gap:12px;padding:6px 6px;border-bottom:1px solid #eee;font-size:18px}
.ha .mi::after{content:'›';margin-left:auto;color:#9e9e9e;font-size:22px}
.ha .sw{display:flex;align-items:center;justify-content:space-between;padding:7px 0;font-size:19px}
.ha .sw small{display:block;font-size:14px;color:#757575;max-width:600px}
/* generic phone */
.ph2{position:absolute;left:60px;top:0;width:300px;height:460px;border-radius:36px;background:#0f1a24;border:8px solid #2a3a4a;padding:24px 14px;color:#fff;overflow:hidden}
.ph2 .t{font-size:15px;color:#9fb3c8;margin-bottom:10px;text-align:center}
.ph2 .it{background:#1c2c3c;border-radius:12px;padding:10px 12px;margin-bottom:8px;font-size:15px;line-height:1.3}
.ph2 .it small{display:block;color:#9fb3c8;font-size:12px}
.ph2 .act{display:flex;gap:6px;margin-top:8px}.ph2 .act span{flex:1;background:#2b4057;border-radius:8px;padding:6px 4px;text-align:center;font-size:12px}
.ph2side{position:absolute;left:420px;top:10px;right:0}
"""

TABS = ["Build", "Code", "Test", "Distribution", "Certification", "Analytics"]
NAV = [
    ("sec", "CUSTOM"), ("item", "Invocations"), ("sub", "Skill Invocation Name"),
    ("item", "Interaction Model"), ("sub", "Intents"), ("sub", "JSON Editor"),
    ("item", "Multimodal Responses"), ("item", "Interfaces"),
    ("item", "Endpoint"), ("sec", "TOOLS"), ("item", "Permissions"),
]


def esc(text: str) -> str:
    return html.escape(text)


def console(tab: str, active: str, body: str) -> str:
    tabs = "".join(f'<span class="{"on" if t == tab else ""}">{t}</span>' for t in TABS)
    if tab == "Build":
        nav = ""
        for kind, label in NAV:
            on = label == active or (active == "Invocations" and label == "Skill Invocation Name")
            cls = {"sec": "sec", "item": "", "sub": "sub"}[kind] + (" on" if on else "")
            nav += f'<div class="{cls}">{label}</div>'
    elif tab == "Code":
        nav = ('<div class="sec">DATEIEN</div><div>📁 lambda</div>'
               '<div class="sub on">lambda_function.py</div><div class="sub">requirements.txt</div>'
               '<div class="sub">utils.py</div>')
    else:
        nav = '<div class="sec">ALEXA SIMULATOR</div><div class="on">Manual JSON</div><div>Voice &amp; Tone</div>'
    return (f'<div class="win"><div class="bar"><b>Alexa Developer Console</b>'
            f'<span style="color:#c9d3df">Brainstorm</span><div class="tabs">{tabs}</div></div>'
            f'<div class="side">{nav}</div><div class="main">{body}</div></div>'
            '<div class="schema">Schematische Darstellung der Konsole</div>')


def console_body(kind: str) -> str:
    if kind == "apl":
        return ('<h3>Interfaces</h3>'
                '<div class="row"><span class="tog off"></span>Audio Player</div>'
                '<div class="row hl"><span class="tog"></span><b>Alexa Presentation Language</b></div>'
                '<div class="row" style="flex-wrap:wrap;gap:14px;font-size:15px">'
                '<span><span class="cb">✓</span>Hub Round</span><span><span class="cb">✓</span>Hub Landscape Small</span>'
                '<span><span class="cb">✓</span>Hub Landscape Medium</span><span><span class="cb">✓</span>Hub Landscape Large</span></div>'
                '<div style="margin-top:12px"><span class="btn hl">Save</span></div>')
    if kind == "perm":
        return ('<h3>Permissions</h3>'
                '<div class="row"><span class="tog off"></span>Device Address</div>'
                '<div class="row"><span class="tog off"></span>Customer Name</div>'
                '<div class="row hl"><span class="tog"></span><b>Reminders</b></div>'
                '<div class="row"><span class="tog off"></span>Lists Read</div>')
    if kind == "json":
        code = ('<span class="c">// gesamten Inhalt ersetzen</span>\n{\n  <span class="s">"interactionModel"</span>: {\n'
                '    <span class="s">"languageModel"</span>: {\n      <span class="s">"invocationName"</span>: '
                '<span class="s">"brainstorm"</span>,\n      <span class="s">"intents"</span>: [ '
                '<span class="s">"CaptureIdeaIntent"</span>, <span class="s">"ReminderIntent"</span>, …')
        return ('<h3>JSON Editor</h3><div style="margin-bottom:10px"><span class="btn alt hl">Save</span>'
                '<span class="btn hl">Build Skill</span></div>'
                f'<div class="pre hl">{code}</div>'
                '<div class="row" style="margin-top:12px;color:#1d8102;font-weight:700">✔ Build Successful</div>')
    if kind == "inv":
        return ('<h3>Skill Invocation Name</h3>'
                '<div class="field"><label>Skill Invocation Name</label>'
                '<div class="val hl">brainstorm</div></div>'
                '<p style="color:#545b64">„Alexa, sage <b>Brainstorm</b> …“ · „Alexa, öffne <b>Brainstorm</b>“</p>')
    if kind == "code":
        code = ('<span class="s">"""Brainstorm Hub Alexa skill. Keep this code private …"""</span>\n'
                '<span class="k">import</span> json\n<span class="k">import</span> urllib.request\n\n'
                'WEBHOOK_URL = <span class="s">"https://•••••••/api/webhook/brainstorm_••••"</span>\n'
                'TIMEOUT_SECONDS = 6\n…\n<span class="k">def</span> lambda_handler(event, context):')
        return ('<div style="margin-bottom:10px"><span class="btn alt">Save</span><span class="btn hl">Deploy</span></div>'
                f'<div class="pre hl">{code}</div>'
                '<div class="row" style="margin-top:12px;color:#1d8102;font-weight:700">✔ Successfully deployed</div>')
    if kind == "test":
        return ('<div class="field"><label>Skill testing is enabled in:</label>'
                '<div class="val hl" style="width:260px">Development ▾</div></div>'
                '<p style="color:#545b64">Off · <b>Development</b> · Live</p>')
    if kind == "testrun":
        return ('<div class="field"><label>Skill testing is enabled in:</label>'
                '<div class="val" style="width:260px">Development ▾</div></div>'
                '<div class="row hl">⌨️ sage brainstorm notiere testidee</div>'
                '<div class="row" style="background:#e6f7ff">🔵 Gespeichert unter Inbox.</div>')
    raise ValueError(kind)


def stage(v: tuple) -> str:
    kind = v[0]
    if kind == "title":
        return f'<div class="tt"><img src="icon.png"><h1>{esc(v[1])}</h1><p>{esc(v[2])}</p></div>'
    if kind == "bullets":
        items = "".join(f'<li><span class="ic">{i}</span><span>{t}</span></li>' for i, t in v[2])
        return f'<div class="bl"><h2>{esc(v[1])}</h2><ul>{items}</ul></div><div class="note">{v[3]}</div>'
    if kind == "wizard":
        names = ["Name, Locale", "Experience, Model, Hosting service", "Templates", "Review"]
        steps = "".join(f'<span class="{"on" if n == v[1] else ""}">{n_i}. {n_t}</span>'
                        for n, (n_i, n_t) in enumerate([(i + 1, t) for i, t in enumerate(names)], 1))
        fields = "".join(
            f'<div class="field"><label>{esc(lb)}</label><div class="val{" hl" if hl else ""}">{esc(val)}</div></div>'
            for lb, val, hl in v[3])
        body = f'<div class="steps">{steps}</div><h3>{esc(v[2])}</h3>{fields}'
        win = console("Build", "", body).replace('<div class="side">', '<div class="side" style="display:none">')
        win = win.replace('<div class="main">', '<div class="main" style="left:0">')
        win = win.replace('<div class="tabs">', '<div class="tabs" style="display:none">')
        return win.replace("<span style=\"color:#c9d3df\">Brainstorm</span>",
                           "<span style=\"color:#c9d3df\">Create a new skill</span>") + f'<div class="note">{esc(v[4])}</div>'
    if kind == "console":
        return console(v[1], v[2], console_body(v[3])) + f'<div class="note">{esc(v[4])}</div>'
    if kind == "ha":
        rows = ""
        for lb, val, hl, ds in v[2]:
            rows += (f'<div class="lb">{esc(lb)}</div><div class="in{" hl" if hl else ""}">{esc(val)}</div>'
                     f'<div class="ds">{ds}</div>')
        return (f'<div class="path">{esc(v[3])}</div><div class="ha" style="top:20px"><div class="hd">{esc(v[1])}</div>'
                f'<div class="bd">{rows}</div><div class="ft"><span>{esc(v[4]).upper()}</span></div></div>')
    if kind == "speech":
        who = {"du": "Du", "alexa": "Alexa", "ha": "Home Assistant"}
        bubs = "".join(f'<div class="bub {w if w != "ha" else "hab"}"><span class="who">{who[w]}</span>{esc(t)}</div>' for w, t in v[1])
        return f'<div class="sph">{esc(v[2])}</div><div class="sp">{bubs}</div>'
    if kind == "shot":
        # Real card screenshot with bullets: ("shot", file, img_height, bullets, note)
        items = "".join(f'<li><span class="ic">{i}</span><span>{t}</span></li>' for i, t in v[3])
        return (f'<div class="shot"><img src="{v[1]}" style="height:{v[2]}px"></div>'
                f'<div class="shotside bl"><ul>{items}</ul></div><div class="note">{esc(v[4])}</div>')
    if kind == "yaml":
        # ("yaml", heading, code, note)
        return (f'<div class="bl"><h2>{esc(v[1])}</h2></div><div class="pre" style="font-size:22px;'
                f'padding:22px 28px;max-width:900px">{esc(v[2])}</div><div class="note">{esc(v[3])}</div>')
    if kind == "transform":
        # ("transform", spoken sentence, result text, chips, note)
        chips = "".join(f'<span class="chip">{c}</span>' for c in v[3])
        return (f'<div class="tf"><div class="tfin">🗣️ „{esc(v[1])}“</div><div class="tfarrow">⬇</div>'
                f'<div class="tfout"><div class="tftext">{esc(v[2])}</div><div>{chips}</div></div></div>'
                f'<div class="note">{esc(v[4])}</div>')
    if kind == "grid":
        # ("grid", heading, [(icon, title, text)], note)
        tiles = "".join(f'<div class="tile"><div class="ti">{i}</div><b>{esc(a)}</b><span>{b}</span></div>'
                        for i, a, b in v[2])
        return f'<div class="bl"><h2>{esc(v[1])}</h2></div><div class="grid">{tiles}</div><div class="note">{esc(v[3])}</div>'
    if kind == "menu":
        # ("menu", dialog title, [(item, highlighted)], path, note)
        items = "".join(f'<div class="mi{" hl" if hl else ""}">{esc(t)}</div>' for t, hl in v[2])
        return (f'<div class="path">{esc(v[3])}</div><div class="ha" style="top:20px"><div class="hd">{esc(v[1])}</div>'
                f'<div class="bd" style="padding:8px 24px">{items}</div></div><div class="note">{esc(v[4])}</div>')
    if kind == "switches":
        # ("switches", dialog title, [(label, value, highlighted, description)], path, note)
        rows = ""
        for lb, val, hl, ds in v[2]:
            val_html = ('<span class="tog"></span>' if val is True else '<span class="tog off"></span>'
                        if val is False else f'<b style="color:#03a9f4">{esc(val)}</b>')
            rows += (f'<div class="sw{" hl" if hl else ""}"><span>{esc(lb)}<small>{esc(ds)}</small></span>'
                     f'{val_html}</div>')
        return (f'<div class="path">{esc(v[3])}</div><div class="ha" style="top:20px"><div class="hd">{esc(v[1])}</div>'
                f'<div class="bd" style="padding:10px 24px">{rows}</div></div><div class="note">{esc(v[4])}</div>')
    if kind == "phone":
        # ("phone", screen title, [(html, highlighted)], [(icon, text)], note)
        items = "".join(f'<div class="it{" hl" if hl else ""}">{h}</div>' for h, hl in v[2])
        bullets = "".join(f'<li><span class="ic">{i}</span><span>{t}</span></li>' for i, t in v[3])
        return (f'<div class="ph2"><div class="t">{esc(v[1])}</div>{items}</div>'
                f'<div class="ph2side bl"><ul>{bullets}</ul></div><div class="note">{esc(v[4])}</div>')
    if kind == "alexa_app":
        return ('<div class="phone"><div class="t">Alexa-App ➔ Mehr ➔ Skills &amp; Spiele</div>'
                '<div class="it">Meine Skills</div><div class="it hl">Dev · <b>Brainstorm</b></div>'
                '<div class="it">Einstellungen ➔ Berechtigungen verwalten</div>'
                '<div class="it hl"><span class="tog"></span>Erinnerungen</div></div>'
                '<div class="side2 bl"><ul>'
                '<li><span class="ic">📱</span><span>Entwickler-Skills stehen im eigenen Bereich (Dev)</span></li>'
                '<li><span class="ic">⏰</span><span>Berechtigung <b>Erinnerungen</b> einmal erlauben – nur mit Permissions ➔ Reminders</span></li>'
                '<li><span class="ic">🔁</span><span>Fehlt sie, bittet Alexa nach der ersten Erinnerung per Karte in der App darum</span></li>'
                '</ul></div><div class="note">Die Bezeichnungen in der App können je nach Version leicht abweichen.</div>')
    raise ValueError(kind)


def page(chapter_no: int, total: int, title: str, v: tuple, caption: str) -> str:
    prog = "".join(
        f'<div class="{"done" if i < chapter_no else "cur" if i == chapter_no else ""}"></div>'
        for i in range(total))
    badge = "Intro" if chapter_no == 0 else f"Kapitel {chapter_no}"
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div class="top"><span class="badge">{badge}</span><span class="ctitle">{esc(title)}</span>'
            '<span class="logo"><img src="icon.png">Brainstorm Hub</span></div>'
            f'<div class="stage">{stage(v)}</div><div class="cap">{esc(caption)}</div>'
            f'<div class="prog">{prog}</div></body></html>')


def spoken(text: str) -> str:
    for src, dst in SPOKEN:
        text = text.replace(src, dst)
    # Piper drops punctuation right after a [[phoneme]] block and glues the next
    # word on, so move it into the block: "[[x]], y" -> "[[x,]] y"
    return re.sub(r"\]\]([.,;:!?])", r"\1]]", text)


def run(cmd: list[str], **kw) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)


def main() -> None:
    only_frames = "--frames" in sys.argv
    OUT.mkdir(exist_ok=True)
    (OUT / "icon.png").write_bytes((ROOT / "icon.png").read_bytes())
    for shot in (ROOT / "cards").glob("crop_*.png"):
        (OUT / shot.name).write_bytes(shot.read_bytes())
    segments, chapters, t = [], [], 0.0
    intro = ROOT / "intro.mp4"  # made by intro.py, reusable for other videos
    if intro.exists() and "--no-intro" not in sys.argv:
        segments.append(intro)
        t = float(subprocess.run([FFMPEG, "-i", str(intro)], capture_output=True, text=True)
                  .stderr.split("Duration: ")[1].split(",")[0].split(":")[-1])
    total = len(CHAPTERS)
    for c_no, ch in enumerate(CHAPTERS):
        start = 0.0 if c_no == 0 else t
        for s_no, sc in enumerate(ch["scenes"]):
            name = f"c{c_no:02d}_{s_no}"
            (OUT / f"{name}.html").write_text(page(c_no, total, ch["title"], sc["v"], sc["say"]))
            run(["/snap/bin/chromium", "--headless", "--no-sandbox", "--hide-scrollbars",
                 f"--window-size={W},{H}", f"--screenshot={OUT / name}.png", f"file://{OUT / name}.html"])
            if only_frames:
                continue
            # Keyed by the spoken text, so only changed scenes are voiced again
            key = hashlib.sha1(spoken(sc.get("speak", sc["say"])).encode()).hexdigest()[:10]
            wav = OUT / f"{name}_{key}.wav"
            if not wav.exists():
                run([PIPER, "-m", VOICE, "-f", str(wav), "--sentence-silence", "0.35"],
                    input=spoken(sc.get("speak", sc["say"])).encode())
            with wave.open(str(wav)) as w:
                dur = w.getnframes() / w.getframerate() + PAD_BEFORE + PAD_AFTER
            seg = OUT / f"{name}.mp4"
            run([FFMPEG, "-y", "-loop", "1", "-framerate", "25", "-i", str(OUT / f"{name}.png"),
                 "-i", str(wav), "-filter_complex",
                 f"[1:a]adelay={int(PAD_BEFORE * 1000)}:all=1,apad,aresample=44100[a]",
                 "-map", "0:v", "-map", "[a]", "-t", f"{dur:.3f}",
                 "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "25",
                 "-c:a", "aac", "-b:a", "96k", "-ac", "1", str(seg)])
            segments.append(seg)
            t += dur
        chapters.append((ch["title"], start, t))
    if only_frames:
        return
    (OUT / "list.txt").write_text("".join(f"file '{s}'\n" for s in segments))
    meta = [";FFMETADATA1", f"title={VIDEO_TITLE}", "artist=Brainstorm Hub"]
    for i, (title, a, b) in enumerate(chapters):
        label = "Einleitung" if i == 0 else f"{i}. {title}"
        meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(a * 1000)}", f"END={int(b * 1000)}", f"title={label}"]
    (OUT / "meta.txt").write_text("\n".join(meta) + "\n")
    final = ROOT / f"{OUT_NAME}.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(OUT / "list.txt"), "-i", str(OUT / "meta.txt"),
         "-map_metadata", "1", "-map_chapters", "1", "-c", "copy", "-movflags", "+faststart", str(final)])
    (ROOT / f"chapters_{OUT_NAME}.json").write_text(json.dumps(chapters, ensure_ascii=False, indent=1))
    print(final, f"{t:.1f}s", final.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
