# USED FOR TESTING
import sqlite3

from Repo_root import JOBS_DB
from Summarize_db import Summarize_db

# UPDATES THE JOBS HISTORY TABLE
# UNIQUE KEY IS final_job_id (IGNORE WON'T INSERT DUPLICATES)
def Update_jobs_hist(JOBS_DB, input_table) -> None:
    conn = sqlite3.connect(JOBS_DB)
    cursor = conn.cursor()
    # PRINTS NEW_JOBS COUNT
    print("Updating jobs_hist...")
    start_count = Summarize_db(JOBS_DB,"jobs_hist","")
    cols = "final_job_id, platform, company, slug, job_id, title, location, is_remote, is_hybrid, url"
    # INSERTS RECORDS
    cursor.execute(f"""
        INSERT OR IGNORE INTO jobs_hist
        ({cols})
        SELECT {cols}
        FROM {input_table}
        where is_remote=1 or is_hybrid=1
    """)
    # COMMITS
    conn.commit()
    conn.close()
    # GET STATS
    end_count = Summarize_db(JOBS_DB,"jobs_hist","")
    print("Start count:",start_count)
    print("End count:",end_count)
    print("Added",end_count-start_count,"records to jobs_hist table")

# UPDATE JOBS_HIST FROM SPECIFIED INPUT TABLE
if __name__ == "__main__": 
    Update_jobs_hist(JOBS_DB,"new_jobs")

# TOTAL TABLE COUNT
# total_count = Summarize_db(JOBS_DB,"jobs_hist","") 

# PRINTS NEW_JOBS COUNT
# Summarize_db(JOBS_DB,"new_jobs","where New=0")