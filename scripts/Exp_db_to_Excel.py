# USE THIS CODE TO INSPECT ANY OF THE DB TABLES
# USED FOR DEVELOPMENT
import pandas as pd
from pathlib import Path
import sqlite3

from Repo_root import REPO_ROOT, JOBS_DB, ATS_DB, INDUS_DB

def Exp_db_to_Excel_conn(conn, input_table: str, suff: str, sql_filter: str) -> None:
    output_file = f"{input_table}{suff}.xlsx"
    EXCEL_FILE = REPO_ROOT / "Excel" / output_file

    # SAVE QUERY OUTPUT TO A DF
    df = pd.read_sql_query(f"SELECT * FROM {input_table} {sql_filter}", conn)
    df.to_excel(EXCEL_FILE, index=False)
    # DISPLAY MSG
    print("Table",input_table,"exported to",output_file)

# EXPORT A DB TABLE TO EXCEL
def Exp_db_to_Excel(JOBS_DB, input_table: str, suff: str, sql_filter: str) -> None:
    output_file = f"{input_table}{suff}.xlsx"
    EXCEL_FILE = REPO_ROOT / "Excel" / output_file
    conn = sqlite3.connect(JOBS_DB)

    # SAVE QUERY OUTPUT TO A DF
    df = pd.read_sql_query(f"SELECT * FROM {input_table} {sql_filter}", conn)
    df.to_excel(EXCEL_FILE, index=False)
    # DISPLAY MSG
    print("Table",input_table,"exported to",output_file)
    conn.close()

# MAIN CODE
if __name__ == "__main__":
    # Exp_db_to_Excel(JOBS_DB,"new_jobs","(post)","WHERE (is_remote = 1 OR is_hybrid = 1) and New = 1 and is_US = 1")
    Exp_db_to_Excel(JOBS_DB,"new_jobs","(guide)","")

    # Exp_db_to_Excel(INDUS_DB,"Industry","(new)","")

    # EXPORT ATS TABLES
    # Exp_db_to_Excel(ATS_DB,"Ashby","(new)","")
    # Exp_db_to_Excel(ATS_DB,"Workday","(new)","")
    # Exp_db_to_Excel(ATS_DB,"Lever","(new)","")
    # Exp_db_to_Excel(ATS_DB,"Greenhouse","(new)","")
    # Exp_db_to_Excel(ATS_DB,"Watchlist","(new)","")
