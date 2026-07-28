import requests
from urllib.parse import quote


def get_company_logo(company_name: str) -> str:
    """
    Returns a Clearbit logo URL if available.
    Falls back to empty string.
    """

    if not company_name:
        return ""

    company = company_name.lower().strip()

    replacements = {
        "tcs": "tcs.com",
        "infosys": "infosys.com",
        "wipro": "wipro.com",
        "accenture": "accenture.com",
        "capgemini": "capgemini.com",
        "cognizant": "cognizant.com",
        "ibm": "ibm.com",
        "google": "google.com",
        "amazon": "amazon.com",
        "microsoft": "microsoft.com",
        "oracle": "oracle.com",
        "airbnb": "airbnb.com",
        "stripe": "stripe.com",
        "mongodb": "mongodb.com",
        "cgi": "cgi.com",
        "ey": "ey.com",
        "ernst & young": "ey.com",
        "kpmg": "kpmg.com",
        "deloitte": "deloitte.com",
        "pwc": "pwc.com",
        "ust": "ust.com",
        "ust global": "ust.com",
        "allianz": "allianz.com",
        "bosch": "bosch.com",
        "siemens": "siemens.com",
    }

    if company in replacements:
        domain = replacements[company]
    else:
        company = company.replace("&", "")
        company = company.replace(",", "")
        company = company.replace(".", "")
        company = company.replace("  ", " ")
        company = company.replace(" ", "")
        domain = f"{company}.com"

    logo = f"https://logo.clearbit.com/{quote(domain)}"

    try:

        r = requests.get(
            logo,
            timeout=5,
        )

        if r.status_code == 200:
            return logo

    except:
        pass

    return ""