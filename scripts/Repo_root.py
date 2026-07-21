from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# THE SQLITE JOBS DB
JOBS_DB = REPO_ROOT / "Database" / "jobs.db"

# THE SQLITE ATS DB
ATS_DB = REPO_ROOT / "Database" / "ATS.db"
