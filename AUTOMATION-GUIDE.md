# Automation & Monetization Guideline — AI Faceless-Content Pipeline

**Companion to `RESEARCH.md` (verified policy data) and `IDEAS.md` (12 ideas).**
Goal: a one-person, automation-first pipeline that produces platform-compliant
faceless content and earns via every available monetization path.

## 1 · Pipeline architecture

```
[1 RESEARCH]     simurg.websearch.search() → trending topics, keywords, competitor gaps
[2 SCRIPT]       LLM (any OpenAI-compatible API) generates the narration stream
[3 GUARD ★]      Simurg().feed(chunk) → CLEAN / SUSPECT / CORRUPT verdicts
                 → corruption cut mid-stream, host regenerates (zero-leak)
[4 FACT-CHECK]   simurg.websearch.ground(subject_query) → attested / thin / no_record
[5 SEO PACK]     titles, descriptions, tags, hashtags, hooks (AI + rules in §5)
[6 VOICE]        TTS (edge-tts is free) → per-scene audio
[7 VISUALS]      stock (Pexels/Pixabay APIs) or AI images; licensed only
[8 ASSEMBLE]     FFmpeg (captions, cuts, 9:16 + 16:9 renders)
[9 UPLOAD]       YouTube Data API v3 / Meta Graph API / Bilibili API (scheduled)
[10 ANALYTICS]   daily pull → RPM/retention per video → feeds back into [1]
```

## 2 · SIMURG integration (its legitimate role)

SIMURG is a **streaming-integrity monitor** — it guards *delivery*, not facts:

**a) Guard the script stream (the core).** When the LLM writes narration, feed each
chunk to the guard; on `CORRUPT` abort and regenerate instead of shipping a repetition
loop / language-drift / garbage script downstream to TTS:

```python
from simurg import Simurg, CORRUPT

s = Simurg()
script = ""
for chunk in llm_stream():                 # any OpenAI-compatible stream
    v = s.feed(chunk)
    if v.state == CORRUPT:
        raise RuntimeError(f"script corrupt at {v.onset_char}: {v.reasons}")
    script += v.released                   # only held-released chars pass
script += s.finish().released
```

**b) `websearch`** for topic/keyword research — live with the bundled free key
(verified working 2026-09-27: `websearch.search("faceless YouTube channel monetization RPM 2026", k=6)` returned 6 ranked, sourced results).

**c) `ground()`** — the re-check layer: does the subject have a real-world record?
Combines TinyFish web results (bundled free key) with keyless Wikipedia hit-counts,
and **honestly abstains** on weak evidence (verified live 2026-09-27):

```python
from simurg.websearch import ground
check = ground("automate savings transfer before spending")     # subject query only
#   verdict: "attested"  — ≥2 web results or ≥5 wiki hits AND subject echoed → real
#            "thin"      — one weak signal / generic hits → treat with caution
#            "no_record" — nothing anywhere → likely fabricated, abstain
if check["verdict"] == "attested":         # ship only grounded claims
    ...
```

**d) `GuardedLLM`** (`.integrations.openai_guard`) wraps an OpenAI-compatible client
end-to-end — guard + generation in one object.

**e) Retrain on your domain:** `SIMURG_CORPUS_JSONL=... python -m simurg.data.evaluate --save`
rebuilds weights/thresholds on your clean outputs; `CustomLearnedDetector` /
`fit_custom_detector` teach it your own failure modes; `expected_scripts=("cyrillic",)`
(or hanzi) makes it language-agnostic — required for the Bilibili idea (#8).

**f) `SUSPECT` tier** → non-blocking warning: slow the pipeline, pre-stage a retry,
or flag for human review without discarding a stream that may turn out clean.

## 3 · Tool stack (free / cheap)

| stage | tool | cost |
|---|---|---|
| script + guard | any OpenAI-compatible API + simurg | API tokens; guard is numpy-only, ~197k chars/sec, never the bottleneck |
| voice | edge-tts | free |
| visuals | Pexels / Pixabay APIs, Canva | free / freemium |
| assemble | FFmpeg | free |
| upload | YouTube Data API v3 (default quota ≈ 6 uploads/day), Meta Graph API, Bilibili API | free |
| schedule | Windows Task Scheduler / cron | free |
| analytics | platform analytics APIs → JSON/CSV | free |

**Week-one budget: $0–$30** (API tokens only).