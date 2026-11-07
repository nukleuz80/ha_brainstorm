"""Reusable Brainstorm Hub video intro: neon bulb power-on with sparks and a jingle.

Usage: python intro.py [--title T] [--subtitle S] [--out intro.mp4]
The output matches build.py (1280x720, 25 fps, yuv420p, AAC 44.1 kHz mono),
so it can be put in front of any video with the ffmpeg concat demuxer.
"""
from __future__ import annotations

import argparse
import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).parent
FFMPEG = str(next((ROOT / "vv/lib").glob("python*/site-packages/imageio_ffmpeg/binaries/ffmpeg-*")))
W, H, FPS, DUR, SR = 1280, 720, 25, 5.0, 44100
FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
COLORS = [(255, 183, 3), (0, 202, 255), (190, 110, 255), (255, 120, 200)]
CX, CY, LOGO = W // 2, 290, 330


def ease_out_back(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def clamp01(x: float) -> float:
    return min(max(x, 0.0), 1.0)


def background() -> np.ndarray:
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - CX) / W) ** 2 + ((y - CY) / H) ** 2)
    base = np.stack([13 + 20 * (1 - d), 27 + 30 * (1 - d), 42 + 40 * (1 - d)], -1)
    return np.clip(base * 0.75, 0, 255)


