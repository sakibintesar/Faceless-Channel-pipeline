# Faceless Content Monetization Research — deliverables index

**Built 2026-09-27** inside the SIMURG workspace. Research on earning money from
**YouTube, Instagram, Facebook, and Bilibili with faceless content** — 12 working
ideas executable in week one, verified policy data, and a full automation +
SEO-through-AI guideline.

## Deliverables

| file | what it is |
|---|---|
| `RESEARCH.md` | platform-by-platform verified research: YPP requirements + 2027 overhaul, inauthentic-content policy (July 2025), GenAI disclosure rules, Instagram/Facebook/Bilibili programs, RPM benchmarks — every claim sourced |
| `IDEAS.md` | 12 working ideas with week-one execution plans, automation level, time-to-first-dollar, compliance notes |
| `ideas_dataset.json` | machine-readable dataset of the 12 ideas (automation-ready) |
| `AUTOMATION-GUIDE.md` | full guideline: 10-stage AI pipeline, SIMURG integration, tool stack, per-platform monetization rules, SEO rules, day-by-day week-one schedule |
| `pipeline_demo.py` | runnable guarded-pipeline demo (offline-safe, no API keys needed) |

## Run

```powershell
# from the simurg workspace root
.\.venv\Scripts\Activate.ps1
python faceless-research\pipeline_demo.py
```

## What SIMURG actually did here (honest note)

SIMURG is a **streaming-integrity monitor** (it guards LLM output against decoding
corruption), **not** a research engine. Its genuine contributions:

1. **`websearch` (TinyFish) — used live** for the market research: bundled free key,
   real queries, sourced snippets for Instagram/Facebook/Bilibili eligibility +
   YPP thresholds + RPM data. Verified working 2026-09-27 in this workspace.
2. **`ground()` — used live** to fact-check claims; it honestly abstains
   (`"thin"` / `"abstain"`) instead of fabricating confidence.
3. **The guard core** protects the AI-generated script stream in the pipeline —
   corruption (repetition loops, language drift, garbage) is cut mid-flight before
   it ever reaches TTS/upload.

Official policy docs (YouTube YPP/policies/GenAI rules, Facebook Content
Monetisation, Instagram Bonuses) were pulled via direct page fetches; all revenue
figures are clearly-labeled third-party estimates.

## Key findings (TL;DR)

- **YouTube** = highest RPM ($3–$40 by niche); join YPP **before Feb 1, 2027** to lock
  the old thresholds — new-creator thresholds rise to **8,000 watch hours / 20M Shorts
  views** (official blog, Aug 10 2026).
- **July 15, 2025 "inauthentic content" policy** is the #1 faceless-channel risk:
  mass-produced content is demonetizable; **original commentary/transformation** survives
  (compilation/reaction review unchanged under the reused-content policy).
- **Instagram** = no general ad rev-share; Bonuses invite-only (18+, US/JP/KR);
  earn via affiliate + Gifts + Subscriptions + brand deals.
- **Facebook** = Content Monetisation invite-only — express interest via the dashboard
  form NOW; meanwhile Stars + branded content; Reels ≥10s.
- **Bilibili** = 1,000 followers or 100k cumulative views; ~$0.70/1k views reported
  but **not officially fixed**.
- **Week-one first dollars** come from affiliate (#6) and digital products (#7),
  not platform ad revenue.
