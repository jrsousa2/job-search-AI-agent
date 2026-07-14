"""
Generates a tailored resume + cover letter for ONE job, and renders both
to PDF, following the naming convention from Claude.md:

    <YYYY-MM-DD>_<Company>_<Remote-or-Hybrid>_Resume.pdf
    <YYYY-MM-DD>_<Company>_<Remote-or-Hybrid>_CoverLetter.pdf
"""

import os
import re
import json
import datetime
import requests
from jinja2 import Template
from weasyprint import HTML
from pypdf import PdfReader

import config

REQUIRED_HEALTH_LINE = (
    "I took a break from work for health reasons and am now fully ready "
    "and excited to return to work."
)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


def _safe_filename_part(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "", text.replace(" ", ""))


def _call_claude_for_documents(job: dict, claude_md: str, og_resume: str, projects: str) -> dict:
    system_prompt = f"""
You are tailoring a resume and cover letter for ONE specific job, per
these instructions:

=== FULL INSTRUCTIONS (Claude.md) ===
{claude_md}
=== END INSTRUCTIONS ===

=== MASTER RESUME (og-resume.md) -- do not invent anything beyond this ===
{og_resume}
=== END MASTER RESUME ===

=== SECONDARY PROFILE (projects.md) ===
{projects}
=== END SECONDARY PROFILE ===

Rules:
- Never invent experience, certifications, education, or skills not
  present in the two source documents above.
- The tailored resume must fit within 3 pages -- be concise, prioritize
  the most relevant experience for THIS job, and trim less relevant
  bullets rather than including everything.
- Optimize for ATS keyword matching against the job description.
- The cover letter must include, briefly, positively, and confidently,
  a version of this exact idea: "{REQUIRED_HEALTH_LINE}"
- The cover letter should be 3-4 short paragraphs.

Respond with ONLY valid JSON (no markdown fences, no commentary) in
this exact schema:

{{
  "resume": {{
    "full_name": "string",
    "contact": {{
      "location": "string, e.g. city/state",
      "phone": "string",
      "email": "string, no mailto: prefix",
      "linkedin_url": "string, full https:// URL",
      "linkedin_display": "string, short display text e.g. linkedin.com/in/handle",
      "github_url": "string, full https:// URL",
      "github_display": "string, short display text e.g. github.com/handle"
    }},
    "summary": "string",
    "skills": "string",
    "experience": [
      {{"title": "string", "company": "string", "location": "string",
        "dates": "string", "bullets": ["string", "..."]}}
    ],
    "education": [
      {{"degree": "string", "school": "string", "dates": "string"}}
    ]
  }},
  "cover_letter": {{
    "paragraphs": ["string", "string", "string"]
  }}
}}
"""

    user_content = f"""
=== TARGET JOB ===
Company: {job['company']}
Title: {job['title']}
Location: {job['location']}
Work arrangement: {job['work_arrangement']}
Description:
{job.get('description', '(no description provided)')}
"""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": config.API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": config.MODEL,
            "max_tokens": 4000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_content}],
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Document generation response wasn't valid JSON:\n{text}\n\nError: {e}")


def generate_documents_for_job(job: dict, claude_md: str, og_resume: str, projects: str) -> dict:
    """
    Returns a dict with the paths of the generated resume/cover-letter PDFs
    and a warning if the resume exceeds 3 pages.
    """
    content = _call_claude_for_documents(job, claude_md, og_resume, projects)

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    company_part = _safe_filename_part(job["company"])
    work_type = "Hybrid" if "hybrid" in job.get("work_arrangement", "").lower() else "Remote"

    os.makedirs(config.RESUMES_DIR, exist_ok=True)
    resume_path = os.path.join(
        config.RESUMES_DIR, f"{date_str}_{company_part}_{work_type}_Resume.pdf"
    )
    letter_path = os.path.join(
        config.RESUMES_DIR, f"{date_str}_{company_part}_{work_type}_CoverLetter.pdf"
    )

    # --- Render resume ---
    with open(os.path.join(TEMPLATES_DIR, "resume_template.html"), encoding="utf-8") as f:
        resume_html = Template(f.read()).render(**content["resume"])
    HTML(string=resume_html).write_pdf(resume_path)

    # --- Render cover letter ---
    with open(os.path.join(TEMPLATES_DIR, "cover_letter_template.html"), encoding="utf-8") as f:
        letter_html = Template(f.read()).render(
            full_name=content["resume"]["full_name"],
            contact=content["resume"]["contact"],
            date=datetime.datetime.now().strftime("%B %d, %Y"),
            company=job["company"],
            job_title=job["title"],
            paragraphs=content["cover_letter"]["paragraphs"],
        )
    HTML(string=letter_html).write_pdf(letter_path)

    page_count = len(PdfReader(resume_path).pages)
    warning = None
    if page_count > 3:
        warning = f"Resume for {job['company']} rendered at {page_count} pages (limit is 3)."

    return {"resume_path": resume_path, "letter_path": letter_path, "page_warning": warning}
