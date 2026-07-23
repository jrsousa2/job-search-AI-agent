from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

WATCHLIST_PATH = REPO_ROOT / "data" / "watchlist.json"

# AN EXTERNAL LOG FILE THAT LOGS INVALID URLs (SLUG)
Log_file = REPO_ROOT / "Logs" / "Errors_log.txt"

# THE SQLITE JOBS DB
JOBS_DB = REPO_ROOT / "Database" / "jobs.db"

# THE SQLITE ATS DB
ATS_DB = REPO_ROOT / "Database" / "ATS.db"

# THE CHROME DB
CHROME_DB = Path(r"D:\Agent\Database\Chrome_db.db")

INDUS_DB = r"D:\Agent\Database\Industry.db"