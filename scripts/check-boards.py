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
from os.path import exists
from pathlib import Path

import sqlite3

REPO_ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_PATH = REPO_ROOT / "data" / "watchlist.json"
# EVALUATED_CSV = REPO_ROOT / "data" / "evaluated-jobs.csv"

# AN EXTERNAL LOG FILE THAT LOGS INVALID URL'S (SLUG)
Log_file = REPO_ROOT / "Logs" / "Errors_log.txt"

DESC_MAX_CHARS = 2000

# DB_FILE = "Database/jobs.db"
DB_FILE = REPO_ROOT / "Database" / "jobs.db"

# DO NOT PRINT TO TERMINAL
VERBOSE = False

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

# PRINTS TO EXTERNAL LOG FILE 
# OVERWITES THE FILE SO ONE KNOWA WHAT ATS URL ERRORS REMAIN
# args NEEDS TO BE A TUPLE
def print_to_log(Arq, txt, *args):
    mode = "w" if not hasattr(print_to_log, "called") else "a"

    with open(Arq, mode, encoding="utf-8") as file:
        file.write(txt.format(*args))

    print_to_log.called = True        

# SAVES THE RESULTS TO A SQLITE DB
def save_jobs_db(jobs: list[dict]) -> None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # DROP TABLE IF IT EXISTS
    cursor.execute("DROP TABLE IF EXISTS new_jobs")

    cursor.execute("""
        CREATE TABLE new_jobs (
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

    fields = ["platform", "company", "slug", "job_id", "title", "location", "is_remote", "is_hybrid", "url", "description",]

    # rows = [tuple(job.get(field) for field in fields) for job in jobs]

    # LOOP TO ADD A NEW FIELD
    rows = []
    for job in jobs:
        desc = (job.get("description") or "").lower()

        job["is_remote"] = 1 if job.get("is_remote") == 1 or "remote" in desc else 0
        job["is_hybrid"] = 1 if "hybrid" in desc else 0

        rows.append(tuple(job.get(field) for field in fields))

    cursor.executemany(f"""
        INSERT INTO new_jobs ({','.join(fields)})
        VALUES ({','.join(['?'] * len(fields))})
    """, rows)

    conn.commit()
    conn.close()

    print(f"\nSaved {len(jobs)} jobs to {DB_FILE} table new_jobs")

# UPDATES THE JOBS HISTORY TABLE
def update_history_jobs() -> None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO jobs_history (
            platform,
            company,
            slug,
            job_id,
            title,
            location,
            is_remote,
            is_hybrid,
            url
        )
        SELECT
            platform,
            company,
            slug,
            job_id,
            title,
            location,
            is_remote,
            is_hybrid,
            url
        FROM new_jobs
    """)

    conn.commit()
    conn.close()

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
    # evaluated, evaluated_ids = load_evaluated()

    if args.company:
        q = args.company.lower()
        watchlist = [w for w in watchlist if q in w["slug"].lower() or q in w["company"].lower()]
        if not watchlist:
            print(f"No watchlist entry matching '{args.company}'", file=sys.stderr)
            return 1

    new_roles: list[dict] = []
    already_evaluated: list[dict] = []
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

            # CSV dedupe temporarily disabled (moving to SQLite)
            new_roles.append(job)

    # Fetch descriptions for new Greenhouse/Workday roles (Ashby and Lever already include them)
    for job in new_roles:
        if job["platform"] == "greenhouse" and not job["description"] and job["job_id"]:
            job["description"] = fetch_greenhouse_description(job["slug"], job["job_id"])
        elif job["platform"] == "workday" and not job["description"] and job["job_id"]:
            job["description"] = fetch_workday_description(job["slug"], job["job_id"])

    # THIS IS JUST PRINTING INFO TO THE TERMINAL. 
    # SINCE IT NOW GOES IN A DB TABLE, IT'S NOT NEEDED ANYMORE.
    if new_roles and VERBOSE:
        print(f"\n{'='*60}")
        print(f"NEW - pre-deduped against evaluated-jobs.csv by title and job ID ({len(new_roles)})")
        print(f"{'='*60}")
        for j in new_roles:
            remote_tag = " [remote]" if j["is_remote"] else f" [{j['location']}]" if j["location"] else ""
            print(f"\n  {j['company']} — {j['title']}{remote_tag}")
            if j["url"]:
                print(f"  URL: {j['url']}")
            desc = j.get("description", "").strip()
            if desc:
                truncated = desc[:DESC_MAX_CHARS] + ("..." if len(desc) > DESC_MAX_CHARS else "")
                print(f"  ---")
                print(f"  {truncated}")
    elif VERBOSE:
         print("\nNo new matching roles found.")

    if args.show_all and already_evaluated and VERBOSE:
        print(f"\n{'='*60}")
        print(f"Already in evaluated-jobs.csv ({len(already_evaluated)})")
        print(f"{'='*60}")
        for j in already_evaluated:
            remote_tag = " [remote]" if j["is_remote"] else ""
            print(f"  {j['company']} — {j['title']}{remote_tag}")

    if errors:
        print(f"\n{'='*60}")
        print(f"Errors - bad slug or dead board ({len(errors)})")
        print(f"{'='*60}")
        for e in errors:
            print(f"  {e}")

    # UPDATED THIS PART:
    save_jobs_db(new_roles)

    # CREATES HISTORY

    print(f"\nSummary: {len(new_roles)} new | {len(already_evaluated)} already evaluated | {len(errors)} errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
