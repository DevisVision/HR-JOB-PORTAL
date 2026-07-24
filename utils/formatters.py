"""
utils/formatters.py

Formatting helpers for VisionBoard Career Portal.
"""

from datetime import datetime


# ==========================================================
# Title
# ==========================================================

def format_title(title):
    """
    Format job title.
    """
    if not title or str(title).strip() == "":
        return "Untitled Position"

    return str(title).strip()


# ==========================================================
# Company
# ==========================================================

def format_company(company):
    """
    Format company name.
    """
    if not company or str(company).strip() == "":
        return "Confidential Company"

    return str(company).strip()


# ==========================================================
# Salary / Package
# ==========================================================

def format_salary(salary):
    """
    Format salary/package.
    """
    if not salary or str(salary).strip() == "":
        return "Package: Not Disclosed"

    return f"Package: {salary}"


# ==========================================================
# Location
# ==========================================================

def format_location(location, country):
    """
    Combine location and country.
    """
    location = str(location).strip() if location else "Location Not Specified"
    country = str(country).strip() if country else ""

    if country:
        return f"{location}, {country}"

    return location


# ==========================================================
# Employment Type
# ==========================================================

def format_employment(employment):
    """
    Format employment type.
    """
    if not employment or str(employment).strip() == "":
        return "Employment: Not Specified"

    return f"Employment: {employment}"


# ==========================================================
# Work Mode
# ==========================================================

def format_work_mode(location):
    """
    Detect work mode.
    """

    if not location:
        return "On-site"

    text = str(location).lower()

    if "remote" in text:
        return "Remote"

    if "hybrid" in text:
        return "Hybrid"

    return "On-site"


# ==========================================================
# Experience
# ==========================================================

def format_experience(experience):
    """
    Format experience.
    """
    if not experience:
        return "Experience: Not Specified"

    return f"Experience: {experience}"


# ==========================================================
# Skills
# ==========================================================

def format_skills(skills):
    """
    Convert skills into a readable string.
    """

    if not skills:
        return "Skills not available"

    if isinstance(skills, list):
        return " • ".join(str(skill).strip() for skill in skills)

    return str(skills).strip()


# ==========================================================
# Description
# ==========================================================

def format_description(description, max_length=250):
    """
    Short description for job cards.
    """

    if not description:
        return "No job description available."

    description = (
        str(description)
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )

    if len(description) <= max_length:
        return description

    return description[:max_length].rstrip() + "..."


# ==========================================================
# Apply URL
# ==========================================================

def format_apply_url(url):
    """
    Validate Apply URL.
    """

    if not url:
        return None

    url = str(url).strip()

    if url.startswith("http://") or url.startswith("https://"):
        return url

    return None


# ==========================================================
# Source
# ==========================================================

def format_source(source):
    """
    Format job source.
    """

    if not source:
        return "Source: Unknown"

    return f"Source: {source}"


# ==========================================================
# Posted Date
# ==========================================================

def format_posted(posted):
    """
    Format posted date.
    """

    if not posted:
        return "Posted: Recently"

    return f"Posted: {posted}"


# ==========================================================
# Company Initials
# ==========================================================

def get_company_initials(company):
    """
    Return company initials.
    """

    company = format_company(company)

    words = company.split()

    if len(words) == 1:
        return words[0][:2].upper()

    return (words[0][0] + words[1][0]).upper()


# ==========================================================
# Verified Badge
# ==========================================================

def is_verified_source(source):
    """
    Trusted job sources.
    """

    trusted_sources = {
        "Adzuna",
        "Arbeitnow",
        "Greenhouse",
        "Lever",
        "Remotive",
    }

    return str(source).strip() in trusted_sources