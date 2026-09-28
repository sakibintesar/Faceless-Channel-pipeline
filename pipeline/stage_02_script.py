"""
STAGE 2 — SCRIPT: turn a topic into a retention-optimized narration script.

Two providers, both routed through the SIMURG guard (stage 3):
  * DemoLLM         — offline template narrator. $0, no keys, no network.
                      Lets the whole pipeline run end-to-end today.
  * OpenAICompatLLM — any OpenAI-compatible endpoint with SSE streaming.
                      Activated by env vars: OPENAI_BASE_URL, OPENAI_API_KEY,
                      OPENAI_MODEL (OpenRouter free tier, Ollama, LM Studio).

Script shape (retention structure for Shorts/Reels):
  HOOK  (0-3s)  -> curiosity-gap opener
  SETUP (3-10s) -> why this matters now
  BODY  (10-25s)-> 3 fast facts with numbers
  CTA   (25-30s)-> follow + link in bio

Run the live demo:  python -m pipeline.stage_02_script
"""

from __future__ import annotations

import json
import os
from typing import Iterable, Optional

from .common import SCRIPTS_DIR, save_json, slugify, timestamp
from .guard import GuardResult, GuardedLLM

HOOKS = [
    "Stop scrolling — {topic} is the side hustle nobody is talking about.",
    "What if {topic} could pay your rent without ever showing your face?",
    "You are 30 seconds away from understanding {topic}.",
]

CTA = "Follow for the full playbook, and check the link in bio for the free starter pack."


class DemoLLM:
    """Offline template narrator — deterministic, $0, zero dependencies."""

    def __init__(self, topic: str, facts: Iterable[str] = ()) -> None:
        self.topic = topic
        self.facts = list(facts) or [
            "Faceless channels use stock footage and AI voices, so production cost stays near zero.",
            "The fastest first dollar comes from affiliate links, which pay before ad revenue unlocks.",
            "A digital product like a prompt pack sells with zero platform fees on Gumroad.",
        ]

    def stream(self, prompt: Optional[str] = None) -> Iterable[str]:
        """Yield the script in small chunks (exercises the streaming guard)."""
        hook = HOOKS[0].format(topic=self.topic)
        parts = [hook + " ", f"Here is the honest math on {self.topic}. "]
        for fact in self.facts:
            parts.append(fact + " ")
        parts.append(CTA)
        text = "".join(parts)
        for i in range(0, len(text), 24):
            yield text[i : i + 24]


class OpenAICompatLLM:
    """Any OpenAI-compatible /chat/completions endpoint with stream=True."""

    def __init__(self, topic: str, base_url: str, api_key: str, model: str) -> None:
        self.topic = topic
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    @classmethod
    def from_env(cls, topic: str) -> Optional["OpenAICompatLLM"]:
        base = os.getenv("OPENAI_BASE_URL")
        key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if base and key:
            return cls(topic, base, key, model)
        return None

    def stream(self, prompt: Optional[str] = None) -> Iterable[str]:
        import requests

        prompt = prompt or (
            f"Write a 30-second faceless short script about: {self.topic}. "
            "Structure: HOOK (0-3s, curiosity gap), SETUP (3-10s), "
            "BODY (3 fast facts with numbers), CTA (follow + link in bio). "
            "Output ONLY the narration text, no headers, no stage directions."
        )
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "stream": True,
                "messages": [{"role": "user", "content": prompt}],
            },
            stream=True,
            timeout=60,
        )
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            data = line[len("data: "):]
            if data.strip() == "[DONE]":
                break
            try:
                delta = json.loads(data)["choices"][0]["delta"].get("content", "")
                if delta:
                    yield delta
            except (KeyError, IndexError, json.JSONDecodeError):
                continue


def build_script(topic: str, provider: str = "auto") -> dict:
    """Generate + guard a script; returns metadata with the SIMURG verdict."""
    guard = GuardedLLM()
    script_prompt = (
        f"Write a 30-second faceless short script about: {topic}. "
        "Structure: HOOK (0-3s, curiosity gap), SETUP (3-10s), "
        "BODY (3 fast facts with numbers), CTA (follow + link in bio). "
        "Output ONLY the narration text."
    )

    llm = None
    used = ""
    if provider in ("auto", "openai"):
        llm = OpenAICompatLLM.from_env(topic)
        if llm is not None:
            used = "OpenAI-compatible streaming"
    if llm is None:
        llm = DemoLLM(topic)
        used = "DemoLLM (offline template, $0)"

    result: GuardResult = guard.guarded_generate(script_prompt, llm.stream)

    slug = slugify(topic)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SCRIPTS_DIR / f"{slug}.txt"
    path.write_text(result.text, encoding="utf-8")

    meta = {
        "topic": topic,
        "provider": used,
        "script_path": str(path),
        "chars": len(result.text),
        "guard": {
            "state": result.state,
            "p_corrupt": result.p_corrupt,
            "onset_char": result.onset_char,
            "reasons": result.reasons,
            "classes": result.classes,
            "summary": result.summary(),
        },
        "timestamp": timestamp(),
    }
    save_json(SCRIPTS_DIR / f"{slug}.meta.json", meta)
    return meta


if __name__ == "__main__":
    meta = build_script("5 AI side hustles that actually pay in 2026")
    print("[STAGE 2] SCRIPT")
    print("   provider:", meta["provider"])
    print("   guard   :", meta["guard"]["summary"])
    print("   chars   :", meta["chars"])
    print("   saved   :", meta["script_path"])
