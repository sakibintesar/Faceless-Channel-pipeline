# ═══════════════════════════════════════════════════════════════════
# install_scheduler.ps1 — register the daily task with Windows Task Scheduler
# Usage:  powershell -File deploy\install_scheduler.ps1 -Time 06:00
# Remove: schtasks /delete /tn "AffiliateShortsDaily" /f
# ═══════════════════════════════════════════════════════════════════
param([string]$Time = "06:00")

$root = "C:\Users\sakib\.cline\data\workspaces\chat\simurg\faceless-research"
$bat = Join-Path $root "deploy\run_daily.bat"

if (-not (Test-Path $bat)) {
    Write-Output "run_daily.bat not found at $bat"
    exit 1
}

schtasks /create /tn "AffiliateShortsDaily" /tr "`"$bat`"" /sc daily /st $Time /f
Write-Output ""
Write-Output "Task 'AffiliateShortsDaily' registered — runs daily at $Time"
Write-Output "Check status: schtasks /query /tn `"AffiliateShortsDaily`" /v"
Write-Output "Run now:      schtasks /run /tn `"AffiliateShortsDaily`""
Write-Output "Remove:       schtasks /delete /tn `"AffiliateShortsDaily`" /f"
Write-Output "Log file:     $root\logs\daily.log"
