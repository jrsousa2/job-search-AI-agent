# Job Search Agent

Implements the workflow described in your Claude.md: reads new job
postings, verifies URLs, scores/filters them against your two resumes,
generates tailored resume + cover letter PDFs for the top matches, and
discovers new watchlist company candidates via web search.

## Files

| File | Role |
|---|---|
| `config.py` | Edit this once: the 5 file paths + output folder |
| `job_parser.py` | Parses `new_jobs.md` into structured job entries |
| `url_verifier.py` | Best-effort check that each job URL is live and real (see limitation below) |
| `scorer.py` | Scores + filters all valid jobs in one API call, using Claude.md's rules |
| `document_generator.py` | Generates tailored resume + cover letter content per job, renders to PDF |
| `watchlist.py` | Uses the API's web_search tool to find new target companies |
| `agent.py` | Runs the full pipeline end-to-end |
| `templates/resume_template.html` | Resume PDF layout (edit CSS to restyle) |
| `templates/cover_letter_template.html` | Cover letter PDF layout |

## Setup

1. `pip install -r requirements.txt`
2. WeasyPrint system dependencies (Pango/Cairo) — see prior README notes,
   or https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
3. Set your API key: `export ANTHROPIC_API_KEY="sk-ant-..."`
4. Edit `config.py` with your 5 real paths (Claude.md, new_jobs.md,
   og-resume.md, projects.md, watchlist.json) and your output folder.

## Running it

```
python agent.py
```

Each run creates/updates, inside your output folder:
```
resumes/
    2026-07-13_Allstate_Remote_Resume.pdf
    2026-07-13_Allstate_Remote_CoverLetter.pdf
    ...
daily-digest/
    2026-07-13_Job_URLs.md
    2026-07-13_Skipped_Jobs.md   (only if any jobs failed URL verification)
data/
    watchlist_suggestions.json
```

`og-resume.md`, `projects.md`, and `watchlist.json` are only ever read,
never written to.

## Important limitation: URL verification

Workday postings (and some other ATS platforms) render their content
with JavaScript. A plain HTTP request only sees the initial page shell,
not the rendered job title/description — even for genuinely live
postings. `url_verifier.py` handles this honestly:

- Confirms the page loads (no 404, no redirect to a generic careers page)
- For JS-heavy platforms, marks the job `"confidence": "low"` with a note
  to manually double check, rather than either wrongly rejecting it or
  falsely claiming full verification
- For simpler static pages, it also checks that the company name and
  most title words actually appear in the page text

If you want fully automated verification that actually reads rendered
job text (recommended if you're processing many jobs and don't want to
manually spot-check the low-confidence ones), swap in Playwright:

```
pip install playwright
playwright install chromium
```

and replace the `requests.get(...)` call in `url_verifier.py` with a
Playwright page load + `page.content()` after waiting for the job title
element to render. This is a bigger dependency (it installs a real
browser binary) so it's left as an opt-in upgrade rather than the default.

## How "judgment" vs. "mechanics" is split

- **Mechanics that are hardcoded** (and must be manually updated if you
  change them in Claude.md later): folder names (`resumes/`,
  `daily-digest/`, `data/`), the filename convention, the JSON schemas
  passed to the API, the "at least 10 recommended" and "top 10 get
  documents" thresholds (`config.py`).
- **Judgment delegated to Claude via API, using your live Claude.md as
  context**: scoring/ranking logic, resume tailoring content, cover
  letter wording, watchlist company discovery. If you tweak scoring
  weights or preferences in Claude.md, those calls will pick it up
  automatically without any code changes.

## Cost

Roughly 2 API calls per run (1 scoring call for all jobs, 1 watchlist
call) plus 2 calls per job that makes the top-10 cut (resume + cover
letter content). For a typical batch this is well under a dollar in
API credit with claude-sonnet-4-6.
