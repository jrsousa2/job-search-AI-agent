# USED FOR TESTING
import sqlite3
# from check_boards import REPO_ROOT
from check_boards import DB_FILE
from check_boards import summarize_db

# UPDATES THE JOBS HISTORY TABLE
# UNIQUE KEY IS final_job_id (IGNORE WON'T INSERT DUPLICATES)
def update_jobs_hist(input_table) -> None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    start_count = summarize_db("jobs_hist","")
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
    end_count = summarize_db("jobs_hist","")
    print("Start count:",start_count)
    print("End count:",end_count)
    print("Added",end_count-start_count,"records to jobs_hist table")

# UPDATE JOBS_HIST FROM SPECIFIED INPUT TABLE
update_jobs_hist("new_jobs_bak")   

# TOTAL TABLE COUNT
total_count = summarize_db("jobs_hist","") 

# PRINTS NEW_JOBS COUNT
# summarize_db("new_jobs","where New=0")