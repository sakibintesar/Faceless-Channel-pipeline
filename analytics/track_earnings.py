"""
track_earnings.py — first-dollar tracking + Amazon Associates CSV import.

Usage:
    python analytics/track_earnings.py --log 1 youtube amazon_associates 4.31
    python analytics/track_earnings.py --import-csv path\\to\\amazon_report.csv
    python analytics/track_earnings.py --summary

Amazon Associates: dashboard → Reports → 'Earnings summary' → export CSV.
Columns differ per marketplace; this parser looks for date + item + earnings
columns case-insensitively (amazon-standard exports are supported).
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipelines"))
from common import load_env  # noqa: E402

load_env()
DB = Path(__file__).resolve().parent / "earnings.db"


def _conn() -> sqlite3.Connection:
    if not DB.exists():
        print("earnings.db missing — run analytics/setup_tracking.py first")
        sys.exit(1)
    return sqlite3.connect(DB)


def log_earnings(video_id: int | None, platform: str, source: str,
                 amount: float, note: str = "") -> None:
    conn = _conn()
    conn.execute("INSERT INTO earnings (date, video_id, platform, source, "
                 "amount, note) VALUES (?,?,?,?,?,?)",
                 (datetime.now().isoformat(), video_id, platform, source,
                  amount, note))
    conn.commit()
    conn.close()
    if amount > 0:
        print(f"💰 logged: ${amount:.2f} ({platform}/{source})"
              + (f" — {note}" if note else ""))


def import_amazon_csv(path: str) -> int:
    """Parse an Amazon Associates earnings CSV → earnings rows."""
    conn = _conn()
    n, total = 0, 0.0
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        cols = {k.lower().strip(): k for k in (reader.fieldnames or [])}
        date_k = next((cols[c] for c in cols if "date" in c), None)
        amt_k = next((cols[c] for c in cols if ("earn" in c or "commission" in c
                                                or "revenue" in c)), None)
        item_k = next((cols[c] for c in cols if "item" in c or "asin" in c), None)
        if not amt_k:
            print(f"no earnings/commission column found in {reader.fieldnames}")
            return 0
        for row in reader:
            try:
                amt = float(str(row[amt_k]).replace("$", "").replace(",", ""))
            except ValueError:
                continue
            if amt == 0:
                continue
            conn.execute("INSERT INTO earnings (date, video_id, platform, "
                         "source, amount, note) VALUES (?,?,?,?,?,?)",
                         (str(row.get(date_k, "")) if date_k else
                          datetime.now().date().isoformat(), None,
                          "amazon", "amazon_associates", amt,
                          str(row.get(item_k, "")) if item_k else ""))
            n += 1
            total += amt
    conn.commit()
    conn.close()
    print(f"imported {n} earning row(s), total ${total:.2f}")
    return n


def summary() -> None:
    conn = _conn()
    rows = conn.execute(
        "SELECT date, platform, source, amount, note FROM earnings "
        "ORDER BY date").fetchall()
    total = sum(r[3] for r in rows)
    print("═" * 60)
    print(f"EARNINGS SUMMARY — {len(rows)} event(s), total ${total:.2f}")
    print("═" * 60)
    for r in rows[:20]:
        print(f"  {str(r[0])[:10]}  {r[1]:<10} {r[2]:<20} ${r[3]:.2f}"
              + (f"  ({r[4]})" if r[4] else ""))
    vids = conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
    print(f"\nvideos registered: {vids}")
    if total > 0:
        first = rows[0]
        print(f"🎉 FIRST DOLLAR: ${first[3]:.2f} on {str(first[0])[:10]} "
              f"({first[1]}/{first[2]})")
    else:
        print("no earnings yet — keep publishing; affiliate needs clicks, "
              "YPP needs thresholds")
    conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="first-dollar tracking")
    ap.add_argument("--log", nargs=4, metavar=("VIDEO_ID", "PLATFORM", "SOURCE", "AMOUNT"))
    ap.add_argument("--note", default="")
    ap.add_argument("--import-csv", dest="csv")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()
    if args.csv:
        import_amazon_csv(args.csv)
    elif args.log:
        log_earnings(int(args.log[0]) if args.log[0] != "none" else None,
                     args.log[1], args.log[2], float(args.log[3]), args.note)
    summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
