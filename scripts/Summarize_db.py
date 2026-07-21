# SUMMARIZES A DATABASE TABLE
import sqlite3

from Repo_root import JOBS_DB

# GET NUMBER OF ROWS FROM TABLE WITH A FILTER
def Summarize_db(JOBS_DB:str, input_table: str, sql_filter: str)->int:
    conn = sqlite3.connect(JOBS_DB)
    cursor = conn.cursor()
    # ROWS
    cursor.execute(f"SELECT COUNT(*) FROM {input_table} {sql_filter}")
    row_count = cursor.fetchone()[0]
    # DISPLAYS MSG
    print("Table",input_table.upper(),":",row_count,"rows",sql_filter)
    # CLOSE CONNECTION
    conn.close()
    # RETURN ROWS
    return row_count

# PRINTS JOBS_HIST COUNT
if __name__ == "__main__": 
    Summarize_db(JOBS_DB,"jobs_hist","where 1")