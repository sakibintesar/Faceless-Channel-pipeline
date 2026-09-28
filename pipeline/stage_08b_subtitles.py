"""
STAGE 8b — SUBTITLES: word-accurate SRT from edge-tts cues (+ ffsubsync).

Zero-dollar cost: edge-tts emits WordBoundary events during synthesis, so
captions cost nothing — no transcription API. ffsubsync (MIT) re-aligns
the SRT against the rendered video if timing ever drifts after edits.

Run:  python -m pipeline.stage_08b_subtitles
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .common import SUBTITLES_DIR, slugify


def _fmt(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def cues_to_srt(cues: list[dict], words_per_line: int = 4) -> str:
    """Group word cues into caption lines -> standard SRT text."""
    lines: list[str] = []
    idx = 1
    for i in range(0, len(cues), words_per_line):
        group = cues[i : i + words_per_line]
        text = " ".join(c["text"] for c in group)
        start, end = group[0]["start"], group[-1]["end"]
        lines.append(f"{idx}\n{_fmt(start)} --> {_fmt(end)}\n{text}\n")
        idx += 1
    return "\n".join(lines)


def write_srt(cues: list[dict], name: str) -> Path:
    SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)
    path = SUBTITLES_DIR / f"{slugify(name)}.srt"
    path.write_text(cues_to_srt(cues), encoding="utf-8")
    return path


def sync_with_ffsubsync(reference: str | Path, srt_path: str | Path) -> dict:
    """Re-align an SRT to the rendered video/audio with ffsubsync (MIT).

    Optional bonus: edge-tts cues are already word-accurate, so this is
    only needed when editing shifts the timeline (e.g. trimmed intro).
    """
    try:
        proc = subprocess.run(
            ["ffsubsync", str(reference), "-i", str(srt_path), "-o", str(srt_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        return {"ok": False, "reason": "ffsubsync CLI not found (pip install ffsubsync)"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "reason": "ffsubsync timed out"}
    if proc.returncode != 0:
        return {"ok": False, "reason": proc.stderr.strip()[:200] or f"exit {proc.returncode}"}
    return {"ok": True, "srt": str(srt_path)}


if __name__ == "__main__":
    demo_cues = [
        {"text": "Most", "start": 0.10, "end": 0.32},
        {"text": "people", "start": 0.32, "end": 0.58},
        {"text": "think", "start": 0.58, "end": 0.80},
        {"text": "you", "start": 0.80, "end": 0.95},
        {"text": "need", "start": 0.95, "end": 1.20},
        {"text": "a", "start": 1.20, "end": 1.28},
        {"text": "camera.", "start": 1.28, "end": 1.75},
    ]
    path = write_srt(demo_cues, "demo")
    print("[STAGE 8b] SUBTITLES")
    print("   wrote:", path)
    print(path.read_text(encoding="utf-8"))
