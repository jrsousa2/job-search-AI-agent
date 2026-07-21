# CREATES A BACKUP OF A TABLE
import sqlite3
from Repo_root import JOBS_DB
from Summarize_db import Summarize_db

# THE CONNECTION AND CURSOR ARE GLOBAL
conn = sqlite3.connect(JOBS_DB)
cursor = conn.cursor()

def back_up(input_table,suff):
    cursor.execute(f"CREATE TABLE {input_table}{suff} AS SELECT * FROM {input_table}")
    print(f"Table {input_table} has been backed up to {input_table}{suff}")

# BACK UP TABLE
#back_up("jobs_hist","_v1")
Summarize_db(JOBS_DB,"jobs_hist_v1","")
Summarize_db(JOBS_DB,"new_jobs","")

# back_up("new_jobs","_v2")
# Summarize_db(JOBS_DB,"new_jobs_v2","")
# Summarize_db(JOBS_DB,"new_jobs_v2","where New=1")

# CLOSE CONNECTION
conn.close()

