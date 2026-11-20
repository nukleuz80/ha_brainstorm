"""Record the scenes of a storyboard as Full HD video with real motion.

Every scene page is opened in a headless Chromium. Before each frame all CSS and
Web animations (also those of the cards and of the pointer) are paused and set to
the exact video time of that frame, so they play perfectly smoothly however long
a screenshot takes. (Chromium's virtual time hangs now and then in screenshots.)

Static scenes record their entrance animations and then hold the last frame.
Live scenes (``("live", ...)`` in a storyboard) show the real card in an iframe
and play their actions with a visible mouse pointer for the whole scene.
"""
from __future__ import annotations

import asyncio
import base64
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from playwright.async_api import Page, async_playwright

FPS = 30
CSS_W, CSS_H = 1280, 720
SCALE = 1.5  # 1920 x 1080
# JPEG frames: PNG capture at Full HD takes seconds per frame
TICK_JS = """(t) => {
  for (const a of document.getAnimations()) {
    if (a.hdStart === undefined) a.hdStart = t;
    a.pause();
    a.currentTime = t - a.hdStart;
  }
}"""
# Seconds of entrance animation recorded for a static scene
ANIMATION_SECONDS = 2.4
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(Path.home() / "bs-video/pw"))


@dataclass
class Job:
    """One scene to record."""

    url: str
    wav: Path
    duration: float
    out: Path
    pad_before: float
    # (seconds, action, argument) for live scenes, None for a static scene
    actions: list[tuple[float, str, str]] | None = None
    extra: dict = field(default_factory=dict)


CURSOR_JS = """
(() => {
  const c = document.createElement('div');
  c.id = 'hdcursor';
  c.innerHTML = '<svg width="34" height="34" viewBox="0 0 24 24"><path d="M4 2l15 11-6.5 1.2L16 21l-3 1.4-3.4-6.6L4 20z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  Object.assign(c.style, {position:'fixed', left:'0', top:'0', zIndex: 99999, pointerEvents:'none',
    transform:'translate(1180px, 760px)', transition:'transform 0.7s cubic-bezier(.4,.0,.2,1)',
    filter:'drop-shadow(0 3px 6px rgba(0,0,0,.6))'});
  document.body.appendChild(c);
  const r = document.createElement('div');
  r.id = 'hdripple';
  Object.assign(r.style, {position:'fixed', left:'0', top:'0', width:'44px', height:'44px', marginLeft:'-22px',
    marginTop:'-22px', borderRadius:'50%', border:'4px solid #ffb703', opacity:'0', zIndex: 99998,
    pointerEvents:'none'});
  document.body.appendChild(r);
  window.hdMove = (x, y) => { c.style.transform = `translate(${x - 4}px, ${y - 2}px)`; };
  window.hdRipple = (x, y) => {
    r.style.left = x + 'px'; r.style.top = y + 'px';
    r.animate([{opacity: .95, transform: 'scale(.4)'}, {opacity: 0, transform: 'scale(1.6)'}],
              {duration: 550, easing: 'ease-out'});
  };
})();
"""


class Recorder:
    """Record jobs with one browser."""

    def __init__(self, ffmpeg: str) -> None:
        self.ffmpeg = ffmpeg

    async def run(self, jobs: list[Job]) -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                args=["--disable-features=IsolateOrigins,site-per-process", "--hide-scrollbars"]
            )
            for number, job in enumerate(jobs, 1):
                print(f"  scene {number}/{len(jobs)} {job.out.name} {job.duration:.1f}s", flush=True)
                page = await browser.new_page(
                    viewport={"width": CSS_W, "height": CSS_H}, device_scale_factor=SCALE
                )
                try:
                    await self._record(page, job)
                finally:
                    await page.close()
            await browser.close()

    async def _record(self, page: Page, job: Job) -> None:
        await page.goto(job.url, wait_until="load")
        if job.actions is not None:
            # The card inside the iframe needs a moment for its first render
            await page.wait_for_timeout(2500)
            await page.evaluate(CURSOR_JS)
        await page.evaluate("document.fonts.ready")
        cdp = await page.context.new_cdp_session(page)
        live = job.actions is not None
        frames = round((job.duration if live else min(ANIMATION_SECONDS, job.duration)) * FPS)
        hold = max(0.0, job.duration - frames / FPS)
        encoder = subprocess.Popen(
            [self.ffmpeg, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
             "-i", "-", "-i", str(job.wav), "-filter_complex",
             f"[0:v]tpad=stop_mode=clone:stop_duration={hold:.3f},scale=in_range=pc:out_range=tv,format=yuv420p[v];"
             f"[1:a]adelay={int(job.pad_before * 1000)}:all=1,apad,aresample=48000[a]",
             "-map", "[v]", "-map", "[a]", "-t", f"{job.duration:.3f}", "-r", str(FPS),
             "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-profile:v", "high", "-color_range", "tv",
             "-c:a", "aac", "-b:a", "128k", "-ac", "2", str(job.out)],
            stdin=subprocess.PIPE,
        )
        pending = sorted(job.actions or [])
        for index in range(frames):
            now = index / FPS
            while pending and pending[0][0] <= now:
                _, action, argument = pending.pop(0)
                if action == "click":
                    # The pointer glides over first, the click follows
                    await self._act(page, "point", argument)
                    pending.append((now + 0.8, "tap", argument))
                    pending.sort()
                else:
                    await self._act(page, action, argument)
            await self._tick(page, now * 1000)
            shot = await cdp.send(
                "Page.captureScreenshot",
                {"format": "jpeg", "quality": 95,
                 "clip": {"x": 0, "y": 0, "width": CSS_W, "height": CSS_H, "scale": SCALE}},
            )
            assert encoder.stdin is not None
            encoder.stdin.write(base64.b64decode(shot["data"]))
        assert encoder.stdin is not None
        encoder.stdin.close()
        if encoder.wait() != 0:
            raise RuntimeError(f"ffmpeg failed for {job.out}")

    @staticmethod
    async def _tick(page: Page, milliseconds: float) -> None:
        for frame in page.frames:
            try:
                await frame.evaluate(TICK_JS, milliseconds)
            except Exception:  # a frame that is just navigating
                continue

    async def _target(self, page: Page, text: str):
        frame = page.frame_locator("iframe#live")
        locator = frame.get_by_text(text, exact=False).locator("visible=true").first
        box = await locator.bounding_box(timeout=4000)
        return locator, box

    async def _act(self, page: Page, action: str, argument: str) -> None:
        """Play one action; 'point' moves the pointer, 'click' also clicks."""
        try:
            if action in ("point", "tap"):
                locator, box = await self._target(page, argument)
                if box is None:
                    return
                x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                await page.evaluate(f"hdMove({x}, {y})")
                if action == "tap":
                    await page.evaluate(f"hdRipple({x}, {y})")
                    await locator.click(force=True, no_wait_after=True, timeout=4000)
            elif action == "move":
                x, y = (float(v) for v in argument.split(","))
                await page.evaluate(f"hdMove({x}, {y})")
            elif action == "wheel":
                await page.mouse.wheel(0, float(argument))
            elif action == "js":
                await page.frame_locator("iframe#live").locator("body").evaluate(argument)
        except Exception as err:  # a missing element must not stop the whole video
            print(f"    ! {action} {argument!r}: {err.__class__.__name__}", flush=True)


def record(ffmpeg: str, jobs: list[Job]) -> None:
    """Record all jobs."""
    asyncio.run(Recorder(ffmpeg).run(jobs))
