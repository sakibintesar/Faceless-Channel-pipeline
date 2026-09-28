"""
create_accounts.py — Phase 0/1: create every account Idea #6 needs.

Honest split:
  * ALL account signups are MANUAL (browser, human identity) — this script
    opens each URL with notes and waits for you.
  * What IS automated: .env scaffolding, opening the right pages in order,
    and post-setup verification (verify_accounts.py).

Usage:
    python create_accounts.py               # interactive (opens browser)
    python create_accounts.py --no-browser  # just print the checklist
"""
from __future__ import annotations

import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / ".env.template"
ENV_FILE = ROOT / ".env"

# Ordered: what the first dollar actually depends on first.
ACCOUNTS = [
    ("google", "https://accounts.google.com/signup",
     "Google account (brand account for YouTube). Enable 2-Step Verification "
     "immediately — YPP requires it."),
    ("youtube_channel", "https://www.youtube.com/channel_switcher",
     "Create the YouTube channel from the Google account. ⏰ Join YPP BEFORE "
     "2027-02-01 to lock the old thresholds (1k subs + 4k watch-hrs) — after "
     "that, new creators need 8,000 hrs / 20M Shorts views."),
    ("youtube_data_api", "https://console.cloud.google.com/apis/library/youtube.googleapis.com",
     "Enable YouTube Data API v3 → APIs & Services → Credentials → Create "
     "OAuth 2.0 Client ID (Desktop app) → download client_secret.json into "
     "faceless-research/. Default quota ≈ 6 uploads/day."),
    ("meta_business", "https://business.facebook.com/overview",
     "Meta Business Portfolio → add a Facebook Page. Then dashboard → "
     "Monetisation tab → Content Monetisation → EXPRESS INTEREST NOW "
     "(invite-only, months-long wait)."),
    ("instagram_pro", "https://www.instagram.com/accounts/switch_to_professional_account/",
     "Convert to Professional (Creator) account → link it to the Facebook "
     "Page in Meta Business Suite. Note: IG Bonuses are invite-only and "
     "limited to US/JP/KR tax residency — affiliate is your path."),
    ("amazon_associates", "https://affiliate-program.amazon.com/",
     "Sign up → complete tax interview (W-8BEN for Bangladesh) → get your "
     "Associate Tag (e.g. yourname-20) → put it in .env. PAAPI access comes "
     "after 3 qualifying sales in 180 days; keep 3 sales/180d to stay active."),
    ("gumroad", "https://gumroad.com/",
     "Digital-product delivery (idea #7). Connect Stripe or PayPal. Create "
     "one product — a prompt pack or template — no threshold to earn."),
    ("pexels", "https://www.pexels.com/api/",
     "Instant free key for B-roll. Paste into .env: PEXELS_API_KEY=..."),
    ("pixabay", "https://pixabay.com/api/docs/",
     "Instant free key (fallback footage). Paste into .env: PIXABAY_API_KEY=..."),
]


def scaffold_env() -> None:
    if ENV_FILE.exists():
        print(f"[env] {ENV_FILE.name} already exists — kept")
        return
    if TEMPLATE.exists():
        ENV_FILE.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[env] created {ENV_FILE} from template — fill in your keys")
    else:
        print(f"[env] template missing: {TEMPLATE}")


def main() -> None:
    scaffold_env()
    print("\n=== ACCOUNT CREATION CHECKLIST (in first-dollar order) ===")
    no_browser = "--no-browser" in sys.argv
    for name, url, notes in ACCOUNTS:
        print(f"\n[{name}] {url}")
        print(f"  → {notes}")
        if not no_browser:
            webbrowser.open(url)
            try:
                input("  press Enter after completing this one...")
            except EOFError:
                pass
    print("\n✅ Checklist done. Next: python account_setup/verify_accounts.py")


if __name__ == "__main__":
    main()
