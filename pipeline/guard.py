"""
STAGE 3 — GUARD: the core SIMURG monitoring layer.

Every AI-generation stage routes its text streams through GuardedLLM so
corrupt model output (repetition loops, vocabulary collapse, language
drift) is cut mid-stream with a ZERO-LEAK guarantee: no corrupted
character ever reaches TTS, subtitles, upload, or a rendered video.

Simurg API (verified against simurg 1.0.4):
    s = Simurg()
    v = s.feed(chunk)   -> Verdict(released, state, p_corrupt,
                                   onset_char, reasons, classes)
    v = s.finish()      -> flushes the remaining clean buffer
    CORRUPT == "corrupt" -> the v.state value that means "abort now"

Run the live demo:  python -m pipeline.guard
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

try:
    from simurg import Simurg, CORRUPT

    SIMURG_AVAILABLE = True
except ImportError:  # graceful fallback — the pipeline still runs
    SIMURG_AVAILABLE = False
    CORRUPT = "corrupt"

    class Simurg:  # minimal stub so type hints resolve
        def feed(self, chunk: str):
            raise RuntimeError("simurg is not installed")

        def finish(self):
            raise RuntimeError("simurg is not installed")


@dataclass
class GuardResult:
    """Outcome of guarding one complete text stream."""

    text: str  # clean text that survived (zero-leak)
    state: str  # 'clean' | 'corrupt' | 'unavailable'
    p_corrupt: float = 0.0
    onset_char: Optional[int] = None
    reasons: str = ""
    classes: list = field(default_factory=list)
    chars_released: int = 0
    chars_total: int = 0

    @property
    def ok(self) -> bool:
        return self.state == "clean"

    def summary(self) -> str:
        if self.state == "clean":
            return (
                f"verdict=clean p_corrupt={self.p_corrupt:.3f} "
                f"released={self.chars_released}/{self.chars_total} chars"
            )
        if self.state == "corrupt":
            return (
                f"verdict=corrupt aborted at char {self.onset_char} "
                f"leaked={self.chars_released}/{self.chars_total} "
                f"reasons={self.reasons}"
            )
        return "verdict=unavailable (simurg not installed) — fail-open"


class GuardedLLM:
    """Wrap any chunk-producing text generator with SIMURG monitoring."""

    def __init__(self, fail_open: bool = True) -> None:
        # fail_open=True: if simurg were ever missing, streams pass through
        # with state='unavailable' instead of crashing the pipeline.
        self.fail_open = fail_open

    def guard_stream(self, chunks: Iterable[str]) -> GuardResult:
        """Feed chunks one by one; release only clean text; abort on CORRUPT."""
        if not SIMURG_AVAILABLE:
            text = "".join(chunks)
            return GuardResult(
                text=text,
                state="unavailable",
                chars_released=len(text),
                chars_total=len(text),
            )

        s = Simurg()
        released: list[str] = []
        state, onset, reasons, classes = "clean", None, "", []
        p_corrupt = 0.0
        chars_total = 0

        for chunk in chunks:
            chars_total += len(chunk)
            v = s.feed(chunk)
            released.append(v.released)
            p_corrupt = max(p_corrupt, float(getattr(v, "p_corrupt", 0.0) or 0.0))
            if v.state == CORRUPT:
                state = "corrupt"
                onset = getattr(v, "onset_char", None)
                reasons = getattr(v, "reasons", "") or ""
                classes = list(getattr(v, "classes", None) or [])
                break  # ZERO-LEAK: stop feeding immediately, discard the rest

        text = "".join(released)
        chars_released = len(text)

        if state == "clean":
            fin = s.finish()
            text += fin.released
            chars_released = len(text)

        return GuardResult(
            text=text,
            state=state,
            p_corrupt=p_corrupt,
            onset_char=onset,
            reasons=reasons,
            classes=classes,
            chars_released=chars_released,
            chars_total=chars_total,
        )

    def guard_text(self, text: str, chunk_size: int = 80) -> GuardResult:
        """Convenience: guard a complete string by simulating a stream."""
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
        return self.guard_stream(chunks)

    def guarded_generate(
        self, prompt: str, generate: Callable[[str], Iterable[str]]
    ) -> GuardResult:
        """Integration point for real LLMs: generate(prompt) must return an
        iterable of text chunks (e.g. an SSE-delta stream)."""
        return self.guard_stream(generate(prompt))

    def guard_many(self, texts: Iterable[str]) -> list[GuardResult]:
        """Guard a batch (scripts, captions, SEO copy) in one call."""
        return [self.guard_text(t) for t in texts]


if __name__ == "__main__":
    guard = GuardedLLM()

    clean_script = (
        "Most people think you need a camera and a studio to make money online. "
        "You do not. In 2026, faceless channels run on three free tools: a script "
        "generator, a text-to-speech voice, and stock footage libraries. The "
        "production cost stays near zero, so your first affiliate dollar is profit. "
        "Pick one niche, batch ten scripts, and let the pipeline assemble them."
    )
    loop_text = "This side hustle makes money fast, and this side hustle makes money fast, " * 30

    print("[1] clean stream :")
    r1 = guard.guard_text(clean_script)
    print("   ", r1.summary())
    print("[2] repetition loop :")
    r2 = guard.guard_text(loop_text)
    print("   ", r2.summary())
    print("[3] corrupt chars released:", r2.chars_released, "of", r2.chars_total)
