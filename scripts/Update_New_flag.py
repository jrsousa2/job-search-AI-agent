# THIS CODE LISTS TABLES IN THE SQLITE DB
# USED FOR DEVELOPMENT
import sqlite3

from check_boards import DB_FILE
from Summarize_db import summarize_db

# ADD AND UPDATE FLAG "NEW" IN TABLE NEW_JOBS
def add_New_flag(DB_FILE) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # START ROWS
    total_count = summarize_db(DB_FILE,"new_jobs","")

    # CHECK IF COLUMN EXISTS
    cursor.execute("PRAGMA table_info(new_jobs)")
    columns = [row[1] for row in cursor.fetchall()]

    if "New" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN New INTEGER")
    else:
        # GET NUMBER OF NEW JOBS
        start_count = summarize_db(DB_FILE,"new_jobs","where New=1")    

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
    end_count = summarize_db(DB_FILE,"new_jobs","where New=1")
    conn.close()
    return end_count

# ADDS FLAG "NEW" TO TABLE NEW_JOBS
new_jobs_count = add_New_flag(DB_FILE)
# TOTAL TABLE COUNT
#total_count = summarize_db("new_jobs","")