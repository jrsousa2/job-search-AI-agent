# THIS CODE MANUALLY ADDS A FIELD
# USED FOR DEVELOPMENT
from pathlib import Path
import sqlite3

REPO_ROOT = Path(__file__).resolve().parent.parent

DB_FILE = REPO_ROOT / "Database" / "jobs.db"

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