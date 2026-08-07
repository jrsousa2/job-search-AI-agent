# USED TO LOAD GREENHOUSE, ASHBY AND LEVER
# FOR WORKDAY, THE DATA LOAD IS DIFFERENT
import sqlite3
import json

# ADD SUBOLDER scripts
from pathlib import Path
import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# MY FUNCTIONS IN scripts
from Repo_root import REPO_ROOT, WATCHLIST, ATS_DB

def load_json_to_table(json_file, input_db, output_table=None):
    table_name = output_table or Path(json_file).stem
    conn = sqlite3.connect(input_db)
    cursor = conn.cursor()

    # LOAD JSON
    with open(json_file, "r") as f:
        data = json.load(f)

    if not data:
        raise ValueError("JSON file is empty")

    # Get columns from JSON keys
    # columns = data[0].keys()
    # Restrict columns to only these fields
    columns = ["ats", "platform", "company", "slug", "status", "last_probed_at", "host", "site"]

    # DROP TABLE BEFORE RELOADING
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    # CREATE TABLE WITH LAYOUT BASED ON VAR COLUMNS
    # if table_name != "workday":
    cursor.execute(f"""
    CREATE TABLE {table_name} (
        {", ".join(f"{col} TEXT" for col in columns)}  )""")
    # else:
    # CREATES DB TABLE WITH FIXED LAYOUT
    # cursor.execute(f"""
    # CREATE TABLE {table_name} (
    #     ats TEXT,
    #     company TEXT,
    #     slug TEXT,
    #     status TEXT,
    #     last_probed_at TEXT,
    #     host TEXT,
    #     site TEXT
    # ) 
    # """)

    # INSERT DATA
    for row in data:
        # LOAD IS DIFFERENT FOR WORKDAY (IT HAS METADA FIELDS)
        if table_name != "workday":
            cursor.execute(
                f"""
                INSERT INTO {table_name} ({", ".join(columns)})
                VALUES ({", ".join("?" for _ in columns)})
                """,
                #tuple(row[col] for col in columns) 
                tuple(row.get(col) for col in columns)
                )
        else:
            metadata = row.get("metadata", {})

            cursor.execute(
                f"""
                INSERT INTO {table_name}
                (ats, company, slug, status, last_probed_at, host, site)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("ats") or row.get("platform"),
                    row.get("company"),
                    row.get("slug"),
                    row.get("status"),
                    row.get("last_probed_at"),
                    metadata.get("host"),
                    metadata.get("site")
                ) )
    conn.commit()

    # COUNT ROWS
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]

    conn.close()

    print(f"Created DB table {table_name} with {row_count:,} rows.")

    return row_count

if __name__ == "__main__":
    # ALL BELOW HAVE BEEN LOADED
    # load_json_to_table(r"D:\Agent\openroles\tenants\icims.json", ATS_DB)
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\workday.json", ATS_DB)
    
    # LOCATION OF THIS ONE IS EXCEPTION
    # load_json_to_table(r"D:\Agent\openroles\watchlist.json", ATS_DB)
    
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\greenhouse.json", ATS_DB) 
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\lever.json", ATS_DB)
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\ashby.json", ATS_DB)
    
    # LOADS THE CURRENT WATCHLIST AND GIVE IT A NEW NAME
    load_json_to_table(WATCHLIST, ATS_DB, "CUR_WATCHLIST")
    
    
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\csod.json", "csod")
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\icims.json", "icims")
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\taleo.json", "taleo")
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\brassring.json", "brassring")
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\successfactors.json", "successfactors")
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\oraclecloud.json", "oraclecloud")
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\phenom.json", "phenom")
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\eightfold.json", "eightfold")
    # load_json_to_table(r"D:\Agent\Json\openroles\data\tenants\smartrecruiters.json", "smartrecruiters")