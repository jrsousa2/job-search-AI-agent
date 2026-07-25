# CREATES A BACKUP OF A TABLE
import sqlite3
from Repo_root import JOBS_DB
import datetime

from Summarize_db import Summarize_db

 # TODAY'S DATE
date_str = datetime.datetime.now().strftime("%Y_%m_%d")

# THE CONNECTION AND CURSOR ARE GLOBAL
conn = sqlite3.connect(JOBS_DB)
cursor = conn.cursor()

def back_up(input_table,suff):
    # ROWS
    Summarize_db(JOBS_DB,input_table,"")

    cursor.execute(f"""
    CREATE TABLE {input_table}{suff} 
    AS SELECT * FROM 
    {input_table}
    """)
    
    print(f"Table {input_table} has been backed up to {input_table}{suff}")

def restore_backup(bak_table,target_table):
    cursor.execute(f"DELETE FROM {target_table};")
    
    cursor.execute(f"""
    INSERT INTO {target_table}
    SELECT *
    FROM {bak_table};
    """)
    # APPLY CHANGES
    rows = cursor.rowcount
    conn.commit()
    # DISPLAY MSG
    print(f"Inserted {rows:,} rows into {target_table}")

# BACK UP TABLE
#back_up("jobs_hist","_v1")
if __name__=="__main__":
    # TAKE BACKUP
    # back_up("new_jobs",f"_{date_str}")
    
    # RESTORE
    restore_backup(f"new_jobs_{date_str}","new_jobs")

    # Summarize_db(JOBS_DB,"jobs_hist_v1","")
    # back_up("new_jobs","_v2")
    # Summarize_db(JOBS_DB,"new_jobs_v2","")
    # Summarize_db(JOBS_DB,"new_jobs_v2","where New=1")

    # CLOSE CONNECTION
    conn.close()

