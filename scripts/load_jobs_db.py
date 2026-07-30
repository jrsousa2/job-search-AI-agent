# CREATES THE LIST OF JOBS FROM THE DB
import sqlite3
from pathlib import Path
import sys

# ADD SUBOLDER scripts
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import Update_flags

filter_cols = ",\n       ".join(
    f"{expr} AS {name}"
    for name, expr in Update_flags.filters.items() )


def load_jobs_db(DB_FILE) -> list[dict]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT platform,
               company,
               title,
               location,
               is_remote,
               is_hybrid,
               url,
               job_id,
               slug,
               description,
               New,
               is_Us,
               score,
               top_company_job,
               post_date,
               {filter_cols}
        FROM new_jobs
        where (is_remote = 1 OR is_hybrid = 1) and New = 1 
        and is_US = 1 and (TZ in ('ET','CT') or TZ is null) and top_company_job = 1
        ORDER BY score DESC
    """)

    jobs = []

    for row in cursor.fetchall():
        job = {
            "company": row["company"],
            "title": row["title"],
            "location": row["location"],
            "remote": "Yes" if row["is_remote"] else "No",
            "work_arrangement": ("Remote" if row["is_remote"] else "Hybrid"),
            "platform": row["platform"],
            "url": row["url"],
            "job_id": row["job_id"],
            "slug": row["slug"],
            "description": row["description"] or "",
            "score": row["score"],
            "top_company_job": row["top_company_job"],
            "post_date": row["post_date"],
        }
        job.update({name: row[name] for name in Update_flags.filters})
        jobs.append(job)


    conn.close()
    return jobs