def neon_logo() -> Image.Image:
    """The bulb only: brightness becomes alpha, so the dark tile disappears."""
    img = Image.open(ROOT / "icon.png").convert("RGB").resize((LOGO, LOGO), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32)
    lum = arr.max(-1)
    alpha = np.clip((lum - 28) * 1.6, 0, 255)
    # Fade out the rounded tile frame towards the edges
    y, x = np.mgrid[0:LOGO, 0:LOGO].astype(np.float32)
    r = np.sqrt((x - LOGO / 2) ** 2 + (y - LOGO * 0.5) ** 2) / (LOGO / 2)
    alpha *= np.clip((0.76 - r) / 0.06, 0, 1)
    rgba = np.dstack([arr, alpha]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def gradient_text(text: str, font: ImageFont.FreeTypeFont) -> Image.Image:
    box = font.getbbox(text)
    w, h = box[2] + 8, box[3] + 12
    mask = Image.new("L", (w, h))
    ImageDraw.Draw(mask).text((4, 4), text, font=font, fill=255)
    xs = np.linspace(0, 1, w)[None, :, None]
    a, b, c = (np.array(col, np.float32)[None, None] for col in COLORS[:3])
    grad = np.where(xs < 0.5, a + (b - a) * xs * 2, b + (c - b) * (xs - 0.5) * 2)
    grad = np.repeat(grad, h, 0)
    img = Image.fromarray(grad.astype(np.uint8), "RGB").convert("RGBA")
    img.putalpha(mask)
    return img


class Sparks:
    """Particles that rush towards the bulb, then burst outwards on power-on."""

    def __init__(self, n: int = 140, seed: int = 7) -> None:
        rng = np.random.default_rng(seed)
        self.ang = rng.uniform(0, 2 * np.pi, n)
        self.dist = rng.uniform(500, 900, n)
        self.delay = rng.uniform(0, 0.7, n)
        self.speed = rng.uniform(250, 700, n)
        self.col = [COLORS[i % 4] for i in range(n)]
        self.size = rng.uniform(1.5, 4, n)

    def draw(self, d: ImageDraw.ImageDraw, t: float) -> None:
        for i in range(len(self.ang)):
            ca, sa = math.cos(self.ang[i]), math.sin(self.ang[i])
            if t < 1.3:  # converge
                p = ease_out(clamp01((t - self.delay[i]) / (1.3 - self.delay[i])))
                if p <= 0:
                    continue
                r0 = self.dist[i] * (1 - p) + 30
                r1 = r0 + 60 * (1 - p) + 6
                alpha = int(255 * min(p * 3, 1))
            else:  # burst
                q = t - 1.3
                r0 = 40 + self.speed[i] * q
                r1 = r0 + 25
                alpha = int(255 * clamp01(1 - q / 1.4))
                if alpha <= 0:
                    continue
            col = (*self.col[i], alpha)
            d.line([(CX + ca * r0, CY + sa * r0), (CX + ca * r1, CY + sa * r1)],
                   fill=col, width=max(1, int(self.size[i])))


def flicker(t: float) -> float:
    """Neon tube power-on: off, two stutters, then fully on with a gentle pulse."""
    if t < 0.75:
        return 0.0
    if t < 1.3:
        steps = [(0.75, 0.55), (0.82, 0.05), (0.9, 0.8), (0.97, 0.15), (1.05, 0.9), (1.13, 0.4)]
        level = 0.0
        for start, val in steps:
            if t >= start:
                level = val
        return level
    return 1.0 + 0.05 * math.sin((t - 1.3) * 4)


def render_frames(title: str, subtitle: str, tmp: Path) -> None:
    bg = background()
    logo = neon_logo()
    glow_src = logo.filter(ImageFilter.GaussianBlur(28))
    halo = Image.new("RGBA", (W, H))
    ImageDraw.Draw(halo).ellipse([CX - 230, CY - 230, CX + 230, CY + 230], fill=(90, 120, 255, 90))
    halo = halo.filter(ImageFilter.GaussianBlur(70))
    title_img = gradient_text(title, ImageFont.truetype(FONT_BOLD, 78))
    sub_font = ImageFont.truetype(FONT_REG, 30)
    sparks = Sparks()
    n = int(DUR * FPS)
    for f in range(n):
        t = f / FPS
        frame = Image.fromarray(bg.astype(np.uint8), "RGB").convert("RGBA")
        fl = flicker(t)
        # Halo behind the bulb
        if fl > 0:
            h_arr = np.asarray(halo).copy()
            h_arr[..., 3] = (h_arr[..., 3] * min(fl, 1.05)).astype(np.uint8)
            frame.alpha_composite(Image.fromarray(h_arr, "RGBA"))
        layer = Image.new("RGBA", (W, H))
        sparks.draw(ImageDraw.Draw(layer), t)
        frame.alpha_composite(layer)
        # Bulb: grows in, dim until it powers on
        scale = 0.6 + 0.4 * ease_out_back((t - 0.15) / 1.1)
        size = max(2, int(LOGO * scale))
        level = 0.18 + 0.82 * min(fl, 1.0) if t > 0.15 else 0
        if level > 0:
            lg = logo.resize((size, size), Image.LANCZOS)
            gl = glow_src.resize((size, size), Image.LANCZOS)
            pos = (CX - size // 2, CY - size // 2)
            for img, mul in ((gl, 1.6 * min(fl, 1.05)), (lg, level)):
                a = np.asarray(img).copy()
                a[..., 3] = np.clip(a[..., 3] * mul, 0, 255).astype(np.uint8)
                frame.alpha_composite(Image.fromarray(a, "RGBA"), pos)
        # Shockwave ring and flash at power-on
        if 1.3 <= t < 2.2:
            q = (t - 1.3) / 0.9
            ring = Image.new("RGBA", (W, H))
            r = 60 + 620 * ease_out(q)
            ImageDraw.Draw(ring).ellipse([CX - r, CY - r, CX + r, CY + r],
                                         outline=(200, 230, 255, int(220 * (1 - q))), width=6)
            frame.alpha_composite(ring.filter(ImageFilter.GaussianBlur(2)))
        if 1.3 <= t < 1.6:
            flash = Image.new("RGBA", (W, H), (255, 255, 255, int(105 * (1 - (t - 1.3) / 0.3))))
            frame.alpha_composite(flash)
        # Light sweep over the bulb
        if 2.0 <= t < 2.8:
            q = (t - 2.0) / 0.8
            sweep = Image.new("L", (W, H))
            x = CX - 260 + 520 * q
            ImageDraw.Draw(sweep).polygon([(x - 30, CY - 200), (x + 10, CY - 200), (x - 30, CY + 200),
                                           (x - 70, CY + 200)], fill=110)
            sweep = sweep.filter(ImageFilter.GaussianBlur(10))
            mask = np.asarray(logo.resize((LOGO, LOGO)))[..., 3]
            m = Image.new("L", (W, H))
            m.paste(Image.fromarray(mask), (CX - LOGO // 2, CY - LOGO // 2))
            s = np.minimum(np.asarray(sweep), np.asarray(m) // 2).astype(np.uint8)
            frame.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, H), 255)] * 3 + [Image.fromarray(s)]))
        # Title: slides up letter group by letter group
        if t >= 1.5:
            q = ease_out((t - 1.5) / 0.7)
            reveal = int(title_img.width * clamp01((t - 1.5) / 0.9))
            if reveal > 0:
                part = title_img.crop((0, 0, reveal, title_img.height))
                a = np.asarray(part).copy()
                a[..., 3] = (a[..., 3] * q).astype(np.uint8)
                y = int(500 + 30 * (1 - q))
                frame.alpha_composite(Image.fromarray(a, "RGBA"), (CX - title_img.width // 2, y))
        if t >= 2.3 and subtitle:
            q = ease_out((t - 2.3) / 0.6)
            sub = Image.new("RGBA", (W, H))
            sd = ImageDraw.Draw(sub)
            tw = sd.textlength(subtitle, font=sub_font)
            sd.text((CX - tw / 2, 600 + 12 * (1 - q)), subtitle, font=sub_font,
                    fill=(185, 205, 224, int(255 * q)))
            frame.alpha_composite(sub)
        # Fade out to black
        if t > DUR - 0.5:
            frame.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (t - DUR + 0.5) / 0.5))))
        frame.convert("RGB").save(tmp / f"f{f:04d}.png")


