"""
STAGE 7 — VISUALS: stock footage/images via Pexels & Pixabay (free keys).

Zero-dollar cost: both APIs have free tiers — get keys in 2 minutes:
  Pexels  -> https://www.pexels.com/api/     (env: PEXELS_API_KEY)
  Pixabay -> https://pixabay.com/api/docs/   (env: PIXABAY_API_KEY)
With no keys configured, this stage returns [] + prints instructions, and
the assembler falls back to an ffmpeg-drawn background so the demo still
renders at $0.

SIMURG guard: AI image-prompt generation passes through the guard, so a
drifted prompt never reaches a generator.

Run the live demo (set a key first):  python -m pipeline.stage_07_visuals
"""

from __future__ import annotations

import os
from pathlib import Path

import requests

from .common import VISUALS_DIR, slugify
from .guard import GuardedLLM

PEXELS_SEARCH = "https://api.pexels.com/v1/search"
PEXELS_VIDEO_SEARCH = "https://api.pexels.com/videos/search"
PIXABAY_SEARCH = "https://pixabay.com/api/"


def search_pexels(query: str, per_page: int = 5, videos: bool = False) -> list[dict]:
    key = os.getenv("PEXELS_API_KEY", "")
    if not key:
        print("   [skip] set PEXELS_API_KEY (free at https://www.pexels.com/api/)")
        return []
    url = PEXELS_VIDEO_SEARCH if videos else PEXELS_SEARCH
    try:
        resp = requests.get(
            url,
            headers={"Authorization": key},
            params={"query": query, "per_page": per_page, "orientation": "portrait"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if videos:
            return [
                {
                    "url": v["video_files"][0]["link"],
                    "type": "video",
                    "credit": v.get("user", {}).get("name", ""),
                }
                for v in data.get("videos", [])
            ]
        return [
            {
                "url": p["src"]["portrait"],
                "type": "image",
                "credit": p.get("photographer", ""),
            }
            for p in data.get("photos", [])
        ]
    except Exception as exc:
        print(f"   [warn] pexels failed: {exc}")
        return []


def search_pixabay(query: str, per_page: int = 5) -> list[dict]:
    key = os.getenv("PIXABAY_API_KEY", "")
    if not key:
        print("   [skip] set PIXABAY_API_KEY (free at https://pixabay.com/api/docs/)")
        return []
    try:
        resp = requests.get(
            PIXABAY_SEARCH,
            params={
                "key": key,
                "q": query,
                "per_page": per_page,
                "orientation": "vertical",
                "image_type": "photo",
            },
            timeout=15,
        )
        resp.raise_for_status()
        return [
            {"url": hit["largeImageURL"], "type": "image", "credit": hit.get("user", "")}
            for hit in resp.json().get("hits", [])
        ]
    except Exception as exc:
        print(f"   [warn] pixabay failed: {exc}")
        return []


def download_assets(items: list[dict], out_dir: Path | None = None) -> list[Path]:
    """Download stock assets to content/visuals/<dir>."""
    if not items:
        return []
    out_dir = out_dir or VISUALS_DIR / "session"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i, item in enumerate(items):
        try:
            resp = requests.get(item["url"], timeout=30)
            resp.raise_for_status()
            ext = ".mp4" if item.get("type") == "video" else ".jpg"
            path = out_dir / f"asset_{i:02d}{ext}"
            path.write_bytes(resp.content)
            paths.append(path)
        except Exception as exc:
            print(f"   [warn] download {i} failed: {exc}")
    return paths


def ai_image_prompts(topic: str, n: int = 3) -> list[str]:
    """Prompts for free generators (Copilot/Bing, local Stable Diffusion).
    Guarded so a drifted prompt never reaches a generator."""
    guard = GuardedLLM()
    templates = [
        f"Cinematic vertical 9:16 illustration about {topic}, dark navy "
        "background, bold empty space at top for text, moody rim lighting, "
        "no text, no faces",
        f"Minimal flat-design scene symbolizing {topic}, teal and orange "
        "palette, vertical composition, generous negative space, no words",
        f"Abstract 3D render representing {topic}, glossy shapes on charcoal "
        "gradient, vertical 9:16, studio lighting, no text overlays",
    ]
    out = []
    for t in templates[:n]:
        r = guard.guard_text(t)
        if r.ok:
            out.append(r.text)
    return out


def collect_visuals(topic: str, per_page: int = 5) -> dict:
    """Try Pexels then Pixabay; return assets + AI-prompt fallback."""
    items = search_pexels(topic, per_page=per_page)
    if not items:
        items = search_pixabay(topic, per_page=per_page)
    paths = download_assets(items)
    prompts = ai_image_prompts(topic)
    return {
        "query": topic,
        "stock_items": len(items),
        "downloaded": [str(p) for p in paths],
        "ai_prompts": prompts,
    }


if __name__ == "__main__":
    report = collect_visuals("laptop side hustle workspace")
    print("[STAGE 7] VISUALS")
    print("   stock items :", report["stock_items"])
    print("   downloaded  :", len(report["downloaded"]))
    print("   ai prompts  :", len(report["ai_prompts"]))
    for p in report["ai_prompts"]:
        print("     -", p[:80])
