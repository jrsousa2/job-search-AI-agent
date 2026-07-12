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
# from os.path import exists
from pathlib import Path

import pandas as pd
import sqlite3

REPO_ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_PATH = REPO_ROOT / "data" / "watchlist.json"

# AN EXTERNAL LOG FILE THAT LOGS INVALID URL'S (SLUG)
Log_file = REPO_ROOT / "Logs" / "Errors_log.txt"

# THE SQLITE DB
DB_FILE = REPO_ROOT / "Database" / "jobs.db"

# DO NOT PRINT TO TERMINAL
VERBOSE = True

# THIS IS THE LIST OF KW'S TO LOOK FOR IN THE JOB TITLE
TITLE_KEYWORDS = [
    "data analyst",
    "senior data analyst",
    "data scientist",
    "analytics",
    "business intelligence",
    "bi analyst",
    "sql",
    "python",
    "machine learning",
    "data engineer",
    "analytics engineer",
    "risk analyst",
    "fraud analyst",
    "aml",
    "modeling",
    "insurance",
    "predictive",
    "sas",
    "viya",
    "statistical",
    "statistics",
    "statistician",
    "data manager",]

###########################################################################
###########################################################################
###########################################################################
# NEW FUNCTIONS ADDED BY JOSE

# PRINTS TO EXTERNAL LOG FILE 
# OVERWITES THE FILE SO ONE KNOWS WHAT ATS URL ERRORS REMAIN
# args IS A TUPLE
def print_to_log(Arq, txt, *args):
    mode = "w" if not hasattr(print_to_log, "called") else "a"

    with open(Arq, mode, encoding="utf-8") as file:
        file.write(txt.format(*args))

    print_to_log.called = True        

# GET NUMBER OF ROWS FROM TABLE WITH A FILTER
def summarize_db(input_table: str,filter: str)->int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # ROWS
    cursor.execute(f"SELECT COUNT(*) FROM {input_table} {filter}")
    row_count = cursor.fetchone()[0]
    conn.close()
    print("Table",input_table,":",row_count,"rows")
    # SUMMARY
    return row_count

# EXPORT A DB TABLE TO EXCEL
def exp_to_excel(input_table: str, suff: str, filter: str) -> None:
    output_file = f"{input_table}{suff}.xlsx"
    EXCEL_FILE = REPO_ROOT / "Excel" / output_file
    conn = sqlite3.connect(DB_FILE)

    # SAVE QUERY OUTPUT TO A DF
    df = pd.read_sql_query(f"SELECT * FROM {input_table} {filter}", conn)
    df.to_excel(EXCEL_FILE, index=False)
    # DISPLAY MSG
    print("Table",input_table,"exported to",output_file)
    conn.close()

