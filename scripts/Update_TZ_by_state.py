import sqlite3

from Repo_root import DB_FILE

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

ET_cities = """
    location LIKE '%Alexandria%'
OR  location LIKE '%Albany%'
OR  location LIKE '%Ann Arbor%'
OR  location LIKE '%Arlington%'
OR  location LIKE '%Atlanta%'
OR  location LIKE '%Baltimore%'
OR  location LIKE '%Boston%'
OR  location LIKE '%Buffalo%'
OR  location LIKE '%Charleston%'
OR  location LIKE '%Charlotte%'
OR  location LIKE '%Cincinnati%'
OR  location LIKE '%Cleveland%'
OR  location LIKE '%Columbus%'
OR  location LIKE '%Detroit%'
OR  location LIKE '%Durham%'
OR  location LIKE '%Fort Lauderdale%'
OR  location LIKE '%Hartford%'
OR  location LIKE '%Indianapolis%'
OR  location LIKE '%Jacksonville%'
OR  location LIKE '%Jersey City%'
OR  location LIKE '%Knoxville%'
OR  location LIKE '%Lexington%'
OR  location LIKE '%Louisville%'
OR  location LIKE '%Miami%'
OR  location LIKE '%Nashville%'
OR  location LIKE '%New York%'
OR  location LIKE '%Newark%'
OR  location LIKE '%Norfolk%'
OR  location LIKE '%NYC%'
OR  location LIKE '%Orlando%'
OR  location LIKE '%Philadelphia%'
OR  location LIKE '%Pittsburgh%'
OR  location LIKE '%Providence%'
OR  location LIKE '%Raleigh%'
OR  location LIKE '%Richmond%'
OR  location LIKE '%Rochester%'
OR  location LIKE '%Savannah%'
OR  location LIKE '%Tampa%'
OR  location LIKE '%Washington%'
OR  location LIKE '%Washington DC%'
OR  location LIKE '%West Palm Beach%'
"""

CT_states = """
    (instr(location,'AL')>0) OR location LIKE '%Alabama%'
OR  (instr(location,'AR')>0) OR location LIKE '%Arkansas%'
OR  (instr(location,'IA')>0) OR location LIKE '%Iowa%'
OR  (instr(location,'IL')>0) OR location LIKE '%Illinois%'
OR  (instr(location,'KS')>0) OR location LIKE '%Kansas%'
OR  (instr(location,'LA')>0) OR location LIKE '%Louisiana%'
OR  (instr(location,'MN')>0) OR location LIKE '%Minnesota%'
OR  (instr(location,'MO')>0) OR location LIKE '%Missouri%'
OR  (instr(location,'MS')>0) OR location LIKE '%Mississippi%'
OR  (instr(location,'NE')>0) OR location LIKE '%Nebraska%'
OR  (instr(location,'ND')>0) OR location LIKE '%North Dakota%'
OR  (instr(location,'OK')>0) OR location LIKE '%Oklahoma%'
OR  (instr(location,'SD')>0) OR location LIKE '%South Dakota%'
OR  (instr(location,'WI')>0) OR location LIKE '%Wisconsin%'
"""

CT_cities = """
    location LIKE '%Chicago%'
OR  location LIKE '%Dallas%'
OR  location LIKE '%Fort Worth%'
OR  location LIKE '%Houston%'
OR  location LIKE '%Austin%'
OR  location LIKE '%San Antonio%'
OR  location LIKE '%Minneapolis%'
OR  location LIKE '%St. Paul%'
OR  location LIKE '%Saint Paul%'
OR  location LIKE '%St Louis%'
OR  location LIKE '%St. Louis%'
OR  location LIKE '%Kansas City%'
OR  location LIKE '%Omaha%'
OR  location LIKE '%Oklahoma City%'
OR  location LIKE '%Tulsa%'
OR  location LIKE '%New Orleans%'
OR  location LIKE '%Baton Rouge%'
OR  location LIKE '%Little Rock%'
OR  location LIKE '%Des Moines%'
OR  location LIKE '%Madison%'
OR  location LIKE '%Milwaukee%'
OR  location LIKE '%Wichita%'
OR  location LIKE '%Lincoln%'
OR  location LIKE '%Sioux Falls%'
"""

PT_states = """
    (instr(location,'CA')>0) OR location LIKE '%California%'
OR  (instr(location,'WA')>0) OR location LIKE '%Washington%'
OR  (instr(location,'OR')>0) OR location LIKE '%Oregon%'
OR  (instr(location,'NV')>0) OR location LIKE '%Nevada%'
"""

PT_cities = """
    location LIKE '%San Francisco%'
OR  location LIKE '%SF%'
OR  location LIKE '%San Jose%'
OR  location LIKE '%Silicon Valley%'
OR  location LIKE '%Palo Alto%'
OR  location LIKE '%Mountain View%'
OR  location LIKE '%Sunnyvale%'
OR  location LIKE '%Santa Clara%'
OR  location LIKE '%Fremont%'
OR  location LIKE '%Oakland%'
OR  location LIKE '%Berkeley%'
OR  location LIKE '%Sacramento%'
OR  location LIKE '%San Mateo%'
OR  location LIKE '%Redwood City%'
OR  location LIKE '%Foster City%'
OR  location LIKE '%Irvine%'
OR  location LIKE '%Los Angeles%'
OR  location LIKE '%LA%'
OR  location LIKE '%San Diego%'
OR  location LIKE '%Santa Monica%'
OR  location LIKE '%Pasadena%'
OR  location LIKE '%Burbank%'
OR  location LIKE '%Anaheim%'
OR  location LIKE '%Long Beach%'
OR  location LIKE '%Riverside%'
OR  location LIKE '%Fresno%'
OR  location LIKE '%Bakersfield%'
OR  location LIKE '%Seattle%'
OR  location LIKE '%Bellevue%'
OR  location LIKE '%Redmond%'
OR  location LIKE '%Kirkland%'
OR  location LIKE '%Tacoma%'
OR  location LIKE '%Portland%'
OR  location LIKE '%Eugene%'
OR  location LIKE '%Salem%'
OR  location LIKE '%Las Vegas%'
OR  location LIKE '%Reno%'
"""

def Update_TZ(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Updating timezone by state...")
    # ADD COLUMN IF MISSING
    cursor.execute("PRAGMA table_info(new_jobs)")
    columns = [row[1] for row in cursor.fetchall()]

    if "TZ" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN TZ TEXT")

    # UPDATE JOBS TABLE
    cursor.execute(f"""
    UPDATE new_jobs
    SET TZ = CASE
        WHEN ({ET_states}) OR ({ET_cities}) THEN 'ET'
        WHEN ({CT_states}) OR ({CT_cities}) THEN 'CT'
        WHEN ({PT_states}) OR ({PT_cities}) THEN 'PT'
        ELSE (
            SELECT TZ
            FROM location_TZ lt
            WHERE lt.location = LOWER(TRIM(new_jobs.location))
        ) END""")

    # CLOSE CONNECTION
    conn.commit()
    conn.close()

    print("Timezone update based on state/cities complete.")

# CALL FUNCTION
if __name__ == "__main__":
    Update_TZ(DB_FILE)