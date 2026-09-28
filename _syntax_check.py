import ast
import sys

root = r"C:\Users\sakib\.cline\data\workspaces\chat\simurg\faceless-research"
files = [
    root + r"\pipelines\common.py",
    root + r"\pipelines\pipeline_affiliate_shorts.py",
    root + r"\pipelines\crosspost.py",
    root + r"\account_setup\create_accounts.py",
    root + r"\account_setup\verify_accounts.py",
    root + r"\analytics\setup_tracking.py",
    root + r"\analytics\track_earnings.py",
]
fails = 0
for f in files:
    try:
        src = open(f, encoding="utf-8").read()
        ast.parse(src)
        print(f.split("\\")[-1], "OK -", len(src.splitlines()), "lines")
    except SyntaxError as e:
        fails += 1
        print(f.split("\\")[-1], "SYNTAX ERROR:", e)
print("ALL OK" if not fails else f"{fails} SYNTAX ERRORS")
sys.exit(1 if fails else 0)
