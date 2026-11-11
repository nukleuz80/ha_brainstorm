"""Take the card screenshots used by the videos (needs the http server from README.md)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).parent
CHROMIUM = "/snap/bin/chromium"
URL = "http://localhost:8799/index.html?"
# name, window size, query, maximum height of the crop in pixels at scale 2
SHOTS = [
    ("list", "640,1000", "card=list&w=560", 1060),
    ("projekte", "640,800", "card=list&w=560&click=Projekte", None),
    ("done", "640,700", "card=list&w=560&click=Erledigt", None),
    ("mindmap", "1100,700", "card=mindmap&w=1060", None),
    ("mmprojekte", "1100,700", "card=mindmap&w=1060&click=Projekte", None),
    ("kanban", "1100,700", 'card=mindmap&w=1060&cfg={"layout":"kanban"}&click=Projekte', None),
    ("outline", "1100,700", 'card=mindmap&w=1060&cfg={"layout":"tree"}&click=Projekte', None),
    ("social", "1100,700", 'card=mindmap&w=1060&cfg={"default_category":"Ausflug"}&scene=social', None),
    ("comments", "700,760", 'card=list&w=640&cfg={"default_category":"Ausflug"}&scene=comments', None),
    ("aimap", "1000,800", 'card=mindmap&w=900&cfg={"default_category":"Sommerfest","height":"700px"}&scene=aimap', None),
]


# English labels for the queries above, used with ``shots.py en`` (output in cards/en)
EN = {"Projekte": "Projects", "Erledigt": "Completed", "Ausflug": "Day trip", "Sommerfest": "Summer party"}


def main() -> None:
    lang = sys.argv[1] if len(sys.argv) > 1 else "de"
    out = HERE / "en" if lang == "en" else HERE
    out.mkdir(exist_ok=True)
    for name, size, query, max_height in SHOTS:
        if lang == "en":
            for de, en in EN.items():
                query = query.replace(de, en)
            query += "&lang=en"
        raw = out / f"{name}.png"
        subprocess.run([CHROMIUM, "--headless", "--no-sandbox", "--hide-scrollbars",
                        "--force-device-scale-factor=2", f"--window-size={size}",
                        "--virtual-time-budget=8000", f"--screenshot={raw}", URL + query],
                       check=True, capture_output=True)
        image = Image.open(raw).convert("RGB")
        background = Image.new("RGB", image.size, (17, 17, 17))
        box = ImageChops.difference(image, background).point(lambda v: 255 if v > 12 else 0).getbbox()
        image = image.crop((box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4))
        if max_height and image.height > max_height:
            image = image.crop((0, 0, image.width, max_height))
        image.save(out / f"crop_{name}.png")
        if name == "mindmap":
            # Zoomed onto the notes, so the text stays readable in the video
            Image.open(raw).crop((400, 215, 1830, 1190)).save(out / "crop_mindmapzoom.png")


if __name__ == "__main__":
    main()
