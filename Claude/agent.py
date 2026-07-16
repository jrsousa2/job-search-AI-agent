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

import config
from job_parser import parse_jobs
from url_verifier import verify_url
from scorer import score_jobs
from docs_gen import gen_docs_for_job
from watchlist import disc_watchlist_comps, load_existing_watchlist, save_suggestions
from pricing import estimate_token_cost, estimate_search_cost
import json 

# I ADDED THIS FUNCTION TO SHORTEN THE CODE
from write_html_digest import write_html_digest
# MY FUNCTIONS
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

    print("Reading source files...")
    claude_md = read_file(config.CLAUDE_MD_FILE)
    new_jobs_md = read_file(config.NEW_JOBS_FILE)
    og_resume = read_file(config.OG_RESUME_FILE)
    projects = read_file(config.PROJECTS_FILE)

    print("Parsing job postings...")
    jobs = parse_jobs(new_jobs_md)
    print(f"\tFound {len(jobs)} job(s) in new_jobs.md")

    print("Verifying job URLs...")
    valid_jobs, skipped = [], []
    for job in jobs:
        result = verify_url(job, timeout=config.URL_REQUEST_TIMEOUT)
        # if result["valid"]:
        if result["valid"] and result.get("confidence") == "high":
            job["_url_check"] = result
            valid_jobs.append(job)
        else:
            skipped.append({**job, "skip_reason": result["reason"]})
    print(f"  {len(valid_jobs)} valid, {len(skipped)} skipped")

    print("\n\nScoring jobs against resumes...")
    # scored = score_jobs(valid_jobs, claude_md, og_resume, projects)
    scored, scorer_usage = score_jobs(valid_jobs, claude_md, og_resume, projects)

    # TODAY'S DATE
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # SAVES RESULTS TO JSON FILE
    json_file = os.path.join(config.DATA_DIR, f"{date_str}_scored_jobs.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(scored, f, indent=2, ensure_ascii=False)

    recommended = sorted(
        [j for j in scored if j.get("meets_filters")],
        key=lambda j: j.get("score", 0),
        reverse=True,
    )

    print(f"  {len(recommended)} job(s) meet all filters")
    if len(recommended) < config.MIN_RECOMMENDED_JOBS:
        print(
            f"  NOTE: fewer than {config.MIN_RECOMMENDED_JOBS} qualifying jobs were "
            f"available in this batch ({len(recommended)} found)."
        )

    # TOP 10 JOBS
    top_for_docs = recommended[: config.TOP_N_FOR_DOCUMENTS]
    # ALL REMAINING JOBS (complement of top 10)
    remain_jobs = recommended[config.TOP_N_FOR_DOCUMENTS:]

    # --- Write daily-digest files ---
    os.makedirs(config.DIGEST_DIR, exist_ok=True)

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

    # JobS_URLs.html
    other_URLs_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Other_Job_URLs.html")

    write_html_digest(
        other_URLs_path,
        f"Job URLs — {date_str}",
        remain_jobs,
        [
          ("Score", "score"),
          ("Work arrangement", "work_arrangement"),
          ("URL", "url"),
        ],)

    # SKIPPED URLs HTML
    digest_skip_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Skipped_Jobs.html")

    # write_html_digest(
    #     digest_URLs_path,
    #     f"Skipped Jobs — {date_str}",
    #     skipped,
    #     [
    #        ("URL", "url"),
    #        ("Reason", "skip_reason"),
    #     ],)

    print(f"\n\nGenerating tailored resume + cover letter for top {len(top_for_docs)} job(s)...\n")
    doc_warnings = []
    for i, job in enumerate(top_for_docs):
        result = gen_docs_for_job(i, job, claude_md, og_resume, projects)
        job["_documents"] = result
        print(f"{i}. {job['company']} — {job['title']}: done")
        if result.get("page_warning"):
            doc_warnings.append(result["page_warning"])

    if doc_warnings:
        print("\nWarnings:")
        for w in doc_warnings:
            print(f"  - {w}")

    # --- Watchlist discovery ---
    print("\nRunning watchlist discovery (web search)...")
    existing_watchlist = load_existing_watchlist(config.WATCHLIST_FILE)
    # suggestions = disc_watchlist_comps(claude_md, og_resume, existing_watchlist)
    suggestions, watchlist_usage = disc_watchlist_comps(claude_md, og_resume, existing_watchlist)
    suggestions_path = save_suggestions(suggestions, date_str)
    print(f"Wrote {suggestions_path} ({len(suggestions)} suggestion(s))")

    # PRICING (IT'S MADE UP OF SCORER AND WATCHLIST AND TAILORED RESUMES)
    # --- Cost estimate ---
    total_input = scorer_usage.get("input_tokens", 0) + watchlist_usage.get("input_tokens", 0)
    total_output = scorer_usage.get("output_tokens", 0) + watchlist_usage.get("output_tokens", 0)
    
    # COST OF THE TAILORED FILES
    for job in top_for_docs:
        u = job.get("_documents", {}).get("usage", {})
        total_input += u.get("input_tokens", 0)
        total_output += u.get("output_tokens", 0)

    token_cost = estimate_token_cost(config.MODEL, total_input, total_output)
    search_count = watchlist_usage.get("server_tool_use", {}).get("web_search_requests", 0)
    search_cost = estimate_search_cost(search_count)
    total_cost = token_cost + search_cost

    print("\n--- Cost estimate for this run ---")
    print(f"  Input tokens:  {total_input:,}")
    print(f"  Output tokens: {total_output:,}")
    print(f"  Token cost:    ${token_cost:.2f}")
    print(f"  Web searches:  {search_count} (${search_cost:.2f})")
    print(f"  TOTAL:         ${total_cost:.2f}")
    print("  (Estimate only, at published list rates -- check console.anthropic.com for actual billing.)")
    
    # END OF THE CODE
    print("\nDone.")


if __name__ == "__main__":
    # CREATE AI INPUT
    rows = Create_AI_input(DB_FILE)
    if rows>0:
       main()