def jingle(path: Path) -> None:
    """Whoosh, neon buzz, impact and a bright chord, synthesized."""
    n = int(DUR * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(3)
    out = np.zeros(n)
    # Rising whoosh 0..1.3 s: noise through a sweeping one-pole lowpass
    noise = rng.normal(0, 1, n)
    cut = np.clip(0.01 + 0.25 * (t / 1.3), 0, 0.3)
    lp = np.zeros(n)
    for i in range(1, int(1.45 * SR)):
        lp[i] = lp[i - 1] + cut[i] * (noise[i] - lp[i - 1])
    env = np.clip(t / 1.3, 0, 1) ** 2 * (t < 1.45)
    out += 0.5 * lp * env
    # Neon buzz while flickering
    buzz = np.sign(np.sin(2 * np.pi * 100 * t)) * 0.06
    gate = np.array([flicker(x) > 0.3 and x < 1.3 for x in t[::100]]).repeat(100)[:n]
    out += buzz * gate
    # Impact at 1.3 s
    k = t - 1.3
    on = k >= 0
    out += on * 0.8 * np.sin(2 * np.pi * (45 + 60 * np.exp(-k.clip(0) * 20)) * k) * np.exp(-k.clip(0) * 5)
    # Chord C-E-G-C, softly arpeggiated, with shimmer
    for j, freq in enumerate([523.25, 659.25, 783.99, 1046.5]):
        s = t - (1.35 + 0.08 * j)
        a = (s >= 0) * np.exp(-s.clip(0) * 1.3) * 0.13
        out += a * (np.sin(2 * np.pi * freq * s) + 0.3 * np.sin(2 * np.pi * 2 * freq * s))
    out *= np.clip((DUR - t) / 0.5, 0, 1)
    out = out / max(1e-6, np.abs(out).max()) * 0.85
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", default="Brainstorm Hub")
    ap.add_argument("--subtitle", default="Ideen sammeln mit Home Assistant")
    ap.add_argument("--out", default=str(ROOT / "intro.mp4"))
    args = ap.parse_args()
    tmp = ROOT / "intro_frames"
    tmp.mkdir(exist_ok=True)
    render_frames(args.title, args.subtitle, tmp)
    jingle(tmp / "jingle.wav")
    subprocess.run([FFMPEG, "-y", "-framerate", str(FPS), "-i", str(tmp / "f%04d.png"),
                    "-i", str(tmp / "jingle.wav"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-r", str(FPS), "-c:a", "aac", "-b:a", "96k", "-ar", str(SR), "-ac", "1",
                    "-shortest", args.out], check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    print(args.out)


if __name__ == "__main__":
    main()
