import re
import sqlite3

from Create_WL_from_db import matches_industry
from Repo_root import ATS_DB, INDUS_DB
from Summarize_db import Summarize_db


def create_ind_table(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS industry")

    cursor.execute("""
        CREATE TABLE industry (
            company TEXT,
            platform TEXT,
            slug TEXT,
            last_probed_at TEXT,
            industry TEXT
        )
    """)

    # ATTACH THE COPY OF CHROME DB
    cursor.execute("ATTACH DATABASE ? AS ATS_DB", (str(ATS_DB),))

    # CHECK THAT THE DB IS OK
    cursor.execute("PRAGMA database_list")
    print(cursor.fetchall())

    cursor.execute("SELECT COUNT(*) FROM ATS_DB.ATS")
    print("row count:",cursor.fetchone())

    cursor.execute("""
        SELECT
            company,
            platform,
            slug,
            last_probed_at
        FROM ATS_DB.ATS
    """)

    rows = cursor.fetchall()

    for company, platform, slug, last_probed_at in rows:

        # ATS-discovered companies
        industry = matches_industry(company)

        if industry is None:
            continue

        # if industry == "insurance":
        #     industry = "Ins"
        # elif industry == "banking_finance":
        #     industry = "Bank"
        # elif industry == "healthcare":
        #     industry = "HC"
        # else:
        #     continue

        cursor.execute("""
            INSERT INTO industry
            VALUES (?, ?, ?, ?, ?)
        """, (company, platform, slug, last_probed_at, industry))

    # ROWS INSERTED
    # print(f"New URLs inserted: {cursor.rowcount}")

    conn.commit()
    conn.close()

    print("Industry table created.")

if __name__ == "__main__":
    create_ind_table(INDUS_DB)
    Summarize_db(INDUS_DB,"industry","")