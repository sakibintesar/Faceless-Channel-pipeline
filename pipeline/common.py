"""Shared paths and helpers for the faceless-content pipeline.

Every stage imports its directories from here so the whole pipeline can be
relocated by moving one folder. All outputs land under content/ and analytics/.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

try:
    import yaml

    HAS_YAML = True
except ImportError:  # config files become optional, presets kick in
    HAS_YAML = False

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SCRIPTS_DIR = CONTENT / "scripts"
AUDIO_DIR = CONTENT / "audio"
VISUALS_DIR = CONTENT / "visuals"
RENDERED_DIR = CONTENT / "rendered"
SUBTITLES_DIR = CONTENT / "subtitles"
ANALYTICS_DIR = ROOT / "analytics"
CONFIG_DIR = ROOT / "config"
PRODUCTS_DIR = ROOT / "products"


def slugify(text: str, max_len: int = 48) -> str:
    """Filesystem-safe slug: '5 AI side hustles!' -> '5-ai-side-hustles'."""
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:max_len].rstrip("-") or "untitled"


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def save_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_yaml(name: str) -> dict:
    """Load a config YAML if pyyaml is installed and the file exists."""
    if not HAS_YAML:
        return {}
    path = CONFIG_DIR / name
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def ensure_dirs() -> None:
    for d in (
        SCRIPTS_DIR,
        AUDIO_DIR,
        VISUALS_DIR,
        RENDERED_DIR,
        SUBTITLES_DIR,
        ANALYTICS_DIR,
    ):
        d.mkdir(parents=True, exist_ok=True)
