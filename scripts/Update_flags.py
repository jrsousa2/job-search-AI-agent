# THIS CODE ADDS AND/OR UPDATES FLAGS "NEW", "IS_US" AND "SCORE"
# AS A SINGLE CODE IT'S EASIER TO MAINTAIN
import sqlite3

from Repo_root import JOBS_DB, CHROME_DB
from Summarize_db import Summarize_db
# from Create_HTMLs import create_html
from Update_TZ_by_state import (ET_states, ET_cities, 
                                CT_states, CT_cities, 
                                MT_states, MT_cities, 
                                PT_states, PT_cities)

# MAX AGE OF POSTING IN DAYS
posting_days = 21

not_foreign_country = """
    location NOT LIKE '%Afghanistan%'
AND location NOT LIKE '%Albania%'
AND location NOT LIKE '%Algeria%'
AND location NOT LIKE '%Andorra%'
AND location NOT LIKE '%Angola%'
AND location NOT LIKE '%Antigua and Barbuda%'
AND location NOT LIKE '%Argentina%'
AND location NOT LIKE '%Armenia%'
AND location NOT LIKE '%Australia%'
AND location NOT LIKE '%Austria%'
AND location NOT LIKE '%Azerbaijan%'
AND location NOT LIKE '%Bahamas%'
AND location NOT LIKE '%Bahrain%'
AND location NOT LIKE '%Bangladesh%'
AND location NOT LIKE '%Barbados%'
AND location NOT LIKE '%Belarus%'
AND location NOT LIKE '%Belgium%'
AND location NOT LIKE '%Belize%'
AND location NOT LIKE '%Benin%'
AND location NOT LIKE '%Bhutan%'
AND location NOT LIKE '%Bolivia%'
AND location NOT LIKE '%Bosnia and Herzegovina%'
AND location NOT LIKE '%Botswana%'
AND location NOT LIKE '%Brazil%'
AND location NOT LIKE '%Brunei%'
AND location NOT LIKE '%Bulgaria%'
AND location NOT LIKE '%Burkina Faso%'
AND location NOT LIKE '%Burundi%'
AND location NOT LIKE '%Cabo Verde%'
AND location NOT LIKE '%Cambodia%'
AND location NOT LIKE '%Cameroon%'
AND location NOT LIKE '%Canada%'
AND location NOT LIKE '%Central African Republic%'
AND location NOT LIKE '%Chad%'
AND location NOT LIKE '%Chile%'
AND location NOT LIKE '%China%'
AND location NOT LIKE '%Colombia%'
AND location NOT LIKE '%Comoros%'
AND location NOT LIKE '%Congo%'
AND location NOT LIKE '%Costa Rica%'
AND location NOT LIKE '%Croatia%'
AND location NOT LIKE '%Cuba%'
AND location NOT LIKE '%Cyprus%'
AND location NOT LIKE '%Czech%'
AND location NOT LIKE '%Czechia%'
AND location NOT LIKE '%Denmark%'
AND location NOT LIKE '%Djibouti%'
AND location NOT LIKE '%Dominica%'
AND location NOT LIKE '%Dominican Republic%'
AND location NOT LIKE '%Ecuador%'
AND location NOT LIKE '%Egypt%'
AND location NOT LIKE '%El Salvador%'
AND location NOT LIKE '%EMEA%'
AND location NOT LIKE '%England%'
AND location NOT LIKE '%Equatorial Guinea%'
AND location NOT LIKE '%Eritrea%'
AND location NOT LIKE '%Estonia%'
AND location NOT LIKE '%Eswatini%'
AND location NOT LIKE '%Ethiopia%'
AND location NOT LIKE '%Europe%'
AND location NOT LIKE '%Fiji%'
AND location NOT LIKE '%Finland%'
AND location NOT LIKE '%France%'
AND location NOT LIKE '%Gabon%'
AND location NOT LIKE '%Gambia%'
AND location NOT LIKE '%Georgia%'
AND location NOT LIKE '%Germany%'
AND location NOT LIKE '%Ghana%'
AND location NOT LIKE '%Greece%'
AND location NOT LIKE '%Grenada%'
AND location NOT LIKE '%Guatemala%'
AND location NOT LIKE '%Guinea%'
AND location NOT LIKE '%Guinea-Bissau%'
AND location NOT LIKE '%Guyana%'
AND location NOT LIKE '%Haiti%'
AND location NOT LIKE '%Honduras%'
AND location NOT LIKE '%Hungary%'
AND location NOT LIKE '%Iceland%'
AND location NOT LIKE '%India%'
AND location NOT LIKE '%Indonesia%'
AND location NOT LIKE '%Iran%'
AND location NOT LIKE '%Iraq%'
AND location NOT LIKE '%Ireland%'
AND location NOT LIKE '%Israel%'
AND location NOT LIKE '%Italy%'
AND location NOT LIKE '%Ivory Coast%'
AND location NOT LIKE '%Jamaica%'
AND location NOT LIKE '%Japan%'
AND location NOT LIKE '%Jordan%'
AND location NOT LIKE '%Kazakhstan%'
AND location NOT LIKE '%Kenya%'
AND location NOT LIKE '%Kiribati%'
AND location NOT LIKE '%Kuwait%'
AND location NOT LIKE '%Kyrgyzstan%'
AND location NOT LIKE '%Laos%'
AND location NOT LIKE '%LATAM%'
AND location NOT LIKE '%Latvia%'
AND location NOT LIKE '%Lebanon%'
AND location NOT LIKE '%Lesotho%'
AND location NOT LIKE '%Liberia%'
AND location NOT LIKE '%Libya%'
AND location NOT LIKE '%Liechtenstein%'
AND location NOT LIKE '%Lithuania%'
AND location NOT LIKE '%Luxembourg%'
AND location NOT LIKE '%Madagascar%'
AND location NOT LIKE '%Malawi%'
AND location NOT LIKE '%Malaysia%'
AND location NOT LIKE '%Maldives%'
AND location NOT LIKE '%Mali%'
AND location NOT LIKE '%Malta%'
AND location NOT LIKE '%Marshall Islands%'
AND location NOT LIKE '%Mauritania%'
AND location NOT LIKE '%Mauritius%'
AND location NOT LIKE '%Mexico%'
AND location NOT LIKE '%Micronesia%'
AND location NOT LIKE '%Moldova%'
AND location NOT LIKE '%Monaco%'
AND location NOT LIKE '%Mongolia%'
AND location NOT LIKE '%Montenegro%'
AND location NOT LIKE '%Morocco%'
AND location NOT LIKE '%Mozambique%'
AND location NOT LIKE '%Myanmar%'
AND location NOT LIKE '%Namibia%'
AND location NOT LIKE '%Nauru%'
AND location NOT LIKE '%Nepal%'
AND location NOT LIKE '%Netherlands%'
AND location NOT LIKE '%New Zealand%'
AND location NOT LIKE '%Nicaragua%'
AND location NOT LIKE '%Niger%'
AND location NOT LIKE '%Nigeria%'
AND location NOT LIKE '%North Korea%'
AND location NOT LIKE '%North Macedonia%'
AND location NOT LIKE '%Norway%'
AND location NOT LIKE '%Oman%'
AND location NOT LIKE '%Pakistan%'
AND location NOT LIKE '%Palau%'
AND location NOT LIKE '%Palestine%'
AND location NOT LIKE '%Panama%'
AND location NOT LIKE '%Papua New Guinea%'
AND location NOT LIKE '%Paraguay%'
AND location NOT LIKE '%Peru%'
AND location NOT LIKE '%Philippines%'
AND location NOT LIKE '%Poland%'
AND location NOT LIKE '%Portugal%'
AND location NOT LIKE '%Qatar%'
AND location NOT LIKE '%Romania%'
AND location NOT LIKE '%Russia%'
AND location NOT LIKE '%Rwanda%'
AND location NOT LIKE '%Saint Kitts and Nevis%'
AND location NOT LIKE '%Saint Lucia%'
AND location NOT LIKE '%Saint Vincent and the Grenadines%'
AND location NOT LIKE '%Samoa%'
AND location NOT LIKE '%San Marino%'
AND location NOT LIKE '%Sao Tome and Principe%'
AND location NOT LIKE '%Saudi Arabia%'
AND location NOT LIKE '%Senegal%'
AND location NOT LIKE '%Serbia%'
AND location NOT LIKE '%Seychelles%'
AND location NOT LIKE '%Sierra Leone%'
AND location NOT LIKE '%Singapore%'
AND location NOT LIKE '%Slovakia%'
AND location NOT LIKE '%Slovenia%'
AND location NOT LIKE '%Solomon Islands%'
AND location NOT LIKE '%Somalia%'
AND location NOT LIKE '%South Africa%'
AND location NOT LIKE '%South Korea%'
AND location NOT LIKE '%South Sudan%'
AND location NOT LIKE '%Spain%'
AND location NOT LIKE '%Sri Lanka%'
AND location NOT LIKE '%Sudan%'
AND location NOT LIKE '%Suriname%'
AND location NOT LIKE '%Sweden%'
AND location NOT LIKE '%Switzerland%'
AND location NOT LIKE '%Syria%'
AND location NOT LIKE '%Taiwan%'
AND location NOT LIKE '%Tajikistan%'
AND location NOT LIKE '%Tanzania%'
AND location NOT LIKE '%Thailand%'
AND location NOT LIKE '%Timor-Leste%'
AND location NOT LIKE '%Togo%'
AND location NOT LIKE '%Tonga%'
AND location NOT LIKE '%Trinidad and Tobago%'
AND location NOT LIKE '%Tunisia%'
AND location NOT LIKE '%Turkey%'
AND location NOT LIKE '%Turkmenistan%'
AND location NOT LIKE '%Tuvalu%'
AND location NOT LIKE '%Uganda%'
AND location NOT LIKE '%Ukraine%'
AND location NOT LIKE '%United Arab Emirates%'
AND location NOT LIKE '%United Kingdom%'
AND location NOT LIKE '%United States%'
AND location NOT LIKE '%Uruguay%'
AND location NOT LIKE '%Uzbekistan%'
AND location NOT LIKE '%Vanuatu%'
AND location NOT LIKE '%Vatican%'
AND location NOT LIKE '%Venezuela%'
AND location NOT LIKE '%Vietnam%'
AND location NOT LIKE '%Yemen%'
AND location NOT LIKE '%Zambia%'
AND location NOT LIKE '%Zimbabwe%'
AND location NOT LIKE '%UK%'
"""

