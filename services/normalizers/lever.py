"""Lever Job Normalizer."""


def normalize(job):
    categories = job.get("categories", {}) or {}
    created = job.get("createdAt") or job.get("created_at") or job.get("updatedAt") or ""

    return {
        "job_id": f"lever_{job.get('id')}",
        "title": job.get("text", ""),
        "company": job.get("company_name", ""),
        "location": categories.get("location", ""),
        "country": "",
        "employment_type": categories.get("commitment", ""),
        "skills": "",
        "salary": "",
        "description": job.get("descriptionPlain", ""),
        "source": "Lever",
        "apply_url": job.get("hostedUrl", ""),
        "posted_date": created,
    }
