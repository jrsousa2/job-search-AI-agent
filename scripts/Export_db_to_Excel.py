import pandas as pd
from pathlib import Path
import sqlite3

REPO_ROOT = Path(__file__).resolve().parent.parent
# DB_FILE = "Database/jobs.db"
DB_FILE = REPO_ROOT / "Database" / "jobs.db"
EXCEL_FILE = REPO_ROOT / "Excel" / "New_jobs.xlsx"

conn = sqlite3.connect(DB_FILE)

df = pd.read_sql_query("SELECT * FROM new_jobs", conn)

df.to_excel(r"D:\Agent\Excel\New_jobs.xlsx", index=False)