not_foreign_city = """
    location NOT LIKE '%Aschheim%'
AND location NOT LIKE '%Berlin%'
AND location NOT LIKE '%Budapest%'
AND location NOT LIKE '%Bangalore%'
AND location NOT LIKE '%Barcelona%'
AND location NOT LIKE '%Dublin%'
AND location NOT LIKE '%Hong Kong%'
AND location NOT LIKE '%Hyderabad%'
AND location NOT LIKE '%London%'
AND location NOT LIKE '%Leeds%'
AND location NOT LIKE '%Madrid%'
AND location NOT LIKE '%Mississauga%'
AND location NOT LIKE '%Melbourne%'
AND location NOT LIKE '%New Delhi%'
AND location NOT LIKE '%Mumbai%'
AND location NOT LIKE '%Ontario%'
AND location NOT LIKE '%Paris%'
AND location NOT LIKE '%São Paulo%'
AND location NOT LIKE '%Sabana%'
AND location NOT LIKE '%Sydney%'
AND location NOT LIKE '%Toronto%'
AND location NOT LIKE '%Yorkshire%'
"""

loc_US="""(
   location LIKE '%United States%' 
OR location LIKE '%USA%' 
OR location LIKE '%U.S.%'
OR (instr(location,'US')>0 )
)
"""

