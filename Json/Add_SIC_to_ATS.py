# THIS CODE JOINS FIELDS FROM THE SEC TABLE TO THE ATS TABLE
import sqlite3
import re

# ADD SUBOLDER scripts
from pathlib import Path
import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# IMPORT
from Repo_root import ATS_DB
from Exp_db_to_Excel import Exp_db_to_Excel

conn = sqlite3.connect(ATS_DB)
cursor = conn.cursor()

# RETURNS TABLE COLS
def table_cols(cursor, input_table):
    cursor.execute(f"PRAGMA table_info({input_table})")
    cols = [row[1] for row in cursor.fetchall()]
    return cols

# THIS FUNCTION NORMALIZES THE COMPANY TO INCREASE THE MATCH
def normalize_company(name):
    if not name:
        return ""

    name = name.upper()

    # Remove punctuation
    name = re.sub(r"[^A-Z0-9 ]", " ", name)
    name = re.sub(r"[^A-Z0-9 ]", " ", name)

    # Remove legal suffixes
    suffixes = [
        "INCORPORATED",
        "INC",
        "CORPORATION",
        "CORP",
        "COMPANY",
        "CO",
        "LIMITED",
        "LTD",
        "LLC",
        "LP",
        "PLC",
        "NV",
        "AG",
        "SA"
    ]

    for s in suffixes:
        name = re.sub(rf"\b{s}\b", "", name)

    # Remove extra spaces
    name = re.sub(r"\s+", " ", name).strip()

    return name

# MAIN CODE

conn.create_function("NORMALIZE_COMPANY", 1, normalize_company)

# Add cleaned names
if "company_clean" not in table_cols(cursor, "ATS"):
    cursor.execute("ALTER TABLE ATS ADD COLUMN company_clean TEXT")

# cursor.execute("""
# UPDATE ATS 
# SET company_clean = NORMALIZE_COMPANY(company)
# """)

if "company_clean" not in table_cols(cursor, "SEC_companies"):
    cursor.execute("ALTER TABLE SEC_companies ADD COLUMN company_clean TEXT")

# cursor.execute("""
# UPDATE SEC_companies
# SET company_clean = NORMALIZE_COMPANY(title)
# """)


# Create deduplicated SEC table
cursor.execute("DROP TABLE IF EXISTS SEC_companies_clean")

cursor.execute("""
CREATE TEMP TABLE SEC_companies_clean AS
SELECT
     company_clean
    ,title
    ,ticker
    ,cik_str
    --sic,
    --sicDescription
FROM (
       SELECT *,
           ROW_NUMBER() OVER (PARTITION BY company_clean ORDER BY ticker) AS rn
       FROM SEC_companies
)
WHERE rn = 1
""")

# Join ATS with SEC
cursor.execute("DROP TABLE IF EXISTS ATS_SIC")

cursor.execute("""
CREATE TABLE ATS_SIC AS

SELECT
    count(*) as N
    ,a.*
    ,b.title
    ,b.ticker
    ,b.cik_str
    --,s.sic
    --,s.sicDescription
FROM ATS a LEFT JOIN SEC_companies_clean b
     --ON a.company_clean = s.company_clean
     ON length(a.company)>=4 
        AND instr(LOWER(REPLACE(b.title, ' ', '')),LOWER(REPLACE(a.company, ' ', '')))>0 
        --LOWER(REPLACE(a.company, ' ', '')) like '%' || LOWER(REPLACE(b.title, ' ', '')) || '%'
GROUP BY a.company, a.platform, a.slug
ORDER BY a.company, a.platform, a.slug

""")

conn.commit()

# TOTAL ROWS
cursor.execute("SELECT COUNT(*) FROM ATS_SIC")
rows =  cursor.fetchone()[0]

# POPULATED ROWS
cursor.execute("""
SELECT COUNT(*) 
FROM ATS_SIC 
WHERE ticker IS NOT NULL
""")
rows_pop =  cursor.fetchone()[0]

print("ATS_SIC rows:", rows, "SEC matches:", rows_pop)

conn.close()

Exp_db_to_Excel(ATS_DB,"ATS_SIC","(2)","")