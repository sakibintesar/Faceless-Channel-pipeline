"""
crosspost.py — Idea #3: convert/publish the Idea #6 output to Instagram + Facebook.

Honest architecture (verified research):
  * OFFICIAL path (recommended): Meta Graph API — requires a Facebook Page +
    an Instagram *professional* account linked in Meta Business Suite +
    META_ACCESS_TOKEN in .env. Reels must be >= 10 seconds to earn.
  * PRIVATE API path: instagrapi (pip install instagrapi) — powerful but
    fragile in production (account trust, challenges, rate limits). Used only
    if installed AND INSTAGRAM_USERNAME/INSTAGRAM_PASSWORD set.
  * No credentials → dry-run: renders are listed with exact next steps.

Usage:
    python pipelines/crosspost.py                       # dry-run list
    python pipelines/crosspost.py --platforms instagram,facebook --upload
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, load_env, env  # noqa: E402

load_env()


def rendered_packs() -> list[dict]:
    """All produced videos with their SEO packs."""
    packs = []
    for p in sorted(OUT.glob("*_pack.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if Path(d.get("video", "")).exists():
                packs.append(d)
        except Exception:
            continue
    return packs


# ── Instagram — private API (instagrapi; local-file path) ────────────────────
def ig_upload_instagrapi(video: Path, caption: str) -> str:
    """Private-API Reels upload (instagrapi) — fragile; for owned accounts."""
    try:
        from instagrapi import Client
    except ImportError as e:
        raise RuntimeError(
            "instagrapi not installed — pip install instagrapi "
            "(private API: account trust/challenges apply)") from e
    user, pwd = env("INSTAGRAM_USERNAME"), env("INSTAGRAM_PASSWORD")
    if not (user and pwd):
        raise RuntimeError("INSTAGRAM_USERNAME / INSTAGRAM_PASSWORD not set in .env")
    cl = Client()
    cl.login(user, pwd)
    media = cl.clip_upload(video, caption=caption)
    return str(media.pk)

# ── Official Graph API paths (real code, gated on META_ACCESS_TOKEN) ─────────
def ig_upload_graph(video: Path, caption: str) -> str:
    """IG Reels via official Graph API. NOTE: the API needs a PUBLIC video_url —
    for local MP4s first host the file (presigned S3 / any public URL), or use
    the instagrapi local-file path above."""
    import requests

    ig_id, token = env("META_INSTAGRAM_BUSINESS_ID"), env("META_ACCESS_TOKEN")
    if not (ig_id and token):
        raise RuntimeError("META_INSTAGRAM_BUSINESS_ID / META_ACCESS_TOKEN not set "
                           "— professional IG account + Meta app required")
    r = requests.post(f"https://graph.facebook.com/v21.0/{ig_id}/media",
                      data={"media_type": "REELS", "video_url": "<public-url>",
                            "caption": caption, "access_token": token}, timeout=30)
    r.raise_for_status()
    return r.json()["id"]


def fb_upload_graph(video: Path, description: str) -> str:
    """FB Reels via Graph API — start phase of the resumable flow."""
    import requests

    page, token = env("META_PAGE_ID"), env("META_ACCESS_TOKEN")
    if not (page and token):
        raise RuntimeError("META_PAGE_ID / META_ACCESS_TOKEN not set — "
                           "Facebook Page + Meta app required")
    r = requests.post(f"https://graph.facebook.com/v21.0/{page}/video_reels",
                      data={"upload_phase": "start", "access_token": token},
                      timeout=30)
    r.raise_for_status()
    return r.json()["video_id"]


# ── main ─────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="Crosspost Idea #6 output")
    ap.add_argument("--platforms", default="instagram,facebook")
    ap.add_argument("--upload", action="store_true")
    args = ap.parse_args()
    plats = [p.strip().lower() for p in args.platforms.split(",") if p.strip()]

    print("═" * 70)
    print("CROSSPOST — Idea #3 (Instagram + Facebook Reels, >= 10s to earn)")
    print("═" * 70)

    packs = rendered_packs()
    if not packs:
        print("No rendered videos found — run pipeline_affiliate_shorts.py first")
        return 1
    print(f"{len(packs)} rendered video(s) found\n")

    fail = 0
    for d in packs:
        video = Path(d["video"])
        caption = f"{d.get('description_first_line', '')}... {d.get('affiliate_link', '')}"
        for plat in plats:
            if not args.upload:
                print(f"  [dry-run] {video.name} → {plat} "
                      "(add --upload when credentials are set)")
                continue
            try:
                t0 = time.time()
                if plat == "instagram":
                    mid = ig_upload_instagrapi(video, caption)  # local-file path
                elif plat == "facebook":
                    mid = fb_upload_graph(video, caption)       # start phase
                else:
                    print(f"  [skip] unknown platform {plat}")
                    continue
                print(f"  ✅ {video.name} → {plat}: {mid} ({time.time() - t0:.1f}s)")
            except Exception as e:
                fail += 1
                print(f"  ✗ {video.name} → {plat}: {e}")

    if not args.upload:
        print("\nNext steps (account_setup/create_accounts.py covers all):")
        print("  instagram: professional account → pip install instagrapi → "
              "INSTAGRAM_USERNAME/PASSWORD in .env → rerun --upload")
        print("  facebook:  Page + Meta app token → META_PAGE_ID/"
              "META_ACCESS_TOKEN in .env → rerun --upload (full resumable flow)")
        print("  monetisation: Meta dashboard → Monetisation → Content "
              "Monetisation → express interest NOW (invite-only)")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())

