import json
import os
import re
from datetime import date, timedelta

from anthropic import Anthropic

from extensions import db
from models import Company, Opportunity

MODEL = "claude-opus-4-8"
DEFAULT_STAGE = "Wishlist"
MAX_NAME_LEN = 100

# Guards against garbled/hallucinated model output making it into the DB.
# Real job titles/company names legitimately use dashes, slashes, colons,
# ampersands, and parentheses ("Software Engineer (Backend)") — so instead of
# blocking punctuation *runs* (which false-positives on "Engineer – Remote"),
# this allowlists the character set real titles use and rejects anything
# with brackets, quotes, semicolons, or other code-fragment punctuation.
_HAS_LETTER = re.compile(r"[A-Za-z]")
_ALLOWED_CHARS = re.compile(r"^[A-Za-z0-9 \-‐-―,./&'’():+#!]+$")


def _is_sane_text(value, max_length):
    if not value or not (1 < len(value) <= max_length):
        return False
    if not _HAS_LETTER.search(value):
        return False
    if not _ALLOWED_CHARS.match(value):
        return False
    return True


def _clean_job(job):
    """Validate and normalize a single job dict, or return None to drop it."""
    company_name = (job.get("company_name") or "").strip()
    role_title = (job.get("role_title") or "").strip()
    location = (job.get("location") or "").strip() or None
    url = (job.get("url") or "").strip()
    salary = job.get("salary")

    if not _is_sane_text(company_name, MAX_NAME_LEN) or not _is_sane_text(role_title, MAX_NAME_LEN):
        return None
    if not url.startswith("http://") and not url.startswith("https://"):
        return None
    if salary is not None and (not isinstance(salary, (int, float)) or isinstance(salary, bool) or salary < 0):
        salary = None

    return {
        "company_name": company_name,
        "role_title": role_title,
        "location": location,
        "url": url,
        "salary": salary,
    }

JOB_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "jobs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "role_title": {"type": "string"},
                    "location": {"type": "string"},
                    "salary": {"type": ["number", "null"]},
                    "url": {"type": "string"},
                },
                "required": ["company_name", "role_title", "location", "salary", "url"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["jobs"],
    "additionalProperties": False,
}


def search_jobs_with_claude(query, limit):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set in the environment")

    client = Anthropic(api_key=api_key)

    today = date.today()
    one_week_ago = today - timedelta(days=7)

    prompt = (
        f"Today's date is {today.isoformat()}. Search the web for up to {limit} job postings "
        f"matching: {query}. Only include postings first published within the last week "
        f"(on or after {one_week_ago.isoformat()}) — favor search terms like \"past week\" or "
        "\"posted in the last 7 days\", and check any posted/updated date shown in the search "
        "result or page title. If a posting's date isn't visible and you can't confirm it's "
        "recent, leave it out rather than guessing. "
        "Use the title, company, and URL exactly as they appear in your search results — "
        "do not fetch each link individually, and do not invent a company, role, or URL that "
        "didn't come from a search result. It's fine if a result is a job board listing rather "
        "than a company's own careers page. Prefer distinct companies. For salary, only fill it "
        "in if it's shown in the search result; otherwise use null. If you run the search and "
        "genuinely find nothing relevant from the last week, return an empty jobs array rather "
        "than including older postings."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        output_config={"format": {"type": "json_schema", "schema": JOB_SEARCH_SCHEMA}},
        messages=[{"role": "user", "content": prompt}],
    )

    text = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text)
    raw_jobs = data.get("jobs", [])[:limit]

    jobs = []
    for job in raw_jobs:
        cleaned = _clean_job(job)
        if cleaned is not None:
            jobs.append(cleaned)
    return jobs


def add_jobs_to_db(jobs):
    added = []
    skipped = []

    for job in jobs:
        company_name = job["company_name"]
        role_title = job["role_title"]

        company = Company.query.filter(
            db.func.lower(Company.name) == company_name.lower()
        ).first()
        if not company:
            company = Company(name=company_name, location=job.get("location"))
            db.session.add(company)
            db.session.flush()

        existing = Opportunity.query.filter(
            db.func.lower(Opportunity.name) == role_title.lower(),
            Opportunity.company_id == company.id,
        ).first()
        if existing:
            skipped.append({"company": company_name, "role": role_title})
            continue

        opportunity = Opportunity(
            name=role_title,
            value=job.get("salary"),
            stage=DEFAULT_STAGE,
            company_id=company.id,
        )
        db.session.add(opportunity)
        added.append({
            "company": company_name,
            "role": role_title,
            "location": job.get("location"),
            "url": job.get("url"),
        })

    db.session.commit()
    return added, skipped
