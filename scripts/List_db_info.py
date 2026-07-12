# THIS CODE LISTS TABLES IN THE SQLITE DB
# USED FOR DEVELOPMENT
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
def list_db_tables():
    cursor.execute("SELECT name FROM sqlite_master")
    # PRINT
    for (table_name,) in cursor.fetchall():
        print(table_name)

def get_col_names(input_table):
    cursor.execute(f"PRAGMA table_info({input_table})")
    # COLS
    column_names = [row[1] for row in cursor.fetchall()]
    print("\n",input_table,"table Cols:",column_names)
    # ROWS
    cursor.execute(f"SELECT COUNT(*) FROM {input_table}")
    row_count = cursor.fetchone()[0]
    print(input_table,"Row count:",row_count,"\n")

# LIST TABLES
# list_db_tables()

# GET COL NAMES
get_col_names("jobs_hist")
get_col_names("new_jobs")

# CLOSE CONNECTION
conn.close()