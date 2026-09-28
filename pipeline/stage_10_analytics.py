"""
STAGE 10 — ANALYTICS: track RPM, retention, and KPI targets.

Zero-dollar cost: manual CSV import (YouTube Studio export format) +
daily JSON snapshots. The optional YouTube API path needs google libs
and an OAuth dance, so CSV is the $0 default.

KPI ladder (from the week-1 plan):
  Week 1 : 50+ videos, 100 subs, 3 product sales
  Month 1: 200+ videos, 1k subs, 20 sales
  Month 3: YPP eligible, $100-500/mo

Run:
  python -m pipeline.stage_10_analytics --template
  python -m pipeline.stage_10_analytics --import-csv analytics/manual.csv
  python -m pipeline.stage_10_analytics --snapshot
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from .common import ANALYTICS_DIR, save_json, timestamp

KPI_TARGETS = {
    "week_1": {"videos": 50, "subscribers": 100, "product_sales": 3},
    "month_1": {"videos": 200, "subscribers": 1000, "product_sales": 20},
    "month_3": {"videos": 600, "subscribers": 5000, "product_sales": 100},
}

CSV_COLUMNS = [
    "date", "video_id", "views", "likes", "comments", "watch_minutes", "revenue_usd",
]


def _to_int(value) -> int:
    """'1,200' -> 1200 (handles thousands separators in Studio exports)."""
    return int(float(str(value or 0).replace(",", "")))


def import_csv(path: str | Path) -> dict:
    """Read a manual/YouTube-Studio CSV; compute totals + RPM."""
    path = Path(path)
    if not path.exists():
        return {"ok": False, "reason": f"CSV not found: {path}"}
    totals = {"views": 0, "likes": 0, "comments": 0, "watch_minutes": 0, "revenue_usd": 0.0}
    rows = 0
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            rows += 1
            for key in ("views", "likes", "comments", "watch_minutes"):
                totals[key] += _to_int(row.get(key))
            totals["revenue_usd"] += float(str(row.get("revenue_usd") or 0).replace(",", ""))
    rpm = (totals["revenue_usd"] / totals["views"] * 1000) if totals["views"] else 0.0
    summary = {
        "ok": True,
        "rows": rows,
        "totals": totals,
        "rpm_usd_per_1k": round(rpm, 2),
        "timestamp": timestamp(),
    }
    save_json(ANALYTICS_DIR / f"summary_{timestamp()}.json", summary)
    return summary


def write_manual_template(path: str | Path = ANALYTICS_DIR / "manual.csv") -> Path:
    """Write a CSV template with the exact columns this stage expects."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(CSV_COLUMNS)
        writer.writerow([date.today().isoformat(), "demo_video_1", 1200, 45, 6, 310, 2.40])
        writer.writerow([date.today().isoformat(), "demo_video_2", 800, 30, 3, 180, 1.10])
    return path


def snapshot() -> dict:
    """Daily JSON snapshot + KPI ladder reference."""
    snap = {"date": date.today().isoformat(), "timestamp": timestamp(), "kpi_targets": KPI_TARGETS}
    save_json(ANALYTICS_DIR / f"daily_{date.today().isoformat()}.json", snap)
    return snap


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 10 — analytics")
    parser.add_argument("--import-csv", dest="import_csv", default=None)
    parser.add_argument("--template", action="store_true", help="write analytics/manual.csv")
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()

    print("[STAGE 10] ANALYTICS")
    if args.template:
        print("   template:", write_manual_template())
    if args.import_csv:
        print("   import  :", import_csv(args.import_csv))
    if args.snapshot or (not args.import_csv and not args.template):
        snap = snapshot()
        print("   snapshot:", ANALYTICS_DIR / f"daily_{snap['date']}.json")
        print("   KPI ladder:")
        for period, targets in KPI_TARGETS.items():
            print(f"     {period}: {targets}")
