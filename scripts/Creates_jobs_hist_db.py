# RUN THIS CODE ONLY ONCE
# CREATES THE JOBS HISTORY DB TABLE FOR THE FIRST TIME.
# USE IT TO DROP THAT TABLE TOO (IF THE LAYOUT CHANGES)

from __future__ import annotations

from pathlib import Path

import sqlite3

REPO_ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_PATH = REPO_ROOT / "data" / "watchlist.json"

DB_FILE = REPO_ROOT / "Database" / "jobs.db"

# THE CONNECTION AND CURSOR ARE GLOBAL
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# IF TABLE jobs_hist LAYOUT IS MODIFIED, DROP AND RECREATE
def drop_table(input_table) -> None:
    # DROP TABLE
    cursor.execute(f"DROP TABLE IF EXISTS {input_table}")
    # COMMIT THE COMMAND
    conn.commit()
    print("Table jobs_hist dropped!")

# CREATES JOBS HISTORY DB TABLE
# In SQLite, you do not need to specify col lengths, and values will not be truncated.
# The DB handles the lengths
# THE UNIQUE KEYS HERE ARE 
def create_jobs_hist() -> None:
    # CREATES THE HISTORY TABLE LAYOUT
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs_hist (
        final_job_id TEXT NOT NULL,
        platform TEXT NOT NULL,
        company TEXT NOT NULL,
        slug TEXT,
        job_id TEXT,
        title TEXT NOT NULL,
        location TEXT,
        is_remote BOOLEAN,
        is_hybrid BOOLEAN,
        url TEXT,

        UNIQUE(final_job_id))
    """)
    # COMMIT THE COMMAND
    conn.commit()
    print("Table jobs_hist created!")

def back_up(input_table):
    cursor.execute(f"CREATE TABLE {input_table}_bak AS SELECT * FROM {input_table}")
    print("Table",input_table,"has been backed up")

# ADD NEW FLAG TO TABLE NEW_JOBS
def add_New_flag():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # ADD COL "NEW" TO TABLE
    # cursor.execute("ALTER TABLE new_jobs ADD COLUMN New INTEGER")

    cursor.execute("""
    UPDATE new_jobs as a
    SET New = CASE
        WHEN EXISTS (
            SELECT 1
            FROM jobs_hist h
            WHERE h.final_job_id = a.final_job_id
        )
        THEN 1
        ELSE 0
    END
    """)
    # COMMITS CHANGES
    conn.commit()

def summarize_db(input_table: str,filter: str)->int:
    # GET NUMBER OF NEW JOBS
    cursor.execute(f"SELECT COUNT(*) FROM {input_table} {filter}")
    row_count = cursor.fetchone()[0]
    print("Table",input_table,":",row_count,"rows")

    return row_count

# DROP AND RECREATE HISTORY TABLE
# drop_table("jobs_hist")
# create_jobs_hist()

# UPDATES JOBS_HIST MANUALLY
# update_jobs_hist()
# summarize_db("jobs_hist","")

# ADD NEW FLAG TO NEW_JOBS AND SUMMARIZE TABLE
# add_New_flag()
# summarize_db("new_jobs","where New=0")

# BACK UP TABLE
# back_up("new_jobs")
# summarize_db("new_jobs_bak","")

# CLOSE CONNECTION
conn.close()

