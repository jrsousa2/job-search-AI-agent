# Job Search AI Agent

A Claude Code agent that uses Python code with a SQLite database to match jobs to a resume.

This is a work in progress.

```
job-search-AI-agent/
├── .gitignore                      # Git exclusions
├── Claude.md                       # Instructions Claude reads every session
├── SCRIPT.txt                      # Project notes and prompts
├── GitAI.bat                       # Git automation script
├── profile/
│   ├── og-resume.md                # Master resume
│   └── projects.md                 # Portfolio projects
├── data/
│   ├── new_jobs.md                 # Current list of jobs to be scored by Claude
│   └── watchlist.json              # Target companies and ATS platforms (template)
├── daily-digest/                   # Daily AI-generated job summaries
├── Excel/
│   └── New_jobs.xlsx               # Excel export of job matches (for testing)
├── Logs/
│   └── Errors_log.txt              # Runtime error log (usually wrong slug in watchlist)
├── Database/
│   └── jobs.db                     # SQLite database (with tables new_jobs and jobs_hist)
├── scripts/
│   ├── Anthropic.py                # Claude API integration (for testing)
│   ├── check-boards.py             # Queries APIs for supported ATS job boards
│   ├── Creates_jobs_AI_input.py    # Builds the AI input (.md) from the new_jobs table
│   ├── Creates_jobs_hist_db.py     # Maintains job history database
│   └── Export_db_to_Excel.py       # Exports database to Excel
└── README.md                       # Repository overview
```

### The workflow
After querying the APIs of a few ATS systems, the data is saved to a SQLite database table (new_jobs).
<br>Records for onsite jobs are discarded from the table.
<br>Since this batch job is supposed to run daily, the process I envisioned was come up with a single unique key 
for the jobs (final_job_id &ndash; comprised of platform, company and job_id &mdash; if job_id is not missing, which is nearly always the case
). 
<br>If, however, the job_id is missing, the unique key is platform, company and title.

The purpose of the final_job_id is to deduplicate the new jobs list, based on previous results. 
Therefore, a jobs history table is kept as well. Every time the job runs, the new jobs are added to the history table at the end of the process. 

Besides, a flag called New is updated every time the job runs in table new_jobs (by joining it with the history table). The flag is 1 if the job is actually new, and 0 otherwise.

For reporting purposes, the table new_jobs is exported to Excel (the flag allows to know which ones are new, and 
also allows only new jobs to be passed to Claude for evaluation).

File watchlist.json is a template (if you have a more complete list, feel free to send it to me).

The main code (check-boards.py) is based on a code I got from [Scotty Peterson](https://www.scottypeterson.net/blog/how-to-build-a-job-hunt-system-with-claude-code), but I have since made major changes to it 
(I think the SQLite approach has made the data much more manageable).
<br>Eventually, I will upload it here too.

### A snapshot of the table new_jobs:

![New Jobs Snapshot](https://raw.githubusercontent.com/jrsousa2/job-search-AI-agent/main/Excel/New_jobs_snapshot.PNG)

For a guide to this repository, please visit:

https://jrsousa2.github.io/#AI
