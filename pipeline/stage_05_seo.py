"""
STAGE 5 — SEO PACK: platform-specific titles, hooks, hashtags, descriptions.

Honest note: the MIT "skills" repos (youtube-skills, instagram-skills,
tiktok-skills, facebook-skills, linkedin-skills) are instruction/prompt
packs for AI agents, not importable Python modules. This module distills
their patterns into deterministic, dependency-free heuristics — and every
generated string still passes through the SIMURG guard (stage 3), so no
repetitive or drifted copy ever reaches an upload.

Packs: youtube | instagram | tiktok | facebook

Run the live demo:  python -m pipeline.stage_05_seo
"""

from __future__ import annotations

from .common import SCRIPTS_DIR, save_json, slugify
from .guard import GuardedLLM

TITLE_FORMULAS = [
    "5 {topic} Tools That Actually Pay in 2026",
    "Nobody Talks About This {topic} Side Hustle",
    "{topic} in 30 Seconds — The Honest Math",
    "I Tried {topic} So You Don't Have To",
    "The Cheapest Way to Start {topic} Today",
]

HASHTAG_BANK = [
    "faceless", "facelessyoutube", "sidehustle", "sidehustle2026",
    "passiveincome", "aitools", "moneytok", "finance", "onlinebusiness",
    "digitalproducts", "makemoneyonline", "hustle", "entrepreneur",
    "workfromhome", "contentcreator", "youtubeshorts", "reels",
    "reelsinstagram", "aiwriting", "automation", "solopreneur",
    "extraincome", "onlineincome", "ai", "chatgpt",
]


def _guard_pack(guard: GuardedLLM, pack: dict) -> dict:
    """Guard every string field; drop anything the sentinel flags."""
    clean: dict = {}
    for key, value in pack.items():
        if isinstance(value, str):
            r = guard.guard_text(value)
            if r.ok:
                clean[key] = r.text
        elif isinstance(value, list):
            kept = []
            for item in value:
                if isinstance(item, str):
                    r = guard.guard_text(item)
                    if r.ok:
                        kept.append(r.text)
                else:
                    kept.append(item)
            clean[key] = kept
        else:
            clean[key] = value
    return clean


def youtube_pack(topic: str, affiliate_link: str = "https://link-in-bio.example") -> dict:
    guard = GuardedLLM()
    titles = [f.format(topic=topic) for f in TITLE_FORMULAS[:3]]
    description = (
        f"{topic} explained in 30 seconds. Follow for daily faceless "
        "side-hustle playbooks.\n\n"
        f"Free starter pack: {affiliate_link}\n\n"
        "Disclosure: some links are affiliate links — I may earn a "
        "commission at no extra cost to you.\n"
        "This video was created with AI-assisted scripting and a synthetic voice."
    )
    tags = [
        "faceless youtube", "side hustle 2026", "ai tools", "passive income",
        "make money online", "faceless channel",
    ]
    hooks = [
        f"Stop scrolling — {topic} pays before you even hit 1000 subs.",
        f"Your face is optional. Your system is not. {topic}, explained.",
        f"The cheapest {topic} setup is three free tools. Here they are.",
    ]
    pack = {
        "platform": "youtube",
        "titles": titles,
        "title_primary": titles[0],
        "description": description,
        "tags": tags,
        "hooks": hooks,
        "affiliate_link": affiliate_link,
        "disclosures": ["affiliate", "ai-assisted"],
    }
    return _guard_pack(guard, pack)


def instagram_pack(topic: str, affiliate_link: str = "https://link-in-bio.example") -> dict:
    guard = GuardedLLM()
    caption = (
        f"{topic} — the honest math in 30 seconds.\n\n"
        "Faceless means no camera, no studio, no excuses. Stock footage, "
        "an AI voice, and one posting system.\n\n"
        "Free starter pack in bio.\n\n"
        "Disclosure: affiliate links in bio may earn a commission at no cost to you."
    )
    hashtags = HASHTAG_BANK[:25]
    carousel = [
        f"Slide 1 — Hook: {topic} without showing your face?",
        "Slide 2 — The 3 free tools (script, voice, footage)",
        "Slide 3 — The math: $0 cost, first dollar from affiliates",
        "Slide 4 — The 30-day plan (1 render, 3 platforms)",
        "Slide 5 — CTA: Save this + follow for the playbook",
    ]
    pack = {
        "platform": "instagram",
        "caption": caption,
        "hashtags": hashtags,
        "carousel": carousel,
        "affiliate_link": affiliate_link,
        "disclosures": ["affiliate", "ai-assisted"],
    }
    return _guard_pack(guard, pack)


def tiktok_pack(topic: str) -> dict:
    guard = GuardedLLM()
    hooks = [
        f"POV: you started {topic} with $0 and a laptop.",
        f"{topic}, but you never show your face.",
        "3 tools. 30 seconds. One side hustle.",
    ]
    pack = {
        "platform": "tiktok",
        "hooks": hooks,
        "caption": f"{topic} — full playbook in bio",
        "hashtags": ["sidehustle", "moneytok", "aitools", "faceless"],
        "disclosures": ["ai-assisted"],
    }
    return _guard_pack(guard, pack)


def facebook_pack(topic: str) -> dict:
    guard = GuardedLLM()
    post = (
        f"Quick question: has anyone here tried {topic} without showing "
        "their face?\n\n"
        "I ran the honest math: stock footage, an AI voice, and one posting "
        "system keeps production cost near zero. The first dollar usually "
        "comes from affiliate links, not ad revenue.\n\n"
        "Full playbook in the comments.\n\n"
        "Disclosure: some links may be affiliate links, at no extra cost to you."
    )
    pack = {
        "platform": "facebook",
        "post": post,
        "reply_drafts": [
            "Great question — the starter pack in our bio breaks it down step by step.",
            "It is free to start: the tools below are all free tiers. Save this post!",
        ],
        "disclosures": ["affiliate", "ai-assisted"],
    }
    return _guard_pack(guard, pack)


def build_seo_pack(topic: str, platform: str = "youtube", affiliate_link: str = "") -> dict:
    """Build + guard + save the SEO pack for one platform."""
    builders = {
        "youtube": youtube_pack,
        "instagram": instagram_pack,
        "tiktok": tiktok_pack,
        "facebook": facebook_pack,
    }
    builder = builders.get(platform, youtube_pack)
    uses_link = platform in ("youtube", "instagram")
    pack = builder(topic, affiliate_link) if (affiliate_link and uses_link) else builder(topic)
    slug = slugify(topic)
    save_json(SCRIPTS_DIR / f"{slug}.seo_{platform}.json", pack)
    return pack


if __name__ == "__main__":
    topic = "5 AI side hustles that actually pay in 2026"
    for platform in ("youtube", "instagram", "tiktok", "facebook"):
        pack = build_seo_pack(topic, platform)
        print(f"[STAGE 5] SEO PACK — {platform}")
        for key, value in pack.items():
            if isinstance(value, list):
                first = value[0] if value else "-"
                print(f"   {key}: {len(value)} items | first: {str(first)[:60]}")
            elif isinstance(value, str) and len(value) > 60:
                print(f"   {key}: {value[:57]}...")
            else:
                print(f"   {key}: {value}")
        print()
