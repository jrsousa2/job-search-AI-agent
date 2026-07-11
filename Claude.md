# Claude.md

## Purpose

You will receive a file named `new_jobs.md` containing entirely new job postings.

Evaluate each job against my two resume Markdown files and rank them from **0–100** based on how well they match my experience.

---

## Job URL Verification

Before scoring or presenting any job, verify that the job posting URL is valid and points to an active, direct company ATS posting.

Rules:
- Do not trust aggregator links, search result links, or stale URLs.
- Prefer the company's actual careers page or ATS URL (Greenhouse, Lever, Ashby, Workday, etc.).
- Verify that the posting page loads successfully and corresponds to the specific job title and company.
- If the URL is invalid, expired, redirected to a generic careers page, or the posting no longer exists:
  - Do not score the job.
  - Log it as skipped with the reason.
- Never assume a URL is valid only because it came from a search result or API response.

---

## Scoring Rules

- Score jobs from **0 to 100**.
- Give the highest weight to skills that appear in my **main resume**.
- If I possess a skill that exists only in my secondary resume, count it as a positive but with a lower weight.
- If the job strictly requires skills I don't have, score it lower.
- Consider overall experience, seniority, technologies, responsibilities, and industry fit.
- Prioritize big companies (more than 500 employees).

---

## Job Filters

Only consider jobs that meet all applicable criteria:

- **Remote** positions.
- **Hybrid** positions only if they require **3 days/week in the office or fewer**.
- I am willing to relocate anywhere within:
  - Florida
  - Texas
  - North Carolina
- Contract and full-time (FTE) positions are both acceptable.
- I am a **U.S. citizen** and **do not require visa sponsorship**.

Ignore jobs that do not satisfy these requirements.

---

## Industry Preference

Prefer jobs in:

1. Insurance
2. Banking / Financial Services
3. Prioritize big companies (more than 500 employees).
4. Any industry if the match with my experience is very good.

However, if there are not enough good matches, include other industries until there are **at least 10 recommended jobs**.

---

## Applications

**Do NOT automatically apply to any jobs.**

---

## Tailored Documents

Generate tailored resumes and tailored cover letters as PDFs **only for the ten highest-scoring jobs**.

### Resume

Customize the resume based on the master resume to emphasize the most relevant experience **without inventing any qualifications**.
Never exceed 3 pages.

### Cover Letter

Customize each cover letter for the position.

Include that:

> I took a break from work for health reasons and am now fully ready and excited to return to work.

Keep the explanation brief, positive, and confident.

---

## File Naming

Name each tailored resume and cover letter using:

```
<Company>_<Remote-or-Hybrid>_<YYYY-MM-DD>_Resume.pdf
<Company>_<Remote-or-Hybrid>_<YYYY-MM-DD>_CoverLetter.pdf
```

Example:

```
Progressive_Remote_2026-07-10_Resume.md
Progressive_Remote_2026-07-10_CoverLetter.md
```

---

## Job Links

Generate a Markdown file containing the application links for all recommended jobs.

Filename:

```
Job_URLs_<YYYY-MM-DD>.md
```

For each job include:

- Company
- Job title
- Score
- Work arrangement (Remote/Hybrid)
- Application URL

---

## Output Directory

Save every generated file into:

```
daily-digest/
```

This includes:

- Tailored resumes
- Tailored cover letters
- Job_URLs file

---

## General Rules

- Never invent experience, certifications, education, or skills.
- Preserve factual accuracy.
- Optimize resumes for ATS compatibility.
- Tailor documents specifically for each job.
- Rank jobs in descending score order.
- Recommend only the ten highest-scoring jobs.       