# FILTER DESC
f15_desc="remote"
f14_desc="recent post"
f13_desc="ET/CT/miss"
f12_desc="null"
f11_desc="SAS"
f10_desc="insurance/bank"
f9_desc="data analyst"
f8_desc="SQL/ETL"
f7_desc="Analytics/Rpt"
f6_desc="Oracle/TD"
f5_desc="predictive"
f4_desc="AML"
f3_desc="Hadoop"
f2_desc="VBA"
f1_desc="Python"
f0_desc="Spark"

# FILTERS
# THE FIRST 5 FILTERS ARE NOT ABOUT MY SKILLS
filter15="(is_remote=1)"

filter14="( julianday('now')-julianday(post_date)<=10 )"

filter13="(coalesce(TZ,'None') in ('ET','CT') or TZ is null)"

filter12="(False)"

filter11="""(
           (instr(description,'SAS')>0 )
        OR (instr(LOWER(description),'viya')>0)
        )
        """

filter10="""
        (
           (instr(LOWER(company),'bank')>0)
        OR (instr(LOWER(company),'insurance')>0)
        OR (instr(LOWER(title),'insurance')>0)
        OR (instr(LOWER(title),'p&c')>0)
        OR (instr(LOWER(description),'a&h')>0)
        OR (instr(LOWER(description),'p&c')>0)
        OR (instr(LOWER(description),'casualty')>0)
        ) 
        """

