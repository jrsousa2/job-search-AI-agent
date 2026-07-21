# THE AI USAGE HAPPENS IN 3 TASKS: SCORING, WATCHLIST AND DOC GENERATION.
# PROMPT CACHING IS ONLY RECOMMENDED FOR WATCHLIST AND DOC GENERATION.

"""
Full pipeline, following Claude.md:

1. Parse new_jobs.md
2. Verify each job URL (best-effort) -- skip invalid ones with a logged reason
3. Score + filter remaining jobs against og-resume.md / projects.md
4. Rank; recommend jobs that pass filters (aiming for >=10 per config)
5. Generate tailored resume + cover letter PDFs for the top N
6. Write daily-digest/<date>_Job_URLs.md, sorted by score
7. Write daily-digest/<date>_Skipped_Jobs.md for URL failures
8. Run watchlist discovery -> daily-digest/watchlist_suggestions.json (read-only
   against watchlist.json, never modifies it)

Usage:
    python agent.py
    python D:\Agent\Claude\agent.py
"""

import os
import datetime
import json

# OTHER PROGRAMS
import config
from job_parser import parse_jobs
from url_verifier import verify_url
from scorer import score_jobs
from docs_gen import gen_docs_for_job
from pricing import estimate_token_cost
from load_jobs_db import load_jobs_db

Score_with_AI = False

# I ADDED THIS FUNCTION TO SHORTEN THE CODE
from write_html_digest import write_html_digest

from pathlib import Path
import sys

# ADD SUBOLDER scripts
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# MY FUNCTIONS IN scripts
from Create_AI_input import Create_AI_input
from Repo_root import DB_FILE


