"""
common.py — shared utilities for the faceless-content pipelines (Idea #6 first).

Stack (verified installed in ../.venv on 2026-09-27):
  simurg 1.0.4 (guard + websearch) · edge-tts 7.2.8 · moviepy 2.1.2 ·
  requests 2.34.2 · python-dotenv · FFmpeg 9.0 full build (system)

Design philosophy — honest degradation: every stage degrades to a clearly
labeled fallback instead of crashing the run, mirroring SIMURG's abstain
behavior. Nothing ships silently broken.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from dotenv import load_dotenv

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]          # faceless-research/
OUT = ROOT / "output"
ASSETS = ROOT / "assets"
OUT.mkdir(exist_ok=True)
ASSETS.mkdir(exist_ok=True)

ENV_FILE = ROOT / ".env"


def load_env() -> None:
    """Load .env from faceless-research root (never commit .env)."""
    load_dotenv(ENV_FILE)


def env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def has(key: str) -> bool:
    return bool(env(key))


# ── fonts (MoviePy TextClip needs a real font file on Windows) ───────────────
_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arialbd.ttf",   # Arial Bold
    r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\consolab.ttf",
]


def pick_font() -> str:
    for f in _FONT_CANDIDATES:
        if Path(f).exists():
            return f
    raise RuntimeError(
        "No usable Windows font found for TextClip — add a .ttf path to "
        "_FONT_CANDIDATES in common.py"
    )


# ── ffprobe ──────────────────────────────────────────────────────────────────
def ffprobe_duration(path: str | Path) -> float:
    """Media duration in seconds via ffprobe (FFmpeg 9.0 verified)."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


# ── SIMURG guard (the core stage) ────────────────────────────────────────────
def guard_text(text: str, expected_scripts: tuple = ("latin",),
               chunk_size: int = 48) -> dict:
    """Feed a script through the Simurg guard as a simulated token stream.

    Returns {"state": clean|suspect|corrupt, "released": str,
             "reasons": [..], "onset_char": int|None}.
    On CORRUPT the caller must regenerate — nothing past the abort ships.
    """
    from simurg import Simurg  # local import: fast startup for callers that skip this

    s = Simurg(expected_scripts=expected_scripts)
    released = []
    for i in range(0, len(text), chunk_size):
        v = s.feed(text[i:i + chunk_size])
        if v.state == "corrupt":
            return {"state": "corrupt", "released": "".join(released),
                    "reasons": list(v.reasons), "onset_char": v.onset_char}
        released.append(v.released)
    fin = s.finish()
    return {"state": fin.state if fin.state != "clean" else "clean",
            "released": "".join(released) + fin.released,
            "reasons": list(fin.reasons), "onset_char": None}


# ── STUB script generator (swap with GuardedLLM when an LLM endpoint exists) ─
def template_script(product: dict, variant_idx: int = 0) -> str:
    """Deterministic Short script (~50 s, 110-140 words) from product data.

    STUB — clearly labeled. The compliant bit is structural variance: three
    rotating skeletons so consecutive uploads are not templated sameness
    (the July 2025 inauthentic-content policy targets exactly that).
    For real generation wire simurg.integrations.openai_guard.GuardedLLM —
    see pipeline_affiliate_shorts.generate_guarded_script_llm().
    """
    kw = product["keyword"]
    feats = product["features"]
    downs = product["downside"]
    band = product.get("price_band", "the link in the description")
    problem = product["problems"][variant_idx % len(product["problems"])]
    variants = [
        # v0 — hook-first
        f"Most people {problem} — and blame the wrong thing. "
        f"This {kw} fixes it three ways. "
        f"One: {feats[0]}. Two: {feats[1]}. Three: {feats[2]}. "
        f"Honest downside: {downs}. "
        f"If that trade sounds fair, the {band} — link is in the description. "
        f"Subscribe for reviews that say the quiet part out loud.",
        # v1 — question-first
        f"Is the {kw} actually worth it? I tested it so you don't have to. "
        f"The problem it solves: people {problem}. "
        f"What works: {feats[0]}, {feats[1]}, and {feats[2]}. "
        f"What doesn't: {downs} — no reviewer tells you that part. "
        f"Verdict: worth it if the trade sounds fair. "
        f"Current price is in the description — and subscribe for one honest review every week.",
        # v2 — stat-first
        f"Three specs decide whether a {kw} is good — most reviews skip two of them. "
        f"Here: {feats[0]}. Then {feats[1]}. Then {feats[2]}. "
        f"The catch most buyers hit: they {problem}. "
        f"And the honest downside: {downs}. "
        f"That's the whole trade — if it sounds fair, the {band}, link in the description. "
        f"Follow for the specs other reviewers leave out.",
    ]
    return variants[variant_idx % len(variants)]


