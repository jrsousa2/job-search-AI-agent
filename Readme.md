# Job Search AI Agent

A Claude Code agent that uses Python code with a SQLite database to match jobs to a resume.

```
job-search-AI-agent/
├── .gitignore                      # Git exclusions
├── CLAUDE.md                       # Instructions Claude reads every session
├── SCRIPT.txt                      # Project notes and prompts
├── GitAI.bat                       # Git automation script
├── profile/
│   ├── og-resume.md                # Master resume
│   └── projects.md                 # Portfolio projects
├── data/
│   ├── new_jobs.md                 # Current list of jobs to be scored by Claude
│   └── watchlist.json              # Target companies and ATS platforms
├── daily-digest/                   # Daily AI-generated job summaries
├── Excel/
│   └── New_jobs.xlsx               # Excel export of job matches (for testing)
├── Logs/
│   └── Errors_log.txt              # Runtime error log (usually wrong slug in watchlist)
├── Database/
│   └── jobs.db                     # SQLite database (with tables new jobs and history)
├── scripts/
│   ├── Anthropic.py                # Claude API integration
│   ├── check-boards.py             # Scrapes supported ATS job boards
│   ├── Creates_jobs_AI_input.py    # Builds AI input from matched jobs
│   ├── Creates_jobs_history_db.py  # Maintains job history database
│   └── Export_db_to_Excel.py       # Exports database to Excel
└── README.md                       # Repository overview
```

### A snapshot of the New_jobs table:

![New Jobs Snapshot](https://raw.githubusercontent.com/jrsousa2/job-search-AI-agent/main/Excel/New_jobs_snapshot.PNG)

For a guide to this repository, please visit:

https://jrsousa2.github.io/#AI
