"""
STAGE 4 — FACT-CHECK: ground every claim before it ships.

simurg.websearch.ground() combines the free TinyFish web key with the
keyless Wikipedia hit-count and classifies each claim:
  attested   -> real, ship it
  thin       -> one weak signal — flag for manual review or rewrite
  no_record  -> nothing anywhere — remove before upload

Honest abstention is the feature: 'thin' is returned instead of fake
confidence, so a beginner never ships an invented number.

Verified API (simurg 1.0.4):
    ground(query, api_key=None, k=6, wiki=True, timeout=12.0) -> dict

Run the live demo:  python -m pipeline.stage_04_factcheck
"""

from __future__ import annotations

import re

from .common import ANALYTICS_DIR, save_json, slugify, timestamp

FACT_MARKERS = re.compile(
    r"(\d|%|\$|requires|earns|pays|costs|takes|needs|unlocks|thousand"
    r"|million|billion|days|hours|months|per\s)",
    re.IGNORECASE,
)

ACTIONS = {
    "attested": "ship",
    "thin": "flag for manual review or rewrite",
    "no_record": "remove before upload",
}


def extract_claims(script_text: str) -> list[str]:
    """Pull factual sentences (numbers, money, time, requirements)."""
    sentences = re.split(r"(?<=[.!?])\s+", script_text.strip())
    return [s.strip() for s in sentences if s and FACT_MARKERS.search(s)]


def factcheck_claims(claims: list[str]) -> list[dict]:
    """Ground each claim; degrades gracefully when simurg is missing."""
    try:
        from simurg.websearch import ground

        have_ground = True
    except ImportError:
        have_ground = False

    out: list[dict] = []
    for claim in claims:
        if not have_ground:
            out.append(
                {
                    "claim": claim,
                    "verdict": "unverified",
                    "action": "manual review",
                    "reason": "simurg not installed",
                }
            )
            continue
        check = ground(claim)  # returns a dict, never raises
        verdict = check.get("verdict", "no_record")
        out.append(
            {
                "claim": claim,
                "verdict": verdict,
                "action": ACTIONS.get(verdict, "manual review"),
                "evidence": {k: v for k, v in check.items() if k != "verdict"},
            }
        )
    return out


def filter_script(script_text: str, slug: str | None = None) -> dict:
    """Fact-check a full script; returns a report with per-claim verdicts."""
    claims = extract_claims(script_text)
    items = factcheck_claims(claims)
    report = {
        "timestamp": timestamp(),
        "claims_checked": len(claims),
        "attested": sum(1 for r in items if r["verdict"] == "attested"),
        "thin": sum(1 for r in items if r["verdict"] == "thin"),
        "no_record": sum(1 for r in items if r["verdict"] == "no_record"),
        "items": items,
    }
    save_json(
        ANALYTICS_DIR / f"factcheck_{slug or slugify(script_text[:40])}.json", report
    )
    return report


if __name__ == "__main__":
    demo_script = (
        "YouTube monetization requires 1000 subscribers. "
        "Faceless channels can earn from affiliate links before ads unlock. "
        "The sky is blue and coding is fun."
    )
    report = filter_script(demo_script)
    print("[STAGE 4] FACT-CHECK")
    print(
        f"   claims={report['claims_checked']} "
        f"attested={report['attested']} thin={report['thin']} "
        f"no_record={report['no_record']}"
    )
    for item in report["items"]:
        print(
            f"   [{item['verdict']:>9}] {item['action']:<32} "
            f":: {item['claim'][:60]}"
        )