# ── fact-check helpers ───────────────────────────────────────────────────────
_NUM = re.compile(r"\d")


def claims_in(text: str) -> list[str]:
    """Sentences containing numbers/specs — the claims worth grounding."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text)
            if _NUM.search(s) and len(s.strip()) > 8]


def ground_claim(claim: str) -> dict:
    """simurg.websearch.ground — attested / thin / no_record (honest abstain)."""
    from simurg.websearch import ground
    return ground(claim)


# ── TTS (edge-tts, free, no API key) ─────────────────────────────────────────
def tts_with_boundaries(text: str, out_mp3: str | Path,
                        voice: str = "en-US-AriaNeural") -> tuple[Path, list[dict]]:
    """Synthesize narration AND capture word-boundary timings in one stream_sync.

    Returns (mp3_path, boundaries) where each boundary is
    {"offset": sec, "duration": sec, "text": word} — used for word-group captions.
    """
    import edge_tts

    comm = edge_tts.Communicate(text, voice, boundary="WordBoundary")
    audio = bytearray()
    boundaries: list[dict] = []
    for chunk in comm.stream_sync():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            boundaries.append({"offset": chunk["offset"] / 1e7,
                               "duration": chunk["duration"] / 1e7,
                               "text": chunk["text"]})
    if not audio:
        raise RuntimeError("edge-tts produced no audio (network to speech "
                           "servers required) — check connectivity")
    out = Path(out_mp3)
    out.write_bytes(bytes(audio))
    return out, boundaries


# ── B-roll (Pexels; graceful fallback to solid scenes) ───────────────────────
def pexels_broll(query: str, count: int = 5) -> list[Path]:
    """Download vertical B-roll clips from Pexels. [] when no key or on error."""
    import requests

    key = env("PEXELS_API_KEY")
    if not key:
        return []
    try:
        r = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": key},
            params={"query": query, "orientation": "portrait",
                    "per_page": count, "size": "large"},
            timeout=30,
        )
        r.raise_for_status()
        paths: list[Path] = []
        for i, v in enumerate(r.json().get("videos", [])[:count]):
            files = [f for f in v.get("video_files", []) if f.get("width", 0) >= 720]
            if not files:
                continue
            best = max(files, key=lambda f: f["width"])
            p = ASSETS / f"broll_{re.sub(r'[^a-z0-9]+', '_', query.lower())}_{i}.mp4"
            with requests.get(best["link"], stream=True, timeout=60) as dl:
                dl.raise_for_status()
                with open(p, "wb") as fh:
                    for ch in dl.iter_content(1 << 15):
                        fh.write(ch)
            paths.append(p)
        return paths
    except Exception as e:  # honest degradation, never crash the run
        print(f"    [b-roll] Pexels unavailable ({type(e).__name__}) → solid-scene fallback")
        return []


_SCENE_PALETTE = [(15, 23, 42), (30, 27, 75), (6, 78, 59), (76, 29, 66)]


def solid_scenes(n: int, dur_total: float, size=(1080, 1920)) -> list:
    """Solid-color scene clips (no external assets needed) — labeled fallback."""
    from moviepy import ColorClip

    d = dur_total / max(1, n)
    return [ColorClip(size=size, color=_SCENE_PALETTE[i % len(_SCENE_PALETTE)]
                      ).with_duration(d) for i in range(n)]


# ── assembly (MoviePy 2.1.2 + FFmpeg 9.0) ────────────────────────────────────
def _broll_clip(path: Path, dur: float, size=(1080, 1920)):
    """One B-roll clip cropped/resized to 9:16 for a fixed duration."""
    from moviepy import VideoFileClip

    clip = VideoFileClip(str(path))
    src_dur = clip.duration or dur
    c = clip.subclipped(0, min(dur, src_dur))
    c = c.resized(height=size[1])
    if c.w > size[0]:  # center-crop to exact 9:16 width
        c = c.cropped(x_center=c.w / 2, width=size[0])
    return c.with_duration(dur)


def _word_group_captions(boundaries: list[dict], words_per: int = 5) -> list:
    """Group word timings into caption clips (Shorts-style, bottom-third)."""
    from moviepy import TextClip

    font = pick_font()
    groups, cur = [], []
    for b in boundaries:
        cur.append(b)
        if len(cur) >= words_per or b["text"].endswith((".", "!", "?")):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    clips = []
    for g in groups:
        t0, t1 = g[0]["offset"], g[-1]["offset"] + g[-1]["duration"]
        txt = " ".join(w["text"] for w in g)
        clip = TextClip(font=font, text=txt, font_size=52, color="white",
                        stroke_color="black", stroke_width=2,
                        size=(980, None), method="caption", text_align="center"
                        ).with_duration(max(0.4, t1 - t0)
                        ).with_position(("center", 1450))
        clips.append((t0, clip))
    return clips

def assemble_short(audio_path: Path, boundaries: list[dict],
                   broll: list[Path], out_path: Path,
                   hook_text: str) -> Path:
    """Assemble the 9:16 Short: scenes/B-roll + narration + captions + hook."""
    from moviepy import (AudioFileClip, CompositeVideoClip, TextClip,
                         concatenate_videoclips)

    audio = AudioFileClip(str(audio_path))
    dur = audio.duration or ffprobe_duration(audio_path)

    if broll:
        seg = dur / len(broll)
        scenes = [_broll_clip(p, seg) for p in broll]
        base = concatenate_videoclips(scenes).with_duration(dur)
    else:
        base = concatenate_videoclips(solid_scenes(5, dur)).with_duration(dur)

    base = base.with_audio(audio)

    parts = [base]
    for t0, cap in _word_group_captions(boundaries):
        parts.append(cap.with_start(t0))

    hook = TextClip(font=pick_font(), text=hook_text, font_size=64,
                    color="yellow", stroke_color="black", stroke_width=3,
                    size=(980, None), method="caption", text_align="center"
                    ).with_duration(min(3.0, dur)).with_position(("center", 260))
    parts.append(hook)

    final = CompositeVideoClip(parts, size=(1080, 1920))
    final.write_videofile(str(out_path), fps=30, codec="libx264",
                          audio_codec="aac", preset="fast",
                          threads=os.cpu_count() or 2, logger=None)
    return out_path


# ── SEO pack + affiliate link ────────────────────────────────────────────────
def seo_pack(script: str, product: dict) -> dict:
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    kw = product["keyword"]
    return {
        "title": f"Honest Review: {kw.title()} — Worth It? (Tested)",
        "description_first_line": sents[0] if sents else "",
        "tags": [kw, f"{kw} review", "honest review", product["niche"],
                 "shorts", "review"],
        "hook_first_3s": sents[0] if sents else "",
    }


def affiliate_link(asin: str) -> tuple[str, str]:
    """Amazon Associates link from the Associate Tag (tag= attribution).

    Returns (link, note). Demo ASINs are flagged honestly.
    """
    tag = env("AMAZON_ASSOCIATE_TAG")
    note = ""
    if asin.startswith("B0DEMO"):
        note = "DEMO ASIN — swap PRODUCTS in pipeline_affiliate_shorts.py with real ones"
    if not tag:
        note = (note + " | " if note else "") + \
            "AMAZON_ASSOCIATE_TAG not set — set it in .env after joining Amazon Associates"
    return f"https://www.amazon.com/dp/{asin}?tag={tag or 'YOURTAG-20'}", note



