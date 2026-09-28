@echo off
REM ═══════════════════════════════════════════════════════════════════
REM run_daily.bat — daily Affiliate Shorts run (Task Scheduler entry point)
REM Full pipeline with real upload + earnings summary, logged to logs\daily.log
REM ═══════════════════════════════════════════════════════════════════
set VENV=C:\Users\sakib\.cline\data\workspaces\chat\simurg\.venv\Scripts\python.exe
set ROOT=C:\Users\sakib\.cline\data\workspaces\chat\simurg\faceless-research

if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"
cd /d "%ROOT%"

echo [%date% %time%] daily run START >> logs\daily.log
"%VENV%" pipelines\pipeline_affiliate_shorts.py --products 3 --upload >> logs\daily.log 2>&1
"%VENV%" analytics\track_earnings.py --summary >> logs\daily.log 2>&1
echo [%date% %time%] daily run END >> logs\daily.log
