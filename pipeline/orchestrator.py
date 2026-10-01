"""
ORCHESTRATOR — run the full SIMURG-guarded pipeline end-to-end.

Demo mode needs NO API keys and costs $0:
  1. RESEARCH   simurg.websearch (free bundled key) w/ seed fallback
  2. GUARD      SIMURG zero-leak monitor (demo-corrupt flag shows the cut)
  3. SCRIPT     DemoLLM (or your OpenAI-compatible endpoint) -> guard
  4. FACT-CHECK ground() honest-abstention verdicts on script claims
  5. SEO PACK   platform pack -> guard -> seo_pack.json
  6. VOICE      edge-tts (free, keyless) + word-level caption cues
  7. VISUALS    Pexels/Pixabay (free keys) + guarded AI prompts
  8. ASSEMBLE   moviepy (MIT) render, ffmpeg fallback
  8b.SUBTITLES  cues -> SRT (+ optional ffsubsync)
  9. UPLOAD     dry-run metadata gate (nothing is published)
  10.REPORT     analytics/run_<timestamp>.json

Run:
  python -m pipeline.orchestrator
  python -m pipeline.orchestrator --topic "5 AI side hustles" --platform youtube
  python -m pipeline.orchestrator --demo-corrupt   # show the zero-leak cut
  python -m pipeline.orchestrator --no-render      # skip the video render
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .common import ANALYTICS_DIR, RENDERED_DIR, ensure_dirs, save_json, slugify, timestamp
from .stage_01_research import research_topics
from .stage_02_script import build_script
from .stage_04_factcheck import filter_script
from .stage_05_seo import build_seo_pack
from .stage_06_tts import synthesize_narration
from .stage_07_visuals import collect_visuals
from .stage_08_assemble import assemble_vertical
from .stage_08b_subtitles import write_srt


def demo_corrupt_stream() -> str:
    """A repetition loop that trips the sentinel — for the zero-leak demo."""
    return "This side hustle makes money fast, and this side hustle makes money fast, " * 30


def run_pipeline(
    topic: str | None = None,
    platform: str = "youtube",
    render: bool = True,
    demo_corrupt: bool = False,
) -> dict:
    ensure_dirs()
    topic = topic or "5 AI side hustles that actually pay in 2026"
    slug = slugify(topic)
    report: dict = {"topic": topic, "platform": platform, "timestamp": timestamp(), "stages": {}}

    print("=" * 64)
    print("FACELESS PIPELINE — SIMURG-GUARDED, $0 COST")
    print("=" * 64)

    # ---- Stage 1: RESEARCH -------------------------------------------------
    print("\n[STAGE 1] RESEARCH — simurg.websearch (free bundled key)")
    research = research_topics(topic)
    print("   source:", research["source"])
    for i, r in enumerate(research["results"][:3], 1):
        print(f"   {i}. {r.get('title', '')[:70]}")
    report["stages"]["research"] = {"source": research["source"], "count": research["count"]}

    # ---- Stages 2/3: SCRIPT + GUARD ----------------------------------------
    print("\n[STAGE 2/3] SCRIPT + GUARD — SIMURG zero-leak monitor")
    if demo_corrupt:
        from .guard import GuardedLLM

        corrupt = GuardedLLM().guard_text(demo_corrupt_stream())
        print("   injected loop ->", corrupt.summary())
        report["stages"]["guard_demo"] = {
            "state": corrupt.state,
            "onset_char": corrupt.onset_char,
            "reasons": corrupt.reasons,
        }
    meta = build_script(topic)
    print("   provider:", meta["provider"])
    print("   guard   :", meta["guard"]["summary"])
    script_text = Path(meta["script_path"]).read_text(encoding="utf-8")
    report["stages"]["script"] = {
        "provider": meta["provider"],
        "guard": meta["guard"]["state"],
        "chars": meta["chars"],
    }

    # ---- Stage 4: FACT-CHECK ------------------------------------------------
    print("\n[STAGE 4] FACT-CHECK — ground() honest abstention")
    factcheck = filter_script(script_text, slug=slug)
    print(
        f"   claims={factcheck['claims_checked']} "
        f"attested={factcheck['attested']} thin={factcheck['thin']} "
        f"no_record={factcheck['no_record']}"
    )
    report["stages"]["factcheck"] = {
        k: factcheck[k] for k in ("claims_checked", "attested", "thin", "no_record")
    }

    # ---- Stage 5: SEO PACK ---------------------------------------------------
    print("\n[STAGE 5] SEO PACK — platform skills distilled (MIT)")
    seo = build_seo_pack(topic, platform)
    headline = str(seo.get("title_primary") or seo.get("caption") or seo.get("post") or topic)
    print("   headline:", headline[:70])
    report["stages"]["seo"] = {"platform": platform, "fields": list(seo.keys())}

    # ---- Stage 6: VOICE ---------------------------------------------------------
    print("\n[STAGE 6] VOICE — edge-tts (free, keyless)")
    tts = synthesize_narration(script_text, platform=platform)
    if tts["ok"]:
        print("   voice   :", tts["voice"])
        print("   audio   :", tts["audio_path"])
        print("   duration:", tts["duration_sec"], "s |", tts["words"], "words")
    else:
        print("   SKIPPED :", tts.get("error", tts.get("guard", "offline")))
    report["stages"]["tts"] = {
        "ok": tts["ok"],
        "voice": tts.get("voice"),
        "duration_sec": tts.get("duration_sec"),
    }

    # ---- Stage 7: VISUALS ---------------------------------------------------------
    print("\n[STAGE 7] VISUALS — Pexels/Pixabay (free keys) + guarded AI prompts")
    visuals = collect_visuals(topic)
    print(
        "   stock:", visuals["stock_items"],
        "| downloaded:", len(visuals["downloaded"]),
        "| ai prompts:", len(visuals["ai_prompts"]),
    )
    report["stages"]["visuals"] = {
        "stock_items": visuals["stock_items"],
        "downloaded": len(visuals["downloaded"]),
        "ai_prompts": len(visuals["ai_prompts"]),
    }

    # ---- Stage 8: ASSEMBLE -----------------------------------------------------------
    if render and tts["ok"]:
        print("\n[STAGE 8] ASSEMBLE — moviepy (MIT) render")
        visual_paths = [Path(p) for p in visuals["downloaded"]][:5]
        result = assemble_vertical(visual_paths, Path(tts["audio_path"]), headline, slug=slug)
        if result.get("ok"):
            print(
                "   rendered:", result["out"], "|",
                result.get("engine", ""), "|",
                result.get("duration_sec"), "s",
            )
        else:
            print("   render failed:", result)
        report["stages"]["assemble"] = result

    # ---- Stage 8b: SUBTITLES ------------------------------------------------------------
    if tts["ok"] and tts.get("cues"):
        print("\n[STAGE 8b] SUBTITLES — word-accurate SRT from edge-tts cues")
        srt_path = write_srt(tts["cues"], slug)
        print("   wrote:", srt_path)
        report["stages"]["subtitles"] = {"srt": str(srt_path)}

    # ---- Stage 9: UPLOAD (dry-run gate) ---------------------------------------------------
    print("\n[STAGE 9] UPLOAD — dry-run gate (nothing is published)")
    from .stage_09_upload import upload_youtube

    # Build description with all required disclosures
    base_desc = seo.get("description") or (
        "Disclosure: affiliate links may earn a commission at no cost to you. "
        "This video was created with AI-assisted scripting and a synthetic voice."
    )
    # Ensure earnings disclaimer is present (FTC guidance)
    earnings_disclaimer = "Results shown are not typical; your results will vary. Not financial advice — do your own research."
    if "results" not in base_desc.lower() or ("vary" not in base_desc.lower() and "typical" not in base_desc.lower()):
        base_desc += "\n\n" + earnings_disclaimer
    description = base_desc
    up = upload_youtube(
        RENDERED_DIR / f"{slug}.mp4",
        headline[:100],
        description,
        seo.get("tags", ["faceless"]),
    )
    print("   youtube ->", up["mode"] if up.get("ok") else f"FAILED: {up.get('problems', up)}")
    report["stages"]["upload"] = {"mode": up.get("mode"), "ok": up.get("ok")}

    # ---- REPORT ---------------------------------------------------------------------------
    report_path = save_json(ANALYTICS_DIR / f"run_{timestamp()}.json", report)
    print("\n" + "=" * 64)
    print("PIPELINE COMPLETE — report saved:")
    print("  ", report_path)
    print("=" * 64)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="SIMURG-guarded faceless pipeline")
    parser.add_argument("--topic", default=None, help="video topic")
    parser.add_argument(
        "--platform", default="youtube",
        choices=["youtube", "instagram", "tiktok", "facebook"],
    )
    parser.add_argument("--no-render", dest="render", action="store_false")
    parser.add_argument(
        "--demo-corrupt", action="store_true",
        help="inject a repetition loop to show the zero-leak cut",
    )
    args = parser.parse_args()
    run_pipeline(
        topic=args.topic, platform=args.platform, render=args.render, demo_corrupt=args.demo_corrupt
    )


if __name__ == "__main__":
    main()

