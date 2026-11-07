# MAKING MODIFICATIONS TO SCOTTY'S CODE 
# I THINK I NOW UNDERSTAND THIS CODE
# REQUIRE TWO KW HITS NOT JUST ONE
#!/usr/bin/env python3
"""
Query Ashby, Lever, Greenhouse, and Workday job board APIs for target companies
and cross-check against evaluated-jobs.csv to find gaps.

Usage:
    python3 scripts/check-boards.py              # show new roles only
    python3 scripts/check-boards.py --all        # include already-evaluated roles
    python3 scripts/check-boards.py --company figma
    python3 scripts/check-boards.py --no-filter  # skip keyword filter, show all roles
"""

from __future__ import annotations

import argparse
import html as html_module
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

# import pandas as pd
import sqlite3
from datetime import datetime, timezone
from timeit import default_timer
from time import sleep

# NEW MODULES
from Repo_root import JOBS_DB, WATCHLIST, Log_file
from Summarize_db import Summarize_db
from Update_flags import Update_flags
from Exp_db_to_Excel import Exp_db_to_Excel
from Update_TZ_by_state import Update_TZ_by_state
from print_to_log import print_to_log
from Chrome_db_hist import Chrome_db_hist 
from Create_HTMLs import create_html
from Update_jobs_hist import Update_jobs_hist
from fetch_icims import fetch_icims

# DO NOT PRINT TO TERMINAL
VERBOSE = False

# TIME OUT
TO_value = 20

# SLEEP TIME TO FETCH WD DESCRIPTION
sleep_time = 5

# THIS IS THE LIST OF KEYWORD TO LOOK FOR IN THE JOB TITLE (LOWER CASE)
TITLE_KEYWORDS = [
    "aml",
    "analyst",
    "analytics",
    "bank",
    "banking",
    "bi analyst",
    "business intelligence",
    "claims",
    "compliance",
    "credit",
    "data analyst",
    "data engineer",
    "data manager",
    "data scientist",
    "data ",
    "database",
    "developer",
    "etl",
    "finance",
    "financial",
    "forecasting",
    "fraud",
    "insurance",
    "investment"
    "modeling",
    "pandas",
    "predictive",
    "pricing",
    "python",
    "risk analyst",
    "risk",
    "sas",
    "sql",
    "statist",
    "viya",
]

###########################################################################
###########################################################################
###########################################################################
# NEW FUNCTIONS ADDED BY JOSE

import re
from datetime import datetime, timedelta

def convert_workday_date(value):
    today = datetime.now().date()

    if not value:
        return None

    if "Today" in value:
        return today.isoformat()

    if "Yesterday" in value:
        return (today - timedelta(days=1)).isoformat()

    # match = re.search(r"Posted (\d+) Days Ago", value)
    match = re.search(r"Posted (\d+)\+? Days Ago", value)

    if match:
        days = int(match.group(1))
        return (today - timedelta(days=days)).isoformat()

    return None        

