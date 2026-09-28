"""
STAGE 1 — RESEARCH: trending topics via simurg.websearch.

Zero-dollar cost: the bundled TinyFish key ships with simurg — no API keys,
no paid search APIs. search() returns [] (never raises) when offline or
rate-limited, so we fall back to a curated seed list distilled from IDEAS.md.

Verified API (simurg 1.0.4):
    search(query, api_key=None, k=6, timeout=12.0) -> list[dict]
    each dict: {title, snippet, url, site_name}  (rank order)

Run the live demo:  python -m pipeline.stage_01_research
"""

from __future__ import annotations

from collections import Counter

from .common import ANALYTICS_DIR, save_json, timestamp

SEED_TOPICS = [
    {
        "title": "5 AI side hustles that actually pay in 2026",
        "url": "",
        "site_name": "seed",
        "snippet": "Affiliate product-review shorts + digital products — fastest first dollar.",
    },
    {
        "title": "Faceless YouTube niches with the highest RPM in 2026",
        "url": "",
        "site_name": "seed",
        "snippet": "Finance, AI tools, and business niches pay the most per 1k views.",
    },
    {
        "title": "How faceless channels hit YPP without showing a face",
        "url": "",
        "site_name": "seed",
        "snippet": "1k subs + 4k watch hours (or 10M Shorts views) via volume + retention.",
    },
    {
        "title": "Digital product funnel: prompt packs and templates",
        "url": "",
        "site_name": "seed",
        "snippet": "Sell on Gumroad/Ko-fi at $0 platform cost; funnel from Shorts link-in-bio.",
    },
    {
        "title": "Instagram Reels + Facebook Reels cross-posting pipeline",
        "url": "",
        "site_name": "seed",
        "snippet": "One render, three platforms: professional accounts, Bonuses interest form.",
    },
    {
        "title": "Bilibili faceless content with Mandarin TTS",
        "url": "",
        "site_name": "seed",
        "snippet": "Underserved market: zh-CN voices, danmaku engagement, identity verification.",
    },
]

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with",
    "how", "why", "what", "your", "you", "that", "this", "is", "are",
    "without", "from", "about", "actually", "much", "do", "does", "it",
}


def research_topics(
    query: str = "faceless YouTube channel monetization 2026", k: int = 6
) -> dict:
    """Run a live web search; fall back to seed topics when it returns []."""
    results: list[dict] = []
    source = "simurg.websearch (live)"
    try:
        from simurg.websearch import search

        results = search(query, k=k) or []
    except ImportError:
        source = "seed list (simurg not installed)"
    if not results:
        source = "seed list (offline or rate-limited)"
        results = SEED_TOPICS[:k]
    report = {
        "query": query,
        "source": source,
        "count": len(results),
        "top_keywords": rank_keywords(results),
        "results": results,
    }
    save_json(ANALYTICS_DIR / f"research_{timestamp()}.json", report)
    return report


def rank_keywords(results: list[dict]) -> list[str]:
    """Crude keyword-frequency rank across result titles and snippets."""
    words: Counter = Counter()
    for r in results:
        text = f"{r.get('title', '')} {r.get('snippet', '')}".lower()
        for w in text.split():
            w = w.strip(".,:;!?()[]\"'—-")
            if w and w not in STOPWORDS and len(w) > 3:
                words[w] += 1
    return [w for w, _ in words.most_common(10)]


if __name__ == "__main__":
    report = research_topics()
    print("[STAGE 1] RESEARCH — source:", report["source"])
    for i, r in enumerate(report["results"], 1):
        print(f"  {i}. {r.get('title', '')}  ({r.get('site_name', '') or 'n/a'})")
    print("  top keywords:", ", ".join(report["top_keywords"]))
