# USE THIS CODE TO INSPECT ANY OF THE DB TABLES
# USED FOR DEVELOPMENT
import pandas as pd
from pathlib import Path
import sqlite3

REPO_ROOT = Path(__file__).resolve().parent.parent

DB_FILE = REPO_ROOT / "Database" / "jobs.db"
# EXCEL_FILE = REPO_ROOT / "Excel" / Table / ".xlsx"

# EXPORT A DB TABLE TO EXCEL
def Exp_db_to_Excel(DB_FILE, input_table: str, suff: str, sql_filter: str) -> None:
    output_file = f"{input_table}{suff}.xlsx"
    EXCEL_FILE = REPO_ROOT / "Excel" / output_file
    conn = sqlite3.connect(DB_FILE)

    # SAVE QUERY OUTPUT TO A DF
    df = pd.read_sql_query(f"SELECT * FROM {input_table} {sql_filter}", conn)
    df.to_excel(EXCEL_FILE, index=False)
    # DISPLAY MSG
    print("Table",input_table,"exported to",output_file)
    conn.close()

# MAIN CODE
if __name__ == "__main__":
    # exp_to_excel("new_jobs","3","")
    # Exp_db_to_Excel(DB_FILE,"new_jobs","Test","")
    Exp_db_to_Excel(DB_FILE,"new_jobs","(flags)2","")

    # EXPORT ALREADY EVALUATED TO EXCEL
    # Exp_db_to_excel(DB_FILE,"new_jobs_bak","(orig)","")
    # Exp_db_to_excel(DB_FILE,"jobs_hist","(orig)","")