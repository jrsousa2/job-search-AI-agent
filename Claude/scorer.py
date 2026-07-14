"""
Sends all verified jobs + both resumes + the Claude.md rules to the API
in one call, and gets back a score (0-100), filter pass/fail, and brief
reasoning for each job. Scoring all jobs together (rather than one call
per job) keeps the ranking internally consistent.
"""

import json
import requests

import config


def score_jobs(jobs: list[dict], claude_md: str, og_resume: str, projects: str) -> list[dict]:
    if not jobs:
        return []

    system_prompt = f"""
You are scoring job postings against a candidate's resume, following the
rules below exactly.

=== FULL INSTRUCTIONS (Claude.md) ===
{claude_md}
=== END INSTRUCTIONS ===

=== MAIN RESUME (og-resume.md) -- weight this most heavily ===
{og_resume}
=== END MAIN RESUME ===

=== SECONDARY PROFILE (projects.md) -- weight this less heavily ===
{projects}
=== END SECONDARY PROFILE ===

You will be given a JSON array of job postings. For EACH job, return an
object with this exact schema. Respond with ONLY a JSON array, no
markdown fences, no commentary:

[
  {{
    "company": "string, copied from input",
    "title": "string, copied from input",
    "score": 0-100,
    "meets_filters": true/false,
    "filter_notes": "brief note on which filter rules passed/failed (remote/hybrid days, US location/relocation, citizenship/sponsorship, industry, seniority)",
    "reasoning": "1-2 sentence explanation of the score"
  }}
]

Apply every filter and scoring rule from the instructions above (remote
preferred over hybrid, hybrid only if <=3 onsite days and a great match,
US jobs only, relocation limited to Florida/North Carolina, no visa
sponsorship needed since candidate is a US citizen, score managerial
roles very low, weight skills from the main resume higher than the
secondary profile, prefer the listed industries and higher pay/larger
companies). Jobs that fail a hard filter (not remote/qualifying hybrid,
not US, requires sponsorship-incompatible status, etc.) should have
meets_filters=false and typically a low score.
"""

    jobs_input = [
        {"company": j["company"], "title": j["title"], "location": j["location"],
         "work_arrangement": j["work_arrangement"], "description": j["description"]}
        for j in jobs
    ]

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": config.API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": config.MODEL,
            "max_tokens": 8000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": json.dumps(jobs_input, indent=2)}],
        },
        timeout=180,
    )
    response.raise_for_status()
    data = response.json()

    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        scores = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Scoring response wasn't valid JSON:\n{text}\n\nError: {e}")

    # Merge scores back onto the original job dicts (keep URL, platform, etc.)
    merged = []
    for job in jobs:
        match = next(
            (s for s in scores if s["company"].lower() == job["company"].lower()
             and s["title"].lower() == job["title"].lower()),
            None,
        )
        if match:
            job = {**job, **match}
        else:
            job = {**job, "score": 0, "meets_filters": False,
                    "filter_notes": "Could not match scoring response to this job.",
                    "reasoning": ""}
        merged.append(job)

    return merged
