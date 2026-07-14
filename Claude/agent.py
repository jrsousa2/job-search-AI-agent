"""
Full pipeline, following Claude.md:

1. Parse new_jobs.md
2. Verify each job URL (best-effort) -- skip invalid ones with a logged reason
3. Score + filter remaining jobs against og-resume.md / projects.md
4. Rank; recommend jobs that pass filters (aiming for >=10 per config)
5. Generate tailored resume + cover letter PDFs for the top N
6. Write daily-digest/<date>_Job_URLs.md, sorted by score
7. Write daily-digest/<date>_Skipped_Jobs.md for URL failures
8. Run watchlist discovery -> data/watchlist_suggestions.json (read-only
   against watchlist.json, never modifies it)

Usage:
    python agent.py
"""

import os
import datetime

import config
from job_parser import parse_jobs
from url_verifier import verify_url
from scorer import score_jobs
from document_generator import generate_documents_for_job
from watchlist import discover_watchlist_companies, load_existing_watchlist, save_suggestions


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
    print(f"  Found {len(jobs)} job(s) in new_jobs.md")

    print("Verifying job URLs...")
    valid_jobs, skipped = [], []
    for job in jobs:
        result = verify_url(job, timeout=config.URL_REQUEST_TIMEOUT)
        if result["valid"]:
            job["_url_check"] = result
            valid_jobs.append(job)
        else:
            skipped.append({**job, "skip_reason": result["reason"]})
    print(f"  {len(valid_jobs)} valid, {len(skipped)} skipped")

    print("Scoring jobs against resumes...")
    scored = score_jobs(valid_jobs, claude_md, og_resume, projects)

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

    top_for_docs = recommended[: config.TOP_N_FOR_DOCUMENTS]

    print(f"Generating tailored resume + cover letter for top {len(top_for_docs)} job(s)...")
    doc_warnings = []
    for job in top_for_docs:
        result = generate_documents_for_job(job, claude_md, og_resume, projects)
        job["_documents"] = result
        print(f"  {job['company']} — {job['title']}: done")
        if result.get("page_warning"):
            doc_warnings.append(result["page_warning"])

    # --- Write daily-digest files ---
    os.makedirs(config.DIGEST_DIR, exist_ok=True)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    digest_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Job_URLs.md")
    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(f"# Job URLs — {date_str}\n\n")
        for job in recommended:
            arrangement = "Hybrid" if "hybrid" in job.get("work_arrangement", "").lower() else "Remote"
            f.write(f"## {job['company']} — {job['title']}\n")
            f.write(f"- Score: {job.get('score')}\n")
            f.write(f"- Work arrangement: {arrangement}\n")
            f.write(f"- URL: {job['url']}\n\n")
    print(f"Wrote {digest_path}")

    if skipped:
        skip_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Skipped_Jobs.md")
        with open(skip_path, "w", encoding="utf-8") as f:
            f.write(f"# Skipped Jobs — {date_str}\n\n")
            for job in skipped:
                f.write(f"- **{job.get('company')}** — {job.get('title')}\n")
                f.write(f"  - URL: {job.get('url')}\n")
                f.write(f"  - Reason: {job['skip_reason']}\n\n")
        print(f"Wrote {skip_path}")

    if doc_warnings:
        print("\nWarnings:")
        for w in doc_warnings:
            print(f"  - {w}")

    # --- Watchlist discovery ---
    print("\nRunning watchlist discovery (web search)...")
    existing_watchlist = load_existing_watchlist(config.WATCHLIST_FILE)
    suggestions = discover_watchlist_companies(claude_md, og_resume, existing_watchlist)
    suggestions_path = save_suggestions(suggestions)
    print(f"Wrote {suggestions_path} ({len(suggestions)} suggestion(s))")

    print("\nDone.")


if __name__ == "__main__":
    main()
