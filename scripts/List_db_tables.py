# THIS CODE LISTS TABLES IN THE SQLITE DB
from pathlib import Path
import sqlite3

REPO_ROOT = Path(__file__).resolve().parent.parent

# Table = "new_jobs"
Table = "jobs_hist"

DB_FILE = REPO_ROOT / "Database" / "jobs.db"
EXCEL_FILE = REPO_ROOT / "Excel" / Table / ".xlsx"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# WHERE type='table'
cursor.execute("SELECT name FROM sqlite_master ")
print(cursor.fetchall())