"""
pipeline_affiliate_shorts.py — Idea #6 END-TO-END: affiliate product-review Shorts.

The fastest credible path to the first dollar (no platform threshold).

Pipeline (all stages degrade to honestly-labeled fallbacks):
  [1 RESEARCH]    simurg.websearch.search — live, bundled TinyFish key
  [2 SCRIPT]      template stub (labeled) OR GuardedLLM if LLM_API_* in .env
  [3 GUARD ★]     Simurg chunk-feed — CORRUPT aborts regenerate, zero-leak
  [4 FACT-CHECK]  simurg.websearch.ground — attested / thin / no_record
  [5 TTS]         edge-tts 7.2.8 (free) + word-boundary capture
  [6 B-ROLL]      Pexels if PEXELS_API_KEY, else solid-scene fallback
  [7 ASSEMBLE]    MoviePy 2.1.2 + FFmpeg 9.0 → 1080x1920 MP4
  [8 UPLOAD]      YouTube Data API v3 with --upload (OAuth) — else dry-run note
  [9 SEO+LINK]    SEO pack + Amazon Associates link → per-video JSON

Usage:
    python pipeline_affiliate_shorts.py                 # 3 products, dry-run
    python pipeline_affiliate_shorts.py --products 3
    python pipeline_affiliate_shorts.py --upload        # attempt real upload
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ROOT, OUT, load_env, env, has, guard_text, template_script,
                    claims_in, ground_claim, tts_with_boundaries, pexels_broll,
                    assemble_short, seo_pack, affiliate_link, ffprobe_duration)

load_env()

# ── PRODUCTS — swap with real ones after joining Amazon Associates ──────────
# Demo ASINs are flagged honestly by affiliate_link(); features/downsides are
# the honest-review skeleton each script is built from.
PRODUCTS = [
    {
        "asin": "B0DEMO0001", "keyword": "wireless earbuds", "niche": "tech",
        "features": ["active noise cancelling that actually silences a bus",
                     "36-hour total battery with the case",
                     "USB-C fast charge — 10 minutes buys an hour"],
        "downside": "the touch controls take a week of muscle memory",
        "problems": ["they die halfway through the commute",
                     "engine noise drowns out every podcast"],
        "price_band": "pair is under $50 and linked in the description",
    },
    {
        "asin": "B0DEMO0002", "keyword": "ergonomic office chair", "niche": "home office",
        "features": ["adjustable lumbar support you can tune daily",
                     "4D armrests that fit any desk height",
                     "breathable mesh for 8-hour sessions"],
        "downside": "assembly takes 30 minutes and the instructions are vague",
        "problems": ["their lower back gives out by 3 PM",
                     "cheap chairs squeak within two months"],
        "price_band": "current price is linked in the description",
    },
    {
        "asin": "B0DEMO0003", "keyword": "smart water bottle", "niche": "health",
        "features": ["glow reminders that track your intake",
                     "keeps drinks cold for 24 hours",
                     "self-cleaning UV cap"],
        "downside": "the app account is required for reminders",
        "problems": ["they drink half of what they should daily",
                     "plain bottles are forgotten by noon"],
        "price_band": "price is in the description",
    },
]


# ── [1] RESEARCH — live via simurg.websearch ─────────────────────────────────
def research_product(keyword: str) -> list[dict]:
    query = f"{keyword} review 2026 problems features worth it"
    try:
        results = search(query, k=6) if (search := _websearch_search()) else []
    except Exception as e:
        print(f"    [research] websearch unavailable ({type(e).__name__}) → proceeding unaided")
        return []
    return results


def _websearch_search():
    from simurg.websearch import search
    return search


# ── [2+3] SCRIPT — guarded; stub or real LLM ─────────────────────────────────
def make_script(product: dict, research: list[dict], idx: int) -> tuple[str, dict]:
    """Return (script, guard_info). Rotates template variants; on CORRUPT regenerate."""
    for attempt in range(3):
        script = template_script(product, variant_idx=idx + attempt)
        g = guard_text(script)
        if g["state"] != "corrupt":
            return g["released"], g
        print(f"    [guard] CORRUPT at char {g['onset_char']}: {g['reasons']}"
              f" → regenerating (attempt {attempt + 1})")
    raise RuntimeError("script corrupt after 3 attempts — swapping the template "
                       "stub for GuardedLLM is the real fix")


def generate_guarded_script_llm(product: dict, research: list[dict]) -> str:
    """REAL generation path — requires LLM_API_BASE + LLM_MODEL (+ key) in .env.

    Uses simurg.integrations.openai_guard.GuardedLLM: heal-then-retry ladder,
    zero-leak protocol. GuardResult.text is the accepted clean answer.
    """
    from simurg.integrations.openai_guard import GuardedLLM

    base, model = env("LLM_API_BASE"), env("LLM_MODEL")
    if not (base and model):
        raise RuntimeError("LLM_API_BASE / LLM_MODEL not set in .env — "
                           "template stub is in use")
    llm = GuardedLLM(base_url=base, model=model, api_key=env("LLM_API_KEY", "EMPTY"),
                     expected_scripts=("latin",))
    prompt = (
        f"Write a 50-second faceless YouTube Short honestly reviewing "
        f"{product['keyword']}. Structure: hook (0-3s), problem, 2-3 specific "
        f"features, one honest downside, CTA (link in description). "
        f"Conversational, no hype, max 140 words. Research context: "
        f"{json.dumps([r.get('snippet', '') for r in research[:3]])}"
    )
    result = llm.chat([{"role": "user", "content": prompt}])
    if not result.ok:
        raise RuntimeError(f"guarded LLM failed all rungs: {result.verdict}")
    return result.text

# ── [4] FACT-CHECK — simurg.ground on every numeric claim ────────────────────
def fact_check(script: str) -> dict:
    claims = claims_in(script)
    out: dict[str, dict] = {}
    for c in claims:
        try:
            out[c] = ground_claim(c)
        except Exception as e:
            out[c] = {"verdict": "no_record", "error": str(e)}
    return out


# ── [5+6+7] TTS → B-roll → assemble ──────────────────────────────────────────
def produce_video(script: str, product: dict, idx: int) -> tuple[Path, list[dict], str]:
    """TTS + B-roll + assembly. Returns (video_path, boundaries, broll_note)."""
    asin = product["asin"]
    mp3, bounds = tts_with_boundaries(script, OUT / f"{asin}_voice.mp3")
    dur = ffprobe_duration(mp3)
    print(f"    [tts] {dur:.1f}s, {len(bounds)} word boundaries ✅")

    broll = pexels_broll(f"{product['keyword']} close up", count=5)
    note = "Pexels B-roll" if broll else "solid-scene fallback (no PEXELS_API_KEY)"
    print(f"    [b-roll] {len(broll)} clips — {note}")

    out = assemble_short(mp3, bounds, broll, OUT / f"{asin}_short.mp4",
                         hook_text=script.split(".")[0][:90] + ".")
    print(f"    [assemble] {out.name} ✅")
    return out, bounds, note


# ── [8] UPLOAD — YouTube Data API v3 (real, gated on OAuth) ──────────────────
def get_youtube_service():
    try:
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as e:
        raise RuntimeError(
            f"google libs missing ({e}) — pip install google-api-python-client "
            f"google-auth-oauthlib"
        ) from e
    import pickle

    from common import ROOT

    secret = ROOT / env("YOUTUBE_CLIENT_SECRET_FILE", "client_secret.json")
    if not secret.exists():
        raise RuntimeError(
            f"{secret.name} not found — create OAuth 2.0 credentials in Google "
            f"Cloud Console (YouTube Data API v3, Desktop app) and download it"
        )
    token = ROOT / "token.pickle"
    creds = None
    if token.exists():
        creds = pickle.loads(token.read_bytes())
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(secret), ["https://www.googleapis.com/auth/youtube.upload"])
            creds = flow.run_local_server(port=0)   # browser consent — one time
        token.write_bytes(pickle.dumps(creds))
    return build("youtube", "v3", credentials=creds)


def upload_to_youtube(video_path: Path, title: str, description: str,
                      tags: list[str]) -> str:
    """Resumable upload → video id. GenAI disclosure not required (non-realistic
    content: stock footage + text overlays), per YouTube's GenAI rules."""
    from googleapiclient.http import MediaFileUpload

    yt = get_youtube_service()
    body = {
        "snippet": {"title": title[:100], "description": description,
                    "tags": tags, "categoryId": "28"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True,
                            mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"    [upload] {int(status.progress() * 100)}%")
    return resp["id"]

# ── MAIN PIPELINE ────────────────────────────────────────────────────────────
def run(n_products: int, do_upload: bool) -> int:
    print("═" * 70)
    print("AFFILIATE PRODUCT-REVIEW SHORTS — Idea #6 end-to-end")
    print(f"mode: {'REAL UPLOAD' if do_upload else 'DRY-RUN (no upload)'} · "
          f"products: {n_products}")
    print("═" * 70)

    use_llm = has("LLM_API_BASE") and has("LLM_MODEL")
    script_mode = (f"GuardedLLM ({env('LLM_MODEL')})" if use_llm
                   else "template stub (set LLM_API_BASE/LLM_MODEL for real generation)")
    print(f"[config] script stage: {script_mode}")
    print(f"[config] associate tag: {env('AMAZON_ASSOCIATE_TAG') or 'NOT SET'}")

    rows = []
    for idx, product in enumerate(PRODUCTS[:n_products]):
        kw = product["keyword"]
        print(f"\n── {idx + 1}/{n_products} · {kw} ({product['asin']}) ──")

        # [1] research — live
        research = research_product(kw)
        print(f"    [research] {len(research)} sourced results"
              + (f" · top: {research[0].get('url', '')}" if research else ""))

        # [2+3] guarded script — regenerate on CORRUPT
        try:
            if use_llm:
                script = generate_guarded_script_llm(product, research)
                g = guard_text(script)   # belt-and-braces on the real LLM path
                if g["state"] == "corrupt":
                    raise RuntimeError(f"LLM output corrupt: {g['reasons']}")
                script = g["released"]
                guard_state = g["state"]
            else:
                script, g = make_script(product, research, idx)
                guard_state = g["state"]
            print(f"    [script] {len(script)} chars, guard={guard_state} ✅")
        except Exception as e:
            print(f"    [script] FAILED — {e}")
            rows.append({"keyword": kw, "error": str(e)})
            continue

        # [4] fact-check — honest abstain
        checks = fact_check(script)
        thin = [c for c, r in checks.items() if r.get("verdict") == "thin"]
        no_rec = [c for c, r in checks.items() if r.get("verdict") == "no_record"]
        print(f"    [fact-check] {len(checks)} claims: "
              f"{len(checks) - len(thin) - len(no_rec)} attested, "
              f"{len(thin)} thin, {len(no_rec)} no_record")
        if thin:
            print(f"      ⚠️ review manually: {thin}")

        # [5+6+7] produce the video
        try:
            video_path, _, broll_note = produce_video(script, product, idx)
        except Exception as e:
            print(f"    [produce] FAILED — {e}")
            rows.append({"keyword": kw, "error": f"produce: {e}",
                         "script_chars": len(script)})
            continue

        # [9] SEO pack + affiliate link
        pack = seo_pack(script, product)
        link, link_note = affiliate_link(product["asin"])
        desc = (f"{script}\n\n🔗 {link}\n"
                f"{'#shorts #review #' + product['niche'].replace(' ', '')}")
        pack.update({
            "asin": product["asin"], "video": str(video_path),
            "guard_state": guard_state, "broll": broll_note,
            "affiliate_link": link, "affiliate_note": link_note,
            "fact_check": checks, "upload": "pending",
        })
        (OUT / f"{product['asin']}_pack.json").write_text(
            json.dumps(pack, indent=1, ensure_ascii=False), encoding="utf-8")

        # [8] upload
        if do_upload:
            try:
                vid = upload_to_youtube(video_path, pack["title"], desc, pack["tags"])
                print(f"    [upload] 🎉 https://youtu.be/{vid}")
                pack["upload"] = f"https://youtu.be/{vid}"
                (OUT / f"{product['asin']}_pack.json").write_text(
                    json.dumps(pack, indent=1, ensure_ascii=False), encoding="utf-8")
            except Exception as e:
                print(f"    [upload] FAILED — {e}")
                pack["upload"] = f"failed: {e}"
        else:
            print("    [upload] dry-run — add --upload after OAuth setup "
                  "(client_secret.json + browser consent)")

        rows.append({"keyword": kw, "video": str(video_path),
                     "guard": guard_state, "thin_claims": len(thin),
                     "broll": broll_note, "upload": pack["upload"]})

    # summary
    print("\n" + "═" * 70)
    print("SUMMARY")
    print("═" * 70)
    for r in rows:
        if "error" in r:
            print(f"  ✗ {r['keyword']}: {r['error']}")
        else:
            print(f"  ✓ {r['keyword']}: {Path(r['video']).name} "
                  f"(guard={r['guard']}, thin={r['thin_claims']}, "
                  f"upload={'✅' if r['upload'].startswith('http') else r['upload']})")
    ok = sum(1 for r in rows if "video" in r)
    print(f"\n{ok}/{len(rows)} Shorts produced → {OUT}")
    print("affiliate links live in description + per-video *_pack.json")
    if not do_upload:
        print("next: python account_setup/create_accounts.py → OAuth → rerun with --upload")
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Idea #6: affiliate review Shorts")
    ap.add_argument("--products", type=int, default=3)
    ap.add_argument("--upload", action="store_true",
                    help="attempt real YouTube upload (requires OAuth setup)")
    args = ap.parse_args()
    sys.exit(run(args.products, args.upload))


