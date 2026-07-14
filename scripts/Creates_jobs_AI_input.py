# CREATES THE JOBS INPUT MD FILE FOR CLAUDE
from pathlib import Path
import sqlite3
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.append(str(REPO_ROOT))

from scripts.check_boards import DB_FILE, summarize_db

OUTPUT_FILE = REPO_ROOT / "data" / "new_jobs.md"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
        SELECT
            company,
            title,
            location,
            is_remote,
            is_hybrid,
            platform,
            slug,
            url,
            job_id,
            description
        FROM new_jobs a
        WHERE (is_remote = 1 OR is_hybrid = 1) and New = 1;
""")

rows = cursor.fetchall()

# THIS PART CREATES THE JOB LIST MD FILE THAT WILL BE FED TO CLAUDE
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("# New Jobs\n\n")

    for i, row in enumerate(rows, start=1):
        company, title, location, is_remote, is_hybrid, platform, slug, url, job_id, description = row

        f.write(f"## Job {i}\n\n")
        f.write(f"**Company:** {company}\n\n")
        f.write(f"**Title:** {title}\n\n")
        f.write(f"**Location:** {location}\n\n")
        f.write(f"**Remote:** {'Yes' if is_remote else 'No'}\n\n")
        f.write(f"**Work Arrangement:** {'Remote' if is_remote else 'Hybrid' if is_hybrid else 'On-site'}\n\n")
        f.write(f"**Platform:** {platform}\n\n")
        f.write(f"**URL:** {url}\n\n")
        f.write(f"**Job ID:** {job_id}\n\n")
        f.write(f"**Slug:** {slug}\n\n")
        f.write("### Description\n\n")
        f.write(f"{description}\n\n")
        f.write("---\n\n")

conn.close()

print(f"Created {OUTPUT_FILE} with {len(rows)} jobs.")