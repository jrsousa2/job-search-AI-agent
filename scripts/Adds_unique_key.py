# THIS CODE MANUALLY ADDS A FIELD
# USED ONLY ONCE FOR DEVELOPMENT
import sqlite3

from check_boards_old import DB_FILE

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create new table with final_job_id as first column
cursor.execute("""
CREATE TABLE new_jobs_temp AS
SELECT
    CASE
        WHEN job_id IS NOT NULL AND job_id != ''
            THEN lower(trim(platform || '|' || company || '|' || job_id))
        ELSE lower(trim(platform || '|' || company || '|' || title))
    END AS final_job_id,
    *
FROM new_jobs
""")

# Replace old table
cursor.execute("DROP TABLE new_jobs")

cursor.execute("""
ALTER TABLE new_jobs_temp
RENAME TO new_jobs
""")

conn.commit()

# CLOSE CONNECTION
conn.close()