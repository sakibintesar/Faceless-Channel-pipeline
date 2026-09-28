"""
STAGE 9 — UPLOAD: YouTube Data API v3 + Meta Graph API (dry-run by default).

Zero-dollar cost: both APIs are free. YouTube gives 10k quota units/day
and one upload costs ~1600 units -> ~6 uploads/day default. Meta Graph is
free with a page access token.

DRY-RUN default is deliberate: the demo validates metadata and prints the
exact go-live steps without touching your accounts. Flip dry_run=False
once OAuth tokens are configured:
  YouTube            -> Google Cloud Console -> enable YouTube Data API v3
                        -> OAuth desktop client -> client_secrets.json
  Instagram/Facebook -> Meta for Developers -> app -> Page access token
                        with content_publish permission

Run the dry-run demo:  python -m pipeline.stage_09_upload
"""

from __future__ import annotations

import os
from pathlib import Path

from .common import RENDERED_DIR

YT_TITLE_MAX = 100
YT_DESC_MAX = 5000
YT_TAGS_MAX = 500  # total characters across all tags


def validate_metadata(title: str, description: str, tags: list[str]) -> dict:
    """Policy gate: platform limits + FTC affiliate + AI disclosure."""
    problems = []
    if not title or len(title) > YT_TITLE_MAX:
        problems.append(f"title must be 1-{YT_TITLE_MAX} chars (got {len(title)})")
    if len(description) > YT_DESC_MAX:
        problems.append(f"description too long: {len(description)} > {YT_DESC_MAX}")
    tags_text = ",".join(tags)
    if len(tags_text) > YT_TAGS_MAX:
        problems.append(f"tags too long: {len(tags_text)} > {YT_TAGS_MAX}")
    if "affiliate" not in description.lower():
        problems.append("missing affiliate disclosure (FTC)")
    if not ("ai" in description.lower() and "synthetic" in description.lower()):
        problems.append("missing AI/synthetic content disclosure (platform policy)")
    return {"ok": not problems, "problems": problems}


def upload_youtube(
    video: Path,
    title: str,
    description: str,
    tags: list[str],
    dry_run: bool = True,
) -> dict:
    meta = validate_metadata(title, description, tags)
    if not meta["ok"]:
        return {"ok": False, "stage": "validate", "problems": meta["problems"]}
    if dry_run:
        return {
            "ok": True,
            "mode": "dry-run",
            "platform": "youtube",
            "video": str(video),
            "title": title,
            "tags": tags,
            "go_live": [
                "1. Google Cloud Console -> new project -> enable YouTube Data API v3",
                "2. OAuth consent screen -> External -> add yourself as test user",
                "3. Credentials -> OAuth client ID -> Desktop app -> download JSON",
                "4. pip install google-api-python-client google-auth-oauthlib",
                "5. Set YT_CLIENT_SECRETS env var, then call upload_youtube(dry_run=False)",
            ],
            "quota_note": "an upload costs ~1600 of 10k units/day -> ~6 uploads/day",
        }
    # Live path: import lazily so the dry-run works without google libs
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        return {"ok": False, "reason": "pip install google-api-python-client google-auth-oauthlib"}
    secrets = os.getenv("YT_CLIENT_SECRETS", "")
    flow = InstalledAppFlow.from_client_secrets_file(
        secrets, ["https://www.googleapis.com/auth/youtube.upload"]
    )
    creds = flow.run_local_server(port=0)
    yt = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(video), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   upload progress: {int(status.progress() * 100)}%")
    return {"ok": True, "mode": "live", "video_id": response.get("id"), "platform": "youtube"}


def upload_meta_reels(
    video: Path, caption: str, platform: str = "facebook", dry_run: bool = True
) -> dict:
    """Facebook/Instagram Reels via Graph API (needs a page token)."""
    if dry_run:
        return {
            "ok": True,
            "mode": "dry-run",
            "platform": platform,
            "video": str(video),
            "caption": caption[:80],
            "go_live": [
                "1. Meta for Developers -> create app -> add the product",
                "2. Generate a Page access token with content_publish",
                "3. Set META_PAGE_TOKEN (+ META_PAGE_ID) env vars",
                "4. Reels flow: POST /{page-id}/video_reels (init -> rupload -> publish)",
            ],
        }
    token = os.getenv("META_PAGE_TOKEN", "")
    if not token:
        return {"ok": False, "reason": "set META_PAGE_TOKEN env var"}
    import requests

    page_id = os.getenv("META_PAGE_ID", "me")
    with open(video, "rb") as fh:
        resp = requests.post(
            f"https://graph.facebook.com/v21.0/{page_id}/videos",
            data={"description": caption, "access_token": token},
            files={"source": fh},
            timeout=300,
        )
    resp.raise_for_status()
    return {"ok": True, "mode": "live", "response": resp.json(), "platform": platform}


if __name__ == "__main__":
    video = RENDERED_DIR / "demo.mp4"
    print("[STAGE 9] UPLOAD (dry-run — nothing is published)")
    if not video.exists():
        print("   (no rendered demo video yet — metadata validation only)")
    description = (
        "The honest math on faceless side hustles.\n\n"
        "Disclosure: affiliate links may earn a commission at no cost to you.\n"
        "This video was created with AI-assisted scripting and a synthetic voice."
    )
    r1 = upload_youtube(
        video,
        "5 AI Side Hustles That Actually Pay in 2026",
        description,
        ["faceless youtube", "side hustle", "ai tools"],
    )
    print("   youtube ->", r1["mode"] if r1.get("ok") else f"FAILED: {r1}")
    if r1.get("ok"):
        for step in r1["go_live"]:
            print("     ", step)
        print("     ", r1["quota_note"])
    r2 = upload_meta_reels(video, "Faceless side hustles — full playbook in bio", platform="facebook")
    print("   facebook ->", r2["mode"] if r2.get("ok") else f"FAILED: {r2}")
    if r2.get("ok"):
        for step in r2["go_live"]:
            print("     ", step)
