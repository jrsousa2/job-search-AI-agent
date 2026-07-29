# DROPS A TABLE FROM A DATABASE
import sqlite3

# ADD SUBOLDER scripts
from pathlib import Path
import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# MY FUNCTIONS IN scripts
from Repo_root import JOBS_DB, ATS_DB

# IF TABLE jobs_hist LAYOUT IS MODIFIED, DROP AND RECREATE
def drop_table(input_db,input_table) -> None:
    # THE CONNECTION AND CURSOR ARE GLOBAL
    conn = sqlite3.connect(input_db)
    cursor = conn.cursor()
    # DROP TABLE
    cursor.execute(f"DROP TABLE IF EXISTS {input_table}")
    # COMMIT THE COMMAND
    conn.commit()
    print(f"Table {input_table} dropped!")

    # CLOSE CONNECTION
    conn.close()

# MAIN CODE
if __name__ == "__main__":
    drop_table(ATS_DB,"watchlist_orig")
