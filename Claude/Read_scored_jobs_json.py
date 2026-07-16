# IMPORTS SAVED JSON FILE
# CREATES JOB_URLs HTML FILE
import json
import config
import os
import datetime

# I ADDED THIS FUNCTION TO SHORTEN THE CODE
from write_html_digest import write_html_digest

# TODAY'S DATE
date_str = datetime.datetime.now().strftime("%Y-%m-%d")

json_file = os.path.join(config.DATA_DIR, f"{date_str}_scored_jobs.json")
with open(json_file, encoding="utf-8") as f:
     scored = json.load(f)

# THESE ARE THE RECOMMENDED JOBS
recommended = sorted(
    [j for j in scored if j.get("meets_filters")],
    key=lambda j: j.get("score", 0),
    reverse=True,)    

print(f"  {len(recommended)} job(s) meet all filters")
if len(recommended) < config.MIN_RECOMMENDED_JOBS:
    print(
        f"  NOTE: fewer than {config.MIN_RECOMMENDED_JOBS} qualifying jobs were "
        f"available in this batch ({len(recommended)} found).")

# --- Write daily-digest files ---
os.makedirs(config.DIGEST_DIR, exist_ok=True)

# TOP 10 JOBS
top_for_docs = recommended[: config.TOP_N_FOR_DOCUMENTS]
# ALL REMAINING JOBS (complement of top 10)
remain_jobs = recommended[config.TOP_N_FOR_DOCUMENTS:]

# Top 10 Job_URLs.html
top10_URLs_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Top10_Job_URLs.html")

write_html_digest(
    top10_URLs_path,
    f"Job URLs — {date_str}",
    top_for_docs,
    [
        ("Score", "score"),
        ("Work arrangement", "work_arrangement"),
        ("URL", "url"),
    ],)

# OTHER Job_URLs.html
other_URLs_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Other_Job_URLs.html")

write_html_digest(
    other_URLs_path,
    f"Job URLs — {date_str}",
    remain_jobs,
    [
        ("URL", "url"),
        ("Reason", "skip_reason"),
    ],)

# OTHER Job_URLs.html
skip_URLs_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Other_Job_URLs.html")

write_html_digest(
        skip_URLs_path,
        f"Job URLs — {date_str}",
        remain_jobs,
        [
         ("URL", "url"),
         ("Reason", "skip_reason"),       
        ],)