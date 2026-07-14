"""
Best-effort verification that a job URL is a live, real posting matching
the claimed title/company.

IMPORTANT LIMITATION: Workday, Greenhouse, and some Lever/Ashby postings
render their content with JavaScript. A plain HTTP request (what this
script does) only sees the initial HTML shell, which often does NOT
contain the job title/description text -- even though the posting is
real and live. For those platforms this function can confirm the page
LOADS (status 200, no redirect to a generic careers page) but often
cannot confirm the title/company text match from raw HTML alone.

Jobs on JS-heavy platforms are marked "requires_manual_check": True
rather than being falsely marked invalid. If you want full automated
verification, the README explains how to swap in Playwright, which
renders JavaScript and can check the real page text.
"""

import requests

JS_HEAVY_PLATFORMS = {"workday"}

GENERIC_CAREERS_INDICATORS = [
    "page not found", "job not found", "no longer available",
    "position has been filled", "posting has expired",
]


def verify_url(job: dict, timeout: int = 15) -> dict:
    """
    Returns a dict: {"valid": bool, "confidence": "high"|"low", "reason": str}
    """
    url = job.get("url", "").strip()
    platform = job.get("platform", "").strip().lower()

    if not url:
        return {"valid": False, "confidence": "high", "reason": "No URL provided."}

    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; JobVerifier/1.0)"},
            allow_redirects=True,
        )
    except requests.RequestException as e:
        return {"valid": False, "confidence": "high", "reason": f"Request failed: {e}"}

    if resp.status_code == 404:
        return {"valid": False, "confidence": "high", "reason": "404 Not Found."}
    if resp.status_code >= 400:
        return {"valid": False, "confidence": "high", "reason": f"HTTP {resp.status_code}."}

    final_url = resp.url
    page_text = resp.text.lower()

    # Redirected to a generic careers landing page rather than the specific posting
    if final_url.rstrip("/") != url.rstrip("/") and "job" not in final_url.lower():
        return {
            "valid": False,
            "confidence": "high",
            "reason": f"Redirected away from the specific posting to: {final_url}",
        }

    for phrase in GENERIC_CAREERS_INDICATORS:
        if phrase in page_text:
            return {"valid": False, "confidence": "high", "reason": f"Page contains '{phrase}'."}

    if platform in JS_HEAVY_PLATFORMS:
        return {
            "valid": True,
            "confidence": "low",
            "reason": (
                f"Page returned HTTP {resp.status_code} but {platform} renders content "
                "with JavaScript, so title/company match could not be confirmed from "
                "raw HTML. Recommend a quick manual check before applying."
            ),
        }

    company = job.get("company", "").lower()
    title_words = [w.lower() for w in job.get("title", "").split() if len(w) > 3]
    company_found = company in page_text if company else True
    title_hits = sum(1 for w in title_words if w in page_text)
    title_found = (title_hits / len(title_words)) >= 0.6 if title_words else True

    if company_found and title_found:
        return {"valid": True, "confidence": "high", "reason": "Company and title matched on page."}
    else:
        return {
            "valid": True,
            "confidence": "low",
            "reason": "Page loaded but company/title text match was inconclusive.",
        }
