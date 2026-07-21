# THIS CODE LISTS TABLES IN THE SQLITE DB
# USED FOR DEVELOPMENT
import sqlite3

from Repo_root import JOBS_DB, ATS_DB
from Summarize_db import Summarize_db


def get_col_names(input_db,input_table):
    conn = sqlite3.connect(input_db)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({input_table})")
    tables = cursor.fetchall()
    # COLS
    column_names = [row[1] for row in tables]
    #print("\n")
    print(input_table.upper(),"table Cols:",column_names)
    # ROWS
    cursor.execute(f"SELECT COUNT(*) FROM {input_table}")
    row_count = cursor.fetchone()[0]
    print(input_table.upper(),"Row count:",row_count,"\n")
    conn.close() 

# WHERE type='table'
def list_db_tables(input_db):
    conn = sqlite3.connect(input_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    # ROWS PER TABLE
    for (table_name,) in tables:
        # print(table_name.upper())
        Summarize_db(input_db,f"{table_name}","")
    print()
    # COLS PER TABLE    
    for (table_name,) in tables:
        get_col_names(input_db,f"{table_name}")
    conn.close()  

def list_table_index(input_db,input_table):
    conn = sqlite3.connect(input_db)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA index_list({input_table})")
    indexes = cursor.fetchall()

    for idx in indexes:
        print("\nTable",input_table.upper(),"index:",idx)
        if idx[2] == 1:  # unique
            index_name = idx[1]
            cursor.execute(f"PRAGMA index_info({index_name})")
            print(cursor.fetchall())  
    conn.close()          

# LIST TABLES
# list_db_tables(JOBS_DB)
list_db_tables(ATS_DB)

# GET COL NAMES
# get_col_names("jobs_hist")
# get_col_names("new_jobs")

# INDEX
# list_table_index("jobs_hist")

# SUMMARIZE NEW_JOBS
# row_count = Summarize_db(JOBS_DB,"new_jobs","where New=1")

# CLOSE CONNECTION