filter9="""(
            (instr(LOWER(title),'data')>0) AND 
            ( 
                (instr(LOWER(title),'analyst')>0)
             OR (instr(LOWER(title),'analytic')>0)
             OR (instr(LOWER(title),'management')>0) 
            ) 
            )
        """

filter8="""(
            (instr(LOWER(description),'sql')>0)
         OR (instr(LOWER(description),'database')>0)
         OR (instr(LOWER(description),'warehouse')>0)
         OR (instr(LOWER(description),'etl')>0)
        )
        """

filter7="""(
           (instr(LOWER(description),'analytics')>0)
        OR (instr(LOWER(description),'reports')>0)
        OR (instr(LOWER(description),'reporting')>0)  
        OR (instr(LOWER(description),'power bi')>0)
        )
        """

filter6="""(
            (instr(LOWER(description),'oracle')>0)
         OR (instr(LOWER(description),'teradata')>0)
         OR (instr(LOWER(description),'db2')>0)
         OR (instr(LOWER(description),'ibm mainframe')>0)
         OR (instr(LOWER(description),'sql server')>0)
        )
        """

filter5="""(
                (instr(LOWER(description),'statistic')>0)
             OR (instr(LOWER(description),'predictive')>0)
           )  
        """     

filter4="""(
                (instr(LOWER(description),' aml ')>0)
             OR (instr(LOWER(title),' aml ')>0)
             OR (instr(LOWER(description),' kyc ')>0)
             OR (instr(LOWER(description),' cdd ')>0)
             OR (instr(LOWER(description),' fcc ')>0)
            )
        """

filter3="(instr(LOWER(description),'hadoop')>0)"

filter2="(instr(LOWER(description),'vba')>0)"

filter1="(instr(LOWER(description),'python')>0)"

filter0="(instr(LOWER(description),'spark')>0)"

filter_1="(instr(LOWER(description),'databrick')>0)"

