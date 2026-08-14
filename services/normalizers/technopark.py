"""Normalize Technopark jobs into the VisionBoard schema."""

from datetime import datetime


def _normalize_posted_date(value):
    value = str(value or "").strip()
    if not value:
        return ""

    for fmt in (
        "%d,%B %Y",
        "%d, %B %Y",
        "%d,%B,%Y",
        "%d, %B, %Y",
        "%d,%b %Y",
        "%d, %b %Y",
        "%d,%b,%Y",
        "%d, %b, %Y",
    ):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return value


def normalize(job):
    if not job:
        return None

    return {
        "job_id": str(job.get("job_id", "")),
        "title": str(job.get("title", "")).strip(),
        "company": str(job.get("company", "")).strip(),
        "location": str(job.get("location", "")).strip(),
        "country": str(job.get("country", "India")).strip(),
        "employment_type": str(job.get("employment_type", "")).strip(),
        "skills": str(job.get("skills", "")).strip(),
        "salary": str(job.get("salary", "")).strip(),
        "description": str(job.get("description", "")).strip(),
        "source": "Technopark",
        "apply_url": str(job.get("apply_url", "")).strip(),
        "posted_date": _normalize_posted_date(job.get("posted_date", "")),
        "closing_date": _normalize_posted_date(job.get("closing_date", "")),
    }
