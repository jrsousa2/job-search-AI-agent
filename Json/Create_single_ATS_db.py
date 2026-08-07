# COMBINES ALL 4 ATS INTO A SINGLE DB
# RECORDS ARE DEDUPED BY PLATFORM AND SLUG
# RECORDS ARE ONLY DEDUPED IF IN THE SAME ATS SOURCE FILE
import sqlite3

# ADD SUBOLDER scripts
from pathlib import Path
import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# IMPORT
from Repo_root import ATS_DB
from Exp_db_to_Excel import Exp_db_to_Excel

def stack_ATS_tables(input_db,output_table):
    conn = sqlite3.connect(input_db)
    cursor = conn.cursor()

    cursor.executescript(f"""
    DROP TABLE IF EXISTS {output_table};

    CREATE TABLE {output_table} AS

    WITH combined AS (

    SELECT
        UPPER(substr(slug, 1, 1)) || substr(slug, 2) AS company,
        ats as platform,
        slug,
        status,
        date(last_probed_at) as last_probed_at
    FROM ashby
    WHERE status = 'live'

    --UNION ALL

    --SELECT
        --UPPER(substr(slug, 1, 1)) || substr(slug, 2) AS company,
        --ats as platform,
        --slug,
        --status,
        --date(last_probed_at) as last_probed_at
    --FROM icims
    --WHERE status = 'live'

    UNION ALL

    SELECT
        UPPER(substr(slug, 1, 1)) || substr(slug, 2) AS company,
        ats,
        slug,
        status,
        date(last_probed_at) as last_probed_at
    FROM greenhouse
    WHERE status = 'live'

    UNION ALL

    SELECT
        UPPER(substr(slug, 1, 1)) || substr(slug, 2) AS company,
        ats,
        slug,
        status,
        date(last_probed_at) as last_probed_at
    FROM lever
    WHERE status = 'live'

    UNION ALL

    SELECT
        UPPER(substr(slug, 1, 1)) || substr(slug, 2) AS company,
        ats,
        slug || '/' ||
        substr(host,instr(host,'.wd')+1,instr(substr(host, instr(host, '.wd') + 1), '.') - 1)
        || '/' || site AS slug,
        status,
        date(last_probed_at) as last_probed_at
    FROM workday
    WHERE status = 'live' and site is not null

    UNION ALL

    SELECT
        company,
        platform,
        slug,
        NULL AS status,
        NULL AS last_probed_at
    FROM watchlist
    ),

    deduped AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY platform, lower(company)
               ORDER BY case when last_probed_at IS NULL then 1 else 2 end ASC
               ,(length(slug) - length(replace(slug, '/', ''))) DESC
               ,last_probed_at DESC
           ) AS rn
    FROM combined
    ),

    deduped_slug AS 
    (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY platform, lower(company), lower(slug) ORDER BY last_probed_at DESC) AS rn_slug
    FROM deduped
    where rn = 1 or lower(company) in ('abbott', 'assurant', 'equifax', 'fedex', 'sedgwick')
    )

    -- FINAL TABLE
    SELECT company,platform,slug,status,last_probed_at
    from deduped_slug
    where rn_slug = 1 
    ORDER BY 1,2,3;

    """)

    conn.commit()

    cursor.execute(f"SELECT COUNT(*) FROM {output_table}")
    count = cursor.fetchone()[0]

    conn.close()

    print(f"Created {output_table} table with {count:,} rows.")


if __name__ == "__main__":
    stack_ATS_tables(ATS_DB,"ATS")
    # EXPORT TABLE TO EXCEL
    Exp_db_to_Excel(ATS_DB,"ATS","(All3)","")