def read_file(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Expected input file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    if not config.API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set. See config.py.")
    
    # --- Write daily-digest files ---
    os.makedirs(config.DIGEST_DIR, exist_ok=True)
    
    # TODAY'S DATE
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # CREATING JOBS    
    print("Loading job postings...")
    jobs = load_jobs_db(DB_FILE)

    # ONLY TOP COMPANY JOBS
    jobs = [job for job in jobs if job["top_company_job"] == 1]
    # jobs = parse_jobs(new_jobs_md)
    print(f"\tFound {len(jobs)} job(s) in database")

    print("Verifying job URLs...")
    valid_jobs, skipped = [], []
    verify_urls = False
    if verify_urls:
        for job in jobs:
            result = verify_url(job, timeout=config.URL_REQUEST_TIMEOUT)
            # if result["valid"]:
            if result["valid"] and result.get("confidence") == "high":
                job["_url_check"] = result
                valid_jobs.append(job)
                # IF THE RESULT IS NOT VALID WITH HIGH CONFIDENCE, THE JOB LISTING IS SKIPPED.
            else:
                skipped.append({**job, "skip_reason": result["reason"]})
    # PRINTS COUNTS
    print(f"  {len(valid_jobs)} valid, {len(skipped)} skipped")

    if Score_with_AI:
        print("Reading source files...")
        # new_jobs_md = read_file(config.NEW_JOBS_FILE)
        claude_md = read_file(config.CLAUDE_MD_FILE)
        og_resume = read_file(config.OG_RESUME_FILE)
        projects = read_file(config.PROJECTS_FILE)
        print("\n\nScoring jobs against resumes...")
        scored, scorer_usage = score_jobs(valid_jobs, claude_md, og_resume, projects)

        # COST
        score_input = scorer_usage.get("input_tokens", 0)
        score_cache_write = scorer_usage.get("cache_creation_input_tokens", 0)
        score_cache_read = scorer_usage.get("cache_read_input_tokens", 0)
        score_output = scorer_usage.get("output_tokens", 0)

        # SAVES RESULTS TO JSON FILE
        json_file = os.path.join(config.DATA_DIR, f"{date_str}_scored_jobs.json")
        with open(json_file, "w", encoding="utf-8") as f:
             json.dump(scored, f, indent=2, ensure_ascii=False)

        # THESE PASSED THE FILTER (IN DESC ORDER)
        recommended = sorted(
        [j for j in scored if j.get("meets_filters")],
        key=lambda j: j.get("score", 0), reverse=True, )

        # THESE DIDN'T PASS THE FILTER 
        failed_filter = sorted(
        [j for j in scored if not j.get("meets_filters")],
        key=lambda j: j.get("score", 0), reverse=True, )

        # Failed AI Prompt Filters - Job URLs
        fail_AI_filter_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Fail_AI_Filter_URLs.html")
        write_html_digest(
        fail_AI_filter_path,
        f"Failed filter - Job URLs — {date_str}",
        failed_filter,
        [("Score", "score"),
        ("Work arrangement", "work_arrangement"),
        ("URL", "url"),
        ("Reason", "filter_notes"),],)
    else:
        #recommended = valid_jobs
        recommended = jobs
        score_input = 0
        score_cache_write = 0
        score_cache_read = 0
        score_output = 0 

    # FROM HERE BELOW IT CAN BE EITHE AI OR HEURISTIC
    print(f"  {len(recommended)} job(s) meet all filters")
    if len(recommended) < config.MIN_RECOMMENDED_JOBS:
        print(
            f"  NOTE: fewer than {config.MIN_RECOMMENDED_JOBS} qualifying jobs were "
            f"available in this batch ({len(recommended)} found).")

    # TOP 10 JOBS
    top_for_docs = recommended[: config.TOP_N_FOR_DOCUMENTS]
    # ALL REMAINING JOBS (complement of top 10)
    other_jobs = recommended[config.TOP_N_FOR_DOCUMENTS:]

    # ONLY TOP COMPANY JOBS
    # top_company_jobs = [job for job in recommended if job["top_company_job"] == 1]

    # # TOP N JOBS
    # top_for_docs = top_company_jobs[:config.TOP_N_FOR_DOCUMENTS]

    # # ALL REMAINING TOP COMPANY JOBS
    # other_jobs = top_company_jobs[config.TOP_N_FOR_DOCUMENTS:]

    # Top 10 - Job URLs
    top10_URLs_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Top10_URLs.html")
    write_html_digest(
        top10_URLs_path,
        f"Top 10 Job URLs — {date_str}",
        top_for_docs,
        [("Platform", "platform"),
         ("Posted", "post_date"),
         ("Location", "location"),
         ("Score", "score"),
         ("Work arrangement", "work_arrangement"),
         ("URL", "url"),],)

    # Other Scored - Job URLs
    other_URLs_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Other_URLs.html")
    write_html_digest(
        other_URLs_path,
        f"Other Job URLs — {date_str}",
        other_jobs,
        [("Platform", "platform"),
         ("Posted", "post_date"),
         ("Location", "location"),
         ("Score", "score"),
         ("Work arrangement", "work_arrangement"),
         ("URL", "url"),],)
 
    # Failed URL TEST - Job URLs
    failed_URL_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Failed_URLs.html")
    # SKIPPED JOBS
    write_html_digest(
        failed_URL_path,
        f"Skipped Jobs — {date_str}",
        skipped,
        [("Platform", "platform"),
         ("Posted", "post_date"),
         ("Location", "location"),
         ("Work arrangement", "work_arrangement"),
         ("URL", "url"),
         ("Reason", "skip_reason"),],)

    print(f"\n\nGenerating tailored resume + cover letter for top {len(top_for_docs)} job(s)...\n")
    USE_CACHING_THRESHOLD = 3  # or 3, per the margin note above
    use_caching = len(top_for_docs) >= USE_CACHING_THRESHOLD
    doc_warnings = []
    for i, job in enumerate(top_for_docs):
        result = gen_docs_for_job(i, job, claude_md, og_resume, projects, use_caching)
        job["_documents"] = result
        print(f"{i+1}. {job['company']} — {job['title']}: done")
        if result.get("page_warning"):
            doc_warnings.append(result["page_warning"])

    if doc_warnings:
        print("\nWarnings:")
        for w in doc_warnings:
            print(f"  - {w}")

    # PRICING (IT'S MADE UP OF SCORER,  WATCHLIST AND TAILORED FILES)
    # --- Cost estimate ---
    # COST OF THE TAILORED FILES
    tailor_input = 0
    tailor_cache_write = 0
    tailor_cache_read = 0
    tailor_output = 0
    for job in top_for_docs:
        u = job.get("_documents", {}).get("usage", {})
        tailor_input += u.get("input_tokens", 0)
        tailor_cache_write += u.get("cache_creation_input_tokens", 0)
        tailor_cache_read += u.get("cache_read_input_tokens", 0)
        tailor_output += u.get("output_tokens", 0)

    total_input = score_input + tailor_input
    total_cache_write = score_cache_write + tailor_cache_write
    total_cache_read = score_cache_read + tailor_cache_read
    total_output = score_output + tailor_output

    token_cost = estimate_token_cost(
        config.MODEL, total_input, total_output,
        cache_write_tokens=total_cache_write, cache_read_tokens=total_cache_read,)
    
    # total_cost = token_cost + search_cost (SINCE SEARCH IS NO LONGER BEING DONE)
    total_cost = token_cost

    print("\n--- Cost estimate for this run ---")
    print(f"{'':<15}{'Scorer':>12}{'Watchlist':>12}{'Tailor':>12}{'Total':>12}")
    print(f"{'Input':<15}{score_input:>12,}{tailor_input:>12,}{total_input:>12,}")
    print(f"{'Cache write':<15}{score_cache_write:>12,}{tailor_cache_write:>12,}{total_cache_write:>12,}")
    print(f"{'Cache read':<15}{score_cache_read:>12,}{tailor_cache_read:>12,}{total_cache_read:>12,}")
    print(f"{'Output':<15}{score_output:>12,}{tailor_output:>12,}{total_output:>12,}")
    print()
    print(f"Token cost:   ${token_cost:.2f}")
    #print(f"Web searches: {search_count} (${search_cost:.2f})")
    print(f"TOTAL:        ${total_cost:.2f}")
    print("(Estimate only, at published list rates -- check console.anthropic.com for actual billing.)")

    # END OF THE CODE
    print("\nDone.")

# CALLS THE CODE
if __name__ == "__main__":
    # CREATE AI INPUT
    # rows = Create_AI_input(DB_FILE)
    # if rows>0:
    main()
