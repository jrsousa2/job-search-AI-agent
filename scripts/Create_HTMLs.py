# CREATES THE LIST OF BEST MATCHES PER COMPANY
# ONE FILE PER ATS

from pathlib import Path
import sys
import os
import config

# ADD SUBOLDER scripts
# REPO_ROOT = Path(__file__).resolve().parent.parent
# sys.path.insert(0, str(REPO_ROOT / "scripts"))

# THESE NEED TO BE IN THE ADDED FOLDER
from load_jobs_db import load_jobs_db
from Repo_root import JOBS_DB
from write_html_digest import write_html_digest


def create_html():
    if not config.API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set. See config.py.")
    
    # --- Write daily-digest files ---
    os.makedirs(config.DIGEST_DIR, exist_ok=True)
    
    # CREATING JOBS    
    print("\nLoading job postings...")
    jobs = load_jobs_db(JOBS_DB)

    # ONLY TOP COMPANY JOBS
    top_jobs = [job for job in jobs if job["top_company_job"] == 1]
    # jobs = parse_jobs(new_jobs_md)
    print(f"\tFound {len(jobs)} job(s) in database")

    # Top jobs per company
    write_html_digest(
        top_jobs,
        [("Platform", "platform"),
         ("Posted", "post_date"),
         ("Location", "location"),
         ("Score", "score"),
         ("Work arrangement", "work_arrangement"),
         ("URL", "url"),])

# CALLS THE CODE
if __name__ == "__main__":
    # CREATE HTML LISTS
    create_html()