# SAVES THE ATS RESULTS TO A SQLITE DB TABLE
# POST_DATE_STR IS BEING CONVERTED TO AN ACTUAL DATE HERE
def Save_jobs_db(jobs: list[dict]) -> None:
    conn = sqlite3.connect(JOBS_DB)
    cursor = conn.cursor()

    # DROP TABLE IF IT EXISTS
    cursor.execute("DROP TABLE IF EXISTS new_jobs")

    cursor.execute("""
        CREATE TABLE new_jobs (
            final_job_id TEXT,
            platform TEXT,
            company TEXT,
            slug TEXT,
            job_id TEXT,
            title TEXT,
            post_date_str TEXT,
            post_date TEXT,
            location TEXT,
            is_remote BOOLEAN,
            is_hybrid BOOLEAN,
            url TEXT,
            description TEXT
        )
    """)

    fields = ["final_job_id", "platform", "company", "slug", "job_id", "title", 
              "post_date_str", "post_date", "location", "is_remote", "is_hybrid", "url", "description",]

    # LOOP TO ADD A NEW FIELD
    rows = []
    for job in jobs:
        # LOGIC FOR POSTED DATE
        post_date_str = job.get("post_date_str", "")
        platform = job.get("platform", "")

        if platform == "greenhouse":
            job["post_date"] = datetime.fromisoformat(
                post_date_str.replace("Z", "+00:00")
            ).date().isoformat()

        elif platform == "ashby":
            job["post_date"] = datetime.fromisoformat(
                post_date_str.replace("Z", "+00:00")
            ).date().isoformat()

        elif platform == "lever":
            # already converted to YYYY-MM-DD
            job["post_date"] = post_date_str

        elif platform == "workday":
            job["post_date"] = convert_workday_date(post_date_str)

        else:
            job["post_date"] = None
        # LOGIC FOR FINAL JOB ID
        if job.get("job_id"):
           job["final_job_id"] = f'{job["platform"]}|{job["company"]}|{job["job_id"]}'
        else:
            job["final_job_id"] = f'{job["platform"]}|{job["company"]}|{job["title"]}'
        # NORMALIZE
        job["final_job_id"] = job["final_job_id"].strip().lower()

        # CREATE COLS is_remote AND is_hybrid
        desc = (job.get("description") or "").lower()
        url = (job.get("url") or "").lower()
        title = (job.get("title") or "").lower()
        
        # USE BOTH FIELDS TO CHECK FOR MAIN KEYWORDS
        # REMOVED {desc} FOR A WHILE
        text = f"{url} {title}"

        job["is_remote"] = 1 if job.get("is_remote") == 1 or "remote" in text else 0
        job["is_hybrid"] = 0 if job["is_remote"] else (1 if "hybrid" in text else 0)

        rows.append(tuple(job.get(field) for field in fields))

    # SELECT ONLY JOB RECORDS THAT ARE NOT ONSITE
    rows = [row for row in rows 
            if row[fields.index("is_remote")] == 1 or row[fields.index("is_hybrid")] == 1]
    
    # DEDUPE RECORDS (COMPANIES ADDED MORE THAN ONCE TO WATCHLIST BY MISTAKE)
    seen = set()
    unique_rows = []

    final_job_id_idx = fields.index("final_job_id")

    for row in rows:
        if row[final_job_id_idx] not in seen:
            seen.add(row[final_job_id_idx])
            unique_rows.append(row)

    rows = unique_rows

    cursor.executemany(f"""
        INSERT INTO new_jobs ({','.join(fields)})
        VALUES ({','.join(['?'] * len(fields))})
    """, rows)
    # THE END
    conn.commit()
    conn.close()

    # PRINTS STATS
    print(f"\n\nJobs list had {len(jobs)} records")
    print(f"Saved {len(jobs)} remote/hybrid jobs to {JOBS_DB} table new_jobs")
    # PRINTS RESULTS TO LOG FILE AS WELL
    print_to_log(Log_file,"\n\nJobs list had {} records",len(jobs))
    print_to_log(Log_file,"\nSaved {} remote/hybrid jobs to {} table new_jobs\n\n",len(rows),JOBS_DB)


###########################################################################
###########################################################################
###########################################################################
# THE ORIGINAL FUNCTIONS START BELOW
def normalize_key(company: str, role: str) -> str:
    def norm(v: str) -> str:
        v = v.lower().strip()
        v = re.sub(r"^the\s+", "", v)
        v = re.sub(r"[^a-z0-9&]+", " ", v)
        return re.sub(r"\s+", " ", v).strip()
    return f"{norm(company)}|{norm(role)}"


def extract_job_id(url: str) -> str | None:
    if not url:
        return None
    # Greenhouse: ?gh_jid=1234567 or /jobs/1234567
    m = re.search(r"[?&]gh_jid=(\d+)", url)
    if m:
        return m.group(1)
    m = re.search(r"/jobs/(\d+)", url)
    if m:
        return m.group(1)
    # Lever / Ashby: UUID in path
    m = re.search(r"/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", url)
    if m:
        return m.group(1)
    return None

# FUNCTION THAT CHECKS FOR KEYWORDS IN TITLE
def is_relevant(title: str) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in TITLE_KEYWORDS)


def fetch_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=TO_value) as resp:
        return json.loads(resp.read().decode())


def fetch_json_post(url: str, body: dict) -> object:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=TO_value) as resp:
        return json.loads(resp.read().decode())


def strip_html(text: str) -> str:
    text = html_module.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_module.unescape(text)  # second pass for double-encoded entities
    return re.sub(r"\s+", " ", text).strip()


