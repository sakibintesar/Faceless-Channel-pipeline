# Faceless Content Monetization — Verified Market Research

**Platforms:** YouTube · Instagram · Facebook · Bilibili
**Research date:** 2026-09-27 · **Location:** `faceless-research\` in the SIMURG workspace

## Data provenance (what was verified, and how)

| layer | method | what it produced |
|---|---|---|
| **Official platform docs** | direct page fetches | YouTube YPP eligibility + 2027 changes, monetization policies (July 15 2025 inauthentic-content update), GenAI disclosure rules, Facebook Content Monetisation page, Instagram Bonuses page |
| **SIMURG websearch (TinyFish)** | live queries through the installed package (`websearch.search`, bundled free key) | sourced snippets for Instagram/Facebook/Bilibili eligibility + YPP thresholds + RPM benchmarks |
| **SIMURG ground check** | live `websearch.ground()` | honest-verdict demo (`"attested"`/`"thin"`/`"no_record"` — never fabricates confidence) |
| **Revenue figures** | cited third-party research (faceless.my 2026 RPM data, etc.) | **estimates** — clearly labeled, never guarantees |

> **Honest role note:** SIMURG is a *streaming-integrity monitor*, not a research engine.
> Its legitimate role in a money-making pipeline is guarding AI-generated script/caption
> streams against corruption — see `AUTOMATION-GUIDE.md`. Its `websearch`/`ground`
> features were genuinely used as the live search + fact-check layer for this research.

---

## 1 · YouTube — the highest-RPM platform

### 1.1 YPP entry requirements (current — verified from official docs)

- Follow the [channel monetization policies](https://support.google.com/youtube/answer/1311392); live in an available country/region; no active Community Guidelines strikes; 2-Step Verification on; advanced features access; one active **AdSense for YouTube** account linked ([YPP overview](https://support.google.com/youtube/answer/72851)).
- **Full monetization (ad revenue):** 1,000 subscribers **and** either 4,000 qualified public watch hours (past 365 days) or 10M qualified Shorts views (past 90 days) — confirmed by [youtube.com/creators](https://www.youtube.com/creators/earn/youtube-partner-program/) and cross-confirmed by tubebuddy.com / air.io via SIMURG websearch.
- **Fan-funding tier:** 500 subscribers + 3 qualified public uploads in the past 90 days → memberships, Super Thanks, Shopping (no ad revenue share) — per tubefilter.com; **unchanged by the 2027 update**.

### 1.2 The 2027 YPP overhaul (official blog, Aug 10 2026) — critical for planning

Source: [blog.youtube — YPP updates 2027](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/) · new terms effective **February 1, 2027**.

1. **New-creator entry thresholds raised:** new YPP applicants will need **8,000 qualified watch hours in the last 365 days, or 20 million qualified Shorts views in the last 90 days** for ads/Premium revenue sharing. *"This update won't impact creators already in YPP"* — **joining before Feb 1, 2027 locks in the old (lower) thresholds.**
2. **Shorts revenue sharing restructured:** from Feb 1 2027, creators with **10M qualified Shorts views (last 90 days)** are eligible for ads + subscription revenue sharing on Shorts. Channels below the threshold **remain in YPP, keep earning on long-form**, and Shorts sharing auto-resumes once they cross 10M again. New incentive programs (YouTube Shopping bonuses, brand-deal incentives, trend-boost earnings) create paths for below-threshold channels.
3. **Premium Lite everywhere:** dedicated revenue pools — 30% of net subscription revenue (Premium) and 60% (Premium Lite), distributed by member watch time; creator share **55% long-form / 45% Shorts**.
4. **YPP terms renewal:** accept the updated terms in YouTube Studio by **January 31, 2027** or lose full monetization (per the YPP overview page).
5. Scale context: **3M+ creators in YPP; 200B+ daily Shorts views; 1B+ hours/day watch time on TV.**

### 1.3 ⚠️ Inauthentic content policy (July 15, 2025) — the faceless-channel killer

Source: [channel monetization policies](https://support.google.com/youtube/answer/1311392) (official, verbatim):

> *"July 15, 2025: We're making a minor update to our 'repetitious content' policy to better clarify this includes content that is **repetitive or mass-produced**. We are also renaming this policy from 'repetitious content' to '**inauthentic content**.' This type of content has always been ineligible for monetization under our existing policies, where creators are rewarded for original and authentic content. There is no change to our reused content policy which reviews content like commentary, clips, compilations, and reaction videos."*

**What this means for faceless automation:** templated, mass-produced TTS-slideshow channels are demonetizable at review. Survivable faceless formats add **original commentary, narrative, or transformation** — the compilation/reaction-style review path remains explicitly reviewed (and allowed) under the reused-content policy.

### 1.4 GenAI disclosure rules (official) — mandatory compliance

Source: [Disclosing use of GenAI content](https://support.google.com/youtube/answer/14328491):

- **Must disclose** AI that: makes a real person appear to say/do something they didn't; alters footage of a real event or place; generates a realistic scene that didn't actually occur — via the **'AI use' setting** in YouTube Studio.
- Non-realistic AI content or minor aesthetic edits → **no disclosure needed**.
- **"Disclosing AI content won't limit a video's audience or impact its eligibility to earn money."** (verified, verbatim)
- **Risks of not disclosing:** manual label application, content removal, **suspension from YPP**. YouTube auto-detects via C2PA metadata and internal systems.

### 1.5 Revenue benchmarks (third-party estimates — faceless.my, 2026 RPM data)

- Small faceless channel: **$100–$500/month**; strong niche channel: **$2,000–$15,000/month**; top finance/AI/business/documentary: **$25,000+/month** when AdSense + sponsors + affiliates + products work together.
- Faceless RPM range: **$3–$40** by niche and audience. **Finance, business, AI, and software sit near the top**; entertainment, horror, gaming, general facts sit lower.
- Math: RPM = revenue per 1,000 views after YouTube's share → 100,000 monthly views at $15 RPM ≈ **$1,500/month** from ads alone.

---

## 2 · Instagram

- **No general ad revenue share** — the realistic paths are affiliate links, Gifts on Reels, Subscriptions (recurring monthly), and brand deals via **Creator Marketplace** / partnership ads.
- **Bonuses are limited-time and invitation-only** (verified: [creators.instagram.com/bonuses](https://creators.instagram.com/bonuses) — *"Bonuses are limited time and invitation-only as we build towards a sustainable programme"*), rewarding performance of **reels and photos, including carousels and single-image posts**.
- Bonus rules (verified: [help.instagram.com](https://help.instagram.com/708013994693013)): 18+; located/tax status in **Japan, South Korea, or the US**; professional account.
- Official growth tips that affect distribution: relatable/humorous content, inspire connection, **hook within the first few seconds** ([creators.instagram.com/bonuses](https://creators.instagram.com/bonuses)).
- Typical third-party requirements: Professional (Creator) account, 18+, eligible country, ~10,000 followers for most earning features (Hootsuite, ezycourse — via SIMURG websearch).

---

## 3 · Facebook

- **Content Monetisation is currently invitation-only** (verified: [creators.facebook.com/tools/facebook-content-monetization](https://creators.facebook.com/tools/facebook-content-monetization/)) — *"We're sending invitations to millions of creators this year, and we plan to offer open enrolment in the near future."* Express interest via the in-app form: **dashboard → Monetisation tab → 'Content Monetisation'**.
- **Eligible content:** public **reels (minimum 10 seconds), photos, stories, and text posts** (verified: [facebook.com/business/help/1049081556813520](https://www.facebook.com/business/help/1049081556813520)).
- **In-stream ads (ad breaks)** classic thresholds (verified: [creators.facebook.com/tools/ad-breaks/v2](https://creators.facebook.com/tools/ad-breaks/v2/)): **10,000 followers; 600,000 total minutes viewed in the last 60 days** (with at least 60,000 minutes on the Page).
- **Earnings insights** show which posts earn the most and why (verified, official page).
- Other tools: **Stars, Subscriptions, branded content, Breakthrough bonus** (official).
- **Crosspost from Instagram is officially supported** — pipe idea #4's output here.
- Meta's Partner Monetization Policies apply throughout (verified: [facebook.com/business/help/169845596919485](https://www.facebook.com/business/help/169845596919485)).

## 4 · Bilibili

- **Creator incentive eligibility: 1,000 followers or 100,000 cumulative video views** (gadgetsnow.indiatimes.com, via SIMURG websearch).
- **Pay rate:** ~$0.70 per 1,000 views is reported by some (~$700/1M views) — but *"Bilibili has not published an official fixed payment of $0.70 for every 1,000 views. Its creator compensation depends on factors including video [quality/interaction]"* (propakistani.pk, Aug 25 2026). **Treat all per-view figures as estimates.**
- **Two platforms:** bilibili.com (China, the danmaku site) and bilibili.tv (Southeast Asia) run separate creator programs.
- Original content is strongly favored; **Mandarin TTS + localized hooks**; danmaku (bullet-comment) engagement drives distribution.
- SIMURG tie-in: its script-drift features are language-agnostic — declare expected scripts (e.g., hanzi) at construction so the cross-lingual drift guard works for idea #8.

## 5 · Cross-platform comparison

| | YouTube | Instagram | Facebook | Bilibili |
|---|---|---|---|---|
| Ad rev-share | ✅ 55% long-form / 45% Shorts | ❌ (no general program) | ✅ via Content Monetisation (invite) | ✅ incentive (rate varies) |
| Entry threshold | 500-sub + 1k-sub tiers (pre-2027); 8k hrs / 20M Shorts for new creators 2027+ | invite-only (Bonuses) | invite-only (Content Monetisation); 10k followers + 600k min/60d for in-stream | 1k followers or 100k views |
| Week-one earnings path | affiliate / digital products | affiliate | affiliate / digital products | slow (threshold) |
| Faceless risk | inauthentic-content policy (July 2025) | low–moderate | low–moderate | originality enforcement |
| Best idea fit | #1, #2, #5, #6, #11, #12 | #4, #10, #6 | #3, #10, #6 | #8 |

## Sources

- **Official:** support.google.com/youtube/answer/72851 · support.google.com/youtube/answer/1311392 · support.google.com/youtube/answer/14328491 · blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn · youtube.com/creators/earn/youtube-partner-program · creators.facebook.com/tools/facebook-content-monetization · creators.facebook.com/tools/ad-breaks/v2 · facebook.com/business/help/1049081556813520 · facebook.com/business/help/169845596919485 · creators.instagram.com/bonuses · help.instagram.com/708013994693013
- **Via SIMURG websearch (TinyFish), live 2026-09-27:** tubebuddy.com · air.io · tubefilter.com (YPP thresholds cross-confirmation) · gadgetsnow.indiatimes.com (Bilibili threshold) · propakistani.pk (Bilibili $0.70 correction) · Hootsuite / ezycourse (IG requirements)
- **Third-party revenue estimates:** faceless.my/youtube/how-much-do-faceless-youtube-channels-make (2026 RPM data; their stated research base: 90 faceless channels, 350 videos)
- **Pulled with:** direct official-page fetches + SIMURG websearch/ground (live, verified in this workspace)