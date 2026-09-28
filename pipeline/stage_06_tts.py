"""
STAGE 6 — VOICE: narration audio via edge-tts (free, keyless).

Zero-dollar cost: edge-tts uses Microsoft Edge's online voices with no API
key and no paid tier. We capture WordBoundary events during synthesis to
get FREE word-level caption timings (stage 8b) — no transcription service.

SIMURG guard: the narration text is guarded BEFORE synthesis (stage 3
zero-leak) — corrupt text never becomes audio.

Verified API (edge-tts 7.2.8):
    import edge_tts
    comm = edge_tts.Communicate(text, voice)
    async for chunk in comm.stream():
        chunk["type"] == "audio"        -> chunk["data"] bytes
        chunk["type"] == "WordBoundary" -> chunk["offset"] / "duration"
                                           (100-ns ticks), chunk["text"]

Run the live demo:  python -m pipeline.stage_06_tts
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from .common import AUDIO_DIR, load_yaml, slugify
from .guard import GuardedLLM

VOICE_PRESETS = {
    "youtube": "en-US-ChristopherNeural",
    "instagram": "en-US-JennyNeural",
    "tiktok": "en-US-AriaNeural",
    "facebook": "en-US-GuyNeural",
    "bilibili": "zh-CN-YunxiNeural",
}

TICKS_PER_SEC = 10_000_000  # WordBoundary offsets are 100-ns ticks


def pick_voice(platform: str) -> str:
    """Config override (config/voices.yaml) beats the built-in preset."""
    cfg = load_yaml("voices.yaml")
    voices = cfg.get("voices", {}) if isinstance(cfg, dict) else {}
    return voices.get(platform) or VOICE_PRESETS.get(platform, "en-US-GuyNeural")


async def _synthesize(text: str, voice: str, out_path: Path) -> list[dict]:
    import edge_tts

    # NOTE (edge-tts 7.2.8): boundary defaults to SentenceBoundary —
    # pass WordBoundary explicitly to get free word-level caption cues.
    comm = edge_tts.Communicate(text, voice, boundary="WordBoundary")
    cues: list[dict] = []
    audio = bytearray()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            cues.append(
                {
                    "text": chunk["text"],
                    "start": chunk["offset"] / TICKS_PER_SEC,
                    "end": (chunk["offset"] + chunk["duration"]) / TICKS_PER_SEC,
                }
            )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(bytes(audio))
    return cues


def synthesize_narration(
    text: str,
    platform: str = "youtube",
    voice: str | None = None,
    guarded: bool = True,
) -> dict:
    """Guard the narration, then synthesize with word-level caption cues."""
    guard = GuardedLLM()
    guard_summary = "skipped"
    if guarded:
        result = guard.guard_text(text)
        guard_summary = result.summary()
        if not result.ok:
            return {"ok": False, "guard": guard_summary, "audio_path": None}
        text = result.text

    voice = voice or pick_voice(platform)
    out_path = AUDIO_DIR / f"{slugify(text[:40]) or 'narration'}.mp3"
    try:
        cues = asyncio.run(_synthesize(text, voice, out_path))
    except Exception as exc:  # offline / service hiccup — honest degradation
        return {"ok": False, "guard": guard_summary, "error": str(exc), "audio_path": None}

    return {
        "ok": True,
        "voice": voice,
        "audio_path": str(out_path),
        "duration_sec": round(cues[-1]["end"], 2) if cues else None,
        "words": len(cues),
        "cues": cues,
        "guard": guard_summary,
    }


if __name__ == "__main__":
    demo = (
        "Most people think you need a camera to make money online. You do not. "
        "Faceless channels run on three free tools, and production cost stays near zero."
    )
    out = synthesize_narration(demo, platform="youtube")
    print("[STAGE 6] VOICE (edge-tts, free, keyless)")
    if out["ok"]:
        print("   voice   :", out["voice"])
        print("   audio   :", out["audio_path"])
        print("   duration:", out["duration_sec"], "s |", out["words"], "words")
        print("   guard   :", out["guard"])
    else:
        print("   FAILED  :", out.get("guard"), out.get("error", ""))
