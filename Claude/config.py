"""
Edit the paths below ONCE. new_jobs.md is the file you'll replace before
each run; the other 3 stay fixed.
"""

import os

# --- Your 4 source files -------------------------------------------------
CLAUDE_MD_FILE   = "/path/to/Claude.md"
NEW_JOBS_FILE    = "/path/to/new_jobs.md"      # <-- replace this before each run
OG_RESUME_FILE   = "/path/to/og-resume.md"     # never modified by the script
PROJECTS_FILE    = "/path/to/projects.md"      # never modified by the script

# --- Existing watchlist (read-only; script must never write to this) -----
WATCHLIST_FILE   = "/path/to/watchlist.json"

# --- Root output folder. The script creates these subfolders inside it:
#     resumes/            tailored resumes + cover letters (PDF)
#     daily-digest/        <date>_Job_URLs.md and skip logs
#     data/                watchlist_suggestions.json
OUTPUT_ROOT = "/path/to/job_search_agent_output"

RESUMES_DIR      = os.path.join(OUTPUT_ROOT, "resumes")
DIGEST_DIR       = os.path.join(OUTPUT_ROOT, "daily-digest")
DATA_DIR         = os.path.join(OUTPUT_ROOT, "data")

# --- API ------------------------------------------------------------------
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL   = "claude-sonnet-4-6"

# --- Behavior knobs --------------------------------------------------------
MIN_RECOMMENDED_JOBS = 10   # "at least 10" per Claude.md
TOP_N_FOR_DOCUMENTS  = 10   # tailored resume+cover letter only for top N
URL_REQUEST_TIMEOUT  = 15   # seconds, for URL verification
