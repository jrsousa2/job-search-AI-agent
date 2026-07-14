# THIS CODE LISTS TABLES IN THE SQLITE DB
# USED FOR DEVELOPMENT
from pathlib import Path
import sqlite3
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.append(str(REPO_ROOT))

from scripts.check_boards import DB_FILE, summarize_db

# ADDS FLAG "NEW" TO TABLE NEW_JOBS
def add_New_flag() -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # CHECK IF COLUMN EXISTS
    cursor.execute("PRAGMA table_info(new_jobs)")
    columns = [row[1] for row in cursor.fetchall()]

    if "New" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN New INTEGER")

    cursor.execute("""
    UPDATE new_jobs
    SET New = CASE
        WHEN NOT EXISTS (
            SELECT 1
            FROM jobs_hist h
            WHERE h.final_job_id = new_jobs.final_job_id
        )
        THEN 1
        ELSE 0
    END
    """)
    # COMMITS CHANGES
    conn.commit()

    # GET NUMBER OF NEW JOBS
    row_count = summarize_db("new_jobs","where New=1")
    conn.close()

    return row_count

# ADDS FLAG "NEW" TO TABLE NEW_JOBS
new_jobs_count = add_New_flag()
# TOTAL TABLE COUNT
total_count = summarize_db("new_jobs","")