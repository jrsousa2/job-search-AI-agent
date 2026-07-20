import sqlite3

from Repo_root import DB_FILE
from TZ_codes import get_timezone

def Update_TZ(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
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
    Update_TZ(DB_FILE)