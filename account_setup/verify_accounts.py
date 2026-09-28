"""
verify_accounts.py — Phase 0/1 verification: what's ready, what's missing.

Checks (in first-dollar order):
  .env keys · core imports · FFmpeg · fonts · SIMURG guard · edge-tts voices ·
  Pexels/Pixabay API ping (if keys) · YouTube OAuth assets · Amazon tag

Usage: python account_setup/verify_accounts.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipelines"))
from common import ENV_FILE, load_env, env, pick_font, guard_text  # noqa: E402

load_env()


def check(name: str, ok: bool, detail: str = "") -> bool:
    mark = "PASS" if ok else "MISS"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    return ok


def main() -> int:
    print("=== ACCOUNT & TOOL VERIFICATION ===")
    total_fail = 0

    print("\n[.env]")
    if not check(".env exists", ENV_FILE.exists(), str(ENV_FILE)):
        print("  → run: python account_setup/create_accounts.py (optional — empty .env still runs dry-run)")
        # don't return 1 — pipeline still works with fallbacks
    for key in ("PEXELS_API_KEY", "PIXABAY_API_KEY", "AMAZON_ASSOCIATE_TAG",
                "LLM_API_BASE", "LLM_MODEL", "META_ACCESS_TOKEN"):
        v = env(key)
        check(key, bool(v), "set" if v else "empty → fallback/stub for this stage")

    print("\n[core tools]")
    try:
        import simurg, edge_tts, moviepy, requests  # noqa: F401
        check("simurg + edge-tts + moviepy + requests", True)
    except ImportError as e:
        total_fail += check("core imports", False, str(e))
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True)
        check("FFmpeg", r.returncode == 0)
    except FileNotFoundError:
        total_fail += check("FFmpeg", False, "not on PATH")
    try:
        check("Windows font for TextClip", True, pick_font())
    except RuntimeError as e:
        total_fail += check("Windows font", False, str(e))

    print("\n[SIMURG guard]")
    g = guard_text("The guard verifies this clean sentence end to end.")
    check("guard clean pass-through", g["state"] == "clean", f"state={g['state']}")
    bad = guard_text(("repeat this loop. " * 60))
    check("guard catches repetition loop", bad["state"] in ("corrupt", "suspect"),
          f"state={bad['state']}")

    print("\n[live APIs]")
    if env("PEXELS_API_KEY"):
        try:
            import requests
            r = requests.get("https://api.pexels.com/v1/curated?per_page=1",
                             headers={"Authorization": env("PEXELS_API_KEY")}, timeout=15)
            check("Pexels API ping", r.status_code == 200, f"HTTP {r.status_code}")
        except Exception as e:
            total_fail += check("Pexels API ping", False, str(e))
    else:
        print("  [SKIP] Pexels — no key (add PEXELS_API_KEY for real B-roll)")
    if env("PIXABAY_API_KEY"):
        try:
            import requests
            r = requests.get("https://pixabay.com/api/",
                             params={"key": env("PIXABAY_API_KEY"), "q": "test",
                                     "per_page": 3}, timeout=15)
            check("Pixabay API ping", r.status_code == 200, f"HTTP {r.status_code}")
        except Exception as e:
            total_fail += check("Pixabay API ping", False, str(e))
    else:
        print("  [SKIP] Pixabay — no key")

    print("\n[YouTube upload assets]")
    secret = ROOT / env("YOUTUBE_CLIENT_SECRET_FILE", "client_secret.json")
    check("client_secret.json", secret.exists(), str(secret))
    check("token.pickle (OAuth done once)", (ROOT / "token.pickle").exists(),
          "run pipeline with --upload to create via browser consent")

    print("\n[affiliate]")
    tag = env("AMAZON_ASSOCIATE_TAG")
    check("AMAZON_ASSOCIATE_TAG", bool(tag),
          tag or "join affiliate-program.amazon.com → W-8BEN → tag into .env")

    print("\n=== SUMMARY ===")
    if total_fail:
        print(f"{total_fail} hard failure(s) — fix before running the pipeline")
        return 1
    print("No hard failures. Empty keys degrade to labeled fallbacks — the "
          "pipeline still runs end-to-end in dry-run mode.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
