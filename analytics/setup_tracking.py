"""
setup_tracking.py — create the earnings SQLite (analytics/earnings.db).

Tables:
  videos    — every produced/uploaded video (attribution)
  earnings  — every observed earning event (first-dollar detection)

Usage: python analytics/setup_tracking.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipelines"))
from common import OUT, load_env  # noqa: E402

load_env()

DB = Path(__file__).resolve().parent / "earnings.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discovered_at TEXT NOT NULL,
    asin TEXT, keyword TEXT, platform TEXT,
    file_path TEXT, url TEXT, guard_state TEXT
);
CREATE TABLE IF NOT EXISTS earnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    video_id INTEGER REFERENCES videos(id),
    platform TEXT NOT NULL,
    source TEXT NOT NULL,          -- amazon_associates | gumroad | ypp | stars...
    amount REAL NOT NULL,
    note TEXT
);
"""


def main() -> int:
    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA)

    # seed: register every rendered video already in output/
    import json
    n = 0
    for p in sorted(OUT.glob("*_pack.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        import datetime
        conn.execute(
            "INSERT INTO videos (discovered_at, asin, keyword, platform, "
            "file_path, url, guard_state) VALUES (?,?,?,?,?,?,?)",
            (datetime.datetime.now().isoformat(), d.get("asin"),
             d.get("title", "").replace("Honest Review: ", "").split(" —")[0],
             "youtube", d.get("video"), d.get("upload", ""), d.get("guard_state")))
        n += 1
    conn.commit()
    conn.close()
    print(f"✅ {DB} ready ({n} video(s) registered)")
    print("next: python analytics/track_earnings.py --summary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
