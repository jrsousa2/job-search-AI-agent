"""
Parses new_jobs.md, which contains one or more jobs in this format:

## Job N

**Company:** X
**Title:** Y
**Location:** Z
**Remote:** Yes/No
**Work Arrangement:** Remote/Hybrid/Onsite
**Platform:** workday/greenhouse/lever/ashby/...
**URL:** https://...
**Job ID:** ...
**Slug:** ...

### Description
<free text, possibly empty>

---
"""

import re


FIELD_PATTERN = re.compile(r"\*\*([^*]+):\*\*\s*(.*)")


def parse_jobs(new_jobs_md: str) -> list[dict]:
    # Split on "## Job <n>" headers
    blocks = re.split(r"^##\s+Job\s+\d+\s*$", new_jobs_md, flags=re.MULTILINE)
    jobs = []

    for block in blocks[1:]:  # blocks[0] is the "# New Jobs" preamble
        job = {
            "company": "",
            "title": "",
            "location": "",
            "remote": "",
            "work_arrangement": "",
            "platform": "",
            "url": "",
            "job_id": "",
            "slug": "",
            "description": "",
        }

        # Split off the Description section if present
        desc_split = re.split(r"###\s*Description", block, maxsplit=1)
        header_part = desc_split[0]
        desc_part = desc_split[1] if len(desc_split) > 1 else ""
        # Description ends at a line of dashes ("---") if present
        desc_part = re.split(r"^-{3,}\s*$", desc_part, maxsplit=1, flags=re.MULTILINE)[0]
        job["description"] = desc_part.strip()

        for line in header_part.splitlines():
            m = FIELD_PATTERN.match(line.strip())
            if not m:
                continue
            key, value = m.group(1).strip().lower(), m.group(2).strip()
            key = key.replace(" ", "_")
            if key in job:
                job[key] = value

        if job["company"] or job["title"]:
            jobs.append(job)

    return jobs


if __name__ == "__main__":
    import sys
    with open(sys.argv[1], encoding="utf-8") as f:
        content = f.read()
    for j in parse_jobs(content):
        print(j)
