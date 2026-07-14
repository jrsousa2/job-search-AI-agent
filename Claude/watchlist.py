"""
Uses Claude's web_search tool (via the API) to find NEW companies matching
the candidate's target profile, and writes data/watchlist_suggestions.json.

Per Claude.md: never modifies watchlist.json, only ever writes the
suggestions file for manual review.
"""

import os
import json
import requests

import config


def discover_watchlist_companies(claude_md: str, og_resume: str, existing_watchlist: list) -> list:
    existing_names = [c.get("company", "") for c in existing_watchlist] if existing_watchlist else []

    system_prompt = f"""
You are researching companies that would be strong job-search targets
for this candidate, based on their profile and preferences below.

=== FULL INSTRUCTIONS (Claude.md) ===
{claude_md}
=== END INSTRUCTIONS ===

=== CANDIDATE RESUME (for context on industry/skills fit) ===
{og_resume}
=== END RESUME ===

Companies already on the watchlist (do NOT suggest these again):
{json.dumps(existing_names)}

Use web search to find companies that:
- Match the industry preferences in the instructions (insurance,
  banking, big tech, health care, financial services, or a very strong
  overall match in another industry)
- Are large (500+ employees preferred)
- Have an active, identifiable careers page on a known ATS platform
  (Greenhouse, Lever, Ashby, or Workday)

For each suggested company, search for its actual careers page and
identify the ATS platform and slug (e.g. for Greenhouse the slug is the
part after boards.greenhouse.io/<slug>).

When you're done researching, respond with ONLY a JSON array (no
markdown fences, no commentary) in this schema:

[
  {{
    "company": "string",
    "platform": "greenhouse|lever|ashby|workday",
    "slug": "string",
    "careers_url": "string",
    "reason_for_suggestion": "string, 1 sentence"
  }}
]

Only include companies where you actually found a valid ATS careers
page through search -- do not guess or fabricate slugs/URLs.
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
            "messages": [{"role": "user", "content": "Find 5-10 new candidate companies."}],
            "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        },
        timeout=300,
    )
    response.raise_for_status()
    data = response.json()

    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    # The model may emit some prose around the JSON despite instructions;
    # try to isolate the array.
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        text = text[start:end + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Watchlist discovery response wasn't valid JSON:\n{text}\n\nError: {e}")


def load_existing_watchlist(path: str) -> list:
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_suggestions(suggestions: list):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    out_path = os.path.join(config.DATA_DIR, "watchlist_suggestions.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(suggestions, f, indent=2)
    return out_path
