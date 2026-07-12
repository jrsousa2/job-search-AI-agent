# USE THIS CODE TO INSPECT ANY OF THE DB TABLES
# USED FOR DEVELOPMENT
import pandas as pd
from pathlib import Path
import sqlite3

REPO_ROOT = Path(__file__).resolve().parent.parent

Table = "new_jobs"
# Table = "jobs_hist"

DB_FILE = REPO_ROOT / "Database" / "jobs.db"
EXCEL_FILE = REPO_ROOT / "Excel" / Table / ".xlsx"

conn = sqlite3.connect(DB_FILE)

df = pd.read_sql_query(f"SELECT * FROM {Table}", conn)

df.to_excel(EXCEL_FILE, index=False)