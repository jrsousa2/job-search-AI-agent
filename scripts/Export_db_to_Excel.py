# USE THIS CODE TO INSPECT ANY OF THE DB TABLES
# USED FOR DEVELOPMENT
import pandas as pd
from pathlib import Path
import sqlite3

REPO_ROOT = Path(__file__).resolve().parent.parent

DB_FILE = REPO_ROOT / "Database" / "jobs.db"
# EXCEL_FILE = REPO_ROOT / "Excel" / Table / ".xlsx"

# EXPORT A DB TABLE TO EXCEL
def exp_to_excel(input_table: str, suff: str, filter: str) -> None:
    EXCEL_FILE = REPO_ROOT / "Excel" / f"{input_table}{suff}.xlsx"
    conn = sqlite3.connect(DB_FILE)

    # SAVE QUERY OUTPUT TO A DF
    df = pd.read_sql_query(f"SELECT * FROM {input_table} {filter}", conn)
    df.to_excel(EXCEL_FILE, index=False)

    print("Table",input_table,"exported to Excel")
    conn.close()

# exp_to_excel("new_jobs","3","")
#exp_to_excel("new_jobs","3","")

# EXPORT ALREADY EVALUATED TO EXCEL
exp_to_excel("new_jobs_bak","(orig)","")