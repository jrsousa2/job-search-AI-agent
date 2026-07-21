import sqlite3

from Repo_root import JOBS_DB
from TZ_codes import get_timezone

ET_states = """
    (instr(location,'CT')>0) OR location LIKE '%Connecticut%'
OR  (instr(location,'DE')>0) OR location LIKE '%Delaware%'
OR  (instr(location,'FL')>0) OR location LIKE '%Florida%'
OR  (instr(location,'GA')>0) OR location LIKE '%Georgia%'
OR  (instr(location,'IN')>0) OR location LIKE '%Indiana%'
OR  (instr(location,'KY')>0) OR location LIKE '%Kentucky%'
OR  (instr(location,'ME')>0) OR location LIKE '%Maine%'
OR  (instr(location,'MD')>0) OR location LIKE '%Maryland%'
OR  (instr(location,'MA')>0) OR location LIKE '%Massachusetts%'
OR  (instr(location,'MI')>0) OR location LIKE '%Michigan%'
OR  (instr(location,'NH')>0) OR location LIKE '%New Hampshire%'
OR  (instr(location,'NJ')>0) OR location LIKE '%New Jersey%'
OR  (instr(location,'NY')>0) OR location LIKE '%New York%'
OR  (instr(location,'NC')>0) OR location LIKE '%North Carolina%'
OR  (instr(location,'OH')>0) OR location LIKE '%Ohio%'
OR  (instr(location,'PA')>0) OR location LIKE '%Pennsylvania%'
OR  (instr(location,'RI')>0) OR location LIKE '%Rhode Island%'
OR  (instr(location,'SC')>0) OR location LIKE '%South Carolina%'
OR  (instr(location,'TN')>0) OR location LIKE '%Tennessee%'
OR  (instr(location,'VT')>0) OR location LIKE '%Vermont%'
OR  (instr(location,'VA')>0) OR location LIKE '%Virginia%'
OR  (instr(location,'WV')>0) OR location LIKE '%West Virginia%'
OR  (instr(location,'DC')>0) OR location LIKE '%District of Columbia%'
"""

def Update_TZ(JOBS_DB):
    conn = sqlite3.connect(JOBS_DB)
    cursor = conn.cursor()

    print("Updating timezone...")
    # ADD COLUMN IF MISSING
    cursor.execute("PRAGMA table_info(new_jobs)")
    columns = [row[1] for row in cursor.fetchall()]

    if "TZ" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN TZ TEXT")

    # CREATE CACHE TABLE
    cursor.execute("CREATE TABLE IF NOT EXISTS location_TZ (location TEXT PRIMARY KEY,TZ TEXT)")

    # GET DISTINCT CLEAN LOCATIONS
    cursor.execute("""
        SELECT DISTINCT lower(trim(location))
        FROM new_jobs
        WHERE location is not null
    """)

    locations = [row[0] for row in cursor.fetchall()]

    print(f"Unique locations found: {len(locations)}")

    # GET LOCATIONS NOT ALREADY PROCESSED
    cursor.execute("""
        SELECT location
        FROM location_TZ
    """)

    existing = {row[0] for row in cursor.fetchall()}

    new_locations = [loc for loc in locations if loc not in existing]

    print(f"New locations to geocode: {len(new_locations)}")


    # GEOCODE NEW LOCATIONS ONLY
    timezone_rows = []
    for location in new_locations:
        tz = get_timezone(location)
        print(location, "->", tz)
        timezone_rows.append( (location, tz))

    # SAVE CACHE
    cursor.executemany("""
        INSERT OR REPLACE INTO location_TZ
        (location, TZ)
        VALUES (?, ?)
    """, timezone_rows)


    # UPDATE JOBS TABLE
    cursor.execute("""
        UPDATE new_jobs
        SET TZ =
        (SELECT TZ
         FROM location_TZ lt
         WHERE lt.location = LOWER(TRIM(new_jobs.location))
        )""")

    # CLOSE CONNECTION
    conn.commit()
    conn.close()

    print("Timezone update complete.")

# CALL FUNCTION
if __name__ == "__main__":
    Update_TZ(JOBS_DB)