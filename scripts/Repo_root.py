from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# THE SQLITE DB
DB_FILE = REPO_ROOT / "Database" / "jobs.db"