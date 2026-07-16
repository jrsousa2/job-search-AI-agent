# Edit the paths below ONCE. new_jobs.md is the file you'll replace before
# each run; the other 3 stay fixed.

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# --- Your 4 source files -------------------------------------------------
CLAUDE_MD_FILE = REPO_ROOT / "Claude.md"
NEW_JOBS_FILE = REPO_ROOT / "data" / "new_jobs.md"
OG_RESUME_FILE = REPO_ROOT / "profile" / "og-resume.md"
PROJECTS_FILE = REPO_ROOT / "profile" / "projects.md"

# --- Existing watchlist (read-only; script must never write to this) -----
WATCHLIST_FILE = REPO_ROOT / "data" / "watchlist.json"

# --- Root output folder. 
# The script creates these subfolders inside it:
#     resumes/            tailored resumes + cover letters (PDF)
#     daily-digest/        <date>_Job_URLs.md, skip logs and watchlist_suggestions.json
#     data/                
OUTPUT_ROOT = REPO_ROOT

RESUMES_DIR      = os.path.join(OUTPUT_ROOT, "resumes")
DIGEST_DIR       = os.path.join(OUTPUT_ROOT, "daily-digest")
DATA_DIR         = os.path.join(OUTPUT_ROOT, "data")
TEMPLATES_DIR    = os.path.join(OUTPUT_ROOT, "templates")

# --- API ------------------------------------------------------------------
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL   = "claude-sonnet-4-6"

# --- Behavior knobs --------------------------------------------------------
MIN_RECOMMENDED_JOBS = 10   # "at least 10" per Claude.md
TOP_N_FOR_DOCUMENTS  = 10   # tailored resume+cover letter only for top N
URL_REQUEST_TIMEOUT  = 15   # seconds, for URL verification
