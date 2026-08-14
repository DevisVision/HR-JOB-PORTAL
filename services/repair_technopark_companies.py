"""Repair malformed Technopark company names in the local database.

Run after upgrading V5.5 if the database contains rows from an older
Technopark collector. The normal six-hour sync will also replace these rows,
but this utility lets the HR portal owner repair the current database without
waiting for the next scheduled sync.
"""

import re
import sqlite3
from urllib.parse import urlparse

DB = "database/jobs.db"
PREFIX = "technopark job posting for"

KNOWN = {
    "ust.com": "UST",
    "www.ust.com": "UST",
}


def company_from_url(url):
    host = urlparse(url or "").netloc.lower()
    if host in KNOWN:
        return KNOWN[host]
    if host.startswith("www."):
        host = host[4:]
    if not host or host.endswith("technopark.in"):
        return ""
    label = host.split(".")[0]
    if label in {"gmail", "yahoo", "hotmail", "outlook", "rediffmail"}:
        return ""
    return label.replace("-", " ").title()


conn = sqlite3.connect(DB)
rows = conn.execute(
    "SELECT job_id, company, apply_url FROM jobs "
    "WHERE lower(source)='technopark' AND lower(company) LIKE ?",
    (PREFIX + "%",),
).fetchall()

updated = 0
for job_id, company, url in rows:
    new_company = company
    # URL query contains the job title, not the employer; only use the host.
    candidate = company_from_url(url)
    if candidate:
        new_company = candidate
    if new_company != company:
        conn.execute("UPDATE jobs SET company=?, updated_at=CURRENT_TIMESTAMP WHERE job_id=?", (new_company, job_id))
        updated += 1

conn.commit()
conn.close()
print(f"Technopark company repair complete. Updated {updated} rows.")
