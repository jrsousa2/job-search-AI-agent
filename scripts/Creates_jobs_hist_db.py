# RUN THIS CODE ONLY ONCE
# CREATES THE JOBS HISTORY DB TABLE FOR THE FIRST TIME.
# USE IT TO DROP AND RECREATE THE HIST TABLE TOO (IF THE LAYOUT CHANGES)

from pathlib import Path
import sqlite3

from check_boards import DB_FILE
from Summarize_db import Summarize_db

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


# DROP AND RECREATE HISTORY TABLE
drop_table("jobs_hist")
create_jobs_hist()

# UPDATES JOBS_HIST MANUALLY
# update_jobs_hist()
# Summarize_db("jobs_hist","")

# CLOSE CONNECTION
conn.close()