# HARD SKILLS (9 and 8 DON'T APPLY -- THEY USE TITLE)
hard_skills="""(
   instr(LOWER(description),' aml ')>0
OR instr(LOWER(description),'a&h')>0
OR instr(LOWER(description),'analytics')>0
OR instr(LOWER(description),' cdd ')>0
OR instr(LOWER(description),'credit risk')>0
OR instr(LOWER(description),'data warehouse')>0
OR instr(LOWER(description),'database')>0
OR instr(LOWER(description),'databricks')>0
OR instr(LOWER(description),'dashboard')>0
OR instr(LOWER(description),'db2')>0
OR instr(LOWER(description),'dremio')>0
OR instr(LOWER(description),'etl')>0
OR instr(LOWER(description),' excel ')>0
OR instr(LOWER(description),' fcc ')>0
OR instr(LOWER(description),' git ')>0
OR instr(LOWER(description),'github')>0
OR instr(LOWER(description),'hadoop')>0
OR instr(LOWER(description),'hive')>0
OR instr(LOWER(description),'json')>0
OR instr(LOWER(description),' kyc ')>0
OR instr(LOWER(description),'loss triangle')>0
OR instr(LOWER(description),'mainframe')>0
OR instr(LOWER(description),'oracle')>0
OR instr(LOWER(description),'p&c')>0
OR instr(LOWER(description),'pandas')>0
OR instr(LOWER(description),'power bi')>0
OR instr(LOWER(description),'predictive')>0
OR instr(LOWER(description),'python')>0
OR instr(LOWER(description),'reporting')>0
OR instr(LOWER(description),'reports')>0
OR instr(description,'SAS')>0
OR instr(LOWER(description),'sqlite')>0
OR instr(LOWER(description),'snowflake')>0
OR instr(LOWER(description),'spark')>0
OR instr(LOWER(description),'sql')>0
OR instr(LOWER(description),'statistics')>0
OR instr(LOWER(description),'teradata')>0
OR instr(LOWER(description),'vba')>0
OR instr(LOWER(description),'visualization')>0
OR instr(LOWER(description),'viya')>0
OR instr(LOWER(description),'xml')>0
)
"""

title_excls =f"""(
           (instr(LOWER(title),'account')>0)
        OR (instr(LOWER(title),'actuary')>0)   
        OR (instr(LOWER(title),'actuarial analyst')>0)
        OR (instr(LOWER(title),'audit')>0)
        OR (instr(LOWER(title),'advocate')>0)
        OR (instr(LOWER(title),'attorney')>0)   
        OR (instr(' ' || LOWER(title) || ' ',' agent ')>0)
        OR (instr(LOWER(title),'admin')>0)
        OR (instr(LOWER(title),'application')>0)
        OR (instr(LOWER(title),'biostat')>0) 
        OR (instr(LOWER(title),'broker')>0)
        OR (instr(LOWER(title),'compensation')>0)
        OR (instr(LOWER(title),'compliance')>0 and not {filter4})
        OR (instr(LOWER(title),'customer')>0)
        OR (instr(LOWER(title),'clinic')>0)
        OR (instr(LOWER(title),'cyber')>0)
        OR (instr(LOWER(title),'data entry')>0)
        OR (instr(LOWER(title),'design')>0)
        OR (instr(LOWER(title),'desk')>0)
        OR (instr(LOWER(title),'devops')>0)
        OR (instr(LOWER(title),'director')>0)
        OR (instr(LOWER(title),'entry level')>0)
        OR (instr(LOWER(title),'entry-level')>0)
        OR (instr(LOWER(title),'financ')>0 and not {filter4} and not {filter11})
        OR (instr(LOWER(title),'follow-up')>0)
        OR (instr(LOWER(title),'head of')>0)
        OR (instr(' ' || LOWER(title) || ' ',' intern ')>0)
        OR (instr(LOWER(title),'investigator')>0)
        OR (instr(LOWER(title),'lawyer')>0)
        OR (instr(LOWER(title),'legal')>0)
        OR (instr(LOWER(title),'license')>0)
        OR (instr(lower(title),' loan')>0)
        OR (instr(LOWER(title),'manager')>0)
        OR (instr(LOWER(title),'mortgage')>0)
        OR (instr(LOWER(title),'origination')>0)
        OR (instr(LOWER(title),'officer')>0) 
        OR (instr(LOWER(title),'operation')>0)
        OR (instr(LOWER(title),'paralegal')>0)
        OR (instr(LOWER(title),'payroll')>0)
        OR (instr(LOWER(title),'professional')>0)
        OR (instr(LOWER(title),'psycho')>0)
        OR (instr(LOWER(title),'represe')>0)
        OR (instr(' ' || LOWER(title) || ' ',' sales ')>0)
        OR (instr(LOWER(title),'security')>0)
        OR (instr(LOWER(title),'software')>0)
        OR (instr(LOWER(title),'support')>0)
        OR (instr(' ' || LOWER(title) || ' ',' tax ')>0)
        OR (instr(LOWER(title),'technician')>0)
        OR (instr(LOWER(title),'writer')>0)
        )
        """


