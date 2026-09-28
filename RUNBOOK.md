# RUNBOOK — Daily Operations (Faceless Content Side Gig)

Daily loop, ~2-3 hrs/day. Everything runs from `faceless-research/` with
the venv active: `.\.venv\Scripts\Activate.ps1`

---

## Morning batch (45-60 min)

```powershell
# 1. Research: trending topics + keywords (free, SIMURG websearch)
python -m pipeline.stage_01_research

# 2. Generate + guard scripts (SIMURG zero-leak monitor)
python -m pipeline.stage_02_script

# 3. Fact-check the claims (honest abstention)
python -m pipeline.stage_04_factcheck
```

Review `content/scripts/*.txt` — rewrite any claim flagged `thin` or
`no_record` before it ships.

---

## Midday render (30-45 min)

```powershell
# 4. SEO packs for all 4 platforms (titles, hooks, hashtags)
python -m pipeline.stage_05_seo

# 5. Voice: edge-tts narration + word-level caption cues (free)
python -m pipeline.stage_06_tts

# 6. Visuals: stock assets (set PEXELS_API_KEY / PIXABAY_API_KEY first)
python -m pipeline.stage_07_visuals
```

---

## Afternoon publish (30 min)

```powershell
# 7. Full end-to-end run (research -> render -> subtitles -> dry-run upload)
python -m pipeline.orchestrator --topic "your topic here" --platform youtube

# 8. Analytics snapshot + KPI ladder
python -m pipeline.stage_10_analytics --snapshot
```

Upload manually (or flip stage 9 to live once OAuth tokens are set).
Respect `config/upload_schedule.yaml` caps: 3 YT + 2 IG + 1 FB per day.

---

## Weekly review (Sunday, 30 min)

- Pull the YouTube Studio CSV -> `analytics/manual.csv`
- `python -m pipeline.stage_10_analytics --import-csv analytics/manual.csv`
- Double down on top performers; kill losers; plan next week's topics
- Check Amazon Associates clicks + Gumroad sales

---

## Emergency: output looks wrong?

```powershell
# Show the zero-leak cut on a corruption demo
python -m pipeline.orchestrator --demo-corrupt

# Re-verify the guard layer
python -m pipeline.guard
```

---

## Env vars (all optional)

| Var | Purpose |
|-----|---------|
| `OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_MODEL` | live script generation |
| `PEXELS_API_KEY` | stock images/videos (free key) |
| `PIXABAY_API_KEY` | stock images (free key) |
| `YT_CLIENT_SECRETS` | YouTube upload OAuth (go live) |
| `META_PAGE_TOKEN` / `META_PAGE_ID` | IG/FB Reels upload (go live) |
