# RUN THIS CODE ONLY ONCE
# IT WILL CREATE THE JOBS HISTORY DB TABLE FOR THE FIRST TIME.

from __future__ import annotations

from pathlib import Path

import sqlite3

REPO_ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_PATH = REPO_ROOT / "data" / "watchlist.json"
# EVALUATED_CSV = REPO_ROOT / "data" / "evaluated-jobs.csv"


# DB_FILE = "Database/jobs.db"
DB_FILE = REPO_ROOT / "Database" / "jobs.db"

# CREATES JOBS HISTORY DB TABLE
def create_history_jobs() -> None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # CREATES THE HISTORY TABLE LAYOUT
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs_hist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        platform TEXT NOT NULL,
        company TEXT NOT NULL,
        slug TEXT,
        job_id TEXT,
        title TEXT NOT NULL,
        location TEXT,
        is_remote BOOLEAN,
        is_hybrid BOOLEAN,
        url TEXT,

        UNIQUE(platform, company, job_id),
        UNIQUE(platform, url),
    )
    """)
    
    # COMMIT THE COMMAND
    conn.commit()
    conn.close()

# UPDATES THE JOBS HISTORY TABLE (THIS IS A TEST RUN)
def update_history_jobs() -> None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO jobs_hist (
            platform,
            company,
            slug,
            job_id,
            title,
            location,
            is_remote,
            is_hybrid,
            url
        )
        SELECT
            platform,
            company,
            slug,
            job_id,
            title,
            location,
            is_remote,
            is_hybrid,
            url
        FROM new_jobs
    """)

    conn.commit()
    conn.close()    