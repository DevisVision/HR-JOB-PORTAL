"""
Company Logo Helper

Generates company logo URLs automatically.
"""

import re


def get_company_logo(company: str) -> str:
    """
    Returns a logo URL for a company.

    Example:
        Microsoft
            -> https://logo.clearbit.com/microsoft.com
    """

    if not company:
        return ""

    company = company.lower().strip()

    # Remove special characters
    company = re.sub(r"[^a-z0-9 ]", "", company)

    company = company.replace(" ", "")

    # Common mappings
    mappings = {
        "tcs": "tcs.com",
        "tataconsultancyservices": "tcs.com",
        "infosys": "infosys.com",
        "wipro": "wipro.com",
        "hcl": "hcltech.com",
        "hcltech": "hcltech.com",
        "cognizant": "cognizant.com",
        "accenture": "accenture.com",
        "capgemini": "capgemini.com",
        "ey": "ey.com",
        "ernstandyoung": "ey.com",
        "pwc": "pwc.com",
        "deloitte": "deloitte.com",
        "kpmg": "kpmg.com",
        "ibm": "ibm.com",
        "oracle": "oracle.com",
        "amazon": "amazon.com",
        "google": "google.com",
        "microsoft": "microsoft.com",
        "meta": "meta.com",
        "airbnb": "airbnb.com",
        "mongodb": "mongodb.com",
        "stripe": "stripe.com",
        "anthropic": "anthropic.com",
        "ust": "ust.com",
        "ibs": "ibssoftware.com",
        "ibssoftware": "ibssoftware.com",
        "allianz": "allianz.com",
    }

    if company in mappings:
        domain = mappings[company]
    else:
        domain = f"{company}.com"

    return f"https://logo.clearbit.com/{domain}"