# SAVES THE ATS RESULTS TO A SQLITE DB TABLE
def save_jobs_db(jobs: list[dict]) -> None:
    conn = sqlite3.connect(DB_FILE)
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
            location TEXT,
            is_remote BOOLEAN,
            is_hybrid BOOLEAN,
            url TEXT,
            description TEXT
        )
    """)

    fields = ["final_job_id", "platform", "company", "slug", "job_id", "title", 
              "location", "is_remote", "is_hybrid", "url", "description",]

    # LOOP TO ADD A NEW FIELD
    rows = []
    for job in jobs:
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
        
        # USE BOTH FIELDS TO CHECK FOR MAIN KEYWORDS
        text = f"{desc} {url}"

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

    conn.commit()
    conn.close()

    # PRINTS STATS
    print(f"\nSaved {len(jobs)} jobs to {DB_FILE} table new_jobs")
    # PRINTS RESULTS TO LOG FILE AS WELL
    print_to_log(Log_file,"\n\nSaved {} jobs to {} table new_jobs\n\n",len(jobs),DB_FILE)

# ADDS FLAG "NEW" TO TABLE NEW_JOBS
def add_New_flag() -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE new_jobs ADD COLUMN New INTEGER")

    cursor.execute("""
    UPDATE new_jobs
    SET New = CASE
        WHEN EXISTS (
            SELECT 1
            FROM jobs_hist h
            WHERE h.final_job_id = new_jobs.final_job_id
        )
        THEN 1
        ELSE 0
    END
    """)
    # COMMITS CHANGES
    conn.commit()

    # GET NUMBER OF NEW JOBS
    row_count = summarize_db("new_jobs","where New=1")
    conn.close()

    return row_count

# UPDATES THE JOBS HISTORY TABLE
# UNIQUE KEY IS final_job_id (IGNORE WON'T INSERT DUPLICATES)
def update_jobs_hist() -> None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    start_count = summarize_db("jobs_hist","")
    cols = "final_job_id, platform, company, slug, job_id, title, location, is_remote, is_hybrid, url"
    # INSERTS RECORDS
    cursor.execute(f"""
        INSERT OR IGNORE INTO jobs_hist
        ({cols})
        SELECT {cols}
        FROM new_jobs
        where is_remote=1 or is_hybrid=1
    """)
    # COMMITS
    conn.commit()
    conn.close()
    # GET STATS
    end_count = summarize_db("jobs_hist","")
    print("Added",end_count-start_count,"records to jobs_hist table")


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

def is_relevant(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in TITLE_KEYWORDS)


def fetch_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode())


def fetch_json_post(url: str, body: dict) -> object:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
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
        })
    return jobs


def fetch_greenhouse(company: str, slug: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    data = fetch_json(url)
    jobs = []
    for j in data.get("jobs", []):
        location = j.get("location", {}).get("name", "") or ""
        title = re.sub(r"\s*\|.*$", "", j.get("title", "")).strip()
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
        })
    return jobs


def fetch_greenhouse_description(slug: str, job_id: str) -> str:
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
            })
        offset += 20
        if offset >= data.get("total", 0):
            break
    return jobs


def fetch_workday_description(slug: str, ext_path: str) -> str:
    tenant, host, site = slug.split("/")
    url = f"https://{tenant}.{host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}{ext_path}"
    try:
        data = fetch_json_post(url, {})
        return strip_html(data.get("jobPostingInfo", {}).get("jobDescription", "") or "").strip()
    except Exception:
        return ""

FETCHERS = {
    "ashby": fetch_ashby,
    "lever": fetch_lever,
    "greenhouse": fetch_greenhouse,
    "workday": fetch_workday,
}

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

    watchlist: list[dict] = json.loads(WATCHLIST_PATH.read_text())

    if args.company:
        q = args.company.lower()
        watchlist = [w for w in watchlist if q in w["slug"].lower() or q in w["company"].lower()]
        if not watchlist:
            print(f"No watchlist entry matching '{args.company}'", file=sys.stderr)
            return 1

    new_roles: list[dict] = []
    # already_evaluated: list[dict] = []
    errors: list[str] = []
    # batch_keys: set[str] = set()
    # batch_ids: set[str] = set()

    for entry in watchlist:
        company = entry["company"]
        platform = entry["platform"]
        slug = entry["slug"]
        fetcher = FETCHERS.get(platform)
        if not fetcher:
            errors.append(f"{company}: unknown platform '{platform}'")
            continue

        try:
            jobs = fetcher(company, slug)
        except urllib.error.HTTPError as e:
            errors.append(
                        f"{company}: bad board/API\n"
                        f"\tPlatform: {platform}\n"
                        f"\tSlug: {slug}\n"
                        f"\tError: HTTP {e.code}")
            
            # PRINTS ERRORS TO LOCAL LOG FILE
            print_to_log(Log_file,"{}: bad board/API\n \tPlatform: {}\n \tSlug: {}\n \tError: HTTP {}\n\n",company,platform,slug,e.code)
            continue
        except Exception as e:
            errors.append(
                        f"{company}: API error\n"
                        f"\tPlatform: {platform}\n"
                        f"\tSlug: {slug}\n"
                        f"\tError: {e}")
            
            # PRINTS ERRORS TO LOCAL LOG FILE
            print_to_log(Log_file,"{}: API error\n tPlatform: {}\n \tSlug: {}\n \tError: {}\n\n",company,platform,slug,e)
            continue

        for job in jobs:
            title = job["title"]
            if not args.no_filter and not is_relevant(title):
                continue

            # Workday list-view location text is unreliable ("27 Locations", a single
            # state, or a city with no country) so skip the heuristic filter for it and
            # rely on manual review of the fetched description instead.
            location = job["location"]
            if job["platform"] != "workday" and location and not job["is_remote"] and "remote" not in location.lower():
                if location and "united states" not in location.lower() and "us" not in location.lower():
                    continue

            # key = normalize_key(company, title)
            # job_id = str(job["job_id"]) if job["job_id"] else extract_job_id(job["url"])

            # CSV dedupe disabled (moving to SQLite)
            new_roles.append(job)

    # Fetch descriptions for new Greenhouse/Workday roles (Ashby and Lever already include them)
    for job in new_roles:
        if job["platform"] == "greenhouse" and not job["description"] and job["job_id"]:
            job["description"] = fetch_greenhouse_description(job["slug"], job["job_id"])
        elif job["platform"] == "workday" and not job["description"] and job["job_id"]:
            job["description"] = fetch_workday_description(job["slug"], job["job_id"])

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

    # UPDATED THIS PART:
    save_jobs_db(new_roles)

    # UPDATES HISTORY

    # {len(already_evaluated)}
    print(f"\nSummary: {len(new_roles)} new | ? already evaluated | {len(errors)} errors")

    # ADDS FLAG "NEW" TO TABLE NEW_JOBS
    add_New_flag()

    # EXPORT NEW_JOBS TO EXCEL
    exp_to_excel("new_jobs","new","")

    # UPDATE JOBS_HIST TABLE
    # update_jobs_hist()

    # EXPORT ALREADY EVALUATED TO EXCEL
    # exp_to_excel("new_jobs","(old)","where New=0")

    return 0
    

if __name__ == "__main__":
    raise SystemExit(main())
