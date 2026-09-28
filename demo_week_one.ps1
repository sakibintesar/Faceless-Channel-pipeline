# ═══════════════════════════════════════════════════════════════════
# demo_week_one.ps1 — Week-1 end-to-end execution demo (Idea #6)
# verify accounts → produce 3 affiliate Shorts → crosspost dry-run →
# tracking setup → (optional) scheduler install
#
# Usage:  powershell -File demo_week_one.ps1 [-InstallScheduler]
# ═══════════════════════════════════════════════════════════════════
param([switch]$InstallScheduler)

$py = "C:\Users\sakib\.cline\data\workspaces\chat\simurg\.venv\Scripts\python.exe"
$root = "C:\Users\sakib\.cline\data\workspaces\chat\simurg\faceless-research"
Set-Location $root

Write-Output "════════════════════════════════════════════════════════"
Write-Output "WEEK-1 AFFILIATE SHORTS — END-TO-END DEMO"
Write-Output "════════════════════════════════════════════════════════"

# [1/5] verify accounts + tools
Write-Output "`n[1/5] verifying accounts + tools..."
& $py account_setup\verify_accounts.py
if ($LASTEXITCODE -ne 0) { Write-Output "verification failed — aborting"; exit 1 }

# [2/5] produce 3 affiliate Shorts (dry-run upload; --upload after OAuth)
Write-Output "`n[2/5] producing 3 affiliate Shorts (guarded pipeline)..."
& $py pipelines\pipeline_affiliate_shorts.py --products 3
if ($LASTEXITCODE -ne 0) { Write-Output "pipeline failed — check output above"; exit 1 }

# [3/5] crosspost dry-run (Instagram + Facebook next steps)
Write-Output "`n[3/5] crosspost plan (Instagram + Facebook Reels)..."
& $py pipelines\crosspost.py --platforms instagram,facebook

# [4/5] earnings tracking
Write-Output "`n[4/5] setting up earnings tracking..."
& $py analytics\setup_tracking.py
& $py analytics\track_earnings.py --summary

# [5/5] optional: Windows Task Scheduler
if ($InstallScheduler) {
    Write-Output "`n[5/5] installing daily scheduler task..."
    powershell -File deploy\install_scheduler.ps1 -Time 06:00
} else {
    Write-Output "`n[5/5] scheduler skipped — install with: powershell -File deploy\install_scheduler.ps1"
}

Write-Output "`n════════════════════════════════════════════════════════"
Write-Output "WEEK-1 DEMO COMPLETE"
Write-Output "  videos:  output\*_short.mp4 (1080x1920, guarded, captioned)"
Write-Output "  packs:   output\*_pack.json (SEO + affiliate link + fact-check)"
Write-Output "  upload:  OAuth setup (create_accounts.py) then pipeline --upload"
Write-Output "  tracking: analytics\earnings.db"
Write-Output "════════════════════════════════════════════════════════"
