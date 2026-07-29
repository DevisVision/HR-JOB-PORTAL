"""
=========================================================
VisionBoard Career Portal
Job Ranking Engine
=========================================================
"""

from datetime import datetime

# =========================================================
# Preferred Companies
# =========================================================

FORTUNE_PRIORITY = {
    "IBM": 100,
    "MICROSOFT": 100,
    "GOOGLE": 100,
    "AMAZON": 100,
    "APPLE": 100,
    "META": 100,
    "NETFLIX": 100,

    "ACCENTURE": 95,
    "COGNIZANT": 95,
    "CAPGEMINI": 95,
    "EY": 95,
    "ERNST & YOUNG": 95,
    "KPMG": 95,
    "DELOITTE": 95,
    "PWC": 95,

    "UST": 90,
    "CISCO": 90,
    "ORACLE": 90,
    "ALLIANZ": 90,
    "WIPRO": 90,
    "TECH MAHINDRA": 90,
    "INFOSYS": 90,
    "TCS": 90,
    "HCL": 90,
    "IBS": 85
}

# =========================================================
# India Cities
# =========================================================

INDIA_KEYWORDS = [
    "india",
    "bangalore",
    "bengaluru",
    "hyderabad",
    "pune",
    "mumbai",
    "gurgaon",
    "gurugram",
    "noida",
    "delhi",
    "new delhi",
    "chennai",
    "coimbatore",
    "kochi",
    "cochin",
    "thiruvananthapuram",
    "trivandrum",
    "mysore",
    "kolkata",
    "ahmedabad"
]

REMOTE_KEYWORDS = [
    "remote",
    "work from home",
    "wfh",
    "anywhere"
]


# =========================================================
# Company Score
# =========================================================

def company_score(company):

    if not company:
        return 0

    company = company.upper().strip()

    for preferred, score in FORTUNE_PRIORITY.items():

        if preferred in company:
            return score

    return 0


# =========================================================
# India Score
# =========================================================

def india_score(job):

    text = (
        str(job.get("country", "")) + " " +
        str(job.get("location", ""))
    ).lower()

    if any(city in text for city in INDIA_KEYWORDS):
        return 40

    return 0


# =========================================================
# Remote Score
# =========================================================

def remote_score(job):

    text = (
        str(job.get("country", "")) + " " +
        str(job.get("location", "")) + " " +
        str(job.get("employment_type", ""))
    ).lower()

    if any(word in text for word in REMOTE_KEYWORDS):
        return 25

    return 0


# =========================================================
# Recent Job Score
# =========================================================

def recency_score(posted_date):

    if not posted_date:
        return 0

    try:

        post_date = datetime.strptime(
            str(posted_date)[:10],
            "%Y-%m-%d"
        )

        days = (datetime.now() - post_date).days

        if days <= 1:
            return 30

        if days <= 3:
            return 25

        if days <= 7:
            return 20

        if days <= 15:
            return 10

    except Exception:

        return 0

    return 0


# =========================================================
# Skill Score
# =========================================================

PREFERRED_SKILLS = [
    "azure",
    "spark",
    "pyspark",
    "sql",
    "python",
    "adf",
    "databricks",
    "fabric",
    "snowflake",
    "genai",
    "ai",
    "synapse"
]


def skill_score(job):

    text = (
        str(job.get("skills", "")) + " " +
        str(job.get("description", ""))
    ).lower()

    score = 0

    for skill in PREFERRED_SKILLS:

        if skill in text:
            score += 3

    return score


# =========================================================
# Calculate Score
# =========================================================

def calculate_score(job):

    score = 0

    score += company_score(job.get("company"))

    score += india_score(job)

    score += remote_score(job)

    score += recency_score(job.get("posted_date"))

    score += skill_score(job)

    return score


# =========================================================
# Remove Duplicates
# =========================================================

def remove_duplicates(jobs):

    seen = set()

    cleaned = []

    for job in jobs:

        key = (
            str(job.get("title", "")).lower(),
            str(job.get("company", "")).lower(),
            str(job.get("location", "")).lower()
        )

        if key in seen:
            continue

        seen.add(key)

        cleaned.append(job)

    return cleaned


# =========================================================
# Rank Jobs
# =========================================================

def rank_jobs(jobs):

    jobs = remove_duplicates(jobs)

    for job in jobs:

        job["ranking_score"] = calculate_score(job)

    jobs.sort(
        key=lambda x: (
            x.get("ranking_score", 0),
            str(x.get("posted_date", ""))
        ),
        reverse=True
    )

    return jobs