# THIS CODE ADDS AND/OR UPDATES FLAGS "NEW", "IS_US" AND "SCORE"
# AS A SINGLE CODE IT'S EASIER TO MAINTAIN
import sqlite3

from Repo_root import DB_FILE
from Summarize_db import Summarize_db

loc_not_US = """
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

loc_US="""
   location LIKE '%United States%' 
OR location LIKE '%USA%' 
OR location LIKE '%U.S.%'
OR (instr(location,'US')>0 )
"""

# ADD AND UPDATE FLAG "NEW" IN TABLE NEW_JOBS
def Update_flags(DB_FILE) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # PRINTS NEW_JOBS COUNT
    print("Updating flags New/is_US...")
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
        WHEN ({loc_not_US}) or ({loc_US})
        THEN 1
        ELSE 0
    END
    """)

    # ADD SCORE COLUMN
    # US flag
    if "score" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN score INTEGER DEFAULT 0")

    # CALCULATE SCORE BASED ON KEYWORDS
    cursor.execute("""
        UPDATE new_jobs
        SET score =
          pow(10, 12) * (instr(LOWER(description),'manager')==0)
        + pow(10, 11) * (TZ='ET') 
        + pow(10, 10) * (TZ='CT') 
        + pow(10, 9) * (
                        (instr(LOWER(description),' sas ')>0) OR 
                        (instr(LOWER(description),'viya')>0)
                        )
        + pow(10, 8) * (
                        (instr(LOWER(description),'insurance')>0) OR
                        (instr(LOWER(description),'p&c')>0) OR
                        (instr(LOWER(description),'loss triangle')>0)
                        )
        + pow(10, 7) * ( 
                        (instr(LOWER(title),'data')>0) AND 
                        (
                         (instr(LOWER(title),'analyst')>0) OR 
                         (instr(LOWER(title),'analytic')>0) OR 
                         (instr(LOWER(title),'management')>0)
                         ) 
                         )
        + pow(10, 6) * (
                        (instr(LOWER(description),'sql')>0) OR
                        (instr(LOWER(description),'database')>0) OR
                        (instr(LOWER(description),'data warehouse')>0)
                        )
        + pow(10, 5) * (instr(LOWER(description),'etl')>0)
        + pow(10, 4) * ( 
                        (instr(LOWER(description),'oracle')>0) OR
                        (instr(LOWER(description),'teradata')>0) OR
                        (instr(LOWER(description),'sql server')>0)
                        )
        + pow(10, 3) * (
                        (instr(LOWER(description),'statistic')>0) OR
                        (instr(LOWER(description),'predictive')>0) OR
                        (instr(LOWER(description),' aml ')>0) OR
                        (instr(LOWER(description),' kyc ')>0) OR
                        (instr(LOWER(description),' cdd ')>0) OR
                        (instr(LOWER(description),' fcc ')>0)
                        )
        + pow(10, 2) * (instr(LOWER(description),'hadoop')>0)
        + pow(10, 1) * (instr(LOWER(description),'vba')>0)
        + pow(10, 0) * (instr(LOWER(description),'python')>0)
        + pow(10, -1) * (instr(LOWER(description),'spark')>0)
        + pow(10, -2) * (instr(LOWER(description),'databrick')>0)
        
    """)
    # COMMITS CHANGES
    conn.commit()
    conn.close()
    # GET NUMBER OF NEW JOBS
    print("New after SQL update...")
    end_count = Summarize_db(DB_FILE,"new_jobs","where New=1")
    return end_count

# ADDS FLAG "NEW" TO TABLE NEW_JOBS
if __name__ == "__main__":
    new_jobs_count = Update_flags(DB_FILE)
    # TOTAL TABLE COUNT
    # Hist_count = Summarize_db(DB_FILE,"jobs_hist","")
    # New_count = Summarize_db(DB_FILE,"new_jobs","where New=1")
    # Old_count = Summarize_db(DB_FILE,"new_jobs","where New=0")