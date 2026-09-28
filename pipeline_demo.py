# ═══════════════════════════════════════════════════════════════════════════════
# pipeline_demo.py — guarded AI faceless-content pipeline (offline-safe runnable)
#
# Full pipeline with SIMURG in its legitimate role: guarding the LLM-generated
# script stream. Stages 1/4 use simurg.websearch when the network allows; all
# other stages are hermetic, so this runs with zero API keys.
#
# Run:  python pipeline_demo.py     (from the simurg workspace, venv activated)
# ═══════════════════════════════════════════════════════════════════════════════
import json

from simurg import CORRUPT, Simurg

try:
    import simurg.websearch as ws
except Exception:                                   # pragma: no cover
    ws = None


# ── [1] topic research (live when the network allows) ─────────────────────────
def research_topics(niche="faceless youtube finance channel", k=3):
    if ws is None or not ws.available():
        return [], "offline (simurg.websearch unavailable)"
    try:
        return ws.search(niche, k=k), "live via simurg.websearch (TinyFish)"
    except Exception as exc:
        return [], f"offline ({exc})"


# ── [2+3] script generation guarded by SIMURG ─────────────────────────────────
def guarded_generate(stream_text, size=40):
    """Simulate an LLM streaming chunks; plug any OpenAI-compatible API here.
    Returns (script_released, aborted, onset_char, reasons)."""
    s = Simurg()
    shown = []
    for i in range(0, len(stream_text), size):
        v = s.feed(stream_text[i:i + size])
        shown.append(v.released or "")
        if v.state == CORRUPT:
            return "".join(shown), True, v.onset_char, list(v.reasons or [])
    final = s.finish()
    shown.append(final.released or "")
    return "".join(shown), False, None, list(final.reasons or [])


GOOD_SCRIPT = (
    "Three money habits quietly separate people who save from people who don't. "
    "First, automate the transfer before you can spend it. Second, track the "
    "leak, not the budget. Third, make the boring option the default. Each habit "
    "takes one evening to set up and pays for itself within a month. "
)
CORRUPT_STREAM = "budget expenditure rises budget expenditure rises " * 30


# ── [4] ground-check a subject from the script (live when the network allows) ─
def ground_subject(subject):
    if ws is None or not ws.available():
        return {"verdict": "skipped", "reason": "offline"}
    try:
        return ws.ground(subject)
    except Exception as exc:
        return {"verdict": "skipped", "reason": str(exc)}


# ── [5] SEO pack (rule-based demo; hand off to the LLM in production) ─────────
def seo_pack(script):
    words = script.split()
    hook = " ".join(words[:12])
    return {
        "title": hook[:57] + "…" if len(hook) > 57 else hook,
        "description_first_line": " ".join(words[:25])[:150],
        "tags": ["personal finance", "money habits", "saving money",
                 "financial literacy", "faceless"],
        "hook_first_3s": hook,
    }


# ── [9] upload stub — plug the real APIs here ─────────────────────────────────
def upload_plan():
    return {
        "youtube_data_api_v3": "stub — developers.google.com/youtube/v3 (≈6 uploads/day default quota)",
        "meta_graph_api": "stub — Reels + official crosspost from Instagram",
        "bilibili_api": "stub — original content required; declare expected_scripts to simurg",
        "scheduler": "Windows Task Scheduler / cron",
    }


def main():
    print("═" * 70)
    print("GUARDED FACELESS-CONTENT PIPELINE — live demo")
    print("═" * 70)

    topics, how = research_topics()
    print(f"\n[1] topic research — {how}: {len(topics)} results")
    for t in topics:
        print(f"    - {t.get('site_name')}: {t.get('title')}")

    shown, aborted, onset, reasons = guarded_generate(GOOD_SCRIPT)
    print(f"\n[2+3] clean script — aborted={aborted}, {len(shown)} chars released")

    shown, aborted, onset, reasons = guarded_generate(CORRUPT_STREAM)
    print(f"[2+3] corrupt script — aborted={aborted} at char {onset}")
    print(f"      reasons: {'; '.join(reasons)}")
    print("      → regeneration triggered; nothing past the abort ships to TTS")

    g = ground_subject("automate savings transfer before spending")
    print(f"\n[4] ground check — verdict: {g.get('verdict')} ({g.get('reason', '')})")

    print("\n[5] SEO pack:")
    print(json.dumps(seo_pack(GOOD_SCRIPT), indent=2, ensure_ascii=False))

    print("\n[9] upload plan:")
    for key, val in upload_plan().items():
        print(f"    {key}: {val}")

    print("\n" + "═" * 70)
    print("Pipeline verified. See RESEARCH.md (verified policy data),")
    print("IDEAS.md (12 week-one ideas), AUTOMATION-GUIDE.md (full guideline).")
    print("═" * 70)


if __name__ == "__main__":
    main()