def fetch_ashby(company: str, slug: str) -> list[dict]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{urllib.parse.quote(slug, safe='')}"
    data = fetch_json(url)
    jobs = []
    for j in data.get("jobs", []):
        if not j.get("isListed", True):
            continue
        location = j.get("location", "") or ""
        desc = j.get("descriptionPlain", "") or strip_html(j.get("descriptionHtml", "") or "")
        post_date = j.get("publishedAt", "")
        jobs.append({
            "company": company,
            "title": j.get("title", ""),
            "location": location,
            "is_remote": j.get("isRemote", False),
            "url": j.get("jobUrl", "") or j.get("applicationLink", "") or "",
            "platform": "ashby",
            "description": desc.strip(),
            "job_id": j.get("id", ""),
            "slug": slug,
            "post_date_str": post_date,
        })
    return jobs


def fetch_lever(company: str, slug: str) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    data = fetch_json(url)
    jobs = []
    for j in data:
        cats = j.get("categories", {})
        location = cats.get("location", "") or ""
        desc = j.get("descriptionPlain", "") or strip_html(j.get("description", "") or "")
        for section in j.get("lists", []):
            heading = section.get("text", "")
            body = strip_html(section.get("content", "") or "")
            if heading and body:
                desc += f"\n\n{heading}:\n{body}"
        # post_date = j.get("createdAt", "")
        post_date = datetime.fromtimestamp(
            int(j.get("createdAt")) / 1000,
            tz=timezone.utc ).date().isoformat()        
        jobs.append({
            "company": company,
            "title": j.get("text", ""),
            "location": location,
            "is_remote": "remote" in location.lower(),
            "url": j.get("hostedUrl", ""),
            "platform": "lever",
            "description": desc.strip(),
            "job_id": j.get("id", ""),
            "slug": slug,
            "post_date_str": post_date,
        })
    return jobs


