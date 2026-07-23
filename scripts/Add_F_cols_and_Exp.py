# CREATES THE LIST OF JOBS FROM THE DB
import sqlite3
from pathlib import Path
import sys

from Repo_root import JOBS_DB
from Exp_db_to_Excel import Exp_db_to_Excel

import Update_flags

filter_cols = ",\n       ".join(
    f"{expr} AS {name}"
    for name, expr in Update_flags.filters.items() )

def add_cols_and_exp(input_db):
    conn = sqlite3.connect(input_db)
    cursor = conn.cursor()

    cursor.execute(f"""
    CREATE TEMP TABLE WD_jobs AS
    SELECT *,
            {filter_cols}
    FROM new_jobs
    WHERE platform = 'workday'
    """)

    # Export temp table to Excel here
    Exp_db_to_Excel(JOBS_DB,"WD_jobs","(Expanded)","")

    conn.close()

# ADDS FLAG "NEW" TO TABLE NEW_JOBS
if __name__ == "__main__":
    new_jobs_count = add_cols_and_exp(JOBS_DB)
