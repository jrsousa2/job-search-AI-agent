# THIS CODE ADDS AND/OR UPDATES THE FLAGS "NEW" AND "IS_US"
# AS A SINGLE CODE IT'S EASIER TO MAINTAIN
import sqlite3

from Repo_root import DB_FILE
from Summarize_db import Summarize_db

LOCATION_FILTER = """
    location NOT LIKE '%Canada%'
AND location NOT LIKE '%Toronto%'
AND location NOT LIKE '%Ontario%'
AND location NOT LIKE '%Cyprus%'
AND location NOT LIKE '%Germany%'
AND location NOT LIKE '%Berlin%'
AND location NOT LIKE '%Ireland%'
AND location NOT LIKE '%Dublin%'
AND location NOT LIKE '%England%'
AND location NOT LIKE '%London%'
AND location NOT LIKE '%United Kingdom%'
AND location NOT LIKE '%UK%'
AND location NOT LIKE '%Paris%'
AND location NOT LIKE '%India%'
AND location NOT LIKE '%Bangalore%'
AND location NOT LIKE '%Poland%'
AND location NOT LIKE '%Mexico%'
AND location NOT LIKE '%Europe%'
AND location NOT LIKE '%EMEA%'
AND location NOT LIKE '%LATAM%'
"""

# ADD AND UPDATE FLAG "NEW" IN TABLE NEW_JOBS
def Update_flags(DB_FILE) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # PRINTS NEW_JOBS COUNT
    print("Updating New flag...")
    # START ROWS
    print("Total before SQL update...")
    total_count = Summarize_db(DB_FILE,"new_jobs","")

    # CHECK IF COLUMN EXISTS
    cursor.execute("PRAGMA table_info(new_jobs)")
    columns = [row[1] for row in cursor.fetchall()]

    if "New" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN New INTEGER")
    else:
        # GET NUMBER OF NEW JOBS
        print("New before SQL update...")
        start_count = Summarize_db(DB_FILE,"new_jobs","where New=1")    

    # US flag
    if "is_US" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN is_US INTEGER")

    cursor.execute(f"""
    UPDATE new_jobs
    SET New = CASE
        WHEN NOT EXISTS (
            SELECT 1
            FROM jobs_hist h
            WHERE h.final_job_id = new_jobs.final_job_id
        )
        THEN 1
        ELSE 0
    END,
    is_US = CASE
        WHEN ({LOCATION_FILTER})
        THEN 1
        ELSE 0
    END
    """)
    # COMMITS CHANGES
    conn.commit()
    # GET NUMBER OF NEW JOBS
    print("New after SQL update...")
    end_count = Summarize_db(DB_FILE,"new_jobs","where New=1")
    conn.close()
    return end_count

# ADDS FLAG "NEW" TO TABLE NEW_JOBS
if __name__ == "__main__":
    new_jobs_count = Update_flags(DB_FILE)
    # TOTAL TABLE COUNT
    # Hist_count = Summarize_db(DB_FILE,"jobs_hist","")
    # New_count = Summarize_db(DB_FILE,"new_jobs","where New=1")
    # Old_count = Summarize_db(DB_FILE,"new_jobs","where New=0")