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

# CREATES JOBS HISTORY DB TABLE
# In SQLite, you do not need to specify col lengths, and values will not be truncated.
# The DB handles the lengths
# THE UNIQUE KEYS HERE ARE 
def create_jobs_hist() -> None:
    # CREATES THE HISTORY TABLE LAYOUT
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs_hist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

# UPDATES THE JOBS HISTORY TABLE (THIS IS A TEST RUN)
def update_jobs_hist() -> None:
    cols = "final_job_id, platform, company, slug, job_id, title, location, is_remote, is_hybrid, url"
    # INSERTS RECORDS
    cursor.execute(f"""
        INSERT OR IGNORE INTO jobs_hist
        ({cols})
        SELECT {cols}
        FROM new_jobs
        where is_remote=1 or is_hybrid=1
    """)
    # COMMITS
    conn.commit()

# CREATE HISTORY TABLE
# drop_table("jobs_hist")    

# CREATE HISTORY TABLE
create_jobs_hist()    

# CLOSE CONNECTION
conn.close()