# THIS CODE LISTS TABLES IN THE SQLITE DB
# USED FOR DEVELOPMENT
import sqlite3

from Repo_root import DB_FILE
from Summarize_db import Summarize_db

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# WHERE type='table'
def list_db_tables():
    cursor.execute("SELECT name FROM sqlite_master")
    # PRINT
    for (table_name,) in cursor.fetchall():
        print(table_name.upper())

def get_col_names(input_table):
    cursor.execute(f"PRAGMA table_info({input_table})")
    # COLS
    column_names = [row[1] for row in cursor.fetchall()]
    #print("\n")
    print(input_table.upper(),"table Cols:",column_names)
    # ROWS
    cursor.execute(f"SELECT COUNT(*) FROM {input_table}")
    row_count = cursor.fetchone()[0]
    print(input_table.upper(),"Row count:",row_count,"\n")

def list_table_index(input_table):
    cursor.execute(f"PRAGMA index_list({input_table})")
    indexes = cursor.fetchall()

    for idx in indexes:
        print("\nTable",input_table.upper(),"index:",idx)
        if idx[2] == 1:  # unique
            index_name = idx[1]
            cursor.execute(f"PRAGMA index_info({index_name})")
            print(cursor.fetchall())    

# LIST TABLES
# list_db_tables()

# GET COL NAMES
get_col_names("jobs_hist")
get_col_names("new_jobs")

# INDEX
list_table_index("jobs_hist")

# SUMMARIZE NEW_JOBS
row_count = Summarize_db(DB_FILE,"new_jobs","where New=1")

# CLOSE CONNECTION
conn.close()