# Maps each fXX flag on a job dict to its label, highest bit first
# (f15 -> filter15, f14 -> filter14, ..., f0 -> filter0)
FILTER_LABELS = {
    15: f15_desc, 14: f14_desc, 13: f13_desc, 
    12: f12_desc, 11: f11_desc, 10: f10_desc, 
    9: f9_desc, 8: f8_desc, 7: f7_desc, 
    6: f6_desc, 5: f5_desc, 4: f4_desc,
    3: f3_desc, 2: f2_desc, 1: f1_desc, 
    0: f0_desc,
}

# USED IN CODE LOAD_JOBS_DB
filters = {
    "f15": filter15,
    "f14": filter14,
    "f13": filter13,
    "f12": filter12,
    "f11": filter11,
    "f10": filter10,
    "f9": filter9,
    "f8": filter8,
    "f7": filter7,
    "f6": filter6,
    "f5": filter5,
    "f4": filter4,
    "f3": filter3,
    "f2": filter2,
    "f1": filter1,
    "f0": filter0
}
 
# THE ARGUMENT A SUMMARY OF MATCHES IS PROVIDED
def matched_filters(job):
    """Return a comma-joined string of filter labels where job[f'f{n}'] == 1,
    ordered from f15 down to f0."""
    hits = [
        label
        for n, label in sorted(FILTER_LABELS.items(), reverse=True)
        if job.get(f"f{n}") == 1
    ]
    return ", ".join(hits)

