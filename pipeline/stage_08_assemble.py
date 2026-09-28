"""
STAGE 8 — ASSEMBLE: render the vertical video with moviepy (MIT).

moviepy 2.x is a Pythonic wrapper around FFmpeg — and it bundles its own
ffmpeg binary (imageio-ffmpeg), so no system-wide FFmpeg install is needed.

SIMURG guard coverage (honest scoping): the guard protects LLM-generated
text (scripts, captions, overlay copy, visual prompts). The FFmpeg command
here is deterministically constructed, so instead of a text guard it gets
structural validation — every input must exist. A text guard on CLI arg
strings would false-positive on repetitive flags (long filter chains),
which is exactly why the guard stays scoped to text.

Render logic:
  * visuals found  -> still images, center-cropped to 9:16
  * no visuals     -> ffmpeg-drawn dark background ($0 fallback)
  * audio          -> the stage-6 edge-tts narration
  * title overlay  -> top-third TextClip (Pillow-based in moviepy 2.x)

Run:  python -m pipeline.stage_08_assemble
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .common import AUDIO_DIR, RENDERED_DIR, slugify


def validate_inputs(visual_paths: list[Path], audio_path: Path | None) -> dict:
    """Structural validation (the stage-8 stand-in for the text guard)."""
    problems = []
    for p in visual_paths:
        if not Path(p).exists():
            problems.append(f"missing visual: {p}")
    if audio_path is not None and not Path(audio_path).exists():
        problems.append(f"missing audio: {audio_path}")
    return {"ok": not problems, "problems": problems}


def _font_path() -> str:
    for candidate in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
    ):
        if Path(candidate).exists():
            return candidate
    return "arial"


def _ffmpeg_exe() -> str | None:
    try:
        from imageio_ffmpeg import get_ffmpeg_exe

        return get_ffmpeg_exe()
    except ImportError:
        return None


def render_with_moviepy(
    visual_paths: list[Path],
    audio_path: Path,
    title_text: str,
    out_path: Path,
    size: tuple[int, int] = (1080, 1920),
) -> dict:
    from moviepy import (
        AudioFileClip,
        ColorClip,
        CompositeVideoClip,
        ImageClip,
        TextClip,
        concatenate_videoclips,
    )

    width, height = size
    audio = AudioFileClip(str(audio_path))
    duration = float(audio.duration)

    if visual_paths:
        per = duration / len(visual_paths)
        clips = []
        for p in visual_paths:
            img = ImageClip(str(p)).with_duration(per).resized(width=width)
            if img.h > height:  # center-crop vertically
                y = (img.h - height) // 2
                img = img.cropped(x1=0, y1=y, x2=width, y2=y + height)
            elif img.h < height:
                img = img.resized(height=height)
            clips.append(img)
        base = concatenate_videoclips(clips, method="compose").with_duration(duration)
    else:
        base = ColorClip(size=size, color=(13, 22, 32)).with_duration(duration)

    layers = [base]
    try:
        title = (
            TextClip(
                font=_font_path(),
                text=title_text,
                font_size=64,
                color="white",
                size=(width - 120, None),
                method="caption",
                text_align="center",
            )
            .with_duration(duration)
            .with_position(("center", 180))
        )
        layers.append(title)
    except Exception as exc:
        print(f"   [warn] title overlay skipped: {exc}")

    final = CompositeVideoClip(layers, size=size).with_audio(audio)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(str(out_path), fps=24, codec="libx264", audio_codec="aac", logger=None)
    return {"ok": True, "out": str(out_path), "duration_sec": round(duration, 2)}


def render_with_ffmpeg(
    audio_path: Path, title_text: str, out_path: Path, size: tuple[int, int] = (1080, 1920)
) -> dict:
    """$0 fallback: dark background + narration, no moviepy needed."""
    exe = _ffmpeg_exe()
    if exe is None:
        return {"ok": False, "reason": "moviepy and ffmpeg both unavailable"}
    w, h = size
    cmd = [
        exe, "-y",
        "-f", "lavfi", "-i", f"color=c=0x0D1620:s={w}x{h}:r=24",
        "-i", str(audio_path),
        "-c:v", "libx264", "-c:a", "aac", "-shortest",
        str(out_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        return {"ok": False, "reason": proc.stderr.strip()[-300:]}
    return {"ok": True, "out": str(out_path), "engine": "ffmpeg (imageio-ffmpeg)"}


def assemble_vertical(
    visual_paths: list[Path],
    audio_path: Path,
    title_text: str,
    slug: str | None = None,
) -> dict:
    """Validate, render (moviepy preferred, ffmpeg fallback), report."""
    slug = slug or slugify(title_text)
    out_path = RENDERED_DIR / f"{slug}.mp4"
    validation = validate_inputs(visual_paths, audio_path)
    if not validation["ok"]:
        return {"ok": False, "validation": validation, "out": None}
    try:
        result = render_with_moviepy(visual_paths, audio_path, title_text, out_path)
        result["engine"] = "moviepy 2.x (MIT)"
        return result
    except ImportError:
        print("   [warn] moviepy not installed — trying ffmpeg fallback")
    except Exception as exc:
        print(f"   [warn] moviepy render failed: {exc}")
    return render_with_ffmpeg(audio_path, title_text, out_path)


if __name__ == "__main__":
    audio = AUDIO_DIR / "demo.mp3"
    if not audio.exists():
        print("[STAGE 8] no demo audio found — run: python -m pipeline.stage_06_tts")
    else:
        print("[STAGE 8] ASSEMBLE")
        result = assemble_vertical(
            [], audio, "Faceless Side Hustles — The Honest Math", slug="demo"
        )
        print("   result:", result)
