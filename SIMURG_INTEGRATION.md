# SIMURG Integration — Guard Wiring

## Where the guard sits

```
LLM stream (script)      --> GuardedLLM.guarded_generate()  -> zero-leak text  -> TTS
SEO copy / captions      --> GuardedLLM.guard_text()        -> zero-leak copy  -> upload
AI image prompts         --> GuardedLLM.guard_text()        -> zero-leak prompt-> generator
Research claims          --> websearch.ground()             -> attested / thin / no_record
FFmpeg command (stage 8) --> structural validation only (deterministic command — a
                             text guard would false-positive on repetitive CLI flags)
```

## The zero-leak guarantee

When the sentinel flags CORRUPT mid-stream, feeding stops immediately and
every character after the onset is discarded — corrupt output never
reaches TTS, subtitles, upload, or a rendered video.

## Verified API (simurg 1.0.4, Apache-2.0)

```python
from simurg import Simurg, CORRUPT

s = Simurg()
v = s.feed(chunk)   # -> Verdict(released, state, p_corrupt, onset_char, reasons, classes)
# v.state == CORRUPT  -> abort now
# v.released          -> clean prefix to keep
s.finish()           # flushes the remaining clean buffer
```

## Code pattern (every AI-generation stage)

```python
from pipeline.guard import GuardedLLM

guard = GuardedLLM()
result = guard.guarded_generate(prompt, llm.stream)   # llm.stream yields chunks
if not result.ok:
    raise RuntimeError(f"corrupt: {result.summary()}")
clean_text = result.text
```

## Stage coverage table

| Stage | Function | Role |
|-------|----------|------|
| 1 RESEARCH | `websearch.search()` | trending topics, free bundled key |
| 2/3 SCRIPT | `GuardedLLM.guarded_generate()` | zero-leak script |
| 4 FACT-CHECK | `websearch.ground()` | attested / thin / no_record |
| 5 SEO PACK | `GuardedLLM.guard_text()` per field | no drifted copy |
| 6 VOICE | guard BEFORE edge-tts | corrupt text never becomes audio |
| 7 VISUALS | `GuardedLLM.guard_text()` on prompts | no drifted prompts |
| 8 ASSEMBLE | structural validation | deterministic command, no text guard |
| 9 UPLOAD | `validate_metadata()` | FTC affiliate + AI disclosure gate |

## License note (honest correction)

simurg is **Apache-2.0** (permissive, commercial use OK, keep the NOTICE/
LICENSE attribution) — earlier notes called it MIT; that was wrong.
MIT-strict deps: moviepy, ffsubsync, youtube-transcript-api, pyyaml.
edge-tts is GPL-3.0 — fine as an unmodified tool for a non-distributed
side gig; if you redistribute the app itself, prefer permissive TTS.