# ADD AND UPDATE FLAG "NEW" IN TABLE NEW_JOBS
def Update_flags(JOBS_DB) -> int:
    conn = sqlite3.connect(JOBS_DB)
    cursor = conn.cursor()

    # DELETE ROWS THAT DON'T HAVE HARD SKILLS OR POSTING IS OLD.
    cursor.execute(f"""
    DELETE FROM new_jobs
    WHERE not 
    ( {hard_skills} 
       and not {title_excls}
       and ((julianday('now')-julianday(post_date)<={posting_days}) OR post_date is null)
    );
    """)

    # PRINTS NEW_JOBS COUNT
    print("\nUpdating flags New/is_US...")
    # START ROWS
    print("Total before SQL update...")
    # total_count = Summarize_db(JOBS_DB,"new_jobs","")

    # CHECK IF COLUMN EXISTS
    cursor.execute("PRAGMA table_info(new_jobs)")
    columns = [row[1] for row in cursor.fetchall()]

    if "New" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN New INTEGER")
    else:
        # GET NUMBER OF NEW JOBS
        print("New before SQL update...")
        start_count = Summarize_db(JOBS_DB,"new_jobs","where New=1")    

    # US flag
    if "is_US" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN is_US INTEGER")

    # UPDATES FLAG is_US
    cursor.execute(f"""
    UPDATE new_jobs
    SET is_US = CASE
        WHEN ({not_foreign_country}) and ({not_foreign_city}) THEN 1
        WHEN ({loc_US}) THEN 1
        WHEN ({ET_states}) or ({ET_cities}) THEN 1
        WHEN ({CT_states}) or ({CT_cities}) THEN 1
        WHEN ({MT_states}) or ({MT_cities}) THEN 1
        WHEN ({PT_states}) or ({PT_cities}) THEN 1
        ELSE 0
    END
    """)

    # ATTACH THE CHROME DB
    cursor.execute("ATTACH DATABASE ? AS chrome_db", (str(CHROME_DB),))

    # UPDATE New based on Chrome history
    cursor.execute("""
    UPDATE new_jobs
    SET New = CASE
        WHEN EXISTS (
            SELECT 1
            FROM jobs_hist h
            WHERE h.final_job_id = new_jobs.final_job_id
        ) THEN 0

        WHEN EXISTS (
            SELECT 1
            FROM chrome_db.visited_urls v
            WHERE v.url = new_jobs.url
        ) THEN 0

        ELSE 1
    END
    """)
    
    # ADD SCORE COLUMN
    # US flag
    if "score" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN score INTEGER DEFAULT 0")
    
    # CALCULATE SCORE BASED ON KEYWORDS
    cursor.execute(f"""
        UPDATE new_jobs
        SET score =
          pow(10, 15) * {filter15}      
        + pow(10, 14) * {filter14}          
        + pow(10, 13) * {filter13}
        + pow(10, 12) * {filter12} 
        + pow(10, 11) * {filter11} 
        + pow(10, 10) * {filter10}
        + pow(10, 9) * {filter9}
        + pow(10, 8) * {filter8}
        + pow(10, 7) * {filter7}
        + pow(10, 6) * {filter6}
        + pow(10, 5) * {filter5}
        + pow(10, 4) * {filter4}
        + pow(10, 3) * {filter3}
        + pow(10, 2) * {filter2}
        + pow(10, 1) * {filter1}
        + pow(10, 0) * {filter0}
        + pow(10, -1) * {filter_1}
        
    """)

    # TOP JOB PER COMPANY
    if "top_company_job" not in columns:
        cursor.execute("ALTER TABLE new_jobs ADD COLUMN top_company_job INTEGER DEFAULT 0;")

    # UPDATES FIELD
    cursor.executescript(f"""
    WITH ranked AS (
        SELECT
            rowid,
            ROW_NUMBER() OVER (
                PARTITION BY company, platform
                ORDER BY score DESC, rowid
            ) AS rn
        FROM new_jobs
        WHERE (is_remote = 1 OR is_hybrid = 1) and New = 1 
        and is_US = 1 and (TZ in ('ET','CT') or TZ is null)
    )

    UPDATE new_jobs
    SET top_company_job = CASE
        WHEN rowid IN (
            SELECT rowid
            FROM ranked
            WHERE rn = 1
        ) THEN 1
        ELSE 0
    END;
    """)

    # ORDERS THE TABLE BY SCORE
    cursor.executescript(f"""
    CREATE TABLE new_jobs_sorted AS
    SELECT *
    FROM new_jobs
    ORDER BY score DESC;

    DROP TABLE new_jobs;

    ALTER TABLE new_jobs_sorted RENAME TO new_jobs;
    """)
    # COMMITS CHANGES
    conn.commit()
    conn.close()
    # GET NUMBER OF NEW JOBS
    print("New after SQL update...")
    end_count = Summarize_db(JOBS_DB,"new_jobs","where New=1")
    return end_count

# ADDS FLAG "NEW" TO TABLE NEW_JOBS
if __name__ == "__main__":
    new_jobs_count = Update_flags(JOBS_DB)

    # TOTAL TABLE COUNT
    # Hist_count = Summarize_db(JOBS_DB,"jobs_hist","")
    # New_count = Summarize_db(JOBS_DB,"new_jobs","where New=1")
    # Old_count = Summarize_db(JOBS_DB,"new_jobs","where New=0")