def fetch_greenhouse(company: str, slug: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    data = fetch_json(url)
    jobs = []
    for j in data.get("jobs", []):
        location = j.get("location", {}).get("name", "") or ""
        title = re.sub(r"\s*\|.*$", "", j.get("title", "")).strip()
        post_date = j.get("updated_at", "")
        jobs.append({
            "company": company,
            "title": title,
            "location": location,
            "is_remote": "remote" in location.lower(),
            "url": j.get("absolute_url", ""),
            "platform": "greenhouse",
            "description": "",  # fetched on demand for new roles only
            "job_id": str(j.get("id", "")),
            "slug": slug,
            "post_date_str": post_date,
        })
    return jobs


def fetch_greenhouse_desc(slug: str, job_id: str) -> str:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{job_id}"
    try:
        data = fetch_json(url)
        return strip_html(data.get("content", "") or "").strip()
    except Exception:
        return ""


def fetch_workday(company: str, slug: str) -> list[dict]:
    # slug format: "<tenant>/<wd-host, e.g. wd1>/<site>", e.g. "kcura/wd1/External_Career_Site"
    tenant, host, site = slug.split("/")
    base = f"https://{tenant}.{host}.myworkdayjobs.com"
    api = f"{base}/wday/cxs/{tenant}/{site}/jobs"
    jobs = []
    offset = 0
    while True:
        data = fetch_json_post(api, {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": ""})
        postings = data.get("jobPostings", [])
        if not postings:
            break
        for j in postings:
            ext_path = j.get("externalPath", "")
            post_date = j.get("postedOn", "")
            # @Jose change
            # print(j.keys())
            jobs.append({
                "company": company,
                "title": j.get("title", ""),
                "location": j.get("locationsText", "") or "",
                "is_remote": False,
                "url": f"{base}/en-US/{site}{ext_path}",
                "platform": "workday",
                "description": "",
                "job_id": ext_path,
                "slug": slug,
                "post_date_str": post_date,
            })
        offset += 20
        if offset >= data.get("total", 0):
            break
    return jobs

# @Jose WORKDAY WAS HAVING MANY BLANK DESCRIPTIONS
def fetch_workday_desc(slug: str, ext_path: str) -> str:
    tenant, host, site = slug.split("/")
   
    url = f"https://{tenant}.{host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}{ext_path}"
    retries = 2
    for attempt in range(retries):
        try:
            # @Jose
            data = fetch_json(url)
            # SCOTTY WAS USING
            # data = fetch_json_post(url, {})
            return strip_html(data.get("jobPostingInfo", {}).get("jobDescription", "")).strip()

        except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < retries - 1:
                    sleep(sleep_time * (attempt + 1))
                    continue
                # print(f"\nWORKDAY DESC ERROR: {e} slug: {slug} ext_path: {ext_path}")
                print_to_log(Log_file,"\n\nWORKDAY DESC ERROR: {} slug: {} ext_path: {}\n\n",e,slug, ext_path)
                #print(e.read().decode())
                return ""
        except Exception as e:
                # print(f"\nWORKDAY DESC ERROR: {e} slug: {slug} ext_path: {ext_path}")
                print_to_log(Log_file,"\n\nWORKDAY DESC ERROR: {} slug: {} ext_path: {}\n\n",e,slug, ext_path)
                return ""


FETCHERS = {
    "ashby": fetch_ashby,
    "lever": fetch_lever,
    "greenhouse": fetch_greenhouse,
    "workday": fetch_workday,
    # "icims": fetch_icims,
}

# QUERIES ONE WATCHLIST ENTRY (RUNS INSIDE A THREADPOOLEXECUTOR WORKER)
# RETURNS (filtered_jobs, error_string_or_None) INSTEAD OF MUTATING SHARED
# LISTS DIRECTLY, SO IT'S SAFE TO CALL FROM MULTIPLE THREADS AT ONCE
def process_entry(entry: dict, no_filter: bool) -> tuple[list[dict], str | None]:
    platform = entry["platform"]
    company = entry["company"]
    slug = entry["slug"]
    key = f'{{"company":"{company}", "platform":"{platform}", "slug":"{slug}"}}'

    # fetcher is the function that will be called
    fetcher = FETCHERS.get(platform)
    # IF ATS VALUE DOESN'T HAVE A FETCHER FUNCTION
    if not fetcher:
        return [], f"{company}: unknown platform '{platform}'"

    try:
        jobs = fetcher(company, slug)
        if platform=="icims":
            print(f"{company}: returned {len(jobs)} jobs")
            print(jobs[:2])
    except urllib.error.HTTPError as e:
        err = (f"{company}: bad board/API\n"
               f"\tPlatform: {platform}\n"
               f"\tSlug: {slug}\n"
               f"\tError: HTTP {e.code}")
        print_to_log(Log_file,"Bad board/API Error: HTTP {} \tKey: {}\n\n",e.code,key)
        return [], err
    except Exception as e:
        err = (f"{company}: API error\n"
               f"\tPlatform: {platform}\n"
               f"\tSlug: {slug}\n"
               f"\tError: {e}")
        print_to_log(Log_file,"API Error: {} \tKey: {}\n\n",e,key)
        return [], err

    filtered = []
    for job in jobs:
        title = job["title"]
        if not no_filter and not is_relevant(title):
            continue

        # Workday list-view location text is unreliable ("27 Locations", a single
        # state, or a city with no country) so skip the heuristic filter for it and
        # rely on manual review of the fetched description instead.
        location = job["location"]
        if job["platform"] != "workday" and location and not job["is_remote"] and "remote" not in location.lower():
            if location and "united states" not in location.lower() and "us" not in location.lower():
                continue

        filtered.append(job)

    return filtered, None


# QUERIES ONE JOB'S DESCRIPTION (RUNS INSIDE A THREADPOOLEXECUTOR WORKER)
# MUTATES job IN PLACE -- SAFE BECAUSE EACH THREAD GETS A DIFFERENT job DICT
def fetch_desc(job: dict) -> None:
    if job["platform"] == "greenhouse" and not job["description"] and job["job_id"]:
        job["description"] = fetch_greenhouse_desc(job["slug"], job["job_id"])
    elif job["platform"] == "workday" and not job["description"] and job["job_id"]:
        job["description"] = fetch_workday_desc(job["slug"], job["job_id"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", dest="show_all",
                        help="Also show roles already in evaluated-jobs.csv")
    parser.add_argument("--new-only", action="store_true", dest="new_only",
                        help="Show only new roles (default behavior, included for clarity)")
    parser.add_argument("--company", help="Filter to one company by name or slug")
    parser.add_argument("--no-filter", action="store_true",
                        help="Skip keyword filter and show all roles found")
    args = parser.parse_args()

    watchlist: list[dict] = json.loads(WATCHLIST.read_text())
    print(f"Watchlist entries before dedupe: {len(watchlist)}")
    # DEDUPE JSON LIST
    # DEDUPE WATCHLIST (KEEP FIRST OCCURRENCE)
    seen = set()
    deduped = []
    # DEDUPE JSON
    for entry in watchlist:
        key = (entry["platform"], entry["slug"])
        if key not in seen:
            seen.add(key)
            deduped.append(entry)
    watchlist = deduped
    # DEDUPED JSON
    watchlist_len = len(watchlist)
    print(f"Watchlist entries after dedupe: {watchlist_len}\n")

    if args.company:
        q = args.company.lower()
        watchlist = [w for w in watchlist if q in w["slug"].lower() or q in w["company"].lower()]
        if not watchlist:
            print(f"No watchlist entry matching '{args.company}'", file=sys.stderr)
            return 1

    new_roles: list[dict] = []
    errors: list[str] = []

    # QUERY ALL WATCHLIST ENTRIES CONCURRENTLY (WAS: SEQUENTIAL for-LOOP)
    # max_workers=15 IS A STARTING POINT -- LOWER IT IF YOU SEE A SPIKE IN
    # HTTP ERRORS (RATE LIMITING) AFTER TURNING THIS ON
    with ThreadPoolExecutor(max_workers=15) as executor:
        future_to_entry = {
            executor.submit(process_entry, entry, args.no_filter): entry
            for entry in watchlist}
        
        for i, future in enumerate(as_completed(future_to_entry)):
            entry = future_to_entry[future]
            key = (entry["platform"], entry["company"], entry["slug"])
            if (i+1) % 100 == 0:
                print(f"Querying {i+1} of {watchlist_len}:", entry["company"])
            jobs, error = future.result()
            if error:
                errors.append(error)
            else:
                # CSV dedupe disabled (moving to SQLite)
                new_roles.extend(jobs)

    # Fetch descriptions for new Greenhouse/Workday roles (Ashby and Lever already include them)
    # ALSO PARALLELIZED -- EACH job DICT IS MUTATED IN PLACE BY A DIFFERENT THREAD
    with ThreadPoolExecutor(max_workers=15) as executor:
        list(executor.map(fetch_desc, new_roles))

    # THIS WAS JUST PRINTING INFO TO THE TERMINAL. 
    # SINCE IT NOW GOES IN A DB TABLE, IT'S NOT NEEDED ANYMORE.
    if new_roles and VERBOSE:
        print(f"\n{'='*60}")
        print(f"NEW - pre-deduped by title and job ID ({len(new_roles)})")
        print(f"{'='*60}")
    elif VERBOSE:
         print("\nNo new matching roles found.")

    if errors:
        print(f"\n{'='*60}")
        print(f"Errors - bad slug or dead board ({len(errors)})")
        print(f"{'='*60}")
        # PRINTS THE ERRORS
        if VERBOSE:
           for e in errors:
               print(f"  {e}")

##############################################################################################
##############################################################################################
##############################################################################################

    # UPDATED THIS PART:
    Save_jobs_db(new_roles)

    # UPDATES URL HISTORY
    Chrome_db_hist()

    # UPDATES TIME ZONE IN TABLE NEW_JOBS
    row = Update_TZ_by_state(JOBS_DB)

    # UPDATES FLAGS "NEW" AND IS_US TO TABLE NEW_JOBS
    new_jobs_count = Update_flags(JOBS_DB)

    # TOTAL COUNT
    total_count = Summarize_db(JOBS_DB,"new_jobs","")
    # IF THE NUMBERS DON'T ADD UP, THERE WERE DUPLICATES THAT WERE DISCARDED
    print(f"\nSummary: {new_jobs_count} new | {total_count-new_jobs_count} already evaluated | {len(errors)} errors\n")

    # UPDATE JOBS_HIST FROM SPECIFIED INPUT TABLE
    # TOTAL TABLE COUNT
    # total_count = Summarize_db(JOBS_DB,"jobs_hist","")
    #Update_jobs_hist(JOBS_DB,"new_jobs")

    # CREATE HTML LISTS
    create_html()

    # EXPORT NEW_JOBS TO EXCEL
    # TODAY'S DATE
    date_str = datetime.now().strftime("%Y-%m-%d")
    print()
    Exp_db_to_Excel(JOBS_DB,"new_jobs",f"_{date_str}","")

    return 0
    
# RUN THE CODE BELOW IF THE FILE IS MAIN
if __name__ == "__main__":
    # START
    start_time = default_timer()
    start_time_act = datetime.now()
    # RUN ATS QUERY
    exit_code = main()
    # FINISH
    end_time = default_timer()
    end_time_act = datetime.now()
    print("\nStart time:", start_time_act)
    print("End time:", end_time_act)
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time / 60:.2f} minutes\n")
    # THE END
    raise SystemExit(exit_code)

